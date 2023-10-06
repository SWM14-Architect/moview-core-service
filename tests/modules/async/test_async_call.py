import asynctest
import asyncio
import time
from moview.modules.question_generator.followup_question_giver import FollowUpQuestionGiver
from langchain import LLMChain
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate
)

from moview.utils.prompt_loader import PromptLoader
from langchain.chat_models import ChatOpenAI
from moview.environment.environment_loader import EnvironmentLoader

OPENAI_API_KEY_PARAM = "openai-api-key"


def pasre_result(result):
    import re
    pattern = re.compile(r'(\d\.\s)(.*#)')  # 0번쨰에는 숫자, 1번째에는 질문이 나옵니다.
    matches = pattern.findall(result)

    results = []
    for match in matches:
        results.append(match[1].rstrip(' #'))  # '#'를 제거한 질문을 리스트에 추가합니다.

    return results


async def give_followup_async(chain: LLMChain, question: str, answer: str):
    return await chain.arun({  # run이 아니라 arun이에요!!
        "question": question,
        "answer": answer
    })


async def give_followup_async_concurrently(prompt, question: str, answer: str, task_count: int):
    llm = ChatOpenAI(openai_api_key=EnvironmentLoader.getenv(OPENAI_API_KEY_PARAM),
                     temperature=0.7, model_name='gpt-3.5-turbo', verbose=False)

    prompt = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(
                prompt.format()
            ),
            HumanMessagePromptTemplate.from_template(
                """
                면접관의 질문: {question}

                면접 지원자의 답변: {answer} 

                양식을 지켜서 후속 질문을 생성하세요.    
                """)
        ],
        input_variables=["question", "answer"],
    )

    chain = LLMChain(llm=llm, prompt=prompt)

    # 핵심 비동기 로직
    tasks = [give_followup_async(chain, question, answer) for _ in range(task_count)]
    return await asyncio.gather(*tasks)


class TestAsyncCall(asynctest.TestCase):

    def setUp(self) -> None:
        self.prompt_loader = PromptLoader()
        self.followup_question_giver = FollowUpQuestionGiver(self.prompt_loader)
        self.prompt = self.prompt_loader.load_prompt_json(FollowUpQuestionGiver.__name__)
        self.question = "이 회사에서 어떻게 성과를 낼 건지 말씀해주세요."
        self.answer = "탁월한 개발자로서 이 회사의 핵심 인재가 되겠습니다. 그리고 신입 개발자들의 온보딩을 도움으로써 회사의 효율성을 높이는 시니어 개발자가 될 것입니다."

    # async def test_async_generate_follow_up(self):
    #     start_time = time.perf_counter()
    #     total = 100
    #     fail = 0
    #     result = await give_followup_async_concurrently(self.prompt, self.question, self.answer, total)
    #     for i, elem in enumerate(result):
    #         is_fail = False
    #         print(elem, end="\n")
    #         if len(pasre_result(elem)) != 2:
    #             fail += 1
    #         print(f"{i + 1}번째 시도 {'실패' if is_fail else '성공'}: {result}\n ")
    #     print(f"실패 : {fail} 성공률 : {100 - fail / total * 100}%")
    #
    #     elapsed_time = time.perf_counter() - start_time
    #     print(f"elapsed time: {elapsed_time:0.2f} seconds")
