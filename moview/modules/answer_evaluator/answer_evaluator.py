from langchain import LLMChain
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate
)

from moview.utils.prompt_loader import PromptLoader
from moview.environment.llm_factory import LLMModelFactory
from moview.config.loggers.mongo_logger import prompt_result_logger
from moview.utils.singleton_meta_class import SingletonMeta


class AnswerEvaluator(metaclass=SingletonMeta):
    def __init__(self, prompt_loader: PromptLoader):
        self.prompt = prompt_loader.load_prompt_json(AnswerEvaluator.__name__)
        self.llm = LLMModelFactory.create_chat_open_ai(temperature=0.7)

    async def evaluate_answer(self, question: str, answer: str) -> str:
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
                    self.prompt.format()
                ),
                HumanMessagePromptTemplate.from_template(
                    """
                    면접관의 질문 : {question}
                    면접 지원자의 답변 : {answer}
                    
                    양식을 지켜서 평가하세요. 
                    """)
            ],
            input_variables=["question", "answer"],
        )

        chain = LLMChain(llm=self.llm, prompt=prompt)

        prompt_result = await chain.arun({
            "question": question,
            "answer": answer
        })

        prompt_result_logger("answer analyze prompt result", prompt_result=prompt_result)

        return prompt_result
