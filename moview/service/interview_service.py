from typing import Dict, Optional, Any

from moview.domain.entity.interview_document import Interview
from moview.repository.interview_repository import InterviewRepository
from moview.repository.question_answer.question_answer_repository import QuestionAnswerRepository
from moview.utils.singleton_meta_class import SingletonMeta
from moview.config.loggers.mongo_logger import execution_trace_logger


class InterviewService(metaclass=SingletonMeta):

    def __init__(self, interview_repository: InterviewRepository, question_answer_repository: QuestionAnswerRepository):
        self.interview_repository = interview_repository
        self.question_answer_repository = question_answer_repository

    def create_interview(self, user_id: str) -> str:
        interview_model = Interview(
            user_id=user_id,
        )
        interview_document = self.interview_repository.save_interview(interview_model)
        return str(interview_document.inserted_id)

    def update_interview_with_initial_input_data(self, user_id: str, interview_document_id: str,
                                                 input_data_document_id: Dict[str, Optional[str]]):
        interview_document = self.interview_repository.find_interview_by_object_id(user_id, interview_document_id)
        interview_entity = Interview(**interview_document)
        interview_entity.initial_input_data_id = input_data_document_id
        self.interview_repository.update_interview(interview_entity, interview_document_id)

    def find_interview(self, user_id: str, interview_id: str) -> Dict[str, Any]:
        execution_trace_logger(msg="FIND_INTERVIEW", user_id=user_id, interview_id=interview_id)

        return self.interview_repository.find_interview_by_object_id(user_id=user_id, interview_id=interview_id)

    def add_latest_question_into_interview(self, interview_id: str, interview_dict: Dict[str, Any], question_id: str,
                                           question_content: str):
        execution_trace_logger(msg="ADD_LATEST_QUESTION_INTO_INTERVIEW", interview_id=interview_id,
                               question_id=question_id)

        # 이전 질문들에 현재 질문을 저장하고 그 id를 인터뷰 세션에 저장한다.
        interview_entity = Interview(**interview_dict)
        interview_entity.previous_question_content.append(question_content)
        interview_entity.question_id_list.append({
            "#ref": self.question_answer_repository.collection.name,
            "#id": question_id,
            "#db": self.question_answer_repository.db.name
        })

        self.interview_repository.update_interview(interview_model=interview_entity, interview_id=interview_id)
