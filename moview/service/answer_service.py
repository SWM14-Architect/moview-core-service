import random
from moview.config.db.mongo_config import MongoConfig
from moview.modules.question_generator import AnswerFilter, AnswerCategoryClassifier, AnswerSubCategoryClassifier, \
    FollowUpQuestionGiver
from moview.config.loggers.mongo_logger import execution_trace_logger, error_logger
from moview.repository.question_answer.question_answer_repository import QuestionAnswerRepository


class AnswerService:

    def __init__(self):
        self.mongo_config = (MongoConfig())
        self.mongo_config.db_name = "question_answer"
        self.repository = QuestionAnswerRepository(MongoConfig())

        self.filter = AnswerFilter()
        self.major_classifier = AnswerCategoryClassifier()
        self.sub_classifier = AnswerSubCategoryClassifier()
        self.giver = FollowUpQuestionGiver()

    def answer(self, question_id: str, question_content: str, answer_content: str):
        # 1. answer 서비스에서 answer 필터 로직을 실행한다. answer 필터 로직을 실행한 결과를 지역 변수로 저장한다.
        filter_result = self.filter.exclude_invalid_answer(question=question_content, answer=answer_content)

        # 2. random()을 활용하여 0과 1 사이의 랜덤한 실수를 얻는다.
        random_float = random.random()

        # 3. answer 서비스가 answerCategoryClassifier에게 classify(질문 내용, 답변 내용)을 호출한다. 결과로 대분류를 얻는다. (이를 b라고 하자.)
        category = self.major_classifier.classify_category_of_answer(question=question_content, answer=answer_content)

        # 4. answer 서비스가 answerSubCategoryClassifier에게 classify(질문 내용, 답변 내용, 대분류)를 호출한다. 결과로 대분류 + 중분류 문자열을 얻는다. (이를 c라고 하자.)

        # 5. c를 이용하여, 평가를 진행한다. answer 서비스가 평가 모듈에게 evaluate(질문 내용, 답변 내용, c)를 호출한다. 결과로 평가를 얻는다. (이를 d라고 하자.)

        # 6. Answer 엔티티를 생성한다. 생성자는 (답변 내용, 필터 결과=a, 분류 = c, analysis=d , ref_key = 질문 Id)다.

        # 7. answer 리포지토리의 saveAnswer()를 활용해 Answer 엔티티를 저장한다.

        # 8. random_float를 활용하여, 꼬리 질문을 할지 말지를 결정한다.
        #   8-1. e가 꼬리 질문 확률을 나타내는 상수 f 보다 작다면,
        #     8-1-1. return None. 즉, 꼬리 질문 출제를 하지 않는다는 것이다. 프론트엔드는 다음 초기 질문으로 넘어가야 한다.
        #   8-2. e가 꼬리 질문 확률을 나타내는 상수 f 보다 크다면,
        #     8-2-1. c를 활용하여, answer 서비스가 followupQustionGiver의 giveFollowupQuestion(질문 내용, 답변 내용, 분류 = c)를 호출한다. 결과로 꼬리질문 내용 h을 얻는다.
        #     8-2-2. Question 엔티티를 생성한다. 생성자는 (content=h, feedback_score = None, question_id=질문 내용 Id)이다.
        #     8-2-3. return 꼬리 질문 내용 h
        pass
