from typing import List, Any, Tuple, Dict
import asyncio

from moview.config.loggers.mongo_logger import error_logger, execution_trace_logger
from moview.domain.entity.input_data.coverletter_document import CoverLetter
from moview.domain.entity.input_data.initial_input_data_document import InitialInputData
from moview.domain.entity.question_answer.question import Question
from moview.modules.input.input_analyzer import InputAnalyzer
from moview.modules.input.initial_question_giver import InitialQuestionGiver, InitialQuestionParseError
from moview.repository.input_data.input_data_repository import InputDataRepository
from moview.repository.question_answer.question_answer_repository import QuestionAnswerRepository
from moview.utils.singleton_meta_class import SingletonMeta


class InputDataService(metaclass=SingletonMeta):

    def __init__(
            self,
            input_data_repository: InputDataRepository,
            question_answer_repository: QuestionAnswerRepository,
            initial_input_analyzer: InputAnalyzer,
            initial_question_giver: InitialQuestionGiver
    ):
        self.INIT_QUESTION_NUMBER = 6  # 총 몇개의 초기질문을 생성할지 정합니다.
        self.input_data_repository = input_data_repository
        self.question_answer_repository = question_answer_repository

        self.initial_input_analyzer = initial_input_analyzer
        self.initial_question_giver = initial_question_giver

    async def ask_initial_question_to_interviewee(
            self,
            interviewee_name: str,
            company_name: str,
            job_group: str,
            recruit_announcement: str,
            cover_letter_questions: List[str],
            cover_letter_answers: List[str]
    ) -> Dict[str, Any]:
        """
        Args:
            interviewee_name: 인터뷰 대상자 이름
            company_name: 인터뷰 대상자 회사 이름
            job_group: 인터뷰 대상자 직군
            recruit_announcement: 인터뷰 대상자 공고
            cover_letter_questions: 인터뷰 대상자 자소서 문항 리스트
            cover_letter_answers: 인터뷰 대상자 자소서 답변 리스트

        Returns: {
            "input_data_document": input_data_document_id,
            "question_document_list": [(question_document_id, question_content), ...)]
        }
        """
        # 사용자 입력 정보 분석
        task1 = asyncio.create_task(self.__analyze_initial_inputs_of_interviewee(
            job_group=job_group,
            recruit_announcement=recruit_announcement,
            cover_letter_questions=cover_letter_questions,
            cover_letter_answers=cover_letter_answers
        ))
        # 초기 질문 생성
        task2 = asyncio.create_task(self.__create_initial_question_list(
            job_group=job_group,
            recruit_announcement=recruit_announcement,
            cover_letter_questions=cover_letter_questions,
            cover_letter_answers=cover_letter_answers
        ))
        # 비동기로 병렬처리함
        analyzed_initial_inputs_of_interviewee, initial_question_list = await asyncio.gather(task1, task2)

        # Initial Input Data Entity Model 생성
        initial_input_data_model, cover_letter_model_list = self.__create_interviewee_data_entity(
            interviewee_name=interviewee_name,
            company_name=company_name,
            job_group=job_group, recruit_announcement=recruit_announcement,
            cover_letter_questions=cover_letter_questions,
            cover_letter_answers=cover_letter_answers,
            analyzed_initial_inputs_of_interviewee=analyzed_initial_inputs_of_interviewee
        )

        # Initial Input Data Document 저장
        initial_input_document = self.input_data_repository.save(
            initial_input_data=initial_input_data_model,
            cover_letter_list=cover_letter_model_list
        )

        # Initial Question Entity Model 생성 및 Document 저장
        question_document_id_list = []

        for question_content in initial_question_list:
            question_model = self.__create_question_entity(question_content=question_content)
            question_document = self.question_answer_repository.save_question(question_model)
            question_document_id_list.append(question_document.inserted_id)
        execution_trace_logger("Save Initial Question Document", initial_question_list=initial_question_list)

        return {
            "input_data_document": initial_input_document.inserted_id,
            "question_document_list": list(zip(question_document_id_list, initial_question_list))
        }

    async def __analyze_initial_inputs_of_interviewee(
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

        # 자소서 개수만큼 분석 시작.
        tasks = []
        for i in range(analysis_count):
            tasks.append(asyncio.create_task(self.initial_input_analyzer.analyze_initial_input(
                job_group=job_group,
                recruitment_announcement=recruit_announcement,
                cover_letter_question=cover_letter_questions[i],
                cover_letter_answer=cover_letter_answers[i]
            )))
        analysis_list = await asyncio.gather(*tasks)

        execution_trace_logger(
            "Analyzed Input Data",
            analyzed_initial_inputs_of_interviewee=analysis_list
        )

        return analysis_list

    async def __create_initial_question_list(
            self,
            job_group: str,
            recruit_announcement: str,
            cover_letter_questions: List[str],
            cover_letter_answers: List[str]
    ) -> List[str]:
        """
        Args:
            job_group: 타겟 직군
            recruit_announcement: 모집공고
            cover_letter_questions: 자기소개서 문항 리스트
            cover_letter_answers: 자기소개서 답변 리스트
        """
        # 초기질문 생성
        initial_question_list = []  # List[str]

        try:
            # 직군 정보만 가지고 초기질문 생성.
            created_questions = await self.initial_question_giver.give_initial_questions(
                job_group=job_group,
                question_count=self.INIT_QUESTION_NUMBER // 2
            )
            initial_question_list.extend(created_questions)

            execution_trace_logger("Initial Question By Job", created_questions=created_questions)

        except InitialQuestionParseError:  # 파싱에 실패한 경우
            error_logger("Initial Question Parse Error")

        try:
            # coverletter를 하나의 스트링으로 합침.
            coverletter = ""
            for question, answer in zip(cover_letter_questions, cover_letter_answers):
                coverletter += f"Q. {question}\nA. {answer}\n\n"

            # 자기소개서와 모집공고를 기반으로 초기질문 생성.
            created_questions = await self.initial_question_giver.give_initial_questions_by_input_data(
                recruit_announcement=recruit_announcement,
                coverletter=coverletter,
                question_count=self.INIT_QUESTION_NUMBER // 2,
                exclusion_list=initial_question_list  # 이미 생성된 질문은 제외
            )
            initial_question_list.extend(created_questions)

            execution_trace_logger("Initial Question By Recruit & Coverletter", created_questions=created_questions)

        except InitialQuestionParseError:  # 파싱에 실패한 경우
            error_logger("InitialQuestionParseError")

        execution_trace_logger("End Initial Question Creation", initial_question_list=initial_question_list)
        return initial_question_list

    @staticmethod
    def __create_interviewee_data_entity(
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

    @staticmethod
    def __create_question_entity(question_content: str) -> Question:
        question_model = Question(
            content=question_content,
            feedback_score=0,
        )
        return question_model
