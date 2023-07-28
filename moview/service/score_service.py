

from moview.service.interviewee_data_vo import IntervieweeDataVO
from moview.modules.answer_evaluator.interview_answer_scorer import InterviewAnswerScorer


class ScoreService:
    def __init__(self):
        self.scorer = InterviewAnswerScorer()

    def score_answers_of_interviewee(self, vo: IntervieweeDataVO) -> IntervieweeDataVO:

        for question, answer, category_and_sub_category in vo.answer_score_with_category.categories_ordered_pair_list:
            # 질문과 답변 내용, 대분류와 중분류를 전달하여 사용자 답변에 대한 평가
            score_from_llm = self.scorer.rate_by_main_and_subcategories(question=question,
                                                                        answer=answer,
                                                                        categories_ordered_pair=category_and_sub_category)

            # 평가 저장
            vo.save_score_of_interviewee(score_of_answer=score_from_llm)

        return vo
