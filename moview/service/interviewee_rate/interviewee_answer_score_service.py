from moview.modules.answer_evaluator.answer_scorer import AnswerScorer
from moview.repository.interviewee_data_repository import IntervieweeDataRepository, MongoConfig


class InterviewAnswerScoreService:
    def __init__(self):
        self.repository = IntervieweeDataRepository(mongo_config=MongoConfig())
        self.scorer = AnswerScorer()

    def score_answers_of_interviewee(self, session_id):

        found_interview_data = self.repository.find_by_session_id(session_id=session_id)

        if found_interview_data is None:
            raise Exception("Interview history not found.")

        question_list = found_interview_data.interviewee_answer_scores.question_list
        answer_list = found_interview_data.interviewee_answer_scores.answer_list
        category_and_sub_category_list = found_interview_data.interviewee_answer_scores.category_and_sub_category_list

        for i in range(len(question_list)):
            # 질문과 답변 내용, 대분류와 중분류를 전달하여 사용자 답변에 대한 평가
            score_from_llm = self.scorer.rate_by_main_and_subcategories(question=question_list[i],
                                                                        answer=answer_list[i],
                                                                        categories_ordered_pair=
                                                                        category_and_sub_category_list[i])

            # 평가 저장
            found_interview_data.interviewee_answer_scores.score_of_answer_list.append(score_from_llm)

        updated_id = self.repository.update(session_id=session_id, interviewee_data_entity=found_interview_data)

        return updated_id
