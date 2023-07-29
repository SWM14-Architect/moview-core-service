import datetime
from langchain import LLMChain
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate
)

from moview.utils.llm_interface import *
from moview.utils.util import remove_indent, write_log_in_txt


class InputInfoAnalyzer:
    """
    회사의 모집공고와 직무 정보를 토대로 면접자의 자기소개서와 1분 자기소개를 분석하여 면접관으로써 좋은 점과 아쉬운 점을 분석하여 출력합니다.
    """

    def __init__(self, user_data: str):
        self.user_data = user_data

    def analyze_input_info(self, chat_manager: ChatManager) -> str:
        """
        Args:
            chat_manager: OpenAI의 API를 사용하기 위한 ChatManager 객체

        Returns:
            str: 사용자 정보 평가 결과
        """

        log = {"time": str(datetime.datetime.now()), "message": "Start of InputInfoAnalyzer"}
        write_log_in_txt(log, InputInfoAnalyzer.__name__)

        # 면접자의 자기소개서와 1분 자기소개를 분석하기 위한 프롬프트를 작성합니다.
        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    self._make_system_template_for_analyzing_input_info()
                ),

                HumanMessagePromptTemplate.from_template(
                    self._make_human_template_for_analyzing_input_info()
                )
            ],
            input_variables=["user_data"],
        )

        # 작성된 프롬프트를 이용하여 chain을 생성하고 실행합니다.
        create_question_chain = LLMChain(llm=chat_manager.get_chat_model(),
                                         prompt=prompt)
        output = create_question_chain(self.user_data)
        result = output['text']

        log = {"time": str(datetime.datetime.now()), "message": "End of InputInfoAnalyzer. result is : " + result}
        write_log_in_txt(log, InputInfoAnalyzer.__name__)

        return result

    def _make_system_template_for_analyzing_input_info(self) -> str:
        return "You are an interviewer."

    def _make_human_template_for_analyzing_input_info(self) -> str:
        return remove_indent(
            """Please read the cover letter of the interviewee and provide an evaluation from the perspective, dividing it into positive aspects and areas for improvement. Please write in Korean.
            
            {user_data}
            
            The format is as follows:

            "좋은점":
            - Content of positive aspects
            "아쉬운점":
            - Content of areas for improvement

            Please write in Korean.
            """)
