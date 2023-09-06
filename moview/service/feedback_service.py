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

        for feedback in feedback_list:
            found_question = self.question_answer_repository.find_question_by_object_id(object_id=feedback.question_id)
            found_question["feedback_score"] = feedback.feedback_score
            self.question_answer_repository.update_question(question=found_question, object_id=feedback.question_id)
