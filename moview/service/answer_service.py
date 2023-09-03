import random

from bson import ObjectId

from moview.config.db.mongo_config import MongoConfig
from moview.domain.entity.question_answer.answer import Answer
from moview.modules.question_generator import AnswerFilter, AnswerCategoryClassifier, AnswerSubCategoryClassifier, \
    FollowUpQuestionGiver
from moview.config.loggers.mongo_logger import execution_trace_logger
from moview.repository.question_answer.question_answer_repository import QuestionAnswerRepository
from moview.repository.interview_repository import InterviewRepository
from moview.domain.entity.interview_session_document import InterviewSession
from moview.domain.entity.question_answer.question import Question


class AnswerService:

    def __init__(self):
        self.interview_repository = InterviewRepository(MongoConfig())
        self.question_answer_repository = QuestionAnswerRepository(MongoConfig())

        self.filter = AnswerFilter()
        self.major_classifier = AnswerCategoryClassifier()
        self.sub_classifier = AnswerSubCategoryClassifier()
        self.giver = FollowUpQuestionGiver()

        self.PROBABILITY_OF_FOLLOWUP_QUESTION = 0.5

    # todo 메서드 자체에 transaction 처리가 필요함.
    def answer(self, user_id: str, interview_id: str, question_id: str, question_content: str, answer_content: str):
        # 0. 현재 인터뷰 세션을 불러온 후, 이전 질문들을 저장하고 id를 저장한다.
        execution_trace_logger(msg="LOAD_INTERVIEW_SESSION")
        interview = self.interview_repository.find_interview_by_object_id(user_id=user_id, interview_id=interview_id)

        interview_entity = InterviewSession(**interview)
        interview_entity.previous_question.append(question_content)
        interview_entity.question_id_list.append({"question_id": str(ObjectId(question_id))})

        execution_trace_logger(msg="UPDATE_INTERVIEW_SESSION")
        self.interview_repository.update_interview(interview=interview_entity.dict(), object_id=interview_id)

        # 1. answer 서비스에서 answer 필터 로직을 실행한다. answer 필터 로직을 실행한 결과를 지역 변수로 저장한다.
        execution_trace_logger(msg="FILTER_ANSWER")
        filter_result = self.filter.exclude_invalid_answer(question=question_content, answer=answer_content)

        # 2. random()을 활용하여 0과 1 사이의 랜덤한 실수를 얻는다. 그리고 현재 인터뷰 세션의 질문 개수를 얻어 놓는다.
        random_float = random.random()
        number_of_questions = len(interview_entity.question_id_list)

        # 3. answer 서비스가 answerCategoryClassifier에게 classify(질문 내용, 답변 내용)을 호출한다. 결과로 대분류를 얻는다.
        execution_trace_logger(msg="CLASSIFY_CATEGORY_OF_ANSWER")
        category = self.major_classifier.classify_category_of_answer(question=question_content, answer=answer_content)

        # 4. answer 서비스가 answerSubCategoryClassifier에게 classify(질문 내용, 답변 내용, 대분류)를 호출한다. 결과로 중분류를 얻는다.
        execution_trace_logger(msg="CLASSIFY_SUB_CATEGORY_OF_ANSWER")
        sub_category = self.sub_classifier.classify_sub_category_of_answer(question=question_content,
                                                                           answer=answer_content, category=category)

        # 5. answer 서비스가 평가 모듈에게 evaluate()를 호출한다. 결과로 평가를 얻는다.
        evaluation = self.__evaluate(question_content, answer_content, category, sub_category)

        # 6. Answer 엔티티를 생성한다.
        answer = Answer(content=answer_content, category=category, sub_category=sub_category,
                        filter_result=filter_result, evaluation=evaluation,
                        question_id={"question_id": str(ObjectId(question_id))})

        # 7. answer 리포지토리의 saveAnswer()를 활용해 Answer 엔티티를 저장한다.
        execution_trace_logger(msg="SAVE_ANSWER")
        self.question_answer_repository.save_answer(answer)

        # 8. random_float를 활용하여, 꼬리 질문을 할지 말지를 결정한다.
        #   8-1. e가 꼬리 질문 확률을 나타내는 상수 f 보다 작거나 같다면,
        if random_float <= self.PROBABILITY_OF_FOLLOWUP_QUESTION:
            # 8-1-1. return None. 즉, 꼬리 질문 출제를 하지 않는다는 것이다. 프론트엔드는 다음 초기 질문으로 넘어가야 한다.
            execution_trace_logger(msg="NO_FOLLOWUP_QUESTION")
            return None, None
        #   8-2. e가 꼬리 질문 확률을 나타내는 상수 f 보다 크다면,
        else:
            execution_trace_logger(msg="GIVE_FOLLOWUP_QUESTION")
            #     8-2-1.  answer 서비스가 followupQustionGiver의 giveFollowupQuestion()를 호출한다. 결과로 꼬리질문 내용을 얻는다.
            followup_question_content = self.giver.give_followup_question(question=question_content,
                                                                          answer=answer_content,
                                                                          previous_question=''.join(
                                                                              interview_entity.previous_question),
                                                                          category=category, sub_category=sub_category)

            #     8-2-2. Question 엔티티를 생성한다. question_id를 가리킴으로써, 꼬리질문임을 나타낸다.
            followup_question = Question(content=followup_question_content, feedback_score=0,
                                         interview_id={"interview_id": str(ObjectId(interview_id))},
                                         question_id={"question_id": str(ObjectId(question_id))})

            execution_trace_logger(msg="SAVE_FOLLOWUP_QUESTION")
            #     8-2-3. Question 리포지토리의 saveQuestion()을 활용해 Question 엔티티를 저장한다.
            saved_followup_question = self.question_answer_repository.save_question(followup_question)

            #     8-2-4. return 꼬리 질문 내용, Question 엔티티 id
            return followup_question_content, saved_followup_question.inserted_id

    # todo 평가 모듈은 중간 평가 의견 나온 다음에 프롬프트를 바꾼다.
    def __evaluate(self, question_content, answer_content, category, sub_category) -> str:
        execution_trace_logger(msg="EVALUATE_ANSWER")
        return ""
