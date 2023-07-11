import unittest
from moview.utils.data_manager import *
from unittest.mock import Mock
from moview.modules.analyzer.input_info_analyzer import InputInfoAnalyzer
from langchain.prompts import PromptTemplate


class TestInputInfoAnalyzer(unittest.TestCase):

    def setUp(self):
        self.mock_data_manager = Mock(spec=DataManager)
        self.mock_data_manager.company = "test_company"

        self.evaluation_manager = Mock(spec=EvaluationManager)

        self.input_info_analyzer = InputInfoAnalyzer(
            self.mock_data_manager,
            self.evaluation_manager
        )

    def test__make_system_template_for_analyzing_input_info(self):
        # given
        system_template = self.input_info_analyzer._make_system_template_for_analyzing_input_info(
            "test_company",
            "test_user_data"
        )

        # when
        prompt = PromptTemplate.from_template(system_template)

        # then
        print(remove_indent(prompt.template))
        self.assertEqual(
            prompt.template,
            '\nYou are an interviewer at test_company.\ntest_user_data')
