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


class AnswerFilter:

    def __init__(self):
        abs_path = os.path.dirname(os.path.abspath(__file__))

        with open(abs_path + '/answer_filter_prompt.json', 'r') as f:
            data = json.load(f)

        self.prompt = data['prompt']

    def check_answer_appropriate(self, job_group: str, question: str, answer: str) -> str:
        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    self.prompt
                ),
                HumanMessagePromptTemplate.from_template(
                    """
                    Previous interview question: {question}

                    Candidate's response : {answer}

                    """)
            ],
            input_variables=["question", "answer"],
        )

        llm = ChatOpenAI(temperature=0.3, model_name='gpt-3.5-turbo', verbose=True, streaming=True,
                         callbacks=[StreamingStdOutCallbackHandler()])
        chain = LLMChain(llm=llm, prompt=prompt)

        return chain.run({"question": question, "answer": answer})
