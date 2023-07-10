from langchain import LLMChain
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate
)

from moview.utils.data_manager import *
from moview.utils.util import create_question_parser, remove_indent
from typing import *

QUESTION_COUNT: Final[int] = 10


class InitQuestionGenerator:
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager

    def generate_init_question(
            self,
            chat_manager: ChatManager,
    ) -> List[str]:
        """
        사용자 데이터를 바탕으로, 초기 질문을 생성합니다.
        Returns:
            List: 초기 질문 리스트
        """
        prompt = self.__make_init_question_prompt()
        create_question_chain = LLMChain(llm=chat_manager.get_chat_model(),
                                         prompt=prompt)
        output = create_question_chain(str(QUESTION_COUNT))
        return create_question_parser(output['text'])

    def __make_init_question_prompt(self) -> ChatPromptTemplate:
        """
        초기 질문 생성을 위한 prompt를 생성합니다.
        Returns:
            PromptTemplate: 초기 질문 생성을 위한 prompt
        """
        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    remove_indent(
                        f"""You are an interviewer at {self.data_manager.company}.

                        {self.data_manager.get_userdata()}
                        """)),

                HumanMessagePromptTemplate.from_template(
                    remove_indent(
                        """As an interviewer, you need to generate {question_count} interview questions based on the applicant's desired position, their cover letter. Additionally, consider the qualities and skills the company is looking for in candidates based on the job posting. Please follow the format below when creating the questions:

                        ```
                        1. Question content
                        2. Question content
                        3. Question content
                        ...
                        ```

                        Please write in Korean.
                        """))
            ],
            input_variables=["question_count"],
        )
        return prompt
