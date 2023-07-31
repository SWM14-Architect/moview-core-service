from typing import List
from pydantic import BaseModel
from moview.repository.entity.interviewee_data_subdocument import IntervieweeInitialInputData, InitialInterviewAnalysis, \
    InterviewQuestions, IntervieweeAnswerScore

"""
IntervieweeDataEntity 클래스를 정의할 때 Pydantic의 BaseModel을 사용하였습니다.
Pydantic은 데이터 유효성 검사를 제공하는 Python 라이브러리이며, 편리하게 모델 클래스를 생성하는 데 사용됩니다.
Pydantic 모델은 데이터 유효성 검사, JSON (de)serialization 등을 지원합니다.
"""

"""
이 클래스에 명시적인 생성자(__init__ 메서드)가 정의되어 있지 않은 이유는 Pydantic의 BaseModel이 제공하는 기능을 이용하기 위해서입니다. 
Pydantic의 BaseModel 클래스는 클래스를 정의할 때 선언한 필드에 대한 타입 검사, 필드의 기본값 설정, JSON 직렬화 및 역직렬화 등의 기능을 자동으로 제공합니다.
"""

"""
임베딩 방식: 이 방식에서는 IntervieweeDataEntity를 메인 도큐먼트로 설정하고,
 그 안에 IntervieweeInitialInputData, InitialInterviewAnalysis, InterviewQuestions, IntervieweeAnswerScore를
서브 도큐먼트로 둡니다. 이렇게 하면 모든 데이터는 하나의 도큐먼트에 저장되며, 동일한 session_id를 쉽게 공유할 수 있습니다.
"""


class IntervieweeDataEntity(BaseModel):
    """
    메인 다큐먼트
    """
    session_id: str  # 인터뷰 세션 id
    initial_input_data: IntervieweeInitialInputData
    initial_interview_analysis: InitialInterviewAnalysis
    interview_questions: InterviewQuestions
    interviewee_answer_score_list: List[IntervieweeAnswerScore]

    def give_next_initial_question(self):
        self.interview_questions.get_next_initial_question()

    def save_followup_question(self, followup_question: str):
        self.interview_questions.save_followup_question(followup_question)

    def is_initial_questions_end(self) -> bool:
        return self.interview_questions.is_initial_questions_end()

    def is_followup_questions_end(self) -> bool:
        return self.interview_questions.is_followup_questions_end()
