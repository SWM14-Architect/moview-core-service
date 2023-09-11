from typing import List
from moview.utils.singleton_meta_class import SingletonMeta
from moview.config.loggers.mongo_logger import execution_trace_logger
from moview.repository.question_answer.question_answer_repository import QuestionAnswerRepository


class FeedbackService(metaclass=SingletonMeta):

    def __init__(self, question_answer_repository: QuestionAnswerRepository):
        self.question_answer_repository = question_answer_repository

    def feedback(self, user_id: str, interview_id: str, question_ids: List[str], feedback_scores: List[str]) -> None:
        execution_trace_logger(msg="FEEDBACK", user_id=user_id, interview_id=interview_id)

        if len(question_ids) != len(feedback_scores):
            raise Exception("question_ids와 feedback_scores의 길이가 다릅니다.")

        for i in range(len(question_ids)):
            found_question = self.question_answer_repository.find_question_by_object_id(object_id=question_ids[i])
            found_question["feedback_score"] = int(feedback_scores[i])
            self.question_answer_repository.update_question(question=found_question, object_id=question_ids[i])
