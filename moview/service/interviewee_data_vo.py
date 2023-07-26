from typing import List


class IntervieweeInitialInputData:
    def __init__(self, jop_group: str, recruit_announcement: str, cover_letter_questions: List[str],
                 cover_letter_answers: List[str]):
        self.job_group = jop_group
        self.recruit_announcement = recruit_announcement
        self.cover_letter_questions = cover_letter_questions
        self.cover_letter_answers = cover_letter_answers


class IntervieweeDataVO:
    """
    갖고 있는 데이터
    1. 인터뷰 세션 id
    2. 초기 입력 데이터 (직군,공고, 자소서 문항 리스트, 자소서 답변 리스트)
    3. 초기 질문 리스트
    4. 이전 질문 리스트
    5. 분석 내용 리스트
    6. 초기 질문 인덱스
    7. 꼬리질문 인덱스
    8. 꼬리질문 최대 횟수
    9. 답변에 대한 대분류, 중분류 저장
    10. 답변에 대한 평가 점수 저장
    """

    def __init__(self, session_id, initial_question_list: List[str], initial_interview_analysis: List[str],
                 initial_input_data: IntervieweeInitialInputData):
        self.id = session_id  # flask session id

        self.initial_input_data = initial_input_data

        self.initial_question_list = initial_question_list
        self.exclude_question_list = []

        for question in initial_question_list:
            self.exclude_question_list.append(question)

        self.interview_analysis = initial_interview_analysis

        self.initial_question_index = 0
        self.followup_question_count = 0
        self.MAX_FOLLOWUP_QUESTION_COUNT = 3

        self.categories_ordered_pair_list = []  # (질문, 답변, 대분류+중분류) 순서쌍 리스트
        self.scores_about_answer = []

    # 다음 초기 질문 출제
    def give_next_initial_question(self):
        self.initial_question_index += 1

        # 꼬리질문 초기화
        self.followup_question_count = 0

    # 꼬리질문 저장
    def save_followup_question(self, followup_question: str):
        self.followup_question_count += 1
        self.exclude_question_list.append(followup_question)

    def is_initial_questions_end(self) -> bool:
        return self.initial_question_index == len(self.initial_question_list) - 1

    def is_followup_questions_end(self) -> bool:
        return self.followup_question_count == self.MAX_FOLLOWUP_QUESTION_COUNT

    def save_categories_ordered_pair(self, question: str, answer: str, categories_ordered_pair: str):
        self.categories_ordered_pair_list.append((question, answer, categories_ordered_pair))

    # 평가 내용 저장
    def save_score_of_interviewee(self, score_from_llm):
        self.scores_about_answer.append(score_from_llm)
