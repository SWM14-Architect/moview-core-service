from typing import Dict, Optional, List
from pydantic import BaseModel
from datetime import datetime


class InitialInputData(BaseModel):
    interviewee_name: str
    company_name: str
    job_group: str
    recruit_announcement: str
    coverletter_id_list: List[Dict[str, Optional[str]]] = []
    created_at: str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
