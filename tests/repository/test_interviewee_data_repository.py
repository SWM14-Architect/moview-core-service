import unittest
from moview.repository.interviewee_data_repository import IntervieweeDataRepository, MongoConfig
from moview.repository.entity.interviewee_data_main_document import IntervieweeDataEntity
from moview.repository.entity.interviewee_data_subdocument import IntervieweeInitialInputData, \
    InputDataAnalysisResult, InterviewQuestions, IntervieweeAnswerScores, IntervieweeFeedbacks


class TestIntervieweeDataRepository(unittest.TestCase):
    def setUp(self):
        self.entity = IntervieweeDataEntity(
            session_id='testtest1234',
            initial_input_data=IntervieweeInitialInputData(
                interviewee_name='test',
                job_group='test',
                recruit_announcement='test',
                cover_letter_questions=['test'],
                cover_letter_answers=['test']
            ),
            input_data_analysis_result=InputDataAnalysisResult(
                input_data_analysis_list=['test']
            ),
            interview_questions=InterviewQuestions(
                initial_question_list=[['test']]
            ),
            interviewee_answer_scores=IntervieweeAnswerScores(
                question_list=['test'],
                answer_list=['test'],
                category_and_sub_category_list=['test'],
                score_of_answer_list=['test']
            ),
            interviewee_feedbacks=IntervieweeFeedbacks(
                feedback_list=['test']
            )
        )

        self.repository = IntervieweeDataRepository(
            MongoConfig())

    def tearDown(self) -> None:
        # 테스트용 엔티티 삭제
        self.repository.delete_all_with_id_for_teardown_in_testing(self.entity.session_id)

    def test_singleton(self):
        # given
        mongo_config = (MongoConfig())

        # when
        repository1 = IntervieweeDataRepository(mongo_config)
        repository2 = IntervieweeDataRepository(mongo_config)

        # then
        self.assertEqual(repository1, repository2)  # repository1과 repository2가 같은 객체인지 확인

    def test_save(self):
        # when
        session_id = self.repository.save(self.entity)

        # then
        self.assertEqual(session_id, 'testtest1234')

    def test_find(self):
        # given
        session_id = self.repository.save(self.entity)
        self.assertEqual(session_id, 'testtest1234')

        # when
        loaded_entity = self.repository.find_by_session_id(session_id)

        # Assert
        self.assertEqual(loaded_entity.session_id, session_id)

    def test_update(self):
        # given
        session_id = self.repository.save(self.entity)

        update_entity = IntervieweeDataEntity(
            session_id='testtest1234',
            initial_input_data=IntervieweeInitialInputData(
                interviewee_name='update',
                job_group='update',
                recruit_announcement='update',
                cover_letter_questions=['update'],
                cover_letter_answers=['update']
            ),
            input_data_analysis_result=InputDataAnalysisResult(
                input_data_analysis_list=['update']
            ),
            interview_questions=InterviewQuestions(
                initial_question_list=[['update']]
            ),
            interviewee_answer_scores=IntervieweeAnswerScores(
                question_list=['update'],
                answer_list=['update'],
                category_and_sub_category_list=['update'],
                score_of_answer_list=['update']
            ),
            interviewee_feedbacks=IntervieweeFeedbacks(
                feedback_list=['update']
            ),
        )

        # when
        updated_session_id = self.repository.update(session_id=session_id, interviewee_data_entity=update_entity)

        # then
        self.assertEqual(updated_session_id, session_id)
        self.assertEqual(update_entity.initial_input_data.interviewee_name, 'update')
        self.assertEqual(update_entity.initial_input_data.job_group, 'update')

    if __name__ == '__main__':
        unittest.main()
