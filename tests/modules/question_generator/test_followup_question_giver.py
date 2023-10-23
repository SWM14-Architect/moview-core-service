import unittest
from unittest.mock import patch

from tests.common_code_for_test import is_not_none_string
from moview.modules.question_generator.followup_question_giver import FollowUpQuestionGiver
from moview.utils.prompt_loader import PromptLoader


class TestFollowUpQuestionGiver(unittest.TestCase):

    def setUp(self) -> None:
        self.prompt_loader = PromptLoader()
        self.followup_question_giver = FollowUpQuestionGiver(self.prompt_loader)

    def test_load_prompt(self):
        self.assertTrue(is_not_none_string(self.followup_question_giver.prompt))

    @patch(
        'moview.modules.question_generator.followup_question_giver.FollowUpQuestionGiver'
        '.give_followup_question')
    def test_give_followup_question(self, mock_method):
        # given
        question = "테스트 질문"
        answer = "테스트 답변"
        mock_method.return_value = "followup question"

        # when
        result = self.followup_question_giver.give_followup_question(question, answer)

        # then
        self.assertIn("followup question", result)

    def test_open_ai_call(self):
        # given
        question = "MongoDB에 대해 설명해주세요."
        answer = "MongoDB는 NoSQL 데이터베이스입니다."

        # when
        result = self.followup_question_giver.give_followup_question(question, answer)

        # then
        print(result)
        self.assertTrue(result is not None)
