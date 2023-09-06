from moview.domain.entity.interview_session_document import InterviewSession
from moview.repository.interview_repository import InterviewRepository
from moview.utils.singleton_meta_class import SingletonMeta


class InterviewService(metaclass=SingletonMeta):

    def __init__(self, interview_repository: InterviewRepository):
        self.interview_repository = interview_repository

    def create_interview_session(self, session_id: str) -> str:
        # session_id를 이용해 InterviewSession을 생성함.
        interview_model = InterviewSession(user_id=session_id)
        interview_document = self.interview_repository.save_interview(interview_model)
        return str(interview_document.inserted_id)
