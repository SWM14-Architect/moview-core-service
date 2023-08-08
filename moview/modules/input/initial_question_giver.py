from typing import List
import re

from langchain import LLMChain
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate
)

from moview.modules.prompt_loader.prompt_loader import PromptLoader
from moview.environment.llm_factory import LLMModelFactory
from moview.loggers.mongo_logger import *


class InitialQuestionParseError(Exception):

    def __init__(self, message="initial question parse error"):
        self.message = message
        super().__init__(self.message)


class InitialQuestionGiver:

    def __init__(self):
        prompt_loader = PromptLoader()
        self.prompt = prompt_loader.load_prompt_json(InitialQuestionGiver.__name__)

    def give_initial_questions(self, analysis_about_one_cover_letter: str, question_count: int) -> List[str]:
        """

        Args:
            analysis_about_one_cover_letter: 면접 지원자 자소서 답변 한 개에 대한 분석 내용
            question_count: 출제할 질문 개수

        Returns: 분석 내용을 바탕으로 생성된 초기 질문 문자열 리스트 (question_count만큼 생성)

        """

        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    self.prompt.format(question_count=question_count)
                ),
                HumanMessagePromptTemplate.from_template(
                    """
                    analysis about cover letter : {analysis} 
                    """)
            ],
            input_variables=["analysis"],
        )

        llm = LLMModelFactory.create_chat_open_ai(temperature=0.7)

        chain = LLMChain(llm=llm, prompt=prompt)

        initial_questions_from_llm = chain.run({
            "analysis": analysis_about_one_cover_letter})

        prompt_result_logger("initial question prompt result", prompt_result=initial_questions_from_llm)

        parse_question = self.__parse_result_from_llm(initial_questions_from_llm)
        # 파싱된 질문 개수가 출제할 질문 개수와 같으면, 파싱 성공으로 간주합니다. 파싱이 성공하면, 파싱된 질문 리스트를 반환합니다.
        if len(parse_question) == question_count:
            return parse_question
        else:
            raise InitialQuestionParseError()  # 파싱이 실패하면, InitialQuestionParseError를 발생시킵니다.

    def __parse_result_from_llm(self, initial_questions_from_llm: str) -> List[str]:
        """

        Args:
            initial_questions_from_llm: llm으로부터 온 초기 질문 문자열

        Returns:  초기 질문 문자열 리스트 (파싱됨)

        """
        # 패턴을 정의합니다.
        # 문항 번호와 점 그리고 공백 뒤에 오는 모든 문자(질문)를 찾습니다.
        # 여기서 .*#는 점 뒤에 오는 모든 문자와 '#'를 의미합니다.
        pattern = re.compile(r'(\d\.\s)(.*#)')  # 0번쨰에는 숫자, 1번째에는 질문이 나옵니다.
        matches = pattern.findall(initial_questions_from_llm)

        initial_questions = []
        for match in matches:
            initial_questions.append(match[1].rstrip(' #'))  # '#'를 제거한 질문을 리스트에 추가합니다.

        return initial_questions
