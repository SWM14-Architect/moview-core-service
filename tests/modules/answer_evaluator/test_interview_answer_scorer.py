import unittest
from moview.modules.answer_evaluator.interview_answer_scorer import InterviewAnswerScorer


def is_not_none_string(s):
    return s is not None and isinstance(s, str)


class TestInterviewAnswerScorer(unittest.TestCase):

    def setUp(self) -> None:
        self.scorer = InterviewAnswerScorer()

    def test_prompt_info_for_multi_prompt(self):
        self.assertTrue(is_not_none_string(self.scorer.multi_prompt))

        prompt_info = self.scorer.multi_prompt
        print(
            prompt_info.format(categories_ordered_pair="테스트 순서쌍", question="테스트 질문", answer="테스트 답변"))

    def test_prompt_info_for_router_chain(self):
        for prompt_info_name in self.scorer.prompt_info_for_router_chain:
            self.assertTrue(is_not_none_string(prompt_info_name))
            self.assertTrue(is_not_none_string(self.scorer.prompt_info_for_router_chain[prompt_info_name]))

            print("prompt_info_name : ", prompt_info_name)
            print('prompt_info_value', self.scorer.prompt_info_for_router_chain[prompt_info_name])
            print("----------------------------------------------------")
