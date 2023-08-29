from pydantic import BaseModel


class CoverLetter(BaseModel):
    coverletter_question: str
    coverletter_answer: str
    coverletter_analysis_result: str
