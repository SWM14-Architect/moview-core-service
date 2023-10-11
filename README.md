# Moview Core Serivce

## MVP v2 기준

### 기술 스택
<div>
  <img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white"> 
  <img src="https://img.shields.io/badge/flask-000000?style=for-the-badge&logo=flask&logoColor=white">
  <img src="https://img.shields.io/badge/mongoDB-47A248?style=for-the-badge&logo=MongoDB&logoColor=white">
  <img src="https://img.shields.io/badge/Langchain-412991?style=for-the-badge&logo=OpenAI&logoColor=white">
  <img src="https://img.shields.io/badge/GitHub Actions-2088FF?style=for-the-badge&logo=GitHubActions&logoColor=white">
  <img src="https://img.shields.io/badge/amazon aws-232F3E?style=for-the-badge&logo=amazonaws&logoColor=white">
</div>

***

### API 명세서 (인증 / 인가 관련 명세서는 미포함)

***

#### /interview/input

```
method : POST
request: json(면접자 이름, 회사, 직군, 모집공고, 자소서 문항, 자소서 답변)
response: json(초기 질문 n개에 대한 데이터{"objectId":id, ""}, 인터뷰 아이디)
description: 초기 질문 받아오는 API
GPT call: O
```

request json

```json
{
  "interviewee_name": "아무개",
  "company_name": "아무개 회사",
  "recruit_announcement": "모집 공고",
  "cover_letter_questions": [
    "자소서 문항 1",
    "자소서 문항 2"
  ],
  "cover_letter_answers": [
    "자소서 답변 1",
    "자소서 답변 2"
  ]
}

```

response json

```json
{
  "message": {
    "initial_questions": [
      {
        "question_id": "초기 질문 id",
        "content": "GPT 결과"
      },
      {
        "question_id": "초기 질문 id",
        "content": "GPT 결과"
      },
      {
        "question_id": "초기 질문 id",
        "content": "GPT 결과"
      }
    ],
    "interview_id": "인터뷰 id"
  }
}
```

***

#### /interview/light

```
method : POST
request: json(면접자 이름, 회사, 직군, 직무면접 키워드)
response: json(초기 질문 n개에 대한 데이터{"objectId":id, ""}, 인터뷰 아이디)
description: 초기 질문 받아오는 API (light mode)
GPT call: O
```

request json

```json
{
    "interviewee_name":"tester",
    "company_name":"Facebook",
    "job_group":"Backend",
    "keyword":"아파치 카프카"
}

```

response json

```json
{
  "message": {
    "light_questions": [
      {
        "question_id": "초기 질문 id",
        "content": "GPT 결과"
      },
      {
        "question_id": "초기 질문 id",
        "content": "GPT 결과"
      },
      {
        "question_id": "초기 질문 id",
        "content": "GPT 결과"
      }
    ],
    "interview_id": "인터뷰 id"
  }
}
```

***

#### /interview/answer

```
method : POST
request:cookie(세션id),json(인터뷰 id, 질문 id, 질문 내용, 사용자 답변)
response: json(출제할 질문, 출제 질문 id) 
description: 
GPT call: O (동기 처리)
```

request json

```json
{
  "user_id": "session_id일수도 있음 ",
  "interview_id": "interview_id",
  "question_id": "최근에 출제했던 질문 id",
  "question_content": "최근에 출제했던 질문 내용",
  "answer_content": "사용자 답변"
}
```

response json

```json
{
  "question_content": "꼬리질문 내용 (Nullable)",
  "question_id": "꼬리 질문 id (Nullable)"
}
```

***

#### /interview/evaluation

```
method : POST
request: cookie(세션id), json(user_id, interview_id)
response: json(질문 내용, 답변 내용, 평가 내용)
description: 사용자가 답변했던 내용에 대한 평가 내역을 불러오는 api
GPT call: O
```

