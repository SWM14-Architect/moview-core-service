from typing import Any

from moview.modules.initial_input.initial_input_analyzer import InitialInputAnalyzer
from moview.modules.initial_input.initial_question_giver import InitialQuestionGiver, InitialQuestionParseError
from moview.repository.interviewee_data_repository import IntervieweeDataRepository, MongoConfig
from moview.repository.entity.interviewee_data_main_document import IntervieweeDataEntity
from moview.repository.entity.interviewee_data_subdocument import *


class IntervieweeInputService:
    def __init__(self):
        self.INIT_QUESTION_MULTIPLIER = 2  # 각 자소서 답변에 대해 초기 질문을 몇 개씩 생성할 것인지 결정하는 상수
        # todo MongoConfig 나중에 삭제하거나 수정할 필요 있을 듯.
        self.repository = IntervieweeDataRepository(mongo_config=MongoConfig())

        self.initial_input_analyzer = InitialInputAnalyzer()
        self.initial_question_giver = InitialQuestionGiver()

    def ask_initial_question_to_interviewee(self, session_id, interviewee_name: str,
                                            job_group: str, recruit_announcement: str,
                                            cover_letter_questions: List[str],
                                            cover_letter_answers: List[str]):
        """

        Args:
            session_id: flask session id
            interviewee_name: 인터뷰 대상자 이름
            job_group: 인터뷰 대상자 직군
            recruit_announcement: 인터뷰 대상자 공고
            cover_letter_questions: 인터뷰 대상자 자소서 문항 리스트
            cover_letter_answers: 인터뷰 대상자 자소서 답변 리스트

        Returns: 저장된 다큐먼트의 session_id

        """

        # 적절하지 않은 사용자 정보 필터링.
        interviewee_name, job_group, recruit_announcement, cover_letter_questions, cover_letter_answers = self.__filter_initial_inputs_of_interviewee(
            interviewee_name=interviewee_name,
            job_group=job_group, recruit_announcement=recruit_announcement,
            cover_letter_questions=cover_letter_questions,
            cover_letter_answers=cover_letter_answers)

        # 사용자 입력 정보 분석 (직군, 공고, 자소서 문항 리스트, 자소서 답변 리스트)-> 분석 결과 문자열 리스트 (자소서 입력 개수만큼 분석 내용이 나옵니다.)
        analyzed_initial_inputs_of_interviewee = self.__analyze_initial_inputs_of_interviewee(
            job_group=job_group,
            recruit_announcement=recruit_announcement,
            cover_letter_questions=cover_letter_questions,
            cover_letter_answers=cover_letter_answers)

        initial_question_list = []  # List[List[Any]

        # 각 자소서 답변 분석 내용에 대해 2개씩 초기 질문 생성.
        for analysis_about_one_cover_letter in analyzed_initial_inputs_of_interviewee:

            try:
                # 길이 (INIT_QUESTION_MULTIPLIER) 의 질문 리스트 생성 List[str]
                created_questions = self.initial_question_giver.give_initial_questions(
                    analysis_about_one_cover_letter=analysis_about_one_cover_letter,
                    question_count=self.INIT_QUESTION_MULTIPLIER)

                # 생성된 초기 질문 (INIT_QUESTION_MULTIPLIER)개를 initial_question_list에 추가.
                # List[str] (created_questions) 에서 List[str] (initial_question_list)로 옮기기 위한 코드
                for _ in range(self.INIT_QUESTION_MULTIPLIER):
                    initial_question_list.append(created_questions.pop())

            except InitialQuestionParseError as e:  # 파싱 실패한 경우
                # question_count만큼 빈 문자열 담기
                for _ in range(self.INIT_QUESTION_MULTIPLIER):
                    initial_question_list.append([])

        entity = self.__create_interviewee_data_entity(session_id=session_id,
                                                       interviewee_name=interviewee_name,
                                                       job_group=job_group, recruit_announcement=recruit_announcement,
                                                       cover_letter_questions=cover_letter_questions,
                                                       cover_letter_answers=cover_letter_answers,
                                                       initial_question_list=initial_question_list,
                                                       analyzed_initial_inputs_of_interviewee=analyzed_initial_inputs_of_interviewee)

        return self.repository.save(interviewee_data_entity=entity)

    def __filter_initial_inputs_of_interviewee(self, interviewee_name: str, job_group: str, recruit_announcement: str,
                                               cover_letter_questions: List[str], cover_letter_answers: List[str]):
        """

        Returns: 적절하지 않은 것은 공백 처리된 초기 입력 정보

        """

        # todo mvp 이후 추가할 메서드임. 현재는 모든 입력 정보를 그대로 반환함.

        # 직군 필터.

        # 공고 필터.

        # 자소서 문항 필터. 개수만큼 반복

        # 자소서 답변 필터. 개수만큼 반복
        return interviewee_name, job_group, recruit_announcement, cover_letter_questions, cover_letter_answers

    def __analyze_initial_inputs_of_interviewee(self, job_group: str, recruit_announcement: str,
                                                cover_letter_questions: List[str],
                                                cover_letter_answers: List[str]) -> List[str]:
        """
        (자소서 문항,자소서 답변) 전체 쌍에 대해 LLM을 이용하여 분석하는 메서드
        해당 쌍을 4개 입력 받았다면, 4개의 쌍에 대해 분석을 수행한다.
        cover_letter_questions 와 cover_letter_answers 의 길이는 같아야 한다.
        그리고 인덱스를 i라 할 때, (cover_letter_questions[i], cover_letter_answers[i]) 쌍이다.

        Returns: 입력 파라미터에 대한 분석 결과 문자열 리스트 (올바르지 않은 입력은 공백으로 치환)

        """
        if len(cover_letter_questions) != len(cover_letter_answers):
            raise ValueError("자소서 문항과 자소서 답변의 개수가 일치하지 않습니다.")

        analysis_count = len(cover_letter_questions)

        analysis_list = []
        # 자소서 개수만큼 분석 시작.
        for i in range(analysis_count):
            analysis_about_one_cover_letter = self.initial_input_analyzer.analyze_initial_input(
                job_group=job_group,
                recruitment_announcement=recruit_announcement,
                cover_letter_question=cover_letter_questions[i],
                cover_letter_answer=cover_letter_answers[i])

            analysis_list.append(analysis_about_one_cover_letter)

        return analysis_list

    def __create_interviewee_data_entity(self, session_id,
                                         interviewee_name: str, job_group: str, recruit_announcement: str,
                                         cover_letter_questions: List[str],
                                         cover_letter_answers: List[str],
                                         initial_question_list: List[List[Any]],
                                         analyzed_initial_inputs_of_interviewee: List[str]
                                         ) -> IntervieweeDataEntity:

        # 초기 엔티티 상태 저장이므로, 초기 입력 데이터, 초기 분석, 면접 초기 질문만 저장. 그 외에는 아직 비어있음.
        entity = IntervieweeDataEntity(

            session_id=session_id,

            initial_input_data=IntervieweeInitialInputData(
                interviewee_name=interviewee_name,
                job_group=job_group,
                recruit_announcement=recruit_announcement,
                cover_letter_questions=cover_letter_questions,
                cover_letter_answers=cover_letter_answers
            ),

            input_data_analysis_result=InputDataAnalysisResult(
                input_data_analysis_list=analyzed_initial_inputs_of_interviewee),

            interview_questions=InterviewQuestions(initial_question_list=initial_question_list),

            interviewee_answer_scores=IntervieweeAnswerScores(),

            interviewee_feedbacks=IntervieweeFeedbacks()
        )

        return entity
