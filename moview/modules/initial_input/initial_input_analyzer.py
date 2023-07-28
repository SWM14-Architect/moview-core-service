import json
import os

from langchain import LLMChain
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate
)
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler


class InitialInputAnalyzer:
    def __init__(self):
        abs_path = os.path.dirname(os.path.abspath(__file__))

        with open(abs_path + '/InitialInputAnalyzer.json', 'r') as f:
            data = json.load(f)

        self.prompt = data['prompt']

    def analyze_initial_input(self, job_group: str, recruitment_announcement: str, cover_letter_question: str,
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

        llm = ChatOpenAI(temperature=0.5, model_name='gpt-3.5-turbo', verbose=True, streaming=True,
                         callbacks=[StreamingStdOutCallbackHandler()])
        chain = LLMChain(llm=llm, prompt=prompt)

        return chain.run({
            "job_posting": recruitment_announcement,
            "cover_letter_question": cover_letter_question,
            "cover_letter_answer": cover_letter_answer})
