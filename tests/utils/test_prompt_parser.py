import unittest

from moview.utils.prompt_parser import PromptParser


class TestPromptParser(unittest.TestCase):

    def test_parse_question_with_colon(self):
        question = """면접관의 질문: 어떤 방식으로 신입 개발자들의 온보딩을 도와주고 싶으신가요? #
면접관의 질문: 성과를 내기 위해 어떤 역량을 가지고 계신가요? #"""
        result = PromptParser.parse_question(question)
        self.assertEqual(result, ["어떤 방식으로 신입 개발자들의 온보딩을 도와주고 싶으신가요?", "성과를 내기 위해 어떤 역량을 가지고 계신가요?"])

    def test_parse_question_with_number(self):
        question = """1. 어떤 방식으로 신입 개발자들의 온보딩을 도와주고 싶으신가요? #
2. 성과를 내기 위해 어떤 역량을 가지고 계신가요? #"""
        result = PromptParser.parse_question(question)
        self.assertEqual(result, ["어떤 방식으로 신입 개발자들의 온보딩을 도와주고 싶으신가요?", "성과를 내기 위해 어떤 역량을 가지고 계신가요?"])

    def test_parse_question_with_colon_and_number(self):
        question = """1. 면접관의 질문: 어떤 방식으로 신입 개발자들의 온보딩을 도와주고 싶으신가요? #
2. 면접관의 질문: 성과를 내기 위해 어떤 역량을 가지고 계신가요? #"""
        result = PromptParser.parse_question(question)
        self.assertEqual(result, ["어떤 방식으로 신입 개발자들의 온보딩을 도와주고 싶으신가요?", "성과를 내기 위해 어떤 역량을 가지고 계신가요?"])

    def test_parse_question_without_any_pattern(self):
        question = "이 문장에는 : 도 없고 숫자. 도 없습니다."
        result = PromptParser.parse_question(question)
        self.assertIsNone(result)
