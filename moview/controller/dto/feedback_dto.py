from pydantic import BaseModel


class FeedbackDTO(BaseModel):
    question_id: str  # 질문 엔티티의 ObjectId
    feedback_score: int  # 피드백 점수
