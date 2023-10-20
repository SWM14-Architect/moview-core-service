import asynctest

from moview.utils.prompt_loader import PromptLoader
from tests.common_code_for_test import is_not_none_string
from moview.modules.input.initial_question_giver import InitialQuestionGiver


class TestInitialQuestionGiver(asynctest.TestCase):

    def setUp(self) -> None:
        self.prompt_loader = PromptLoader()
        self.giver = InitialQuestionGiver(prompt_loader=self.prompt_loader)

    def test_load_prompt(self):
        self.assertTrue(is_not_none_string(self.giver.prompt["create_question"]))
        print(self.giver.prompt["create_question"].format(exclusion_question="", job_group="백엔드 개발자", question_count=2))

    async def test_give_initial_questions_by_input_data(self):
        recruit_announcement = ("삼성 청년 SW 아카데미\n8기 모집 Coming soon\n청년 SW인재 양성을 위한 SSAFY 8기 모집이 곧 시작됩니다.\n궁금한 SSAFY 8기 "
                                "모집! 미리 알려드립니다!\n\n8기 모집 안내\n지원 자격\n만 29세 이하(92.7.1이후 출생자), 미취업자,\n국내외 4년제 대학 졸업자 및 "
                                "졸업예정자(전공무관)\n\n교육 기간\n2022년 7월 ~ 2023년 6월(1년)\n\n교육 장소\n서울, 대전, 구미, 광주, "
                                "부울경(부산)\n\n교육생 지원 사항\n1. 실전형 SW교육 및 개인별 맞춤형 취업컨설팅 제공\n2. 교육지원금 월 100만원 지급\n3. 우수교육생 "
                                "국내외 연수 및 다양한 시상제도 실시\n4. 교육 중 삼성 SW 역량테스트 응시 기회 제공\n5. 매학기 교육 종료 후 Job Fair 운영\n6. "
                                "대전, 광주, 구미, 부울경 캠퍼스는 내일배움카드를 통한 훈련장려금 추가지급 가능\n\n모집 절차\n지원서 접수 SW 적성진단 Interview 입과 "
                                "및 교육\n\nSW적성진단\nSW적성진단은 지원서상 선택한 전공 기준으로 구분하여 실시\nSW전공 : 기초 코딩테스트\nSW비전공 : 수리/추리논리력 "
                                "및 Computational Thinking 진단\n\n모집 일정\nSSAFY 8기 모집은 5월 진행 예정이며, 자세한 사항은 4월 중 추가 "
                                "안내됩니다.\n\n알림받기\nKakaoTalk 플러스친구 '삼성청년SW아카데미'를 추가하시면,\n가장 빠르게 모집 및 SSAFY 소식을 받아볼 수 "
                                "있습니다.\n홈페이지 APPLY -> 알림받기 -> '알림받기 바로가기' 버튼 클릭!\n\n문의 02-3429-5100 ssafy@ssafy.com")

        cover_letter = "저는 소통할 수 있는 개발자가 되고 싶습니다.\n처음에는 게임을 만들어보고 싶어서 코딩을 배우기 시작했고, 저는 코드를 입력하여 제가 원하는 결과물을 도출한다는 그 자체에 매력을 느끼게 되었습니다. 이후로 디스코드 봇 개발, 필요한 정보를 편하게 가져오는 웹 크롤링, 간단한 웹페이지 제작 등을 만들어보고 사용자에게 배포하면서 개발자라는 직업을 진지하게 고민하게 되었습니다.\n\n저는 부족한 개발 역량을 키우고 싶습니다.\n지금껏 공부하면서 코딩을 하는 동안 다른 사람들과 협업을 해본 경험이 없었고, 사용자에게 배포하는 과정에서 전혀 생각하지 못한 공부 요소들이 많이 등장했었습니다. SSAFY의 교육과정은 제가 원하는 개발에 필요한 기반 지식과 기술 스택을 배울 수 있고, 같은 목표를 가진 동료들과 함께 프로젝트 경험을 쌓아올릴 수 있는 기회라고 생각합니다. 그리고 저는 SSAFY라는 기회를 통해, 개발 역량을 갖추고 성장하여 소통이 가능한 개발자로 거듭나고 싶습니다."

        question_count = 3

        initial_questions = await self.giver.give_initial_questions_by_input_data(
            recruit_announcement=recruit_announcement,
            cover_letter=cover_letter,
            question_count=question_count
        )
        print(initial_questions)
        self.assertTrue(len(initial_questions) == question_count)

    async def test_give_initial_questions(self):
        job_group = "백엔드 개발자"
        question_count = 3

        initial_questions = await self.giver.give_initial_questions(job_group=job_group,
                                                                    question_count=question_count)
        print(initial_questions)
        self.assertTrue(len(initial_questions) == question_count)

    async def test_give_initial_questions_with_exclusion_list(self):
        job_group = "백엔드 개발자"
        question_count = 3
        exclusion_list = [
            "백엔드 개발자로서 가장 자신 있는 기술 영역은 무엇인가요?",
            "이전에 개발한 백엔드 시스템에서 겪은 가장 큰 어려움은 무엇이었나요?"
        ]

        initial_questions = await self.giver.give_initial_questions(job_group=job_group,
                                                                    question_count=question_count,
                                                                    exclusion_list=exclusion_list)
        print(initial_questions)
        self.assertTrue(len(initial_questions) == question_count)
