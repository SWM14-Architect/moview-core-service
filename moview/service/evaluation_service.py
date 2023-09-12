import asyncio
from typing import Dict, List, Optional, Any

from moview.utils.singleton_meta_class import SingletonMeta
from moview.utils.prompt_parser import PromptParser
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

    async def evaluate_answer_of_interviewee(self, user_id: str, interview_id: str):
        # 1. 진행 됐던 모든 question id list를 불러온다.
        question_id_list = self.__get_question_id_list_from_interview_session(user_id, interview_id)

        # 2. 비동기적으로 평가를 진행한다.
        await asyncio.gather(*[self._evaluate_single_pair(question_id) for question_id in question_id_list])

    async def _evaluate_single_pair(self, question_id: Dict[str, str]):
        # 2-1. question과 answer를 불러오고, content를 가져온다.
        question_dict = self.__get_question(question_id=question_id["#id"])
        answer_dict = self.__get_answer(question_id=question_id)

        question_content = question_dict["content"]
        answer_content = answer_dict["content"]

        # 2-2. question_content와 answer_content를 이용하여 평가를 진행한다.
        evaluation = await self.answer_evaluator.evaluate_answer(question=question_content, answer=answer_content)

        # 2-3. evaluation 결과를 [긍정적 내용, 개선해야 할 점]으로 파싱한다.
        parsed_evaluation = self.__parse_evaluation(evaluation_string=evaluation)

        # 2-4. evaluation 결과를 저장한다.
        self.__save_evaluation(answer_dict=answer_dict, question_id=question_id, evaluation=parsed_evaluation)

    def __get_question_id_list_from_interview_session(self, user_id: str, interview_id: str) -> Dict[str, Any]:
        execution_trace_logger(msg="GET_QUESTION_ID_LIST_FROM_INTERVIEW_SESSION",
                               user_id=user_id, interview_id=interview_id)

        interview_session = self.interview_repository.find_interview_by_object_id(user_id, interview_id)
        return interview_session["question_id_list"]

    def __get_question(self, question_id: str) -> Dict[str, Any]:
        execution_trace_logger(msg="GET_QUESTION", question_id=question_id)
        return self.question_answer_repository.find_question_by_object_id(question_id)

    def __get_answer(self, question_id: Dict[str, str]) -> Dict[str, Any]:
        execution_trace_logger(msg="GET_ANSWER", question_id=question_id)
        return self.question_answer_repository.find_answer_by_question_id(question_id)

    def __save_evaluation(self, answer_dict: Dict[str, Any], question_id: str, evaluation: List[str]) -> None:
        execution_trace_logger(msg="SAVE_EVALUATION", question_id=question_id)

        answer_dict["evaluation"] = evaluation
        self.question_answer_repository.update_answer_by_question_id(answer=answer_dict, question_id=question_id)

    def __parse_evaluation(self, evaluation_string: str) -> Optional[List[str]]:
        return PromptParser.parse_evaluation(evaluation_string)
