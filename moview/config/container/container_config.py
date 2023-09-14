from moview.config.db.mongo_config import MongoConfig
from moview.utils.prompt_loader import PromptLoader
from moview.modules.input import InputAnalyzer, InitialQuestionGiver
from moview.modules.question_generator import FollowUpQuestionGiver
from moview.modules.answer_evaluator import AnswerEvaluator
from moview.repository.interview_repository import InterviewRepository
from moview.repository.input_data.input_data_repository import InputDataRepository
from moview.repository.question_answer.question_answer_repository import QuestionAnswerRepository
from moview.service.interview_service import InterviewService
from moview.service.input_data_service import InputDataService
from moview.service.answer_service import AnswerService
from moview.service.evaluation_service import EvaluationService
from moview.service.feedback_service import FeedbackService


class ContainerConfig:
    def __init__(self):
        # Utils
        self.mongo_config = MongoConfig()
        self.prompt_loader = PromptLoader()

        # Modules
        self.initial_question_giver = InitialQuestionGiver(prompt_loader=self.prompt_loader)
        self.initial_input_analyzer = InputAnalyzer(prompt_loader=self.prompt_loader)
        self.followup_question_giver = FollowUpQuestionGiver(prompt_loader=self.prompt_loader)
        self.answer_evaluator = AnswerEvaluator(prompt_loader=self.prompt_loader)

        # Repository
        self.interview_repository = InterviewRepository(mongo_config=self.mongo_config)
        self.input_data_repository = InputDataRepository(mongo_config=self.mongo_config)
        self.question_answer_repository = QuestionAnswerRepository(mongo_config=self.mongo_config)

        # Service
        self.interview_service = InterviewService(interview_repository=self.interview_repository)
        self.input_data_service = InputDataService(
            input_data_repository=self.input_data_repository,
            question_answer_repository=self.question_answer_repository,
            initial_question_giver=self.initial_question_giver,
            initial_input_analyzer=self.initial_input_analyzer
        )
        self.answer_service = AnswerService(
            interview_repository=self.interview_repository,
            question_answer_repository=self.question_answer_repository,
            giver=self.followup_question_giver
        )
        self.evaluation_service = EvaluationService(
            interview_repository=self.interview_repository,
            question_answer_repository=self.question_answer_repository,
            answer_evaluator=self.answer_evaluator
        )
        self.feedback_service = FeedbackService(question_answer_repository=self.question_answer_repository)
