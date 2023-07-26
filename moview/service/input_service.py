from typing import List

from moview.service.interviewee_data_vo import IntervieweeDataVO, IntervieweeInitialInputData


class InputService:
    def __init__(self):
        pass

    def ask_initial_question_to_interviewee(self, session_id, initial_input_data: IntervieweeInitialInputData,
                                            initial_question_count: int) -> IntervieweeDataVO:
        """

        Args:
            session_id: flask session id
            initial_input_data: 면접 지원자의 초기 입력 정보(직군,모집공고, 자소서 문항 리스트, 자소서 답변 리스트)
            initial_question_count: 초기 질문을 몇 번 할 것인지

        Returns: 출제된 초기 질문 리스트 (길이는 initial_question_count)

        """

        # 3. 사용자 입력 정보 분석 (직군, 공고, 자소서 문항, 자소서 답변)
        initial_analysis_about_interviewee = self.__analyze_initial_inputs_of_interviewee(initial_input_data)

        # 7. 초기 질문 생성 요청 (n회)
        initial_questions = []
        for i in range(initial_question_count):
            initial_question = self.__create_initial_question(
                initial_analysis_about_interviewee=initial_analysis_about_interviewee)
            initial_questions.append(initial_question)  # 초기 질문 리스트에 추가

        return IntervieweeDataVO(session_id=session_id, initial_question_list=initial_questions,
                                 initial_interview_analysis=initial_analysis_about_interviewee,
                                 initial_input_data=initial_input_data)

    def __analyze_initial_inputs_of_interviewee(self, initial_input_data: IntervieweeInitialInputData) -> str:
        """
        (자소서 문항,자소서 답변) 전체 쌍에 대해 LLM을 이용하여 분석하는 메서드
        해당 쌍을 4개 컨트롤러에서 입력 받았다면, 4개의 쌍에 대해 분석을 수행한다.
        cover_letter_questions 와 cover_letter_answers 의 길이는 같아야 한다.
        그리고 인덱스를 i라 할 때, (cover_letter_questions[i], cover_letter_answers[i]) 쌍이다.

        Args:
            initial_input_data: 면접 지원자의 초기 입력 정보(직군,모집공고, 자소서 문항 리스트, 자소서 답변 리스트)

        Returns: 입력 파라미터에 대한 분석 결과 문자열

        """
        pass

    def __create_initial_question(self, initial_analysis_about_interviewee: str) -> str:
        """

        Args:
            initial_analysis_about_interviewee: 면접 지원자 초기 입력에 대한 분석 내용

        Returns: 면접 지원자에게 출제할 초기 질문 1개

        """
        pass
