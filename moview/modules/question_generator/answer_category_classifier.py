from langchain import LLMChain
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate
)
from moview.utils.prompt_loader import PromptLoader
from moview.environment.llm_factory import LLMModelFactory
from moview.loggers.mongo_logger import *


class AnswerCategoryClassifier:
    def __init__(self):
        prompt_loader = PromptLoader()
        self.prompt = prompt_loader.load_prompt_json(AnswerCategoryClassifier.__name__)

    def classify_category_of_answer(self, job_group: str, question: str, answer: str) -> str:
        """
        질문과 답변, 직군을 입력 받아서 질문과 답변이 면접 유형 중 어느 대분류에 해당하는 지 분류하는 메서드.
        """

        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    self.prompt.format(job_group=job_group)
                ),
                HumanMessagePromptTemplate.from_template(
                    """
                    Previous interview question: {question}

                    Candidate's response : {answer} 
                    """)
            ],
            input_variables=["question", "answer"],
        )

        llm = LLMModelFactory.create_chat_open_ai(temperature=0.5)

        chain = LLMChain(llm=llm, prompt=prompt)

        prompt_result = chain.run({
            "question": question,
            "answer": answer
        })

        prompt_result_logger("answer category classifier prompt result", prompt_result=prompt_result)

        return prompt_result
