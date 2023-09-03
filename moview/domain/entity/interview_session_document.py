from typing import Dict, Optional, List
from pydantic import BaseModel
from datetime import datetime


class InterviewSession(BaseModel):
    """
    한 유저가 진행하는 인터뷰 세션을 나타내는 엔티티.
    """
    user_id: str
    initial_input_data_id: Dict[str, Optional[str]] = None
    previous_question: List  # 꼬리 질문에서 출제되었던 질문들을 제외하기 위함. todo 초기 질문은 input api 할 때 처리해야 함.
    question_id_list: List[Dict[str, Optional[str]]] = []  # 마이 페이지 구현 시, 한꺼번에 조회하기 위해 만든 id 리스트
    created_at: str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
