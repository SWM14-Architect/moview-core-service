from enum import Enum


# Enum 정의
class InterviewActionEnum(Enum):
    CREATED_FOLLOWUP_QUESTION = 1
    DIRECT_REQUEST = 2
    INAPPROPRIATE_ANSWER = 3
    END_INTERVIEW = 4
    NEXT_INITIAL_QUESTION = 5
