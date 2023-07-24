import re

from moview.modules.question_generator import AnswerFilter, AnswerCategoryClassifier, AnswerSubCategoryClassifier, \
    FollowUpQuestionGiver


# 정규 표현식으로 짜긴 했는데, 간혹 출력값이 이상하게 나올 수 있음. 이럴 떄는 문장 유사도 평가가 좋아보임. 그래서 이러한 함수 간 접합 부분에는 vector db를 쓰는게 나을 듯?
def find_first_number(text):
    match = re.search(r'\d+', text)
    if match:
        return match.group()
    else:
        return None


def find_first_yes_no(text):
    pattern = r'(yes|no)'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group()
    else:
        return None


class InappropriateAnswerError(Exception):
    def __init__(self, message="Inappropriate answer provided."):
        self.message = message
        super().__init__(self.message)


class ResubmissionRequestError(Exception):
    def __init__(self, message="A resubmission has been requested."):
        self.message = message
        super().__init__(self.message)


class FollowUpQuestionManager:
    def __init__(self):
        self.filter = AnswerFilter()
        self.major = AnswerCategoryClassifier()
        self.sub = AnswerSubCategoryClassifier()
        self.giver = FollowUpQuestionGiver()
        # todo 이전 질문만 세션 별로 관리하는 객체가 필요해보인다. 이 클래스를 아예 서비스단으로 올리자.

    def manage_followup_question(self, job_group: str, question: str, answer: str) -> str:

        # 적절하지 않은 답변을 걸러냅니다.
        check = self.filter.exclude_invalid_answer(job_group=job_group, question=question, answer=answer)

        number = find_first_number(check)

        if number == "1":
            raise ResubmissionRequestError()
        elif number == "2" or number == "3" or number == "4":
            raise InappropriateAnswerError()

        # todo 현재 질문을 이전 질문에 추가할 때, [세션 id] :[이전 질문리스트] 형태로 추가해야 함. 그래야 세션 별로 추적 가능

        # 면접 질문과 답변의 대분류
        categories = self.major.classify_category_of_answer(job_group=job_group, question=question, answer=answer)

        # 중분류
        categories_ordered_pair = self.sub.classify_sub_category_of_answer(
            job_group=job_group, question=question,
            answer=answer, categories=categories)

        # 꼬리 질문 출제
        followup_question = self.giver.give_followup_question(
            job_group=job_group, question=question, answer=answer,
            previous_questions=str(self.previous_question), categories_ordered_pair=categories_ordered_pair)

        # todo 꼬리 질문을 이전 질문에 추가할 때, [세션 id] :[이전 질문리스트] 형태로 추가해야 함. 그래야 세션 별로 추적 가능

        return followup_question
