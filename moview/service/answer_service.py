import random
from typing import Dict, Any
from bson import ObjectId
from moview.domain.entity.question_answer.answer import Answer
from moview.modules.question_generator import AnswerFilter, AnswerCategoryClassifier, AnswerSubCategoryClassifier, \
    FollowUpQuestionGiver
from moview.utils.singleton_meta_class import SingletonMeta
from moview.config.loggers.mongo_logger import execution_trace_logger
from moview.repository.question_answer.question_answer_repository import QuestionAnswerRepository
from moview.repository.interview_repository import InterviewRepository
from moview.domain.entity.interview_session_document import InterviewSession
from moview.domain.entity.question_answer.question import Question


class AnswerService(metaclass=SingletonMeta):

    def __init__(self, interview_repository: InterviewRepository, question_answer_repository: QuestionAnswerRepository,
                 answer_filter: AnswerFilter, major_classifier: AnswerCategoryClassifier,
                 sub_classifier: AnswerSubCategoryClassifier, giver: FollowUpQuestionGiver):
        self.interview_repository = interview_repository
        self.question_answer_repository = question_answer_repository

        self.filter = answer_filter
        self.major_classifier = major_classifier
        self.sub_classifier = sub_classifier
        self.giver = giver

    # todo 이 메서드 자체에 transaction 처리가 필요함.
    def answer(self, user_id: str, interview_id: str, question_id: str, question_content: str, answer_content: str):
        # 1. 현재 인터뷰 세션을 불러온 후, 업데이트한다.
        interview_dict = self.__load_interview_session(user_id=user_id, interview_id=interview_id)

        interview_entity = self.__update_interview_session(interview_id=interview_id, interview_dict=interview_dict,
                                                           question_id=question_id, question_content=question_content)

        # 2. 꼬리 질문을 할지 말지를 결정한다.
        need_for_followup_question = self.need_to_give_followup_question(
            number_of_questions=len(interview_entity.question_id_list))

        # 3. 면접 답변 필터링 결과 얻기
        filter_result = self.__filter_answer(question_content=question_content, answer_content=answer_content)

        # 4. 면접 답변 대분류 얻기
        category = self.__classify_category_of_answer(question_content=question_content, answer_content=answer_content)

        # 5. 면접 답변 중분류 얻기
        sub_category = self.__classify_subcategory_of_answer(question_content=question_content,
                                                             answer_content=answer_content, category=category)

        # 6. 면접 답변 평가하기
        evaluation = self.__evaluate(question_content, answer_content, category, sub_category)

        # 7. answer 엔티티 생성 및 저장
        self.__create_and_save_answer(answer_content=answer_content, category=category, sub_category=sub_category,
                                      filter_result=filter_result, evaluation=evaluation, question_id=question_id)

        #   8-1. 꼬리 질문을 해야 한다면.
        if need_for_followup_question:

            followup_question_content = self.__give_followup_question(interview_entity=interview_entity,
                                                                      question_content=question_content,
                                                                      answer_content=answer_content,
                                                                      category=category, sub_category=sub_category)

            saved_followup_question_id = self.__create_and_save_followup_question(interview_id=interview_id,
                                                                                  question_id=question_id,
                                                                                  followup_question_content=followup_question_content)

            # return 꼬리 질문 내용, Question 엔티티 id
            return followup_question_content, saved_followup_question_id
        #   8-2. 꼬리 질문을 할 필요 없다면
        else:
            execution_trace_logger(msg="NO_FOLLOWUP_QUESTION")

            # return None. 즉, 꼬리 질문 출제를 하지 않는다는 것이다. 프론트엔드는 다음 초기 질문으로 넘어가야 한다.
            return None, None

    def __load_interview_session(self, user_id: str, interview_id: str) -> Dict[str, Any]:
        execution_trace_logger(msg="LOAD_INTERVIEW_SESSION")

        return self.interview_repository.find_interview_by_object_id(user_id=user_id, interview_id=interview_id)

    def __update_interview_session(self, interview_id: str, interview_dict: Dict[str, Any], question_id: str,
                                   question_content: str) -> InterviewSession:
        execution_trace_logger(msg="UPDATE_INTERVIEW_SESSION")

        # 이전 질문들에 현재 질문을 저장하고 그 id를 인터뷰 세션에 저장한다.
        interview_entity = InterviewSession(**interview_dict)
        interview_entity.previous_question_content.append(question_content)
        interview_entity.question_id_list.append({"question_id": str(ObjectId(question_id))})

        self.interview_repository.update_interview(interview=interview_entity.dict(), object_id=interview_id)
        return interview_entity

    def __filter_answer(self, question_content: str, answer_content: str):
        execution_trace_logger(msg="FILTER_ANSWER")

        return self.filter.exclude_invalid_answer(question=question_content, answer=answer_content)

    def need_to_give_followup_question(self, number_of_questions: int) -> bool:
        max_num_of_questions = 15  # 한 인터뷰당 최대 질문 수

        if number_of_questions >= max_num_of_questions:
            need = False
        else:
            base_probability_of_question = 0.6  # 기본 확률
            # 출제된 질문이 많아질수록 확률이 감소 (0.6에서 0.25까지 떨어짐)
            probability_of_question = base_probability_of_question / (1 + 0.1 * number_of_questions)

            need = random.random() < probability_of_question

        execution_trace_logger(msg="NEED_TO_GIVE_FOLLOWUP_QUESTION", result=need)

        return need

    def __classify_category_of_answer(self, question_content: str, answer_content: str) -> str:
        execution_trace_logger(msg="CLASSIFY_CATEGORY_OF_ANSWER")

        return self.major_classifier.classify_category_of_answer(question=question_content, answer=answer_content)

    def __classify_subcategory_of_answer(self, question_content: str, answer_content: str, category: str) -> str:
        execution_trace_logger(msg="CLASSIFY_SUB_CATEGORY_OF_ANSWER")

        return self.sub_classifier.classify_sub_category_of_answer(question=question_content,
                                                                   answer=answer_content, category=category)

    # todo 평가 모듈은 중간 평가 의견 나온 다음에 프롬프트를 바꾼다.
    def __evaluate(self, question_content: str, answer_content: str, category: str, sub_category: str) -> str:
        execution_trace_logger(msg="EVALUATE_ANSWER")

        return ""

    def __create_and_save_answer(self, answer_content: str, category: str, sub_category: str, filter_result: str,
                                 evaluation: str, question_id: str):
        execution_trace_logger(msg="CREATE_AND_SAVE_ANSWER")

        answer = Answer(content=answer_content, category=category, sub_category=sub_category,
                        filter_result=filter_result, evaluation=evaluation,
                        question_id={"question_id": str(ObjectId(question_id))})

        self.question_answer_repository.save_answer(answer)

    def __give_followup_question(self, interview_entity: InterviewSession, question_content: str, answer_content: str,
                                 category: str, sub_category: str) -> str:
        execution_trace_logger(msg="GIVE_FOLLOWUP_QUESTION")

        string_previous_question = ''.join(interview_entity.previous_question_content)

        return self.giver.give_followup_question(question=question_content,
                                                 answer=answer_content,
                                                 previous_question=string_previous_question,
                                                 category=category, sub_category=sub_category)

    def __create_and_save_followup_question(self, interview_id: str, question_id: str, followup_question_content: str):
        execution_trace_logger(msg="CREATE_AND_SAVE_FOLLOWUP_QUESTION")

        # Question 엔티티를 생성한다. question_id를 가리킴으로써, 꼬리질문임을 나타낸다.
        followup_question = Question(content=followup_question_content, feedback_score=0,
                                     interview_id={"interview_id": str(ObjectId(interview_id))},
                                     question_id={"question_id": str(ObjectId(question_id))})

        # Question 리포지토리의 saveQuestion()을 활용해 Question 엔티티를 저장한다.
        return self.question_answer_repository.save_question(followup_question).inserted_id
