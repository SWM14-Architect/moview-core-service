import unittest

from moview.service import IntervieweeDataVO, IntervieweeInitialInputData
from moview.service.score_service import ScoreService


class TestScoreService(unittest.TestCase):

    def setUp(self) -> None:
        self.score_service = ScoreService()
        self.initial_input_data = IntervieweeInitialInputData(jop_group="IT", recruit_announcement="공고",
                                                              cover_letter_questions=["질문1", "질문2"],
                                                              cover_letter_answers=["답변1", "답변2"])

        self.vo = IntervieweeDataVO(session_id=1, initial_question_list=["질문1", "질문2"],
                                    initial_interview_analysis=["분석1", "분석 2"],
                                    initial_input_data=self.initial_input_data)

    def test_score_one_answer_of_interviewee(self):
        self.vo.save_categories_ordered_pair(
            question="프로젝트에서 어떤 언어와 프레임워크, 라이브러리를 사용하였나요?",
            answer="언어는 JAVA, JavaScript를 사용했습니다.프레임워크는 스프링 부트를 사용했습니다.",
            categories_ordered_pair="Technical Job-related Questions, specifically the subcategory of Technical Details.")

        result_vo = self.score_service.score_answers_of_interviewee(vo=self.vo)

        self.assertEqual(len(result_vo.scores_about_answer), 1)
        print(result_vo.scores_about_answer)

    def test_score_answers_of_interviewee(self):
        for _ in range(3):
            self.vo.save_categories_ordered_pair(
                question="프로젝트에서 어떤 언어와 프레임워크, 라이브러리를 사용하였나요?",
                answer="언어는 JAVA, JavaScript를 사용했습니다.프레임워크는 스프링 부트를 사용했습니다.",
                categories_ordered_pair="Technical Job-related Questions, specifically the subcategory of Technical Details.")

        result_vo = self.score_service.score_answers_of_interviewee(vo=self.vo)

        self.assertEqual(len(result_vo.scores_about_answer), 5)
        print(result_vo.scores_about_answer)
        """
        출력 형태
        1.
        - Technical Details
            - Technical Knowledge (0-100 points): 80#
            - Technical Depth (0-100 points): 70#
            - Practical Application (0-100 points): 90#
        
        2.
        - Technical Details

            - Technical Knowledge: 85#
            - Technical Depth: 70#
            - Practical Application: 90#   
        
        3.
        - Technical Details

            - Technical Knowledge (85#)
            - Technical Depth (80#)
            - Practical Application (90#)
        
        기타 등등 많음...
        """