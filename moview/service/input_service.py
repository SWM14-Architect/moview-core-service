from typing import List

from moview.service.interviewee_data_vo import IntervieweeDataVO, IntervieweeInitialInputData


class InputService:
    def __init__(self):
        self.INIT_QUESTION_MULTIPLIER = 2  # 각 자소서 답변에 대해 초기 질문을 몇 개씩 생성할 것인지 결정하는 상수

    def ask_initial_question_to_interviewee(self, session_id,
                                            initial_input_data: IntervieweeInitialInputData) -> IntervieweeDataVO:
        """

        Args:
            session_id: flask session id
            initial_input_data: 면접 지원자의 초기 입력 정보(직군,모집공고, 자소서 문항 리스트, 자소서 답변 리스트)

        Returns: 출제된 초기 질문 리스트 (길이는 initial_question_count)

        """

        # 사용자 입력 정보 분석 (직군, 공고, 자소서 문항 리스트, 자소서 답변 리스트)-> 분석 결과 문자열 리스트 (자소서 입력 개수만큼 분석 내용이 나옵니다.)
        initial_analysis_list_about_interviewee = self.__analyze_initial_inputs_of_interviewee(initial_input_data)

        initial_question_list = []  # List[str]

        # 각 자소서 답변 분석 내용에 대해 2개씩 초기 질문 생성.
        for analysis_about_one_cover_letter in initial_analysis_list_about_interviewee:

            # 길이 2의 질문 리스트 생성 List[str]
            created_questions = self.__create_initial_questions(
                analysis_about_one_cover_letter=analysis_about_one_cover_letter,
                question_count=self.INIT_QUESTION_MULTIPLIER)

            # 생성된 초기 질문 2개를 initial_question_list에 추가. List[str] (created_questions) 에서 List[str]
            # (initial_question_list)로 옮기기 위한 코드
            for _ in range(self.INIT_QUESTION_MULTIPLIER):
                initial_question_list.append(created_questions.pop())

        return IntervieweeDataVO(session_id=session_id,
                                 initial_question_list=initial_question_list,  # 자소서 문항, 답변 순서쌍 * 2 만큼 초기질문이 들어있음.
                                 initial_interview_analysis=initial_analysis_list_about_interviewee,
                                 initial_input_data=initial_input_data)

    def __analyze_initial_inputs_of_interviewee(self, initial_input_data: IntervieweeInitialInputData) -> List[str]:
        """
        (자소서 문항,자소서 답변) 전체 쌍에 대해 LLM을 이용하여 분석하는 메서드
        해당 쌍을 4개 입력 받았다면, 4개의 쌍에 대해 분석을 수행한다.
        cover_letter_questions 와 cover_letter_answers 의 길이는 같아야 한다.
        그리고 인덱스를 i라 할 때, (cover_letter_questions[i], cover_letter_answers[i]) 쌍이다.

        Args:
            initial_input_data: 면접 지원자의 초기 입력 정보(직군,모집공고, 자소서 문항 리스트, 자소서 답변 리스트)

        Returns: 입력 파라미터에 대한 분석 결과 문자열 리스트

        """
        pass

    def __create_initial_questions(self, analysis_about_one_cover_letter: str, question_count: int) -> List[str]:
        """

        Args:
            analysis_about_one_cover_letter: 면접 지원자 자소서 답변 한 개에 대한 분석 내용
            question_count: 출제할 질문 개수

        Returns: 분석 내용을 바탕으로 생성된 초기 질문 문자열 리스트 (question_count만큼 생성)

        """
        pass
