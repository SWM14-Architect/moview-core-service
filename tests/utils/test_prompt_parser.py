import unittest

from moview.utils.prompt_parser import PromptParser


class TestPromptParser(unittest.TestCase):

    def test_parse_question_with_colon(self):
        question = "면접관: 어떻게 탁월한 개발자로서의 성과를 이루기 위해 노력하고 계획하고 있나요? #"
        result = PromptParser.parse_question(question)
        self.assertEqual(result, "어떻게 탁월한 개발자로서의 성과를 이루기 위해 노력하고 계획하고 있나요?")

    def test_parse_question_with_number(self):
        question = "1. 어떻게 탁월한 개발자로서의 성과를 이루기 위해 노력하고 계획하고 있나요? #"
        result = PromptParser.parse_question(question)
        self.assertEqual(result, "어떻게 탁월한 개발자로서의 성과를 이루기 위해 노력하고 계획하고 있나요?")

    def test_parse_question_without_any_pattern(self):
        question = "이 문장에는 : 도 없고 숫자. 도 없습니다."
        result = PromptParser.parse_question(question)
        self.assertIsNone(result)
