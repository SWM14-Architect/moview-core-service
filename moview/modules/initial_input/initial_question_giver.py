from typing import List
import json
import os
import re

from langchain import LLMChain
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate
)
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler


class InitialQuestionGiver:
    def __init__(self):
        abs_path = os.path.dirname(os.path.abspath(__file__))

        with open(abs_path + '/initial_question_giver.json', 'r') as f:
            data = json.load(f)

        self.prompt = data['prompt']

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

        llm = ChatOpenAI(temperature=0.7, model_name='gpt-3.5-turbo', verbose=True, streaming=True,
                         callbacks=[StreamingStdOutCallbackHandler()])
        chain = LLMChain(llm=llm, prompt=prompt)

        initial_questions_from_llm = chain.run({
            "analysis": analysis_about_one_cover_letter})

        return self.__parse_result_from_llm(initial_questions_from_llm)

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

        inital_questions = []
        for match in matches:
            inital_questions.append(match[1].rstrip(' #')) # '#'를 제거한 질문을 리스트에 추가합니다.

        return inital_questions