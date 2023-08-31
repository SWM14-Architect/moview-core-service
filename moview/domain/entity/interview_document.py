from typing import Dict, Optional
from pydantic import BaseModel
from datetime import datetime


class Interview(BaseModel):
    session_id: str
    initial_input_data_id: Dict[str, Optional[str]] = None
    question_id: Dict[str, Optional[str]] = None
    created_at: str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
