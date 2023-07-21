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


class FollowUpQuestionGiver:

    def __init__(self):
        abs_path = os.path.dirname(os.path.abspath(__file__))

        with open(abs_path + '/followup_question_prompt.json', 'r') as f:
            data = json.load(f)

        self.prompt1 = data['prompt1']
        self.prompt2 = data['prompt2']
        self.prompt3 = data['prompt3']
        self.prompt4 = data['prompt4']
        
    def give_followup_question(self, job_group: str, question: str, answer: str, previous_question: str,
                               categories_ordered_pair: str) -> str:
        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    self.prompt1 + job_group + "." +
                    self.prompt2 + categories_ordered_pair + "\"" +
                    self.prompt3 + previous_question +
                    self.prompt4
                ),
                HumanMessagePromptTemplate.from_template(
                    """
                    interview question: {question}

                    candidate's answer : {answer}    
                    """)
            ],
            input_variables=["question", "answer"],
        )

        llm = ChatOpenAI(temperature=0.7, model_name='gpt-3.5-turbo', verbose=True, streaming=True,
                         callbacks=[StreamingStdOutCallbackHandler()])
        chain = LLMChain(llm=llm, prompt=prompt)

        return chain.run({"question": question, "answer": answer})
