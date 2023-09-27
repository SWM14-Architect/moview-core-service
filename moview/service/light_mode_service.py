from typing import List, Dict, Any

from moview.config.loggers.mongo_logger import error_logger, execution_trace_logger
from moview.domain.entity.input_data.initial_input_data_document import InitialInputData
from moview.domain.entity.question_answer.question import Question
from moview.exception.light_question_parse_error import LightQuestionParseError
from moview.modules.light.light_question_giver import LightQuestionGiver
from moview.repository.input_data.input_data_repository import InputDataRepository
from moview.repository.question_answer.question_answer_repository import QuestionAnswerRepository
from moview.utils.singleton_meta_class import SingletonMeta


class LightModeService(metaclass=SingletonMeta):

    def __init__(self, input_data_repository: InputDataRepository,
                 question_answer_repository: QuestionAnswerRepository,
                 light_question_giver: LightQuestionGiver):
        self.LIGHT_QUESTION_NUMBER = 6
        self.input_data_repository = input_data_repository
        self.question_answer_repository = question_answer_repository
        self.light_question_giver = light_question_giver

    def ask_light_question_to_interviewee(self, company_name: str, job_group: str) -> Dict[str, Any]:
        """

        Args:
            company_name: 인터뷰 대상자 회사 이름
            job_group: 인터뷰 대상자 직군

        Returns: 직무 기술 중심 면접 질문 리스트

        """

        # light mode 면접 질문 생성
        light_question_list = self.__make_light_questions_by_input_data(job_group=job_group)

        # Initial Input Data Entity Model 생성 (Light mode라서 모집공고 None, 자소서 모델 None)
        initial_input_data_model = self.__create_interviewee_data_entity_for_light_mode(company_name=company_name,
                                                                                        job_group=job_group)

        # Initial Input Data Document 저장
        initial_input_document = self.input_data_repository.save_for_light_mode(
            initial_input_data=initial_input_data_model)

        # Initial Question Entity Model 생성 및 Document 저장
        question_document_id_list = []
        for question_content in light_question_list:
            question_model = self.__create_question_entity(question_content=question_content)
            question_document = self.question_answer_repository.save_question(question_model)
            question_document_id_list.append(question_document.inserted_id)

        execution_trace_logger("Save Light Question Document", initial_question_list=light_question_list)

        return {
            "input_data_document": {
                "#ref": self.input_data_repository.collection.name,
                "#id": str(initial_input_document.inserted_id),
                "#db": self.input_data_repository.db.name
            },
            "question_document_list": list(zip(question_document_id_list, light_question_list))
        }

    def __make_light_questions_by_input_data(self, job_group: str) -> List[str]:
        try:
            light_questions = self.light_question_giver.give_light_questions_by_input_data(
                job_group=job_group,
                question_count=self.LIGHT_QUESTION_NUMBER
            )

            execution_trace_logger("Make Light Question", created_questions=light_questions)

            return light_questions
        except LightQuestionParseError:
            error_logger("Light Question Parse Error")

    @staticmethod
    def __create_interviewee_data_entity_for_light_mode(company_name: str,
                                                        job_group: str) -> InitialInputData:
        # 도메인 모델 InitialInputData을 재사용한다. 이유는 다음과 같다.
        # 이 모델에 모집공고만 None 처리하면 light mode 용 초기 데이터가 만들어지기 때문.
        # 그리고 CoverLetter 모델 역시 만들 필요가 없어진다.
        return InitialInputData(
            company_name=company_name,
            job_group=job_group,
            recruit_announcement=None)

    @staticmethod
    def __create_question_entity(question_content: str) -> Question:
        question_model = Question(
            content=question_content,
            feedback_score=0,
        )
        return question_model
