import unittest
from unittest.mock import patch

from tests.common_code_for_test import is_not_none_string
from moview.modules.light.light_question_giver import LightQuestionGiver
from moview.utils.prompt_loader import PromptLoader

PATCH_PATH = LightQuestionGiver.get_full_class_name() + ".give_light_questions_by_input_data"


class TestLightQuestionGiver(unittest.TestCase):

    def setUp(self) -> None:
        self.prompt_loader = PromptLoader()
        self.light_question_giver = LightQuestionGiver(self.prompt_loader)

    def test_load_prompt(self):
        self.assertTrue(is_not_none_string(self.light_question_giver.prompt))
        print(PATCH_PATH)

    @patch(PATCH_PATH)
    def test_give_light_question(self, mock_method):
        # given
        job_group = "테스트 직군"
        question_count = 10
        keyword = "test"
        mock_method.return_value = "light question"

        # when
        result = self.light_question_giver.give_light_questions_by_input_data(job_group=job_group,
                                                                              keyword=keyword,
                                                                              question_count=question_count)

        # then
        self.assertIn("light question", result)

    def test_open_ai_call(self):
        # given
        job_group = "테스트 직군"
        question_count = 10
        keyword = "test"

        # when
        result = self.light_question_giver.give_light_questions_by_input_data(job_group=job_group,
                                                                              keyword=keyword,
                                                                              question_count=question_count)

        # then
        self.assertLessEqual(len(result), question_count)
