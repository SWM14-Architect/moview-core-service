import unittest

from tests.common_code_for_test import is_not_none_string
from moview.modules.answer_evaluator.answer_analyzer import AnswerAnalyzer


class TestAnswerAnalyzer(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = AnswerAnalyzer()

    def test_load_prompt(self):
        self.assertTrue(is_not_none_string(self.analyzer.prompt))
        print(self.analyzer.prompt.format(categories_ordered_pair="I think it is 테스트 대분류 especially 테스트 중분류"))

    def test_analysis_answer(self):
        question = "테스트 면접 문항"
        answer = "테스트 면접 답변"
        categories_ordered_pair = "I think it is 테스트 대분류 especially 테스트 중분류"

        evaluation_result = self.analyzer.analyze_answer_by_main_and_subcategories(question=question,
                                                                                   answer=answer,
                                                                                   categories_ordered_pair=categories_ordered_pair)
        self.assertTrue(is_not_none_string(evaluation_result))
