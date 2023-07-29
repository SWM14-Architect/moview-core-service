from langchain import LLMChain
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate
)
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from moview.modules.prompt_loader.prompt_loader import PromptLoader


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

        llm = ChatOpenAI(temperature=0.3, model_name='gpt-3.5-turbo', verbose=True, streaming=True,
                         callbacks=[StreamingStdOutCallbackHandler()])
        chain = LLMChain(llm=llm, prompt=prompt)

        return chain.run({"question": question, "answer": answer})
