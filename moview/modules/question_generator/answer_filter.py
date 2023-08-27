from langchain import LLMChain
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate
)

from moview.utils.prompt_loader import PromptLoader
from moview.environment.llm_factory import LLMModelFactory
from moview.loggers.mongo_logger import *


class AnswerFilter:

    def __init__(self):
        prompt_loader = PromptLoader()
        self.prompt = prompt_loader.load_prompt_json(AnswerFilter.__name__)

    def exclude_invalid_answer(self, job_group: str, question: str, answer: str) -> str:
        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    self.prompt.format(job_group=job_group)
                ),
                HumanMessagePromptTemplate.from_template(
                    """
                    Previous interview question: {question}

                    Candidate's response : {answer}

                    """
                )
            ],
            input_variables=["question", "answer"],
        )

        llm = LLMModelFactory.create_chat_open_ai(temperature=0.3)

        chain = LLMChain(llm=llm, prompt=prompt)

        prompt_result = chain.run({
            "question": question,
            "answer": answer
        })

        prompt_result_logger("answer filter prompt result", prompt_result=prompt_result)

        return prompt_result
