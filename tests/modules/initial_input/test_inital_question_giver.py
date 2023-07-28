import unittest
from moview.modules.initial_input.initial_question_giver import InitialQuestionGiver


def is_not_none_string(s):
    return s is not None and isinstance(s, str)


class TestInitialQuestionGiver(unittest.TestCase):
    def setUp(self) -> None:
        self.giver = InitialQuestionGiver()

    def test_load_prompt(self):
        self.assertTrue(is_not_none_string(self.giver.prompt))
        print(self.giver.prompt.format(question_count=2))

    def test_give_initial_questions(self):
        analysis = """면접자는 '객체지향 개발 방법론' 수업에서 협업과 문제 해결에 주도적으로 참여한 경험이 있습니다.
         이는 면접자가 팀원들과 함께 목표를 달성하기 위해 노력하고 협력하는 능력을 갖추고 있다는 것을 보여줍니다.\n
         면접자는 요구사항 분석, 유즈케이스 작성, 테스트 케이스 작성 등의 작업을 통해 프로그램의 청사진을 그렸습니다. 
         이는 면접자가 문제 해결에 필요한 분석 및 설계 역량을 갖추고 있다는 것을 나타냅니다."""

        question_count = 3

        initial_questions = self.giver.give_initial_questions(analysis_about_one_cover_letter=analysis,
                                                              question_count=question_count)
        self.assertTrue(len(initial_questions) == question_count)
