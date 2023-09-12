import asynctest
import asyncio
import re
from typing import List

from tests.common_code_for_test import is_not_none_string
from moview.modules.answer_evaluator.answer_evaluator import AnswerEvaluator
from moview.utils.prompt_loader import PromptLoader


def parse_result(result: str) -> List[str]:
    result_list = []
    matches = re.findall(r':\s*(.*)', result)

    for match in matches:
        result_list.append(match.strip())

    return result_list


class TestAnswerEvaluator(asynctest.TestCase):
    def setUp(self) -> None:
        self.prompt_loader = PromptLoader()
        self.evaluator = AnswerEvaluator(self.prompt_loader)
        self.question = "테스트 면접 문항"
        self.answer = "테스트 면접 답변"

    def test_load_prompt(self):
        self.assertTrue(is_not_none_string(self.evaluator.prompt))
        print(self.evaluator.prompt.format())

    async def test_evaluate_answer(self):
        evaluation_result = await self.evaluator.evaluate_answer(question=self.question,
                                                                 answer=self.answer)
        parsed_result = parse_result(evaluation_result)
        print(parsed_result)
        self.assertTrue(len(parsed_result) == 2)

    async def test_evaluate_answer_concurrently(self):
        total = 10

        tasks = [self.evaluator.evaluate_answer(self.question, self.answer) for _ in range(total)]
        evaluation_result = await asyncio.gather(*tasks)

        result_num = 0
        fail = 0
        for i, result in enumerate(evaluation_result):
            is_fail = False
            parsed_result = parse_result(result)
            result_num = i + 1

            if len(parsed_result) != 2:
                is_fail = True
                fail += 1

            print(f"{i + 1}번째 시도 {'실패' if is_fail else '성공'}:\n{result}\n ")
        print(f"실패 : {fail} 성공률 : {100 - fail / total * 100}%")

        self.assertEqual(result_num, total)
