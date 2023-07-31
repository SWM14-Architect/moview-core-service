from typing import Optional

from pymongo import MongoClient

from moview.repository.entity.interviewee_data_main_document import IntervieweeDataEntity
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

    def find_by_session_id(self, session_id: str) -> Optional[dict]:
        """
        주어진 ID에 해당하는 데이터를 불러옵니다.
        해당하는 데이터가 없는 경우 None을 반환합니다.
        """
        return self.collection.find_one({'session_id': session_id})

    def update(self, session_id: str, interviewee_data_entity: IntervieweeDataEntity) -> str:
        document = self._convert_entity_to_document(interviewee_data_entity)
        self.collection.update_one({'session_id': session_id}, {'$set': document})
        return document['session_id']

    def delete_all_with_id_for_teardown_in_testing(self, session_id: str):
        # 테스트 코드에서 teardown에서 사용하기 위해 만든 함수입니다. 다른데서 절대 사용하지 마세요!!!!!!!!!!
        self.collection.delete_many({'session_id': session_id})

    @staticmethod
    def _convert_entity_to_document(interviewee_data_entity: IntervieweeDataEntity) -> dict:
        return {
            'session_id': interviewee_data_entity.session_id,

            'initial_input_data': {
                'interviewee_name': interviewee_data_entity.initial_input_data.interviewee_name,
                'job_group': interviewee_data_entity.initial_input_data.job_group,
                'recruit_announcement': interviewee_data_entity.initial_input_data.recruit_announcement,
                'cover_letter_questions': interviewee_data_entity.initial_input_data.cover_letter_questions,
                'cover_letter_answers': interviewee_data_entity.initial_input_data.cover_letter_answers
            },

            'initial_interview_analysis': {
                'initial_interview_analysis': interviewee_data_entity.
                initial_interview_analysis.initial_interview_analysis_list
            },

            'interview_questions': {
                'initial_question_list': interviewee_data_entity.interview_questions.initial_question_list,
                'excluded_questions_for_giving_followup_question': interviewee_data_entity.interview_questions.
                excluded_questions_for_giving_followup_question,
                'initial_question_index': interviewee_data_entity.interview_questions.initial_question_index,
                'followup_question_count': interviewee_data_entity.interview_questions.followup_question_count,
            },

            'interviewee_answer_score_list': [
                {
                    'question': score_data.question,
                    'answer': score_data.answer,
                    'category_and_sub_category': score_data.category_and_sub_category,
                    'score_of_answer': score_data.score_of_answer
                } for score_data in interviewee_data_entity.interviewee_answer_score_list
            ]

        }
