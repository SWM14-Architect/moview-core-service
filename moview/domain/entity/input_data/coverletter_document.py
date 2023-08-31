from pydantic import BaseModel
from datetime import datetime


class CoverLetter(BaseModel):
    coverletter_question: str
    coverletter_answer: str
    coverletter_analysis_result: str
    created_at: str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')