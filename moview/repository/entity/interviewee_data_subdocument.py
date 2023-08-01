from typing import List, Any
from pydantic import BaseModel


class IntervieweeInitialInputData(BaseModel):
    """
    인터뷰 세션을 생성할 때 입력받는 데이터를 저장하는 클래스입니다.
    cover_letter_questions[i]에 대한 답변은 cover_letter_answers[i]에 저장됩니다.
    """
    interviewee_name: str = ""
    job_group: str = ""
    recruit_announcement: str = ""
    cover_letter_questions: List[str] = []
    cover_letter_answers: List[str] = []


class InputDataAnalysisResult(BaseModel):
    """
    인터뷰 세션을 생성할 때 입력받은 자소서 문항에 대한 분석 결과를 저장하는 클래스입니다.
    cover_letter_questions [i]에 대해 초기 분석 initial_interview_analysis[i]가 매핑됩니다.
    """
    input_data_analysis_list: List[str] = []


class InterviewQuestions(BaseModel):
    """
    인터뷰 초기 질문과 꼬리질문을 관리하는 클래스입니다.
    """
    initial_question_list: List = []  # 초기 질문 리스트
    followup_question_list = []  # 꼬리 질문 리스트
    initial_question_index: int = 0  # 초기 질문 인덱스 i
    followup_question_count: int = 0  # i 번째 초기 질문에서 출제한 꼬리질문 횟수
    MAX_FOLLOWUP_QUESTION_COUNT: int = 3  # 꼬리질문 최대 횟수

    def get_next_initial_question(self):
        if self.initial_question_index >= len(self.initial_question_list):
            raise ValueError("초기 질문을 모두 사용하였습니다.")

        self.initial_question_index += 1

        # 꼬리질문 초기화
        self.followup_question_count = 0

    def save_followup_question(self, followup_question: str):
        self.followup_question_count += 1
        self.followup_question_list.append(followup_question)

    def is_initial_questions_end(self) -> bool:
        return self.initial_question_index == len(self.initial_question_list) - 1

    def is_followup_questions_end(self) -> bool:
        return self.followup_question_count == self.MAX_FOLLOWUP_QUESTION_COUNT


class IntervieweeAnswerScores(BaseModel):
    """
    면접 지원자의 질문,
    면접 지원자의 답변 ,
    면접 지원자의 답변에 대한 대분류+중분류 문자열, (Ex: I think it is 대분류, especially 중분류)
    면접 지원자 답변에 대한 점수.

    question_list[i]에 대한 답변은 answer_list[i]에 저장됩니다.
    category_and_sub_category_list[i]에는 answer_list[i]에 대한 대분류+중분류 문자열이 저장됩니다.
    그리고 answer_list[i]에 대한 점수는 score_of_answer_list[i]에 저장됩니다.
    """
    question_list: List[str] = []
    answer_list: List[str] = []
    category_and_sub_category_list: List[str] = []
    score_of_answer_list: List[str] = []


class IntervieweeFeedbacks(BaseModel):
    """
    면접 지원자의 인터뷰 피드백을 저장하는 클래스입니다.
    answer_list[i]에 대한 피드백은 feedback_list[i]에 저장됩니다.
    """
    feedback_list: List[str] = []
