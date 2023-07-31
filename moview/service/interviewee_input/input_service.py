from typing import List

from moview.service.interviewee_data_vo import IntervieweeDataVO, IntervieweeInitialInputData
from moview.modules.initial_input.initial_input_analyzer import InitialInputAnalyzer
from moview.modules.initial_input.initial_question_giver import InitialQuestionGiver, InitialQuestionParseError


class IntervieweeInputService:
    def __init__(self):
        self.INIT_QUESTION_MULTIPLIER = 2  # 각 자소서 답변에 대해 초기 질문을 몇 개씩 생성할 것인지 결정하는 상수

        self.initial_input_analyzer = InitialInputAnalyzer()
        self.initial_question_giver = InitialQuestionGiver()

    def ask_initial_question_to_interviewee(self, session_id,
                                            initial_input_data: IntervieweeInitialInputData) -> IntervieweeDataVO:
        """

        Args:
            session_id: flask session id
            initial_input_data: 면접 지원자의 초기 입력 정보(직군,모집공고, 자소서 문항 리스트, 자소서 답변 리스트)

        Returns: 출제된 초기 질문 리스트 (길이는 initial_question_count)

        """

        # 적절하지 않은 사용자 정보 필터링.
        filtered_input_data = self.__filter_initial_inputs_of_interviewee(initial_input_data)

        # 사용자 입력 정보 분석 (직군, 공고, 자소서 문항 리스트, 자소서 답변 리스트)-> 분석 결과 문자열 리스트 (자소서 입력 개수만큼 분석 내용이 나옵니다.)
        analyzed_initial_inputs_of_interviewee = self.__analyze_initial_inputs_of_interviewee(filtered_input_data)

        initial_question_list = []  # List[str]

        # 각 자소서 답변 분석 내용에 대해 2개씩 초기 질문 생성.
        for analysis_about_one_cover_letter in analyzed_initial_inputs_of_interviewee:

            try:
                # 길이 (INIT_QUESTION_MULTIPLIER) 의 질문 리스트 생성 List[str]
                created_questions = self.initial_question_giver.give_initial_questions(
                    analysis_about_one_cover_letter=analysis_about_one_cover_letter,
                    question_count=self.INIT_QUESTION_MULTIPLIER)

                # 생성된 초기 질문 (INIT_QUESTION_MULTIPLIER)개를 initial_question_list에 추가.
                # List[str] (created_questions) 에서 List[str] (initial_question_list)로 옮기기 위한 코드
                for _ in range(self.INIT_QUESTION_MULTIPLIER):
                    initial_question_list.append(created_questions.pop())

            except InitialQuestionParseError as e:  # 파싱 실패한 경우
                # 빈 문자열 담기
                initial_question_list.append([])

        return IntervieweeDataVO(session_id=session_id,
                                 initial_question_list=initial_question_list,
                                 # (자소서 문항, 답변) 순서쌍 길이 * (INIT_QUESTION_MULTIPLIER) 만큼 초기질문이 들어있음.
                                 initial_interview_analysis=analyzed_initial_inputs_of_interviewee,
                                 initial_input_data=filtered_input_data)

    def __filter_initial_inputs_of_interviewee(self, initial_input_data: IntervieweeInitialInputData) \
            -> IntervieweeInitialInputData:
        """

        Args:
            initial_input_data: 면접 지원자의 초기 입력 정보(직군,모집공고, 자소서 문항 리스트, 자소서 답변 리스트)

        Returns: 적절하지 않은 것은 공백 처리된 초기 입력 정보

        """
        # todo mvp 이후 추가할 메서드임. 현재는 모든 입력 정보를 그대로 반환함.

        # 직군 필터.

        # 공고 필터.

        # 자소서 문항 필터. 개수만큼 반복

        # 자소서 답변 필터. 개수만큼 반복

        return initial_input_data

    def __analyze_initial_inputs_of_interviewee(self, initial_input_data: IntervieweeInitialInputData) -> List[str]:
        """
        (자소서 문항,자소서 답변) 전체 쌍에 대해 LLM을 이용하여 분석하는 메서드
        해당 쌍을 4개 입력 받았다면, 4개의 쌍에 대해 분석을 수행한다.
        cover_letter_questions 와 cover_letter_answers 의 길이는 같아야 한다.
        그리고 인덱스를 i라 할 때, (cover_letter_questions[i], cover_letter_answers[i]) 쌍이다.

        Args:
            initial_input_data: 면접 지원자의 초기 입력 정보(직군,모집공고, 자소서 문항 리스트, 자소서 답변 리스트)

        Returns: 입력 파라미터에 대한 분석 결과 문자열 리스트 (올바르지 않은 입력은 공백으로 치환)

        """
        if len(initial_input_data.cover_letter_questions) != len(initial_input_data.cover_letter_answers):
            raise ValueError("자소서 문항과 자소서 답변의 개수가 일치하지 않습니다.")

        analysis_count = len(initial_input_data.cover_letter_questions)

        analysis_list = []
        # 자소서 개수만큼 분석 시작.
        for i in range(analysis_count):
            analysis_about_one_cover_letter = self.initial_input_analyzer.analyze_initial_input(
                job_group=initial_input_data.job_group,
                recruitment_announcement=initial_input_data.recruit_announcement,
                cover_letter_question=initial_input_data.cover_letter_questions[i],
                cover_letter_answer=initial_input_data.cover_letter_answers[i])

            analysis_list.append(analysis_about_one_cover_letter)

        return analysis_list
