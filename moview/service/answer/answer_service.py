import random
from typing import Dict, Any, Optional, Tuple, List
from moview.domain.entity.question_answer.answer_document import Answer
from moview.modules.question_generator import FollowUpQuestionGiver
from moview.utils.singleton_meta_class import SingletonMeta
from moview.config.loggers.mongo_logger import execution_trace_logger
from moview.repository.question_answer.question_answer_repository import QuestionAnswerRepository
from moview.repository.interview_repository import InterviewRepository
from moview.domain.entity.interview_document import Interview
from moview.domain.entity.question_answer.question_document import Question
from moview.utils.prompt_parser import PromptParser


class AnswerService(metaclass=SingletonMeta):

    def __init__(self, interview_repository: InterviewRepository, question_answer_repository: QuestionAnswerRepository,
                 giver: FollowUpQuestionGiver):
        self.interview_repository = interview_repository
        self.question_answer_repository = question_answer_repository

        self.giver = giver

    # todo 이 메서드 자체에 transaction 처리가 필요함.
    def maybe_give_followup_question_about_latest_answer(self, user_id: str, interview_id: str, question_id: str, question_content: str, answer_content: str) -> \
            Tuple[Optional[str], Optional[str]]:
        # 1. 현재 인터뷰 세션을 불러온 후, 업데이트한다.
        interview_dict = self.__load_interview_session(user_id=user_id, interview_id=interview_id)

        self.__add_latest_question_into_interview_session(interview_id=interview_id, interview_dict=interview_dict,
                                                          question_id=question_id, question_content=question_content)

        # 2. 꼬리 질문을 할지 말지를 결정한다.
        need_for_followup_question = self.need_to_give_followup_question()

        # 3. answer 엔티티 생성 및 저장
        self.__save_latest_answer(answer_content=answer_content, question_id=question_id)

        #   4-1. 꼬리 질문을 해야 한다면.
        if need_for_followup_question:

            followup_question_content = self.__give_followup_question(
                question_content=question_content,
                answer_content=answer_content)

            # 4-1-1. 꼬리 질문 파싱
            parsed_questions = self.__parse_questions(followup_question_content)

            if parsed_questions:  # 파싱 성공했다면,
                # 4-1-2. 꼬리 질문 중 하나를 선택
                chosen_question = self.__choose_question(parsed_questions)

                # 4-1-3. 꼬리 질문을 저장하고, 그 id를 반환
                saved_followup_question_id = self.__create_and_save_followup_question(interview_id=interview_id,
                                                                                      question_id=question_id,
                                                                                      followup_question_content=chosen_question)

                # return 파싱된 꼬리 질문 내용, Question 엔티티 id
                return chosen_question, str(saved_followup_question_id)

            else:  # 파싱 실패했다면, 꼬리 질문을 출제하지 않는다.
                execution_trace_logger(msg="NO_FOLLOWUP_QUESTION")
                return None, None
        #   4-2. 꼬리 질문을 할 필요 없다면
        else:
            execution_trace_logger(msg="NO_FOLLOWUP_QUESTION")

            # return None. 즉, 꼬리 질문 출제를 하지 않는다는 것이다. 프론트엔드는 다음 초기 질문으로 넘어가야 한다.
            return None, None

    def __load_interview_session(self, user_id: str, interview_id: str) -> Dict[str, Any]:
        execution_trace_logger(msg="LOAD_INTERVIEW_SESSION", user_id=user_id, interview_id=interview_id)

        return self.interview_repository.find_interview_by_object_id(user_id=user_id, interview_id=interview_id)

    def __add_latest_question_into_interview_session(self, interview_id: str, interview_dict: Dict[str, Any], question_id: str,
                                                     question_content: str) -> Interview:
        execution_trace_logger(msg="UPDATE_INTERVIEW_SESSION", interview_id=interview_id, question_id=question_id)

        # 이전 질문들에 현재 질문을 저장하고 그 id를 인터뷰 세션에 저장한다.
        interview_entity = Interview(**interview_dict)
        interview_entity.previous_question_content.append(question_content)
        interview_entity.question_id_list.append({
            "#ref": self.question_answer_repository.collection.name,
            "#id": question_id,
            "#db": self.question_answer_repository.db.name
        })

        self.interview_repository.update_interview(interview_model=interview_entity, interview_id=interview_id)

        return interview_entity

    def need_to_give_followup_question(self) -> bool:
        base_probability_of_question = 0.5

        need = random.random() < base_probability_of_question

        execution_trace_logger(msg="NEED_TO_GIVE_FOLLOWUP_QUESTION", result=need)

        return need

    def __save_latest_answer(self, answer_content: str, question_id: str):
        execution_trace_logger(msg="CREATE_AND_SAVE_ANSWER")

        answer = Answer(content=answer_content,
                        question_id={
                            "#ref": self.question_answer_repository.collection.name,
                            "#id": question_id,
                            "#db": self.question_answer_repository.db.name
                        })

        self.question_answer_repository.save_answer(answer)

    def __give_followup_question(self, question_content: str,
                                 answer_content: str) -> str:
        execution_trace_logger(msg="GIVE_FOLLOWUP_QUESTION")

        return self.giver.give_followup_question(question=question_content,
                                                 answer=answer_content)

    def __parse_questions(self, questions_string: str) -> Optional[List[str]]:
        return PromptParser.parse_question(questions_string)

    def __choose_question(self, parsed_questions: List[str]) -> str:
        return random.choice(parsed_questions)  # 주어진 리스트에서 랜덤하게 요소 하나 선택

    def __create_and_save_followup_question(self, interview_id: str, question_id: str, followup_question_content: str):
        execution_trace_logger(msg="CREATE_AND_SAVE_FOLLOWUP_QUESTION")

        # Question 엔티티를 생성한다. question_id를 가리킴으로써, 꼬리질문임을 나타낸다.
        followup_question = Question(content=followup_question_content, feedback_score=0,
                                     interview_id={
                                         "#ref": self.interview_repository.collection.name,
                                         "#id": interview_id,
                                         "#db": self.interview_repository.db.name
                                     },
                                     prev_question_id={
                                         "#ref": self.question_answer_repository.collection.name,
                                         "#id": question_id,
                                         "#db": self.question_answer_repository.db.name
                                     })

        # Question 리포지토리의 saveQuestion()을 활용해 Question 엔티티를 저장한다.
        return self.question_answer_repository.save_question(followup_question).inserted_id
