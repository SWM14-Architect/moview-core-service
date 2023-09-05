# Moview Core Serivce

## MVP v2 기준

### API 명세서

#### /interview/session

```
method : POST
request: X
response: cookie(세션id)
description: 플라스크 세션 발급용 API.
GPT call: X
```

***

#### /api/interview/input

```
method : POST
request: json(면접자 이름, 회사, 직군, 모집공고, 자소서 문항, 자소서 답변)
response: json(초기 질문 n개에 대한 데이터, 인터뷰 아이디)
description: 초기 질문 받아오는 API 
GPT call: O
```

request json

```json
{
  "interviewee_name": "아무개",
  "company": {
    "name": "아무개 회사",
    "industry": "IT"
  },
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
```

***

#### /api/interview/answer

```
method : POST
request:cookie(세션id),json(초기 질문 인덱스, 꼬리질문 인덱스, 현재 질문 Q, 면접자 답변 A)
response: json(출제할 질문,인터뷰 플래그) 
description: 
GPT call: O
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

#### api/interview/evaluation

```
method : POST
request: cookie(세션id)
response: answer api에서 미리 처리해놓고 있던 평가 n개 
description: 사용자가 답변했던 내용에 대한 평가 내역을 불러오는 api
GPT call: X (answer api에서 미리 비동기 작업했다고 가정하므로 없다.)
```

response json

아래 json은 Answer 엔티티에서 불러오는 것이다. 특히, question_id는 Answer 엔티티의 외래키인 question_id를 뜻한다!
프론트엔드에서는 question_id와 묶어서 evaluation을 저장하는게?

```json
{
  "evaluations": [
    {
      "evaluation": "평가 내용. Answer 엔티티 칼럼임.",
      "question_id": "질문 id. Answer 엔티티 외래키."
    },
    {
      "evaluation": "평가 내용. Answer 엔티티 칼럼임.",
      "question_id": "질문 id. Answer 엔티티 외래키."
    }
  ]
}
```

***

#### /api/interview/feedback

```
method : POST
request: cookie(세션id), json(각 답변분석에 대한 유저의 평가)
response: X
description: 유저의 서비스평가를 받고, 종료 
GPT call: X
```

request json

```json
{
  "user_id": "session_id일수도 있음 ",
  "interview_id": "interview_id",
  "questions": [
    {
      "question_id": "질문 id",
      "feedback_score": "피드백 점수"
    },
    {
      "question_id": "질문 id",
      "feedback_score": "피드백 점수"
    }
  ]
}
```

***

### 테스트 커버리지

moview 디렉토리 기준 라인 커버리지 88% (v1 기준)
***

### 디렉토리 트리

moview 디렉토리에서 'tree' 명령어를 실행한 결과 (homebrew에서 tree 설치해야 함.)

```
.
├── __init__.py
├── config
│   ├── __init__.py
│   ├── db
│   │   ├── __init__.py
│   │   ├── mongo_config.py
│   │   └── mongo_handler.py
│   ├── llm
│   │   ├── __init__.py
│   │   └── custom_callback_handler.py
│   └── loggers
│       ├── __init__.py
│       └── mongo_logger.py
├── controller
│   ├── __init__.py 
├── domain
│   ├── __init__.py
│   └── entity
│       ├── __init__.py
│       ├── interview_session_document.py
│       └── question_answer
│           ├── __init__.py
│           ├── answer.py
│           └── question.py
├── environment
│   ├── __init__.py
│   ├── environment_loader.py
│   └── llm_factory.py
├── modules
│   ├── __init__.py
│   ├── answer_evaluator
│   │   ├── __init__.py
│   │   ├── answer_analyzer.py
│   │   └── answer_scorer.py
│   ├── input
│   │   ├── __init__.py
│   │   ├── initial_question_giver.py
│   │   └── input_analyzer.py
│   └── question_generator
│       ├── __init__.py
│       ├── answer_category_classifier.py
│       ├── answer_sub_category_classifier.py
│       ├── answer_validator.py
│       └── followup_question_giver.py
├── repository
│   ├── __init__.py
│   ├── interview_repository.py
│   └── question_answer
│       ├── __init__.py
│       └── question_answer_repository.py
├── service
│   ├── __init__.py
│   └── answer_service.py
└── utils
    ├── __init__.py
    ├── prompt_loader
    │   ├── __init__.py
    │   ├── json
    │   │   ├── AnswerAnalyzer.json
    │   │   ├── AnswerCategoryClassifier.json
    │   │   ├── AnswerScorer.json
    │   │   ├── AnswerSubCategoryClassifier.json
    │   │   ├── AnswerValidator.json
    │   │   ├── FollowUpQuestionGiver.json
    │   │   ├── InitialQuestionGiver.json
    │   │   ├── InputAnalyzer.json
    │   │   └── helpme.md
    │   └── prompt_loader.py
    └── singleton_meta_class.py
```

***
