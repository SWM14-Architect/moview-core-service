from typing import Any, Optional, Dict
from pydantic import BaseModel
from datetime import datetime


class Question(BaseModel):
    content: Any
    feedback_score: int
    interview_id: Dict[str, Optional[str]] = None
    question_id: Dict[str, Optional[str]] = None  # 초기 질문인 경우 question_id = None, 꼬리 질문인 경우 이전 question을 가리킴.
    created_at: str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
