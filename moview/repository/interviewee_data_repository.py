from typing import Optional

from pymongo import MongoClient

from moview.repository.entity.interviewee_data_main_document import IntervieweeDataEntity
from moview.repository.entity.interviewee_data_subdocument import *
from moview.utils.singleton_meta_class import SingletonMeta


# todo 아직 몽고 db 연결전이므로 임시로 만들었음.
class MongoConfig:
    def __init__(self, host: str = 'localhost', port: int = 27017, db_name: str = 'interview_database',
                 collection_name: str = 'interview_data'):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.collection_name = collection_name


class IntervieweeDataRepository(metaclass=SingletonMeta):
    def __init__(self, mongo_config: MongoConfig):
        self.client = MongoClient(mongo_config.host, mongo_config.port)
        self.db = self.client[mongo_config.db_name]
        self.collection = self.db[mongo_config.collection_name]

    def save(self, interviewee_data_entity: IntervieweeDataEntity) -> str:
        document = self._convert_entity_to_document(interviewee_data_entity)
        self.collection.insert_one(document)
        return document['session_id']

    def find_by_session_id(self, session_id: str) -> Optional[IntervieweeDataEntity]:
        """
        주어진 ID에 해당하는 데이터를 불러옵니다.
        해당하는 데이터가 없는 경우 None을 반환합니다.
        """
        document = self.collection.find_one({'session_id': session_id})
        if document is None:
            return None
        else:
            entity = self._convert_document_to_entity(document=document)
            return entity

    def update(self, session_id: str, interviewee_data_entity: IntervieweeDataEntity) -> str:
        document = self._convert_entity_to_document(interviewee_data_entity)
        self.collection.update_one({'session_id': session_id}, {'$set': document})
        return document['session_id']

    def delete_all_with_id_for_teardown_in_testing(self, session_id: str):
        # 테스트 코드에서 teardown에서 사용하기 위해 만든 함수입니다. 다른데서 절대 사용하지 마세요!!!!!!!!!!
        self.collection.delete_many({'session_id': session_id})

    @staticmethod
    def _convert_entity_to_document(interviewee_data_entity: IntervieweeDataEntity) -> dict:
        # todo mvp v2에서 데이터 나눌 필요 있음...
        return {
            'session_id': interviewee_data_entity.session_id,

            'initial_input_data': {
                'interviewee_name': interviewee_data_entity.initial_input_data.interviewee_name,
                'job_group': interviewee_data_entity.initial_input_data.job_group,
                'recruit_announcement': interviewee_data_entity.initial_input_data.recruit_announcement,
                'cover_letter_questions': interviewee_data_entity.initial_input_data.cover_letter_questions,
                'cover_letter_answers': interviewee_data_entity.initial_input_data.cover_letter_answers
            },

            'input_data_analysis_result': {
                'input_data_analysis_list': interviewee_data_entity.
                input_data_analysis_result.input_data_analysis_list
            },

            'interview_questions': {
                'initial_question_list': interviewee_data_entity.interview_questions.initial_question_list,
                'followup_question_list': interviewee_data_entity.interview_questions.
                followup_question_list,
                'initial_question_index': interviewee_data_entity.interview_questions.initial_question_index,
                'followup_question_count': interviewee_data_entity.interview_questions.followup_question_count,
            },

            'interviewee_answer_scores': {
                'question_list': interviewee_data_entity.interviewee_answer_scores.question_list,
                'answer_list': interviewee_data_entity.interviewee_answer_scores.answer_list,
                'category_and_sub_category_list': interviewee_data_entity
                .interviewee_answer_scores.category_and_sub_category_list,
                'score_of_answer_list': interviewee_data_entity.interviewee_answer_scores.score_of_answer_list
            },
            'interviewee_feedbacks': {
                'feedback_list': interviewee_data_entity.interviewee_feedbacks.feedback_list
            }

        }

    @staticmethod
    def _convert_document_to_entity(document) -> IntervieweeDataEntity:
        initial_input_data = IntervieweeInitialInputData(
            interviewee_name=document['initial_input_data']['interviewee_name'],
            job_group=document['initial_input_data']['job_group'],
            recruit_announcement=document['initial_input_data']['recruit_announcement'],
            cover_letter_questions=document['initial_input_data']['cover_letter_questions'],
            cover_letter_answers=document['initial_input_data']['cover_letter_answers'],
        )

        input_data_analysis_result = InputDataAnalysisResult(
            input_data_analysis_list=document['input_data_analysis_result']['input_data_analysis_list'],
        )

        interview_questions = InterviewQuestions(
            initial_question_list=document['interview_questions']['initial_question_list'],
            followup_question_list=document['interview_questions']['followup_question_list'],
            initial_question_index=document['interview_questions']['initial_question_index'],
            followup_question_count=document['interview_questions']['followup_question_count'],
        )

        interviewee_answer_scores = IntervieweeAnswerScores(
            question_list=document['interviewee_answer_scores']['question_list'],
            answer_list=document['interviewee_answer_scores']['answer_list'],
            category_and_sub_category_list=document['interviewee_answer_scores']['category_and_sub_category_list'],
            score_of_answer_list=document['interviewee_answer_scores']['score_of_answer_list'],
        )

        interviewee_feedbacks = IntervieweeFeedbacks(
            feedback_list=document['interviewee_feedbacks']['feedback_list']
        )

        return IntervieweeDataEntity(
            session_id=document['session_id'],
            initial_input_data=initial_input_data,
            input_data_analysis_result=input_data_analysis_result,
            interview_questions=interview_questions,
            interviewee_answer_scores=interviewee_answer_scores,
            interviewee_feedbacks=interviewee_feedbacks,
        )
