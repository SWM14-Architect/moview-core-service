import re
from moview.modules.question_generator import AnswerValidator, AnswerCategoryClassifier, AnswerSubCategoryClassifier, \
    FollowUpQuestionGiver
from moview.service.interviewee_answer.interviewer_action_enum import InterviewerActionEnum
from moview.repository.interviewee_data_repository import IntervieweeDataRepository, MongoConfig
from moview.domain.entity.interviewee_data_main_document import IntervieweeDataEntity
from moview.config.loggers.mongo_logger import execution_trace_logger, error_logger


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


class IntervieweeAnswerService:
    def __init__(self):
        self.repository = IntervieweeDataRepository(mongo_config=MongoConfig())

        self.filter = AnswerValidator()
        self.major_classifier = AnswerCategoryClassifier()
        self.sub_classifier = AnswerSubCategoryClassifier()

        self.giver = FollowUpQuestionGiver()

    def determine_next_action_of_interviewer(self, session_id, question: str, answer: str):
        """
        interviewer의 질문과 interviewee의 답변을 받아서, intervieweer의 다음 행동을 결정하는 메서드

        Args:
            session_id: flask session_id
            question: interviewer의 질문
            answer: interviewee의 답변

        Returns:
            1. 심화질문 o인 경우, 심화 질문 반환 (심화질문 저장된 vo, 심화 질문 생성 완료 enum)
            2. 질문 재요청인 경우, 좀 더 구체적인 질문 생성 요청 ( vo, 재요청 enum)
            3. 적절하지 않은 답변의 경우, 다음 초기 질문 진행 (다음 초기질문 이행하는 vo, 적절하지 않은 답변 enum)
            4. 심화 질문 x, 다음 초기 질문 x인 경우, interview 종료 (심화질문 저장된 vo, interview 종료 enum)

        """

        found_interview_data = self.repository.find_by_session_id(session_id=session_id)

        if found_interview_data is None:
            error_logger("Interview history not found.")
            raise Exception("Interview history not found.")

        # 답변 내용을 분류 (적절한가, 재요청인가 등) -> 대분류, 중분류를 받음.
        try:
            category_and_sub_category = self.__classify_answer_of_interviewee(
                job_group=found_interview_data.initial_input_data.job_group,
                question=question,
                answer=answer)

        except InappropriateAnswerError:
            # 적절하지 않은 답변인 경우, 다음 초기 질문 진행
            next_initial_question = found_interview_data.give_next_initial_question()

            execution_trace_logger("InappropriateAnswerError", next_initial_question=next_initial_question)

            self.repository.update(session_id=session_id, interviewee_data_entity=found_interview_data)

            if found_interview_data.is_initial_questions_end():  # 초기 질문 다 떨어지면 인터뷰 종료
                return [], InterviewerActionEnum.END_INTERVIEW
            else:
                return next_initial_question, InterviewerActionEnum.INAPPROPRIATE_ANSWER

        except ResubmissionRequestError:
            # todo 재요청인 경우, 좀 더 구체적인 질문 생성 요청으로 바꿔야 함. 현재는 다음 초기 질문 진행으로 해놓음.
            next_initial_question = found_interview_data.give_next_initial_question()

            execution_trace_logger("ResubmissionRequestError", next_initial_question=next_initial_question)

            self.repository.update(session_id=session_id, interviewee_data_entity=found_interview_data)

            if found_interview_data.is_initial_questions_end():  # 초기 질문 다 떨어지면 인터뷰 종료
                return [], InterviewerActionEnum.END_INTERVIEW
            else:
                return next_initial_question, InterviewerActionEnum.DIRECT_REQUEST

        # 답변에 대한 대분류, 중분류 저장
        found_interview_data.save_category_in_interviewee_answer_evaluations(question=question, answer=answer,
                                                                             category_and_sub_category=category_and_sub_category)

        updated_category_id = self.repository.update(session_id=session_id,
                                                     interviewee_data_entity=found_interview_data)

        if not found_interview_data.is_initial_questions_end() and found_interview_data.is_followup_questions_end():

            # 초기 질문 출제해보기
            next_initial_question = found_interview_data.give_next_initial_question()

            # 다음 초기 질문 x인 경우, interview 종료
            if found_interview_data.is_initial_questions_end():
                execution_trace_logger("END_INTERVIEW", followup_question=[])
                return [], InterviewerActionEnum.END_INTERVIEW
            # 다음 초기 질문 o인 경우, 다음 초기 질문 진행
            else:
                self.repository.update(session_id=updated_category_id,
                                       interviewee_data_entity=found_interview_data)
                execution_trace_logger("NEXT_INITIAL_QUESTION", next_initial_question=next_initial_question)
                return next_initial_question, InterviewerActionEnum.NEXT_INITIAL_QUESTION
        else:
            # 꼬리질문 출제
            followup_question = self.__get_followup_question(question=question, answer=answer,
                                                             categories_ordered_pair=category_and_sub_category,
                                                             found_interview_data=found_interview_data)

            found_interview_data.save_followup_question(followup_question=followup_question)

            self.repository.update(session_id=updated_category_id,
                                   interviewee_data_entity=found_interview_data)

            execution_trace_logger("CREATED_FOLLOWUP_QUESTION", followup_question=followup_question)

            # 그외에 심화질문 o인 경우, 다음 꼬리 질문 진행
            return followup_question, InterviewerActionEnum.CREATED_FOLLOWUP_QUESTION

    def __classify_answer_of_interviewee(self, job_group: str, question: str, answer: str) -> str:
        # 적절하지 않은 답변을 걸러냅니다.
        check = self.filter.validate_answer(job_group=job_group, question=question, answer=answer)

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

    def __get_followup_question(self, question: str, answer: str, categories_ordered_pair: str,
                                found_interview_data: IntervieweeDataEntity) -> str:

        previous_questions = found_interview_data.interview_questions.initial_question_list + found_interview_data.interview_questions.followup_question_list

        # 꼬리 질문 출제
        return self.giver.give_followup_question(
            job_group=found_interview_data.initial_input_data.job_group, question=question, answer=answer,
            previous_questions=str(previous_questions),
            categories_ordered_pair=categories_ordered_pair)
