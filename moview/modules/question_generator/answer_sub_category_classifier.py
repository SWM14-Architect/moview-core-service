from langchain import LLMChain
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate
)

from moview.utils.prompt_loader import PromptLoader
from moview.environment.llm_factory import LLMModelFactory
from moview.config.loggers.mongo_logger import prompt_result_logger


class AnswerSubCategoryClassifier:
    def __init__(self):
        prompt_loader = PromptLoader()
        self.prompt = prompt_loader.load_prompt_json(AnswerSubCategoryClassifier.__name__)

    def classify_sub_category_of_answer(self, question: str, answer: str, category: str) -> str:
        """
        질문과 답변, 대분류를 입력 받아서 질문과 답변이 면접 유형 중 어느 중분류에 해당하는 지 분류하는 메서드.
        """
        
        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    self.prompt.format(category=category)
                ),
                HumanMessagePromptTemplate.from_template(
                    """
                    이전 면접 질문: {question}

                    지원자의 답변: {answer}    
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

        prompt_result_logger("answer sub category classifier prompt result", prompt_result=prompt_result)

        return prompt_result
