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

        self.assertEqual(len(result_vo.answer_score_with_category.scores_about_answer), 1)
        print("\nPRINT\n")
        print("\n", result_vo.answer_score_with_category.scores_about_answer)

    def test_score_answers_of_interviewee(self):
        ANSWER_COUNT = 2

        for _ in range(ANSWER_COUNT):
            self.vo.save_categories_ordered_pair(
                question="프로젝트에서 어떤 언어와 프레임워크, 라이브러리를 사용하였나요?",
                answer="언어는 JAVA, JavaScript를 사용했습니다.프레임워크는 스프링 부트를 사용했습니다.",
                categories_ordered_pair="Technical Job-related Questions, specifically the subcategory of Technical Details.")

        result_vo = self.score_service.score_answers_of_interviewee(vo=self.vo)

        self.assertEqual(len(result_vo.answer_score_with_category.scores_about_answer), ANSWER_COUNT)

        print("\nPRINT\n")
        for i in range(len(result_vo.answer_score_with_category.scores_about_answer)):
            print("\n", result_vo.answer_score_with_category.scores_about_answer[i])
        """
        출력 형태
        (첫 번째 경우)
        - Technical Details
            - Technical Knowledge (0-100 points): 80#
            - Technical Depth (0-100 points): 70#
            - Practical Application (0-100 points): 90#
        
        (두 번째 경우) 
        - Technical Details

            - Technical Knowledge: 85#
            - Technical Depth: 70#
            - Practical Application: 90#   
        
        (세 번째 경우) 
        - Technical Details

            - Technical Knowledge (85#)
            - Technical Depth (80#)
            - Practical Application (90#)
        
        (네 번째 경우)
        Evaluation:
        
        - Technical Knowledge (0-100 points): 80#
        - The candidate accurately identifies the languages and frameworks used in their project.
        - Technical Depth (0-100 points): 70#
        
        Overall Score: 80
        
        (다섯 번째 경우)
         Technical Job-related Questions - Technical Details:
        - Technical Knowledge: 80#
        - Technical Depth: 70#     
        - Practical Application: 90#
        """