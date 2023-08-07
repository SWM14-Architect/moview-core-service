from moview.modules.answer_evaluator.answer_scorer import AnswerScorer
from moview.modules.answer_evaluator.answer_analyzer import AnswerAnalyzer
from moview.repository.interviewee_data_repository import IntervieweeDataRepository, MongoConfig
from moview.loggers.mongo_logger import *


class InterviewAnswerEvaluationService:
    def __init__(self):
        self.repository = IntervieweeDataRepository(mongo_config=MongoConfig())

        self.scorer = AnswerScorer()
        self.analyzer = AnswerAnalyzer()

    def evaluate_answers_of_interviewee(self, session_id):

        found_interview_data = self.repository.find_by_session_id(session_id=session_id)

        if found_interview_data is None:
            error_logger("Interview history not found.")
            raise Exception("Interview history not found.")

        question_list = found_interview_data.interviewee_answer_evaluations.question_list
        answer_list = found_interview_data.interviewee_answer_evaluations.answer_list
        category_and_sub_category_list = found_interview_data.interviewee_answer_evaluations.category_and_sub_category_list

        for i in range(len(question_list)):
            # 질문과 답변 내용, 대분류와 중분류를 전달하여 사용자 답변에 대한 평가
            score_from_llm = self.scorer.rate_by_main_and_subcategories(question=question_list[i],
                                                                        answer=answer_list[i],
                                                                        categories_ordered_pair=
                                                                        category_and_sub_category_list[i])
            evaluation_from_llm = self.analyzer.analyze_answer_by_main_and_subcategories(question=question_list[i],
                                                                                         answer=answer_list[i],
                                                                                         categories_ordered_pair=category_and_sub_category_list[i])

            # 평가 저장
            found_interview_data.save_score_in_interviewee_answer_evaluations(score=score_from_llm)
            found_interview_data.save_analysis_in_interviewee_answer_evaluations(analysis=evaluation_from_llm)

        # DB에 저장
        self.repository.update(session_id=session_id, interviewee_data_entity=found_interview_data)

        # return을 위해 found_interview_data에서 interviewee_answer_evaluations를 가져옴
        interviewee_answer_evaluations = found_interview_data.interviewee_answer_evaluations

        return interviewee_answer_evaluations
