from typing import List


class InputService:
    def __init__(self):
        pass

    def ask_initial_question_to_interviewee(self, job_group: str, recruit_announcement: str,
                                            cover_letter_questions: List[str],
                                            cover_letter_answers: List[str], initial_question_count: int) -> List[str]:
        """

        Args:
            job_group: 직군
            recruit_announcement: 모집 공고
            cover_letter_questions: 자소서 문항 리스트
            cover_letter_answers: 자소서 답변 리스트
            initial_question_count: 초기 질문 횟수

        Returns: 출제된 초기 질문 리스트 (길이는 initial_question_count)

        """

        # 3. 사용자 입력 정보 분석 (직군, 공고, 자소서 문항, 자소서 답변)
        initial_analysis_about_interviewee = self.__analyze_initial_inputs_of_interviewee(job_group=job_group,
                                                                                          recruit_announcement=recruit_announcement,
                                                                                          cover_letter_questions=cover_letter_questions,
                                                                                          cover_letter_answers=cover_letter_answers)

        # 세션 저옵에 맞게 분석한 내용 저장.
        self.__save_initial_analysis_about_interviewee(
            initial_analysis_about_interviewee=initial_analysis_about_interviewee)

        # 7. 초기 질문 생성 요청 (n회)
        initial_questions = []
        for i in range(initial_question_count):
            initial_question = self.__create_initial_question(
                initial_analysis_about_interviewee=initial_analysis_about_interviewee)
            initial_questions.append(initial_question)  # 초기 질문 리스트에 추가

        # 11. 세션 정보에 맞게 생성된 초기질문 저장 및 id 부여
        self.__save_initial_questions_and_allocate_id(initial_questions=initial_questions)

        return initial_questions

    def __analyze_initial_inputs_of_interviewee(self, job_group: str, recruit_announcement: str,
                                                cover_letter_questions: List[str],
                                                cover_letter_answers: List[str]) -> str:
        """
        (자소서 문항,자소서 답변) 전체 쌍에 대해 LLM을 이용하여 분석하는 메서드
        해당 쌍을 4개 컨트롤러에서 입력 받았다면, 4개의 쌍에 대해 분석을 수행한다.
        cover_letter_questions 와 cover_letter_answers 의 길이는 같아야 한다.
        그리고 인덱스를 i라 할 때, (cover_letter_questions[i], cover_letter_answers[i]) 쌍이다.

        Args:
            job_group: 직군
            recruit_announcement: 모집 공고
            cover_letter_questions: 자소서 문항 리스트
            cover_letter_answers: 자소서 답변 리스트


        Returns: 입력 파라미터에 대한 분석 결과 문자열

        """
        pass

    def __save_initial_analysis_about_interviewee(self, initial_analysis_about_interviewee) -> None:
        """

        자소서 분석 내용 db에 저장

        Args:
            initial_analysis_about_interviewee: 면접 지원자 초기 입력에 대한 분석 내용

        Returns:

        """
        pass

    def __create_initial_question(self, initial_analysis_about_interviewee: str) -> str:
        """

        Args:
            initial_analysis_about_interviewee: 면접 지원자 초기 입력에 대한 분석 내용

        Returns: 면접 지원자에게 출제할 초기 질문 1개

        """
        pass

    def __save_initial_questions_and_allocate_id(self, initial_questions: List[str]) -> None:
        """

        생성된 초기 질문을 db에 저장하고, id를 부여하는 메서드

        Args:
            initial_questions: 면접 지원자에게 출제할 초기 질문 리스트

        Returns: 없음

        """
        pass
