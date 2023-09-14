from typing import Optional, List

from langchain import LLMChain
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate
)

from moview.exception.evaluation_parse_error import EvaluationParseError
from moview.utils.retry_decorator import async_retry
from moview.utils.prompt_loader import PromptLoader
from moview.utils.prompt_parser import PromptParser
from moview.environment.llm_factory import LLMModelFactory
from moview.config.loggers.mongo_logger import prompt_result_logger
from moview.utils.singleton_meta_class import SingletonMeta


class AnswerEvaluator(metaclass=SingletonMeta):
    def __init__(self, prompt_loader: PromptLoader):
        self.prompt = prompt_loader.load_prompt_json(AnswerEvaluator.__name__)
        self.llm = LLMModelFactory.create_chat_open_ai(temperature=0.7)

    @async_retry()
    async def evaluate_answer(self, question: str, answer: str) -> List[str]:
        """

        면접자의 답변에 대해서 평가하여 긍정적인 점과 개선해야 할 점을 반환하는 메소드

        Args:
            question: 면접자가 받았던 질문
            answer: 면접자의 답변

        Returns: 면접자의 답변에 대해 분석한 결과 리스트
            List["긍정적인 점", "개선해야 할 점"]

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

        prompt_result_logger("answer analyze prompt result", question=question, answer=answer, prompt_result=prompt_result)

        parsed_result = PromptParser.parse_evaluation(prompt_result)
        # 파싱된 평가의 개수가 2개(긍정적인 점, 개선해야 할 점)이며 비어 있지 않다면, 파싱 성공으로 간주합니다. 파싱이 성공하면, 파싱된 질문 리스트를 반환합니다.
        if len(parsed_result) == 2 and parsed_result[0] != "" and parsed_result[1] != "":
            return parsed_result
        else:
            raise EvaluationParseError()  # 파싱이 실패하면, EvaluationParseError 발생시킵니다.
