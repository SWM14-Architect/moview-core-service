from typing import Any, Optional, Dict
from pydantic import BaseModel, Field
from datetime import datetime


class Question(BaseModel):
    content: Any
    feedback_score: int
    prev_question_id: Dict[str, Optional[str]] = None  # 초기 질문인 경우 question_id = None, 꼬리 질문인 경우 이전 question을 가리킴.
    created_at: str = Field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
