import asynctest
import asyncio
import time
from moview.modules.question_generator.followup_question_giver import FollowUpQuestionGiver
from moview.utils.prompt_loader import PromptLoader
import openai
from moview.environment.llm_factory import LLMModelFactory

OPENAI_API_KEY_PARAM = "openai-api-key"


def pasre_result(result):
    import re
    pattern = re.compile(r'(\d\.\s)(.*#)')  # 0번쨰에는 숫자, 1번째에는 질문이 나옵니다.
    matches = pattern.findall(result)

    results = []
    for match in matches:
        results.append(match[1].rstrip(' #'))  # '#'를 제거한 질문을 리스트에 추가합니다.

    return results


async def give_followup_async(model: str, messages):
    response = await openai.ChatCompletion.acreate(model=model, messages=messages, temperature=0.3)
    return response['choices'][0]['message']['content']


async def give_followup_async_concurrently(prompt: dict, question: str, answer: str, task_count: int):
    openai.api_key = LLMModelFactory.load_api_key_for_open_ai()

    model = "gpt-3.5-turbo-16k"

    messages = [{
        "role": "system",
        "content": prompt.format()
    }, {
        "role": "user",
        "content": f"""
                면접관의 질문: {question}

                면접 지원자의 답변: {answer} 

                양식을 지켜서 후속 질문을 생성하세요.     
                """
    }]

    # 핵심 비동기 로직
    tasks = [give_followup_async(model=model, messages=messages) for _ in range(task_count)]
    return await asyncio.gather(*tasks)


class TestAsyncCall(asynctest.TestCase):

    def setUp(self) -> None:
        self.prompt_loader = PromptLoader()
        self.followup_question_giver = FollowUpQuestionGiver(self.prompt_loader)
        self.prompt = self.prompt_loader.load_prompt_json(FollowUpQuestionGiver.__name__)
        self.question = "이 회사에서 어떻게 성과를 낼 건지 말씀해주세요."
        self.answer = "탁월한 개발자로서 이 회사의 핵심 인재가 되겠습니다. 그리고 신입 개발자들의 온보딩을 도움으로써 회사의 효율성을 높이는 시니어 개발자가 될 것입니다."

    async def test_async_generate_follow_up(self):
        start_time = time.perf_counter()
        total = 5
        fail = 0
        try:
            result = await give_followup_async_concurrently(self.prompt, self.question, self.answer, total)
        except openai.error.RateLimitError as e:
            print("RateLimitError 발생. 1분 뒤에 다시 시도해주세요.")
            print(e)
            result = []

        for i, elem in enumerate(result):
            is_fail = False
            print(elem, end="\n")
            if len(pasre_result(elem)) != 2:
                is_fail = True
                fail += 1
            print(f"{i + 1}번째 시도 {'실패' if is_fail else '성공'}: {result}\n ")
        print(f"실패 : {fail} 성공률 : {100 - fail / total * 100}%")

        elapsed_time = time.perf_counter() - start_time
        print(f"elapsed time: {elapsed_time:0.2f} seconds")
