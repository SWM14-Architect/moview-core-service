from typing import List


class InitialQuestionGiver:
    def __init__(self):
        pass

    def give_initial_questions(self, analysis_about_one_cover_letter: str, question_count: int) -> List[str]:
        """

        Args:
            analysis_about_one_cover_letter: 면접 지원자 자소서 답변 한 개에 대한 분석 내용
            question_count: 출제할 질문 개수

        Returns: 분석 내용을 바탕으로 생성된 초기 질문 문자열 리스트 (question_count만큼 생성)

        """
        pass

    def __parse_result_from_llm(self, initial_questions_from_llm: str) -> List[str]:
        """

        Args:
            initial_questions_from_llm: llm으로부터 온 초기 질문 문자열

        Returns:  초기 질문 문자열 리스트 (파싱됨)

        """
        pass
