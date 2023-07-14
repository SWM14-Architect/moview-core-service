import unittest
from unittest.mock import Mock, patch
from moview.utils.data_manager import *
from moview.modules.prompter.question_prompter import QuestionPrompter


class TestQuestionPrompter(unittest.TestCase):
    def setUp(self):
        self.mock_data_manager = Mock(spec=DataManager)
        self.mock_question_entity = Mock(spec=QuestionEntity)
        self.question_prompter = QuestionPrompter()
        os.environ['PYTHON_PROFILE'] = 'test'

    @patch('builtins.print')
    @patch('builtins.input')
    def test_fetch_question_and_store_answer(self, mock_input, mock_print):
        # given
        self.mock_question_entity.question = "테스트 질문"
        mock_input.return_value = '테스트 답변'

        # when
        self.question_prompter.prompt_question(self.mock_question_entity)

        # then
        mock_print.assert_called_with("면접관: 테스트 질문")
        self.mock_question_entity.add_answer.assert_called_with('테스트 답변')

    @patch('builtins.input')
    def test_return_false_for_non_exit_answer(self, mock_input):
        # given
        self.mock_question_entity.question = "면접관: 테스트 질문"

        # when
        mock_input.return_value = 'exit나 c가 아님'

        # then
        result = self.question_prompter.prompt_question(self.mock_question_entity)
        self.assertEqual(result, False)

    @patch('builtins.input')
    def test_return_true_when_answer_is_exit(self, mock_input):
        # given
        self.mock_question_entity.question = "면접관: 테스트 질문"

        # when
        mock_input.return_value = 'exit'

        # then
        result = self.question_prompter.prompt_question(self.mock_question_entity)
        self.assertEqual(result, True)

    @patch('builtins.input')
    def test_return_true_when_answer_is_c(self, mock_input):
        # given
        self.mock_question_entity.question = "면접관: 테스트 질문"

        # when
        mock_input.return_value = 'c'

        # then
        result = self.question_prompter.prompt_question(self.mock_question_entity)
        self.assertEqual(result, True)