response json
```json
{
  "evaluations": [
    {
      "question_id": "질문 id. Question 엔티티의 _id.",
      "question": "질문 내용. Question 엔티티 content 칼럼.",
      "answer": "답변 내용. Answer 엔티티 content 칼럼.",
      "evaluation": "평가 내용. Answer 엔티티 칼럼."
    },
    {
      "question_id": "질문 id. Question 엔티티의 _id.",
      "question": "질문 내용. Question 엔티티 content 칼럼.",
      "answer": "답변 내용. Answer 엔티티 content 칼럼.",
      "evaluation": "평가 내용. Answer 엔티티 칼럼."
    }
  ]
}
```

***

#### /interview/feedback

```
method : POST
request: cookie(세션id), json(각 답변분석에 대한 유저의 평가)
response: X
description: 유저의 서비스평가를 받고, 종료 
GPT call: X (동기 처리)
```

request json

```json
{
  "user_id": "session_id일수도 있음 ",
  "interview_id": "interview_id",
  "question_ids": [
    "질문 id 1",
    "질문 id 2"
  ],
  "feedback_scores": [
    "질문 id 1에 대한 피드백 점수",
    "질문 id 2에 대한 피드백 점수"
  ]
}
```

***

### 테스트 커버리지 (v2 기준)

moview 디렉토리 기준 file coverage 67%, line coverage 92%
***

### 디렉토리 트리

moview 디렉토리에서 'tree -I '__pycache__|*.pyc|__init__.py'' 명령어를 실행한 결과 (homebrew에서 tree 설치해야 함.)

```
.
├── config
│   ├── container
│   │   └── container_config.py
│   ├── db
│   │   ├── mongo_config.py
│   │   └── mongo_handler.py
│   ├── jwt
│   │   └── jwt_config.py
│   ├── loggers
│   │   └── mongo_logger.py
│   └── oauth
│       └── oauth_config.py
├── controller
│   ├── answer_controller.py
│   ├── evaluation_controller.py
│   ├── feedback_controller.py
│   ├── input_data_controller.py
│   ├── light_mode_controller.py
│   └── oauth
│       ├── oauth_controller.py
│       └── oauth_controller_helper.py
├── domain
│   └── entity
│       ├── input_data
│       │   ├── coverletter_document.py
│       │   └── initial_input_data_document.py
│       ├── interview_document.py
│       ├── question_answer
│       │   ├── answer.py
│       │   └── question.py
│       └── user
│           └── user.py
├── environment
│   ├── environment_loader.py
│   └── llm_factory.py
├── exception
│   ├── evaluation_parse_error.py
│   ├── initial_question_parse_error.py
│   ├── light_question_parse_error.py
│   └── retry_execution_error.py
├── modules
│   ├── answer_evaluator
│   │   └── answer_evaluator.py
│   ├── input
│   │   ├── initial_question_giver.py
│   │   └── input_analyzer.py
│   ├── light
│   │   └── light_question_giver.py
│   └── question_generator
│       └── followup_question_giver.py
├── repository
│   ├── input_data
│   │   └── input_data_repository.py
│   ├── interview_repository.py
│   ├── question_answer
│   │   └── question_answer_repository.py
│   └── user
│       └── user_repository.py
├── service
│   ├── answer_service.py
│   ├── evaluation_service.py
│   ├── feedback_service.py
│   ├── input_data_service.py
│   ├── interview_service.py
│   ├── light_mode_service.py
│   └── user_service.py
└── utils
    ├── async_controller.py
    ├── prompt_loader
    │   ├── json
    │   │   ├── AnswerAnalyzer.json
    │   │   ├── AnswerCategoryClassifier.json
    │   │   ├── AnswerEvaluator.json
    │   │   ├── AnswerScorer.json
    │   │   ├── AnswerSubCategoryClassifier.json
    │   │   ├── AnswerValidator.json
    │   │   ├── FollowUpQuestionGiver.json
    │   │   ├── InitialQuestionGiver.json
    │   │   ├── InputAnalyzer.json
    │   │   ├── LightQuestionGiver.json
    │   │   └── helpme.md
    │   └── prompt_loader.py
    ├── prompt_parser.py
    ├── retry_decorator.py
    └── singleton_meta_class.py
```

***
