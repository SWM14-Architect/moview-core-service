import unittest
from unittest.mock import patch
from flask import Flask
from flask_restx import Api
from moview.controller.generation_controller import *


class TestInitQuestion(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.app.config['SECRET_KEY'] = 'test'
        self.app.config['TESTING'] = True
        self.api.add_resource(InitQuestion, '/question')
        self.client = self.app.test_client()

    def test_get_when_has_no_data_manager(self):
        response = self.client.get('/question')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"messages": "유저 데이터를 먼저 입력해야 합니다."})

    @patch('moview.modules.question_generator.init_question_generator.InitQuestionGenerator.generate_init_question')
    def test_get(self, mock_method):
        mock_method.return_value = "mock response"

        data_manager_mock_data = {
            'user_company': 'Test Company',
            'user_job': 'Test Job Title',
            'job_requirement': 'Test Job Advertisement',
            'cover_letter': 'Test Personal Statement',
            'self_introduce': 'Test Introduce'
        }
        with self.client.session_transaction() as sess:
            sess['data_manager'] = data_manager_mock_data

        response = self.client.get('/question')

        mock_method.assert_called_once()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"messages": "mock response"})


class TestFollowUpQuestion(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.app.config['SECRET_KEY'] = 'test'
        self.app.config['TESTING'] = True
        self.api.add_resource(FollowUpQuestion, '/question/followup')
        self.client = self.app.test_client()

    def test_post_when_has_no_data_manager(self):
        response = self.client.post('/question/followup')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"messages": "유저 데이터를 먼저 입력해야 합니다."})

    def test_post_when_has_no_evaluation_manager(self):
        data_manager_mock_data = {
            'user_company': 'Test Company',
            'user_job': 'Test Job Title',
            'job_requirement': 'Test Job Advertisement',
            'cover_letter': 'Test Personal Statement',
            'self_introduce': 'Test Introduce'
        }
        with self.client.session_transaction() as sess:
            sess['data_manager'] = data_manager_mock_data

        response = self.client.post('/question/followup')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"messages": "평가 데이터가 존재하지 않습니다."})

    def test_post_when_has_no_evaluation_records(self):
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

        # evaluation_manager의 key 는 question, answer 만 가능함.
        evaluation_mock_data_not_working = {
            'not-question-records': 'test',
            'not-answer-records': 'test'
        }

        with self.client.session_transaction() as sess:
            sess['data_manager'] = manager_mock_data
            sess['evaluation_manager'] = evaluation_mock_data_not_working

        response = self.client.post('/question/followup', json=request_mock_data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"messages": "질문을 답변하는 과정이 최소 1회 이상 필요합니다."})

    @patch(
        'moview.modules.question_generator.follow_up_question_generator.FollowUpQuestionGenerator.generate_follow_up_question')
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

        evaluation_mock_data = {
            'question': 'test',
            'answer': 'test'
        }
        with self.client.session_transaction() as sess:
            sess['data_manager'] = manager_mock_data
            sess['evaluation_manager'] = evaluation_mock_data

        response = self.client.post('/question/followup', json=request_mock_data)

        mock_method.assert_called_once()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"messages": "mock response"})


if __name__ == '__main__':
    unittest.main()
