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

### API 명세서

***

#### /interview/input

```
Method        : POST
Request       : json(이름, 회사, 직군, 모집공고, 자소서 문항, 자소서 답변)
Response      : json(초기 질문 리스트, 인터뷰 아이디)
Description   : 초기 질문 받아오는 API
```

Request JSON

```json
{
  "interviewee_name": "홍길동",
  "company_name": "지원 회사 이름",
  "job_group": "지원 직군",
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

Response JSON

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
      ...
    ],
    "interview_id": "인터뷰 id"
  }
}
```

***

#### /interview/light

```
Method        : POST
Request       : json(이름, 회사, 직군, 직무면접 키워드)
Response      : json(초기 질문 리스트, 인터뷰 아이디)
Description   : 초기 질문 받아오는 API (light mode)
```

Request JSON

```json
{
    "interviewee_name":"홍길동",
    "company_name":"지원 회사 이름",
    "job_group":"지원 직군",
    "keyword":"면접 키워드, ..."
}

```

Response JSON

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
      ...
    ],
    "interview_id": "인터뷰 id"
  }
}
```

***

#### /interview/answer

```
Method        : POST
Request       : json(인터뷰 id, 질문 id, 질문 내용, 사용자 답변)
Response      : json(꼬리 질문, 출제 질문 id)
Description   : 꼬리질문을 생성하는 API
```

Request JSON

```json
{
  "interview_id": "인터뷰 id",
  "question_id": "최근에 출제했던 질문 id",
  "question_content": "최근에 출제했던 질문 내용",
  "answer_content": "사용자 답변"
}
```

Response JSON

```json
{
  "message": {
    "question_content": "꼬리질문 내용 (Nullable)",
    "question_id": "꼬리 질문 id (Nullable)"
  }
}
```

***

#### /interview/evaluation

```
Method        : POST
Request       : json(인터뷰 id)
Response      : json(질문 id, 질문 내용, 답변 내용, 평가 내용)
Description   : 사용자가 답변했던 내용에 대한 평가를 생성하고 반환하는 API
```

Request JSON
```json
{
  "interview_id": "인터뷰 id"
}
```

Response JSON
```json
{
  "message": {
    "evaluations": [
      {
          "question_id": "질문 id",
          "question": "질문 내용",
          "answer": "답변 내용",
          "evaluation": "평가 내용"
      },
      ...
    ]
  }
}
```

***

#### /interview/tts

```
Method        : POST
Request       : json(인터뷰 id, 내용)
Response      : json(TTS 음성 내용 - base64)
Description   : Text를 음성파일로 변환하는 API
```

Request JSON
```json
{
  "interview_id": "인터뷰 id",
  "text": "TTS로 변환할 내용"
}
```

Response JSON
```json
{
  "message": {
    "audio_data": "TTS 음성 내용 - base64"
  }
}
```

***

#### /interview/stt

```
Method        : POST
Request       : json(인터뷰 id, 오디오 데이터)
Response      : json(음성을 텍스트로 변환한 내용)
Description   : 음성파일을 Text로 변환하는 API
```

Request JSON
```json
{
  "interview_id": "인터뷰 id",
  "audio_data": "음성을 텍스트로 변환한 내용"
}
```

Response JSON
```json
{
  "message": {
    "text": "음성을 텍스트로 변환한 내용"
  }
}
```

***

#### /slack/feedback

```
Method        : POST
Request       : json(이름, 피드백 내용, 생성 시간)
Response      : json(성공적으로 전달했음을 알리는 메시지)
Description   : 사용자의 피드백 내용을 개발자 Slack의 Feedback 채널로 보내주는 API
```

Request JSON
```json
{
  "profile_nickname": "홍길동",
  "user_message": "피드백 내용",
  "created_at": "생성 시간"
}
```

Response JSON
```json
{
  "message": "OK"
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
