# API 명세서
| API                    | Method | Request              | Response               | Description   | GPT |
|------------------------|--------|----------------------|------------------------|---------------|-----|
| /api/user              | POST   | json(회사,직업,모집공고,자소서) | None                   | 사용자 정보 입력     | X   |
| /api/user/evaluation   | GET    | None                 | json(평가)               | 사용자 정보 평가     | O   |
| /api/question          | GET    | None                 | json(질문리스트)            | 초기 질문리스트 생성   | O   |
| /api/question/followup | POST   | json(질문,답변,평가)       | json(Union[심화질문,None]) | 심화 질문 생성 및 요청 | O   |
| /api/answer/evaluation | POST   | json(질문,답변)          | json(평가)               | 답변 평가         | O   |