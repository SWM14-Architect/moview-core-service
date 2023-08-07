from moview.repository.interviewee_data_repository import IntervieweeDataRepository, MongoConfig


class IntervieweeFeedbackService:
    def __init__(self):
        self.repository = IntervieweeDataRepository(mongo_config=MongoConfig())

    def save_feedback_of_interviewee(self, session_id, feedback_list):

        found_interview_data = self.repository.find_by_session_id(session_id=session_id)

        if found_interview_data is None:
            raise Exception("Interview history not found.")

        # 피드백 저장
        for feedback in feedback_list:
            found_interview_data.save_feedback_in_interviewee_feedback(feedback=feedback)

        updated_id = self.repository.update(session_id=session_id, interviewee_data_entity=found_interview_data)

        return updated_id
