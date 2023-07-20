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


class AnswerCategoryClassifier:
    def __init__(self):
        abs_path = os.path.dirname(os.path.abspath(__file__))

        with open(abs_path + '/category_prompt.json', 'r') as f:
            data = json.load(f)

        self.prompt = data['prompt']

    def classify_category_of_answer(self, job_group: str, question: str, answer: str) -> str:
        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    f"""
                    You are interviewers working at company in job position {job_group}.
                    """
                ),
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

        llm = ChatOpenAI(temperature=0.5, model_name='gpt-3.5-turbo', verbose=True, streaming=True,
                         callbacks=[StreamingStdOutCallbackHandler()])
        chain = LLMChain(llm=llm, prompt=prompt)

        return chain.run({"question": question, "answer": answer})
