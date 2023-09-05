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
        print(self.followup_question_giver.prompt.format(category="테스트 카테고리", sub_category="테스트 서브 카테고리",
                                                         previous_question="테스트 이전 질문"))

    @patch(
        'moview.modules.question_generator.followup_question_giver.FollowUpQuestionGiver'
        '.give_followup_question')
    def test_give_followup_question(self, mock_method):
        # given
        question = "테스트 질문"
        answer = "테스트 답변"
        previous_question = "테스트 이전 질문"
        category = "테스트 카테고리"
        sub_category = "테스트 서브 카테고리"
        mock_method.return_value = "followup question"

        # when
        result = self.followup_question_giver.give_followup_question(question, answer, previous_question,
                                                                     category, sub_category)

        # then
        self.assertIn("followup question", result)
