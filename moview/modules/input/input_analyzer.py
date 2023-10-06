from langchain import LLMChain
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate
)
from moview.utils.prompt_loader import PromptLoader
from moview.environment.llm_factory import LLMModelFactory
from moview.config.loggers.mongo_logger import prompt_result_logger
from moview.utils.retry_decorator import async_retry
from moview.utils.singleton_meta_class import SingletonMeta


class InputAnalyzer(metaclass=SingletonMeta):
    def __init__(self, prompt_loader: PromptLoader):
        self.prompt = prompt_loader.load_prompt_json(InputAnalyzer.__name__)

    @async_retry()
    async def analyze_initial_input(self, job_group: str, recruitment_announcement: str, cover_letter_question: str,
                                    cover_letter_answer: str) -> str:
        """
        자소서 문항과 자소서 답변을 분석하여 분석 결과를 반환하는 메서드 (답변,문항) 한 개의 쌍에 대해서 분석하는 메서드다.

        Args:
            job_group: 직군
            recruitment_announcement: 공고
            cover_letter_question: i번째 자소서 문항
            cover_letter_answer: i 번째 자소서 답번

        Returns: i번째 자소서 답변, 문항 순서쌍에 대해 분석한 결과 문자열

        """
        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    self.prompt.format(job_group=job_group)
                ),
                HumanMessagePromptTemplate.from_template(
                    """
                    job posting : {job_posting}
                    cover letter question : {cover_letter_question}
                    cover letter answer : {cover_letter_answer}    
                    """)
            ],
            input_variables=["job_posting", "cover_letter_question", "cover_letter_answer"],
        )

        llm = LLMModelFactory.create_chat_open_ai(model_name="gpt-3.5-turbo-16k", temperature=0.5)

        chain = LLMChain(llm=llm, prompt=prompt)

        prompt_result = await chain.arun({
            "job_posting": recruitment_announcement,
            "cover_letter_question": cover_letter_question,
            "cover_letter_answer": cover_letter_answer})

        prompt_result_logger("input analyzer prompt result", prompt_result=prompt_result)

        return prompt_result
