from langchain import LLMChain
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate
)
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from moview.modules.prompt_loader.prompt_loader import SingletonPromptLoader


class AnswerSubCategoryClassifier:
    def __init__(self):
        prompt_loader = SingletonPromptLoader()
        self.prompt = prompt_loader.load_prompt_json(AnswerSubCategoryClassifier.__name__)

    def classify_sub_category_of_answer(self, job_group: str, question: str, answer: str, categories: str) -> str:
        """
        질문과 답변, 직군, 대분류를 입력 받아서 질문과 답변이 면접 유형 중 어느 중분류에 해당하는 지 분류하는 메서드.

        """

        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    self.prompt.format(job_group=job_group, categories=categories)
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
