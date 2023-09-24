from typing import List

from moview.domain.entity.interview_document import Interview
from moview.repository.interview_repository import InterviewRepository
from moview.utils.singleton_meta_class import SingletonMeta


class InterviewService(metaclass=SingletonMeta):

    def __init__(self, interview_repository: InterviewRepository):
        self.interview_repository = interview_repository

    def create_interview(self, user_id: str, input_data_document_id: str) -> str:
        interview_model = Interview(
            user_id=user_id,
            initial_input_data_id=input_data_document_id
        )
        interview_document = self.interview_repository.save_interview(interview_model)
        return str(interview_document.inserted_id)
