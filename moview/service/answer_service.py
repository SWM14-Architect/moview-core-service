import re

from moview.modules.question_generator import AnswerFilter, AnswerCategoryClassifier, AnswerSubCategoryClassifier, \
    FollowUpQuestionGiver
from moview.modules.answer_evaluator.interview_answer_scorer import InterviewAnswerScorer


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
        # todo 이 부분에 이전 질문들 관리하는 멤버 변수나 객체 추가 필요 (그리고 이전 질문들은 세션으로 묶여야 한다...)
        pass

    def determine_next_action_of_interviewer(self, job_group: str, question: str, answer: str):
        """
        interviewer의 질문과 interviewee의 답변을 받아서, intervieweer의 다음 행동을 결정하는 메서드

        Args:
            job_group: 직군
            question: interviewer의 질문
            answer: interviewee의 답변

        Returns:
            1. 심화질문 o인 경우, 심화 질문 반환
            2. 질문 재요청인 경우, 좀 더 구체적인 질문 생성 요청
            3. 심화질문 x인 경우, 다음 초기 질문 진행
            4. 심화 질문 x, 다음 초기 질문 x인 경우, interview 종료

        """
        # 답변 내용을 분류 (적절한가, 재요청인가 등)
        categories_ordered_pair = self.__classify_answer_of_interviewee(job_group=job_group, question=question,
                                                                        answer=answer)

        # 질문과 답변 내용을 전달하여 사용자 답변에 대한 평가
        score_from_llm = self.scorer.score_by_main_and_subcategories(question=question, answer=answer,
                                                                     categories_ordered_pair=categories_ordered_pair)

        # todo 평가 내용 정규 표현식 적용해서 가공 필요

        # todo 가공한 평가 내용 어딘가에 저장 필요

        # 평가 결과에 따라 다음 행동 결정

        # 심화 질문 o인 경우, 심화 질문 반환
        followup_question = self.__get_followup_question(job_group=job_group, question=question, answer=answer,
                                                         categories_ordered_pair=categories_ordered_pair)
        pass

    def __classify_answer_of_interviewee(self, job_group: str, question: str, answer: str) -> str:
        # 적절하지 않은 답변을 걸러냅니다.
        check = self.filter.exclude_invalid_answer(job_group=job_group, question=question, answer=answer)

        number = find_first_number(check)

        if number == "1":
            raise ResubmissionRequestError()
        elif number == "2" or number == "3" or number == "4":
            raise InappropriateAnswerError()

        # todo 현재 질문을 이전 질문에 추가할 때, [세션 id] :[이전 질문리스트] 형태로 추가해야 함. 그래야 세션 별로 추적 가능

        # 면접 질문과 답변의 대분류
        categories = self.major_classifier.classify_category_of_answer(job_group=job_group, question=question,
                                                                       answer=answer)

        # 중분류
        return self.sub_classifier.classify_sub_category_of_answer(
            job_group=job_group, question=question,
            answer=answer, categories=categories)

    def __score_answer_of_interviewee(self):
        pass

    def __get_followup_question(self, job_group: str, question: str, answer: str, categories_ordered_pair: str) -> str:

        # # 꼬리 질문 출제
        # return  self.giver.give_followup_question(
        #     job_group=job_group, question=question, answer=answer,
        #     previous_questions=str(self.previous_question),
        #     categories_ordered_pair=categories_ordered_pair)  # todo <- previous question 말고 다른 걸로 대체 필요
        pass
