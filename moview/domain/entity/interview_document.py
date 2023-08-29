from typing import Dict, Optional
from pydantic import BaseModel


class Interview(BaseModel):
    session_id: str
    inital_input_data_id: Dict[str, Optional[str]] = None
    initial_question_id: Dict[str, Optional[str]] = None
