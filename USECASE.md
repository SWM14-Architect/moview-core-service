# 유즈케이스

[Main Flow]
- InputProcess를 통해, 사용자의 정보를 입력받는다.
- InputInfoAnalyzer를 통해, 사용자의 정보에 대한 평가를 생성한다.
- InitQuestionGenerator를 통해, 사용자 정보를 바탕으로 질문리스트를 생성한다.
- (Loop) 아래의 내용을 반복한다.
  - 생성된 질문 중 1개를 가져온다.
  - QuestionPrompter를 통해, 가져온 질문을 사용자에게 출력한다.
  - AnswerAnalyzer를 통해, 사용자의 답변을 평가한다.
  - (Loop) 아래의 내용을 반복한다.
    - FollowupQuestionGenerator를 통해, 심화질문을 생성한다.
    - 만약, 심화질문을 생성하지 않았다면 반복문을 종료한다.
    - QuestionPrompter를 통해, 생성된 심화질문을 사용자에게 출력한다.
    - AnswerAnalyzer를 통해, 사용자의 답변을 평가한다.

[InputInfoAnalyzer]
- DataManager에 저장된 사용자 정보를 입력받는다.
- 평가를 위한 프롬프트를 생성한다.
- 프롬프트를 생성할 때 사용자 정보를 추가한다.
- 평가 프롬프트를 통해 LLMChain을 만든다.
- Chain에 회사 이름을 받는다.
- 해당 입력에 대한 Chain을 적용한다.
- 출력으로 사용자의 자소서에 대한 평가가 생성된다.
- 생성된 평가는 EvaluationManager를 통해 저장된다.

[InitQuestionGenerator]
- DataManager에 저장된 사용자 정보를 입력받는다.
- 질문을 생성하기 위한 프롬프트를 생성한다.
- 프롬프트를 생성할 때 사용자 정보를 추가한다.
- 질문 생성 프롬프트를 통해 LLMChain을 만든다.
- Chain에 입력(생성할 질문 갯수)을 받는다.
- 해당 입력에 대한 Chain을 적용한다.
- 출력으로 N개의 질문이 생성된다.
- 생성된 질문은 CreateQuestionParser를 통해 List형태로 만든다.
- 파싱한 질문리스트를 반환한다.

[QuestionPrompter]
- QuestionEntity(질문)를 입력받는다.
- QuestionEntity를 사용자에게 출력한다.
- 사용자는 질문에 대한 답변을 입력한다.
- QuestionEntity에 답변 내용을 추가한다.

[AnswerAnalyzer]
- QuestionEntity(질문과 답변)를 입력받는다.
- 면접 질문과 답변을 평가하기 위한 프롬프트를 생성한다.
- 더 구체적인 평가를 위해서 면접 평가 기준 프롬프트를 추가한다.
- 2개의 프롬프트를 이용해서 라우터 체인을 만든다.
- 라우터 체인을 적용한다.
- 출력으로 면접 지원자의 답변 분석 내용이 생성된다.
- 생성된 평가는 EvaluationManager를 통해 저장된다.

[FollowupQuestionGenerator]
- EvaluationManager를 입력받는다.
- 심화질문을 생성하기 위한 프롬프트를 생성한다.
- 심화질문 생성 프롬프트를 통해 LLMChain을 만든다.
- Chain에 입력(질문과 답변, 그리고 평가내용)을 받는다.
- 해당 입력에 대한 Chain을 적용한다.
- 출력으로 심화질문이 생성된다.
  - 혹은 심화질문을 생성하지 않는다. (TODO: 심화질문을 생성할지 판단하는 부분과 생성하는 부분을 나눠야함.)
- 생성된 심화질문은 FollowupQuestionParser를 통해 양식에 맞춰서 반환한다.

![InitQuestionGenerator](https://github.com/westreed/Python-Langchain-Study/raw/main/mvp/img/CreateQuestionDiagram.png)

![MainFlow](https://github.com/westreed/Python-Langchain-Study/raw/main/mvp/img/MainFlow.png)