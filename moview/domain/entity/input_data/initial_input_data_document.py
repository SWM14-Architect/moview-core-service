from typing import Dict, Optional, List

from pydantic import BaseModel


class InitialInputData(BaseModel):
    interviewee_name: str
    company_name: str
    job_group: str
    recruit_announcement: str
    interview_id_list: List[Dict[str, Optional[str]]] = []
