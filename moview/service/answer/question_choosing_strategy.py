import random
from typing import List


class QuestionChoosingStrategy:
    """
    질문을 선택하는 행동에 대한 전략 인터페이스를 정의합니다
    """

    def choose_question(self, parsed_questions: List[str]) -> str:
        raise NotImplementedError("Choosing strategy must implement choose_question method.")


class RandomQuestionChoosingStrategy(QuestionChoosingStrategy):
    """
    질문을 랜덤하게 선택하는 전략을 정의합니다(구체 클래스)
    """

    def choose_question(self, parsed_questions: List[str]) -> str:
        return random.choice(parsed_questions)
