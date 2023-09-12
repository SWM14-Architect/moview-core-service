import asynctest

from moview.utils.prompt_loader import PromptLoader
from tests.common_code_for_test import is_not_none_string
from moview.modules.input.input_analyzer import InputAnalyzer


class TestInputAnalyzer(asynctest.TestCase):

    def setUp(self) -> None:
        self.prompt_loader = PromptLoader()
        self.analyzer = InputAnalyzer(prompt_loader=self.prompt_loader)

    def test_load_prompt(self):
        self.assertTrue(is_not_none_string(self.analyzer.prompt))
        print(self.analyzer.prompt.format(job_group="테스트 직군"))

    async def test_analyze_initial_input(self):
        job_group = "IT"
        recruitment_announcement = "테스트 공고"
        cover_letter_question = "테스트 자소서 문항"
        cover_letter_answer = "테스트 자소서 답변"

        analysis_result = await self.analyzer.analyze_initial_input(job_group=job_group,
                                                              recruitment_announcement=recruitment_announcement,
                                                              cover_letter_question=cover_letter_question,
                                                              cover_letter_answer=cover_letter_answer)
        self.assertTrue(is_not_none_string(analysis_result))
