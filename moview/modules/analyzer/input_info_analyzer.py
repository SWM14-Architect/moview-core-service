from langchain import LLMChain
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate
)

from moview.utils.data_manager import *
from moview.utils.util import remove_indent


class InputInfoAnalyzer:
    """
    회사의 모집공고와 직무 정보를 토대로 면접자의 자기소개서와 1분 자기소개를 분석하여 면접관으로써 좋은 점과 아쉬운 점을 분석하여 출력합니다.
    """
    def __init__(self, data_manager: DataManager, evaluation_manager: EvaluationManager):
        self.data_manager = data_manager
        self.evaluation_manager = evaluation_manager

    def analyze_input_info(self, chat_manager: ChatManager):
        """
        Args:
            chat_manager: OpenAI의 API를 사용하기 위한 ChatManager 객체

        Returns:
            None
        """
        chat_manager = ChatManager()

        # 면접자의 자기소개서와 1분 자기소개를 분석하기 위한 프롬프트를 작성합니다.
        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    remove_indent(
                        f"""You are an interviewer at {self.data_manager.company}.

                            {self.data_manager.get_userdata()}
                            """)),

                HumanMessagePromptTemplate.from_template(
                    remove_indent(
                        """As an interviewer, Please read the cover letter and self-introduction of the interviewee and provide an evaluation from the {company}'s perspective, dividing it into positive aspects and areas for improvement. Please write in Korean. The format is as follows:

                        "좋은점":
                        - Content of positive aspects
                        "아쉬운점":
                        - Content of areas for improvement

                        Please write in Korean.
                        """))
            ],
            input_variables=["company"],
        )

        # 작성된 프롬프트를 이용하여 chain을 생성하고 실행합니다.
        create_question_chain = LLMChain(llm=chat_manager.get_chat_model(),
                                         prompt=prompt)
        output = create_question_chain(self.data_manager.company)

        # 분석 결과를 EvaluationManager에 저장합니다.
        self.evaluation_manager.add_coverletter_evaluation(output['text'])
