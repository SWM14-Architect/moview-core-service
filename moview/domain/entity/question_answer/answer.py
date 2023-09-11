from typing import Any, Optional, Dict, List
from pydantic import BaseModel
from datetime import datetime


class Answer(BaseModel):
    content: Any
    category: str
    sub_category: str
    filter_result: str = None  # Answer Filter 결괏값 저장됨
    evaluation: List[str] = None  # 평가 모듈을 통해서 얻은 결과
    question_id: Dict[str, Optional[str]] = None
    created_at: str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
