from typing import List

from langchain import LLMChain
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate
)

from moview.exception.light_question_parse_error import LightQuestionParseError
from moview.utils.prompt_loader import PromptLoader
from moview.environment.llm_factory import LLMModelFactory
from moview.config.loggers.mongo_logger import prompt_result_logger
from moview.utils.prompt_parser import PromptParser
from moview.utils.singleton_meta_class import SingletonMeta
from moview.utils.retry_decorator import retry


class LightQuestionGiver(metaclass=SingletonMeta):

    def __init__(self, prompt_loader: PromptLoader):
        self.prompt = prompt_loader.load_prompt_json(LightQuestionGiver.__name__)
        self.llm = LLMModelFactory.create_chat_open_ai(model_name="gpt-3.5-turbo-16k", temperature=0.7)

    @retry()
    def give_light_questions_by_input_data(self, job_group: str, question_count: int) -> List[str]:
        """

        Args:
            job_group: 직군
            question_count: 출제할 질문 개수

        Returns: 직무 중심으로 출제된 질문 리스트 (light mode 전용)

        """
        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    self.prompt.format(
                        job_group=job_group,
                        question_count=question_count)
                ),
                HumanMessagePromptTemplate.from_template(
                    """
                    양식을 지켜서 직무 기술 면접 질문을 생성하세요.    
                    """
                )
            ]
        )

        chain = LLMChain(llm=self.llm, prompt=prompt)

        prompt_result = chain.run()

        prompt_result_logger("light question prompt result", prompt_result=prompt_result)

        parse_question = PromptParser.parse_question(prompt_result)

        if parse_question is not None:
            return parse_question
        else:
            raise LightQuestionParseError()
