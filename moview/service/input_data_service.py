from typing import List, Any, Tuple, Dict

from moview.config.db.mongo_config import MongoConfig
from moview.config.loggers.mongo_logger import error_logger, execution_trace_logger
from moview.domain.entity.input_data.coverletter_document import CoverLetter
from moview.domain.entity.input_data.initial_input_data_document import InitialInputData
from moview.modules.input.input_analyzer import InputAnalyzer
from moview.modules.input.initial_question_giver import InitialQuestionGiver, InitialQuestionParseError
from moview.repository.input_data_repository import InputDataRepository


class InputDataService:
    def __init__(self, mongo_config: MongoConfig):
        self.INIT_QUESTION_MULTIPLIER = 2  # 각 자소서 답변에 대해 초기 질문을 몇 개씩 생성할 것인지 결정하는 상수
        self.input_data_repository = InputDataRepository(mongo_config=mongo_config)

        self.initial_input_analyzer = InputAnalyzer()
        self.initial_question_giver = InitialQuestionGiver()

    def ask_initial_question_to_interviewee(
            self,
            interviewee_name: str,
            company_name: str,
            job_group: str,
            recruit_announcement: str,
            cover_letter_questions: List[str],
            cover_letter_answers: List[str]
    ) -> List[str]:
        """
        Args:
            interviewee_name: 인터뷰 대상자 이름
            company_name: 인터뷰 대상자 회사 이름
            job_group: 인터뷰 대상자 직군
            recruit_announcement: 인터뷰 대상자 공고
            cover_letter_questions: 인터뷰 대상자 자소서 문항 리스트
            cover_letter_answers: 인터뷰 대상자 자소서 답변 리스트

        Returns: {
            "input_data_document_id" : 면접자 데이터 문서 string id,
            "initial_question_list" : 초기 질문 리스트
        }
        """

        # 적절하지 않은 사용자 정보 필터링.
        result = self.__filter_initial_inputs_of_interviewee(
            interviewee_name=interviewee_name,
            company_name=company_name,
            job_group=job_group, recruit_announcement=recruit_announcement,
            cover_letter_questions=cover_letter_questions,
            cover_letter_answers=cover_letter_answers
        )
        interviewee_name, company_name, job_group, recruit_announcement, cover_letter_questions, cover_letter_answers = result

        execution_trace_logger(
            "filter input",
            interviewee_name=interviewee_name,
            job_group=job_group,
            recruit_announcement=recruit_announcement,
            cover_letter_questions=cover_letter_questions,
            cover_letter_answers=cover_letter_answers
        )

        # 사용자 입력 정보 분석 (직군, 공고, 자소서 문항 리스트, 자소서 답변 리스트)-> 분석 결과 문자열 리스트 (자소서 입력 개수만큼 분석 내용이 나옵니다.)
        analyzed_initial_inputs_of_interviewee = self.__analyze_initial_inputs_of_interviewee(
            job_group=job_group,
            recruit_announcement=recruit_announcement,
            cover_letter_questions=cover_letter_questions,
            cover_letter_answers=cover_letter_answers
        )

        execution_trace_logger(
            "analyze input",
            analyzed_initial_inputs_of_interviewee=analyzed_initial_inputs_of_interviewee
        )

        # TODO: 초기 질문 생성 파트 변경해야함
        initial_question_list = []  # List[List[Any]

        # 각 자소서 답변 분석 내용에 대해 2개씩 초기 질문 생성.
        for analysis_about_one_cover_letter in analyzed_initial_inputs_of_interviewee:

            try:
                # 길이 (INIT_QUESTION_MULTIPLIER) 의 질문 리스트 생성 List[str]
                created_questions = self.initial_question_giver.give_initial_questions(
                    analysis_about_one_cover_letter=analysis_about_one_cover_letter,
                    question_count=self.INIT_QUESTION_MULTIPLIER
                )

                # 생성된 초기 질문 (INIT_QUESTION_MULTIPLIER)개를 initial_question_list에 추가.
                # List[str] (created_questions) 에서 List[str] (initial_question_list)로 옮기기 위한 코드
                for i in range(self.INIT_QUESTION_MULTIPLIER):
                    initial_question_list.append(created_questions[i])

            except InitialQuestionParseError as e:  # 파싱 실패한 경우
                error_logger("InitialQuestionParseError")

                # question_count만큼 빈 문자열 담기
                for _ in range(self.INIT_QUESTION_MULTIPLIER):
                    initial_question_list.append([])

        execution_trace_logger("initial question", initial_question_list=initial_question_list)
        
        # Initial Input Data Entity Model 생성
        initial_input_data_model, cover_letter_model_list = self.__create_interviewee_data_entity(
            interviewee_name=interviewee_name,
            company_name=company_name,
            job_group=job_group, recruit_announcement=recruit_announcement,
            cover_letter_questions=cover_letter_questions,
            cover_letter_answers=cover_letter_answers,
            analyzed_initial_inputs_of_interviewee=analyzed_initial_inputs_of_interviewee
        )
        
        # Initial Input Data Dcoument 저장
        initial_input_document = self.input_data_repository.save(
            initial_input_data=initial_input_data_model,
            cover_letter_list=cover_letter_model_list
        )

        # TODO: Initial Question Entity Model 생성

        # TODO: Initial Question Document 저장
        
        # TODO: Initial Question을 Frontend에게 건내주기 위한 형태로 재가공하기

        return initial_question_list

    def __filter_initial_inputs_of_interviewee(
            self,
            interviewee_name: str,
            company_name: str,
            job_group: str,
            recruit_announcement: str,
            cover_letter_questions: List[str],
            cover_letter_answers: List[str]
    ) -> List[Any]:
        """
        Returns: 적절하지 않은 것은 공백 처리된 초기 입력 정보
        """

        # todo mvp 이후 추가할 메서드임. 현재는 모든 입력 정보를 그대로 반환함.

        # 직군 필터.

        # 공고 필터.

        # 자소서 문항 필터. 개수만큼 반복

        # 자소서 답변 필터. 개수만큼 반복
        return [
            interviewee_name,
            company_name,
            job_group,
            recruit_announcement,
            cover_letter_questions,
            cover_letter_answers
        ]

    def __analyze_initial_inputs_of_interviewee(
            self,
            job_group: str,
            recruit_announcement: str,
            cover_letter_questions: List[str],
            cover_letter_answers: List[str]
    ) -> List[str]:
        """
        (자소서 문항,자소서 답변) 전체 쌍에 대해 LLM을 이용하여 분석하는 메서드
        해당 쌍을 4개 입력 받았다면, 4개의 쌍에 대해 분석을 수행한다.
        cover_letter_questions 와 cover_letter_answers 의 길이는 같아야 한다.
        그리고 인덱스를 i라 할 때, (cover_letter_questions[i], cover_letter_answers[i]) 쌍이다.

        Returns: 입력 파라미터에 대한 분석 결과 문자열 리스트 (올바르지 않은 입력은 공백으로 치환)
        """
        if len(cover_letter_questions) != len(cover_letter_answers):
            error_logger("자소서 문항과 자소서 답변의 개수가 일치하지 않습니다.",
                         cover_letter_questions_count=len(cover_letter_questions),
                         cover_letter_answers_count=len(cover_letter_answers))
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

    def __create_interviewee_data_entity(
            self,
            interviewee_name: str,
            company_name: str,
            job_group: str,
            recruit_announcement: str,
            cover_letter_questions: List[str],
            cover_letter_answers: List[str],
            analyzed_initial_inputs_of_interviewee: List[str]
    ) -> Tuple[InitialInputData, List[CoverLetter]]:

        initial_input_data_model = InitialInputData(
            interviewee_name=interviewee_name,
            company_name=company_name,
            job_group=job_group,
            recruit_announcement=recruit_announcement,
        )
        cover_letter_model_list = [
            CoverLetter(
                coverletter_question=cover_letter_questions[i],
                coverletter_answer=cover_letter_answers[i],
                coverletter_analysis_result=analyzed_initial_inputs_of_interviewee[i]
            ) for i in range(len(cover_letter_questions))
        ]

        return initial_input_data_model, cover_letter_model_list
