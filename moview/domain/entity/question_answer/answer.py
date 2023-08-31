from typing import Any, Optional, Dict
from pydantic import BaseModel


class Answer(BaseModel):
    content: Any
    category: str
    sub_category: str
    evaluation: str  # 평가 모듈을 통해서 얻은 결과
    question_id: Dict[str, Optional[str]] = None
    created_at: str
