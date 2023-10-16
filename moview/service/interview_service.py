from typing import List, Dict, Optional

from moview.domain.entity.interview_document import Interview
from moview.repository.interview_repository import InterviewRepository
from moview.utils.singleton_meta_class import SingletonMeta


class InterviewService(metaclass=SingletonMeta):

    def __init__(self, interview_repository: InterviewRepository):
        self.interview_repository = interview_repository

    def create_interview(self, user_id: str) -> str:
        interview_model = Interview(
            user_id=user_id,
        )
        interview_document = self.interview_repository.save_interview(interview_model)
        return str(interview_document.inserted_id)

    def update_interview_with_initial_input_data(self, user_id:str, interview_document_id: str, input_data_document_id: Dict[str, Optional[str]]) -> str:
        interview_document = self.interview_repository.find_interview_by_object_id(user_id, interview_document_id)
        interview_entity = Interview(**interview_document)
        interview_entity.initial_input_data_id = input_data_document_id
        self.interview_repository.update_interview(interview_entity, interview_document_id)
