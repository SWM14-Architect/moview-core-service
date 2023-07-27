from typing import List, Tuple


class IntervieweeInitialInputData:
    def __init__(self, jop_group: str, recruit_announcement: str, cover_letter_questions: List[str],
                 cover_letter_answers: List[str]):
        self.job_group = jop_group
        self.recruit_announcement = recruit_announcement
        self.cover_letter_questions = cover_letter_questions
        self.cover_letter_answers = cover_letter_answers


class IntervieweeDataVO:
    def __init__(self, session_id, initial_question_list: List[str], initial_interview_analysis: List[str],
                 initial_input_data: IntervieweeInitialInputData):
        # 인터뷰 세션 id
        self.id = session_id

        # 초기 입력 데이터 객체 (직군,공고, 자소서 문항 리스트, 자소서 답변 리스트)
        self.initial_input_data = initial_input_data

        # 인터뷰 초기 질문과 꼬리질문을 담당하는 객체
        self.interview_questions = self.InterviewQuestions(initial_question_list)

        # 각 자소서 문항에 대해 분석한 결과를 담고 있는 객체
        self.interview_analysis = self.InitialInterviewAnalysis(initial_interview_analysis)

        # 답변에 대한 (대분류+중분류, 평가 점수) 순서쌍을 관리하는 객체
        self.answer_score_with_category = self.AnswerScoresWithCategory()

    # 다음 초기 질문 출제
    def give_next_initial_question(self):
        self.interview_questions.give_next_initial_question()

    # 꼬리질문 저장
    def save_followup_question(self, followup_question: str):
        self.interview_questions.save_followup_question(followup_question=followup_question)

    def is_initial_questions_end(self) -> bool:
        return self.interview_questions.is_initial_questions_end()

    def is_followup_questions_end(self) -> bool:
        return self.interview_questions.is_followup_questions_end()

    def save_categories_ordered_pair(self, question: str, answer: str, categories_ordered_pair: str):
        self.answer_score_with_category.add_categories_ordered_pair(question=question, answer=answer,
                                                                    categories_ordered_pair=categories_ordered_pair)

    def save_score_of_interviewee(self, score_of_answer: str):
        """

        Args:
            score_of_answer: # - 기준 : 점수 # 의 여러개의 문자열이 합쳐져있음.

        Returns:

        """
        self.answer_score_with_category.add_score_of_interviewee(score_of_answer=score_of_answer)

    class InitialInterviewAnalysis:
        """
        자소서 문항 [i]에 대해 초기 분석 initial_interview_analysis[i]가 매핑됩니다.
        """

        def __init__(self, initial_interview_analysis: List[str]):
            self.initial_interview_analysis = initial_interview_analysis

    class InterviewQuestions:
        """
        인터뷰 초기 질문과 꼬리질문을 관리하는 클래스입니다.
        """

        def __init__(self, initial_question_list: List[str]):
            # 꼬리질문 최대 횟수
            self.MAX_FOLLOWUP_QUESTION_COUNT = 3

            # 초기 질문 리스트
            self.initial_question_list = initial_question_list

            # 꼬리질문 출제에서 제외할 질문들 (초기 질문은 꼬리질문 출제에서 제외합니다.)
            self.excluded_questions_for_giving_followup_question = self.__exclude_initial_question(
                initial_question_list=initial_question_list)

            # 초기 질문 인덱스 i
            self.initial_question_index = 0

            # i 번째 초기 질문에서 출제한 꼬리질문 횟수
            self.followup_question_count = 0

        def __exclude_initial_question(self, initial_question_list: List[str]):
            excluded_questions = []
            for question in initial_question_list:
                excluded_questions.append(question)
            return excluded_questions

        def give_next_initial_question(self):
            self.initial_question_index += 1

            # 꼬리질문 초기화
            self.followup_question_count = 0

        # 꼬리질문 저장
        def save_followup_question(self, followup_question: str):
            self.followup_question_count += 1
            self.excluded_questions_for_giving_followup_question.append(followup_question)

        def is_initial_questions_end(self) -> bool:
            return self.initial_question_index == len(self.initial_question_list) - 1

        def is_followup_questions_end(self) -> bool:
            return self.followup_question_count == self.MAX_FOLLOWUP_QUESTION_COUNT

    class AnswerScoresWithCategory:

        def __init__(self):
            """
                1.답변에 대한 대분류, 중분류 저장
                2.답변에 대한 평가 점수 저장
            """
            self.categories_ordered_pair_list = []  # (질문, 답변, 대분류+중분류) 순서쌍 리스트
            self.scores_about_answer = []  # i 번째 요소는 categories_ordered_pair_list[i]에 대한 평가 기준과 점수 문자열이 들어가 있다.

        def add_categories_ordered_pair(self, question: str, answer: str, categories_ordered_pair: str):
            self.categories_ordered_pair_list.append((question, answer, categories_ordered_pair))

        def add_score_of_interviewee(self, score_of_answer: str):
            self.scores_about_answer.append(score_of_answer)
