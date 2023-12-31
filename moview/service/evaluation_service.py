import asyncio
from typing import Dict, List, Tuple, Any

from moview.utils.singleton_meta_class import SingletonMeta
from moview.config.loggers.mongo_logger import *

from moview.modules.answer_evaluator.answer_evaluator import AnswerEvaluator
from moview.repository.interview_repository import InterviewRepository
from moview.repository.question_answer.question_answer_repository import QuestionAnswerRepository


class EvaluationService(metaclass=SingletonMeta):

    def __init__(self,
                 interview_repository: InterviewRepository,
                 question_answer_repository: QuestionAnswerRepository,
                 answer_evaluator: AnswerEvaluator):
        self.interview_repository = interview_repository
        self.question_answer_repository = question_answer_repository
        self.answer_evaluator = answer_evaluator

    async def evaluate_answers_of_interviewee(self, user_id: str, interview_id: str) -> List[Tuple[str, str, str, List[str]]]:
        # 1. 진행 됐던 모든 question id list를 불러온다.
        question_id_list = self.__get_question_id_list_from_interview_session(user_id, interview_id)

        # 2. 비동기적으로 평가를 진행한다.
        evaluation_results = await asyncio.gather(*[self._evaluate_single_answer_of_interviewee(question_id) for question_id in question_id_list])

        execution_trace_logger(msg="EVALUATE_ANSWERS_OF_INTERVIEWEE", user_id=user_id, interview_id=interview_id, evaluation_results=evaluation_results)
        return evaluation_results

    async def _evaluate_single_answer_of_interviewee(self, question_id: Dict[str, str]) -> Tuple[str, str, str, List[str]]:
        # 2-1. question과 answer를 불러오고, content를 가져온다.
        question_dict = self.__get_question(question_id=question_id["#id"])
        answer_dict = self.__get_answer(question_id=question_id)

        question_content = question_dict["content"]
        answer_content = answer_dict["content"]

        # 2-2. question_content와 answer_content를 이용하여 평가를 진행한다.
        evaluation = await self.answer_evaluator.evaluate_answer(question=question_content, answer=answer_content)

        # 2-3. evaluation 결과를 저장한다.
        self.__save_evaluation(answer_dict=answer_dict, question_id=question_id, evaluation=evaluation)

        # 2-4. evaluation 결과를 반환한다.
        return str(question_id["#id"]), question_content, answer_content, evaluation

    def __get_question_id_list_from_interview_session(self, user_id: str, interview_id: str) -> List[Dict[str, Any]]:
        interview_session = self.interview_repository.find_interview_by_object_id(user_id, interview_id)

        execution_trace_logger(msg="GET_QUESTION_ID_LIST_FROM_INTERVIEW_SESSION",
                               user_id=user_id,
                               interview_id=interview_id,
                               interview_session=interview_session,
                               question_id_list=interview_session["question_id_list"])
        return interview_session["question_id_list"]

    def __get_question(self, question_id: str) -> Dict[str, Any]:
        found_question = self.question_answer_repository.find_question_by_object_id(question_id)

        execution_trace_logger(msg="GET_QUESTION", question_id=question_id, found_question=found_question)
        return found_question

    def __get_answer(self, question_id: Dict[str, str]) -> Dict[str, Any]:
        found_answer = self.question_answer_repository.find_answer_by_question_id(question_id)

        execution_trace_logger(msg="GET_ANSWER", question_id=question_id, found_answer=found_answer)
        return found_answer

    def __save_evaluation(self, answer_dict: Dict[str, Any], question_id: Dict[str, str], evaluation: List[str]) -> None:
        answer_dict["evaluation"] = evaluation
        self.question_answer_repository.update_answer_by_question_id(answer=answer_dict, question_id=question_id)

        execution_trace_logger(msg="SAVE_EVALUATION", question_id=question_id, answer_dict=answer_dict, evaluation=evaluation)
