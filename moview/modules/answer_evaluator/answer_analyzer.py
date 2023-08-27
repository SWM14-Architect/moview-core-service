from langchain import LLMChain
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate
)
from moview.utils.prompt_loader import PromptLoader
from moview.environment.llm_factory import LLMModelFactory
from moview.loggers.mongo_logger import *


class AnswerAnalyzer:
    def __init__(self):
        prompt_loader = PromptLoader()
        self.prompt = prompt_loader.load_prompt_json(AnswerAnalyzer.__name__)

    def analyze_answer_by_main_and_subcategories(self, question: str, answer: str, categories_ordered_pair: str) -> str:
        """

        면접자의 답변에 대해서 긍정적 평가와 부정적 평가를 반환하는 메소드

        Args:
            question: 면접자가 받았던 질문
            answer: 면접자의 답변
            categories_ordered_pair: "I think it is (대분류) especially (중분류)" 문자열

        Returns: 면접자의 답변에 대해 분석한 결과 문자열

        """
        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    self.prompt.format(categories_ordered_pair=categories_ordered_pair)
                ),
                HumanMessagePromptTemplate.from_template(
                    """
                    question : {question}
                    answer : {answer}
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

        prompt_result_logger("answer analyze prompt result", prompt_result=prompt_result)

        return prompt_result
