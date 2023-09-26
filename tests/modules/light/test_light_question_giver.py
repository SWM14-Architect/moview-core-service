import unittest
from unittest.mock import patch

from tests.common_code_for_test import is_not_none_string
from moview.modules.light.light_question_giver import LightQuestionGiver
from moview.utils.prompt_loader import PromptLoader


class TestLightQuestionGiver(unittest.TestCase):

    def setUp(self) -> None:
        self.prompt_loader = PromptLoader()
        self.light_question_giver = LightQuestionGiver(self.prompt_loader)

    def test_load_prompt(self):
        self.assertTrue(is_not_none_string(self.light_question_giver.prompt))

    @patch("moview.modules.light.light_question_giver.LightQuestionGiver.give_light_questions_by_input_data")
    def test_give_light_question(self, mock_method):
        # given
        job_group = "테스트 직군"
        question_count = 10
        mock_method.return_value = "light question"

        # when
        result = self.light_question_giver.give_light_questions_by_input_data(job_group, question_count)

        # then
        self.assertIn("light question", result)
