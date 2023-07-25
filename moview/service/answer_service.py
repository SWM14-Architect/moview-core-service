import re
from moview.modules.question_generator import AnswerFilter, AnswerCategoryClassifier, AnswerSubCategoryClassifier, \
    FollowUpQuestionGiver
from moview.modules.answer_evaluator.interview_answer_scorer import InterviewAnswerScorer
from moview.service.interviewee_data_vo import IntervieweeDataVO
from moview.service.interview_action_enum import InterviewActionEnum


# 정규 표현식으로 짜긴 했는데, 간혹 출력값이 이상하게 나올 수 있음. 이럴 떄는 문장 유사도 평가가 좋아보임. 그래서 이러한 함수 간 접합 부분에는 vector db를 쓰는게 나을 듯?
def find_first_number(text):
    match = re.search(r'\d+', text)
    if match:
        return match.group()
    else:
        return None


def find_first_yes_no(text):
    pattern = r'(yes|no)'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group()
    else:
        return None


class InappropriateAnswerError(Exception):
    def __init__(self, message="Inappropriate answer provided."):
        self.message = message
        super().__init__(self.message)


class ResubmissionRequestError(Exception):
    def __init__(self, message="A resubmission has been requested."):
        self.message = message
        super().__init__(self.message)


class AnswerService:
    def __init__(self):
        self.scorer = InterviewAnswerScorer()

        self.filter = AnswerFilter()
        self.major_classifier = AnswerCategoryClassifier()
        self.sub_classifier = AnswerSubCategoryClassifier()

        self.giver = FollowUpQuestionGiver()

    def determine_next_action_of_interviewer(self, job_group: str, question: str, answer: str,
                                             vo: IntervieweeDataVO) -> (IntervieweeDataVO, InterviewActionEnum):
        """
        interviewer의 질문과 interviewee의 답변을 받아서, intervieweer의 다음 행동을 결정하는 메서드

        Args:
            vo: 인터뷰 세션 모든 정보를 다 갖고 있는 vo. (db에 저장하는 걸로 바꿔야 합니다.)
            job_group: 직군
            question: interviewer의 질문
            answer: interviewee의 답변

        Returns:
            1. 심화질문 o인 경우, 심화 질문 반환 (심화질문 저장된 vo, 심화 질문 생성 완료 enum)
            2. 질문 재요청인 경우, 좀 더 구체적인 질문 생성 요청 ( vo, 재요청 enum)
            3. 적절하지 않은 답변의 경우, 다음 초기 질문 진행 (다음 초기질문 이행하는 vo, 적절하지 않은 답변 enum)
            4. 심화 질문 x, 다음 초기 질문 x인 경우, interview 종료 (심화질문 저장된 vo, interview 종료 enum)

        """

        # 답변 내용을 분류 (적절한가, 재요청인가 등) -> 대분류, 중분류를 받음.
        try:
            category_and_sub_category = self.__classify_answer_of_interviewee(job_group=job_group, question=question,
                                                                              answer=answer)
        except InappropriateAnswerError:
            # 적절하지 않은 답변인 경우, 다음 초기 질문 진행
            vo.give_next_initial_question()
            return vo, InterviewActionEnum.INAPPROPRIATE_ANSWER
        except ResubmissionRequestError:
            # todo 재요청인 경우, 좀 더 구체적인 질문 생성 요청으로 바꿔야 함. 현재는 다음 초기 질문 진행으로 해놓음.
            vo.give_next_initial_question()
            return vo, InterviewActionEnum.DIRECT_REQUEST

        # 질문과 답변 내용, 대분류와 중분류를 전달하여 사용자 답변에 대한 평가
        score_from_llm = self.scorer.score_by_main_and_subcategories(question=question, answer=answer,
                                                                     categories_ordered_pair=category_and_sub_category)
        # 평가 저장
        vo.save_score_of_interviewee(score_from_llm=score_from_llm)

        if vo.is_initial_questions_end() and vo.is_followup_questions_end():
            # 다음 초기 질문 x, 심화질문 x인 경우, interview 종료
            return vo, InterviewActionEnum.END_INTERVIEW
        elif not vo.is_initial_questions_end() and vo.is_followup_questions_end():
            # 다음 초기 질문 o, 심화질문 x인 경우, 다음 초기 질문 진행
            vo.give_next_initial_question()
            return vo, InterviewActionEnum.NEXT_INITIAL_QUESTION
        else:
            # 꼬리질문 출제
            followup_question = self.__get_followup_question(job_group=job_group, question=question, answer=answer,
                                                             categories_ordered_pair=category_and_sub_category,
                                                             vo=vo)
            vo.save_followup_question(followup_question)

            # 그외에 심화질문 o인 경우, 다음 꼬리 질문 진행
            return vo, InterviewActionEnum.CREATED_FOLLOWUP_QUESTION

    def __classify_answer_of_interviewee(self, job_group: str, question: str, answer: str) -> str:
        # 적절하지 않은 답변을 걸러냅니다.
        check = self.filter.exclude_invalid_answer(job_group=job_group, question=question, answer=answer)

        number = find_first_number(check)

        if number == "1":
            raise ResubmissionRequestError()
        elif number in ["2", "3", "4"]:
            raise InappropriateAnswerError()

        # 면접 질문과 답변의 대분류
        categories = self.major_classifier.classify_category_of_answer(job_group=job_group, question=question,
                                                                       answer=answer)

        # 중분류
        return self.sub_classifier.classify_sub_category_of_answer(
            job_group=job_group, question=question,
            answer=answer, categories=categories)

    def __get_followup_question(self, job_group: str, question: str, answer: str, categories_ordered_pair: str,
                                vo: IntervieweeDataVO) -> str:

        # 꼬리 질문 출제
        return self.giver.give_followup_question(
            job_group=job_group, question=question, answer=answer,
            previous_questions=str(vo.exclude_question_list),
            categories_ordered_pair=categories_ordered_pair)
