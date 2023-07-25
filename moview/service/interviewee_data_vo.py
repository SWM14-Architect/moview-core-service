from flask import session


class IntervieweeDataVO:
    """
    갖고 있는 데이터
    1. 인터뷰 세션 id
    2. 초기 질문 리스트
    3. 이전 질문 리스트
    4. 분석 내용
    5. 초기 질문 인덱스
    6. 꼬리질문 횟수
    7. 답변에 대한 평가 저장
    8. 꼬리질문 최대 횟수
    9. 인터뷰 종료 여부
    """

    def __init__(self, session: session, initial_question_list: list[str], initial_interview_analysis: str):
        self.id = session['id']
        self.initial_question_list = initial_question_list
        self.previous_question_list = []
        self.interview_analysis = initial_interview_analysis
        self.initial_question_index = 0
        self.followup_question_count = 0
        self.scores_about_answer = []
        self.MAX_FOLLOWUP_QUESTION_COUNT = 3
        self.is_end = False

    # 다음 초기 질문 출제
    def give_next_initial_question(self):
        pass



