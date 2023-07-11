import unittest
from unittest.mock import patch
from flask import Flask
from flask_restx import Api
from moview.controller.evaluation_controller import *


class TestUserDataUpload(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.app.config['SECRET_KEY'] = 'test'
        self.app.config['TESTING'] = True
        self.api.add_resource(UserDataUpload, '/user')
        self.client = self.app.test_client()

    def test_post(self):
        mock_data = {
            'user_company': 'Test Company',
            'user_job': 'Test Job Title',
            'job_requirement': 'Test Job Advertisement',
            'cover_letter': 'Test Personal Statement'
        }

        response = self.client.post(
            '/user',
            json=mock_data,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"messages": "success"})


class TestUserEvaluation(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.app.config['SECRET_KEY'] = 'test'
        self.app.config['TESTING'] = True
        self.api.add_resource(UserEvaluation, '/user/evaluation')
        self.client = self.app.test_client()

    # patch 데코레이터를 사용하여 InputInfoAnalyzer의 analyze_input_info 메소드를 직접 모킹합니다.
    @patch('moview.modules.analyzer.input_info_analyzer.InputInfoAnalyzer.analyze_input_info')
    def test_get(self, mock_method):
        # 모킹된 analyze_input_info 메소드가 "mock response"를 반환하도록 설정합니다.
        mock_method.return_value = "mock response"

        mock_data = {
            'user_company': 'Test Company',
            'user_job': 'Test Job Title',
            'job_requirement': 'Test Job Advertisement',
            'cover_letter': 'Test Personal Statement',
            'self_introduce': 'Test Introduce'
        }
        with self.client.session_transaction() as sess:
            sess['data_manager'] = mock_data

        response = self.client.get('/user/evaluation')

        # analyze_input_info 메소드가 한 번 호출되었는지 확인합니다.
        mock_method.assert_called_once()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"messages": "mock response"})


class TestAnswerEvaluation(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.app.config['SECRET_KEY'] = 'test'
        self.app.config['TESTING'] = True
        self.api.add_resource(AnswerEvaluation, '/answer/evaluation')
        self.client = self.app.test_client()

    def test_post_when_has_no_data_manager(self):
        request_mock_data = {
            'question': 'Test question',
            'answer': 'Test answer'
        }

        response = self.client.post('/answer/evaluation', json=request_mock_data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"messages": "유저 데이터를 먼저 입력해야 합니다."})

    def test_post_when_has_no_evaluation_manager(self):
        request_mock_data = {
            'question': 'Test question',
            'answer': 'Test answer'
        }

        data_manager_mock_data = {
            'user_company': 'Test Company',
            'user_job': 'Test Job Title',
            'job_requirement': 'Test Job Advertisement',
            'cover_letter': 'Test Personal Statement',
            'self_introduce': 'Test Introduce'
        }
        with self.client.session_transaction() as sess:
            sess['data_manager'] = data_manager_mock_data

        response = self.client.post('/answer/evaluation', json=request_mock_data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"messages": "평가 데이터가 존재하지 않습니다."})

    @patch('moview.modules.analyzer.answer_analyzer.AnswerAnalyzer.analyze_answer')
    def test_post(self, mock_method):
        mock_method.return_value = "mock response"

        request_mock_data = {
            'question': 'Test question',
            'answer': 'Test answer'
        }

        manager_mock_data = {
            'user_company': 'Test Company',
            'user_job': 'Test Job Title',
            'job_requirement': 'Test Job Advertisement',
            'cover_letter': 'Test Personal Statement',
            'self_introduce': 'Test Introduce'
        }
        with self.client.session_transaction() as sess:
            sess['data_manager'] = manager_mock_data
            sess['evaluation_manager'] = manager_mock_data

        response = self.client.post('/answer/evaluation', json=request_mock_data)

        mock_method.assert_called_once()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"messages": "mock response"})


if __name__ == '__main__':
    unittest.main()
