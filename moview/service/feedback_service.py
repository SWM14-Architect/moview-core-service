from typing import List
from moview.utils.singleton_meta_class import SingletonMeta
from moview.config.loggers.mongo_logger import execution_trace_logger
from moview.repository.question_answer.question_answer_repository import QuestionAnswerRepository
from moview.controller.dto.feedback_dto import FeedbackDTO


class FeedbackService(metaclass=SingletonMeta):

    def __init__(self, question_answer_repository: QuestionAnswerRepository):
        self.question_answer_repository = question_answer_repository

    def feedback(self, user_id: str, interview_id: str, feedback_list: List[FeedbackDTO]) -> None:
        execution_trace_logger(msg="FEEDBACK", user_id=user_id, interview_id=interview_id)

        for question_id, feedback_score in feedback_list:
            self.question_answer_repository.update_question_with_feedback_score(object_id=question_id,
                                                                                feedback_score=feedback_score)
