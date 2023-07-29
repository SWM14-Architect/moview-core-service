import datetime
from langchain import LLMChain
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate
)

from moview.utils.llm_interface import *
from moview.utils.util import create_question_parser, remove_indent, write_log_in_txt
from typing import *

QUESTION_COUNT: Final[int] = 10


class InitQuestionGenerator:
    def __init__(self, user_data: str):
        self.user_data = user_data

    def generate_init_question(
            self,
            chat_manager: ChatManager,
    ) -> List[str]:
        """
        사용자 데이터를 바탕으로, 초기 질문을 생성합니다.
        Returns:
            List: 초기 질문 리스트
        """

        log = {"time": str(datetime.datetime.now()), "message": "Start of InitQuestionGenerator"}
        write_log_in_txt(log, InitQuestionGenerator.__name__)

        prompt = self.__make_init_question_prompt()

        log = {"time": str(datetime.datetime.now()),
               "message": "InitQuestionGenerator made a prompt. prompt is : " + str(prompt)}
        write_log_in_txt(log, InitQuestionGenerator.__name__)

        result = self.__make_result_of_question_chain(chat_manager.get_chat_model(), prompt)

        log = {"time": str(datetime.datetime.now()),
               "message": "End of InitQuestionGenerator. result is : " + str(result)}
        write_log_in_txt(log, InitQuestionGenerator.__name__)

        return result

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
                        f"""You are an interviewer.

                        {self.user_data}""")
                ),

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

    def __make_result_of_question_chain(
        self,
        chat_model: ChatOpenAI,
        prompt: ChatPromptTemplate
    ) -> list:
        create_question_chain = LLMChain(llm=chat_model,
                                         prompt=prompt)
        output = create_question_chain(str(QUESTION_COUNT))

        return create_question_parser(output['text'])
