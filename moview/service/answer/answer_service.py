from typing import Optional, Tuple
from moview.config.loggers.mongo_logger import execution_trace_logger
from moview.service.answer.question_choosing_strategy import QuestionChoosingStrategy
from moview.service.answer.followup_question_determiner import FollowupQuestionDeterminer
from moview.repository.question_answer.question_answer_repository import QuestionAnswerRepository
from moview.repository.interview_repository import InterviewRepository
from moview.domain.entity.question_answer.question_document import Question
from moview.domain.entity.question_answer.answer_document import Answer
from moview.modules.question_generator import FollowUpQuestionGiver
from moview.utils.singleton_meta_class import SingletonMeta
from moview.utils.prompt_parser import PromptParser


class AnswerService(metaclass=SingletonMeta):

    def __init__(self, interview_repository: InterviewRepository, question_answer_repository: QuestionAnswerRepository,
                 choosing_strategy: QuestionChoosingStrategy,
                 followup_question_giver: FollowUpQuestionGiver):
        self.interview_repository = interview_repository
        self.question_answer_repository = question_answer_repository
        self.choosing_strategy = choosing_strategy
        self.followup_question_giver = followup_question_giver

    # todo 이 메서드 자체에 transaction 처리가 필요함.
    def maybe_give_followup_question_about_latest_answer(self, interview_id: str, question_id: str,
                                                         question_content: str, answer_content: str) -> \
            Tuple[Optional[str], Optional[str]]:

        """

        Args:
            interview_id: 인터뷰 세션 id
            question_id: 최근에 답변했던 질문의 id
            question_content: 최근에 답변했던 질문의 내용
            answer_content: 최근의 답변했던 답변의 내용

        Returns: 꼬리 질문을 낼 필요가 있다면, 꼬리질문 내용과 str(꼬리질문의 id)를 반환한다. 그렇지 않다면 None, None을 반환한다.

        """

        self.__save_latest_answer(answer_content=answer_content, question_id=question_id)

        if FollowupQuestionDeterminer.need_to_give_followup_question():

            execution_trace_logger(msg="NEED_TO_GIVE_FOLLOWUP_QUESTION")

            followup_question_content = self.followup_question_giver.give_followup_question(question=question_content,
                                                                                            answer=answer_content)

            parsed_questions = PromptParser.parse_question(followup_question_content)

            if parsed_questions:
                chosen_question = self.choosing_strategy.choose_question(parsed_questions)

                saved_followup_question_id = self.__save_followup_question(interview_id=interview_id,
                                                                           question_id=question_id,
                                                                           followup_question_content=chosen_question)

                return chosen_question, str(saved_followup_question_id)

            else:
                execution_trace_logger(msg="NO_FOLLOWUP_QUESTION")
                return None, None
        else:
            execution_trace_logger(msg="NO_FOLLOWUP_QUESTION")

            return None, None

    def __save_latest_answer(self, answer_content: str, question_id: str):
        execution_trace_logger(msg="CREATE_AND_SAVE_ANSWER")

        answer = Answer(content=answer_content,
                        question_id={
                            "#ref": self.question_answer_repository.collection.name,
                            "#id": question_id,
                            "#db": self.question_answer_repository.db.name
                        })

        self.question_answer_repository.save_answer(answer)

    def __save_followup_question(self, interview_id: str, question_id: str, followup_question_content: str):
        execution_trace_logger(msg="CREATE_AND_SAVE_FOLLOWUP_QUESTION")

        followup_question = Question(content=followup_question_content, feedback_score=0,
                                     interview_id={
                                         "#ref": self.interview_repository.collection.name,
                                         "#id": interview_id,
                                         "#db": self.interview_repository.db.name
                                     },
                                     prev_question_id={
                                         "#ref": self.question_answer_repository.collection.name,
                                         "#id": question_id,  # question_id를 가리킴으로써, 꼬리질문임을 나타낸다.
                                         "#db": self.question_answer_repository.db.name
                                     })

        return self.question_answer_repository.save_question(followup_question).inserted_id
