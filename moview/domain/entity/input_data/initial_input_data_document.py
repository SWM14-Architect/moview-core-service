from typing import Dict, Optional, List
from pydantic import BaseModel
from datetime import datetime


class InitialInputData(BaseModel):
    interviewee_name: str
    company_name: str
    job_group: str
    keyword: Optional[str]
    recruit_announcement: Optional[str]  # light mode 인 경우 None
    coverletter_id_list: List[Dict[str, Optional[str]]] = []
    created_at: str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
