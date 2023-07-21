import unittest
from unittest.mock import patch
from moview.modules.question_generator.followup_question_giver import FollowUpQuestionGiver


class TestFollowUpQuestionGiver(unittest.TestCase):
    def setUp(self) -> None:
        self.followup_question_giver = FollowUpQuestionGiver()

    @patch(
        'moview.modules.question_generator.followup_question_giver.FollowUpQuestionGiver'
        '.give_followup_question')
    def test_give_followup_question(self, mock_method):
        # given
        job_group = "테스트 직군"
        question = "테스트 질문"
        answer = "테스트 답변"
        previous_question = "테스트 이전 질문"
        categories_ordered_pair = "테스트 카테고리 쌍"
        mock_method.return_value = "followup question"

        # when
        result = self.followup_question_giver.give_followup_question(job_group, question, answer, previous_question,
                                                                     categories_ordered_pair)

        # then
        self.assertIn("followup question", result)