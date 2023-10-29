from typing import Any, Optional, Dict, List
from pydantic import BaseModel, Field
from datetime import datetime


class Answer(BaseModel):
    content: Any
    evaluation: List[str] = None  # 평가 모듈을 통해서 얻은 결과
    question_id: Dict[str, Optional[str]] = None
    created_at: str = Field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
