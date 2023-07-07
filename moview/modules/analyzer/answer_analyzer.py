from langchain import LLMChain, ConversationChain
from langchain.chains.router import MultiPromptChain
from langchain.chains.router.llm_router import (
    RouterOutputParser,
    LLMRouterChain,
)
from langchain.chains.router.multi_prompt_prompt import (
    MULTI_PROMPT_ROUTER_TEMPLATE,
)
from langchain.prompts import PromptTemplate
from moview.utils.data_manager import *
from moview.utils.util import remove_indent
from typing import *


class AnswerAnalyzer:

    def __init__(self,
                 data_manager: DataManager,
                 question_entity: QuestionEntity,
                 evaluation_manager: EvaluationManager
                 ):
        """
        Args:
            data_manager:
            question_entity:    질문과 답변을 가지고 있는 객체
            evaluation_manager:     평가를 저장하는 객체
        """
        self.data_manager = data_manager
        self.question = question_entity.question
        self.answer = question_entity.answer
        self.evaluation_manager = evaluation_manager

    def analyze_answer(self, chat_manager: ChatManager) -> str:
        """
        Args:
            chat_manager: OpenAI 모델 객체

        Returns:
            면접관 질문, 면접자 답변, 면접관 평가

        """
        chat_model = chat_manager.get_chat_model()

        prompt_info_array = self._make_specific_prompt_with_knowledge()
        router_chain = self.__make_router_chain(llm=chat_model, prompt_info_array=prompt_info_array)
        default_chain = ConversationChain(llm=chat_model, output_key="text")
        destination_chains = self.__make_destination_chains(llm=chat_model, prompt_info_array=prompt_info_array)

        chain = MultiPromptChain(
            router_chain=router_chain,
            destination_chains=destination_chains,
            default_chain=default_chain,
        )

        evaluation = chain.run(self.answer)

        result = remove_indent(
            f"""
            면접관 질문:
            {self.question}

            면접자 답변:
            {self.answer}

            면접관 평가:
            {evaluation}
            """
        )

        self.evaluation_manager.add_answer_evaluation(result)

        return result

    # protected method (for test)
    def _make_specific_prompt_with_knowledge(
            self,
    ) -> List[Dict]:
        """

        Returns: 프롬프트가 저장된 딕셔너리 배열

        """
        fit_feature_dict = {
            "job_fit": ("직무 적합성", "직무를 수행하는 데 필요한 기술,지식, 그리고 경험을 가지고 있는지 평가하는 것"),
            "cultural_fit": ("문화 적합성", "조직의 가치와 문화에 잘 맞는지 평가하는 것"),
            "project_management": ("프로젝트 관리 능력", "특정 프로젝트를 기획하고, 이를 성공적으로 실행하고, 필요한 변경 사항을 관리하는지 평가하는 것"),
            "communication": ("의사소통 능력", "자신의 아이디어를 명확하게 전달하고, 다른 사람들과 효과적으로 협업할 수 있는지 평가하는 것"),
            "personality": ("인성 및 태도", "성격, 성실성, 성장 마인드셋을 평가하는 것"),
            "motivation": ("열정 및 지원동기", "왜 그 직무를 선택하고, 그 회사에서 일하길 원하는지 평가하는 것"),
            "adaptability": ("적응력", "새로운 환경이나 상황에 얼마나 빠르게 적응하는지를 평가하는 것"),
            "learning_ability": ("학습 능력", "지식이나 기술을 빠르게 습득하고 새로운 정보를 효과적으로 사용하는 지 평가하는 것"),
            "leadership": ("리더십", "팀에서 리더로서 역할을 수행한 경험이나 리더십에 대한 지식을 평가하는 것")
        }

        knowledge_prompt = self.__make_knowledge_prompt()

        # 분석 체인은 라우팅 체인이므로 라우터 적용.
        prompt_info_array = []

        for fit_feature in fit_feature_dict:
            prompt_info = {
                "name": fit_feature,
                "description": knowledge_prompt.format(
                    review_standard_knowledge=fit_feature_dict[fit_feature][0],
                    review_standard_detail=fit_feature_dict[fit_feature][1],
                ),
                "prompt_template": self.__make_prompt_for_router_chain(),
            }
            prompt_info_array.append(prompt_info)
        return prompt_info_array

    def __make_knowledge_prompt(self) -> str:
        return remove_indent(
            """
            {review_standard_detail}을 {review_standard_knowledge}이라 합니다.
            면접관인 당신은 {review_standard_knowledge}의 관점에서 면접자의 답변을 평가해야 합니다.
            """
        )

    def __make_prompt_for_router_chain(self) -> str:
        return remove_indent(
            f"""
            You are an interviewer.
            As an interviewer, please analyze the interviewee's response and provide evaluations by dividing them into positive aspects and areas for improvement. When mentioning areas for improvement, please focus only on the truly disappointing aspects. Please follow the format below:

            ```
            '좋은점':
            - Positive aspect content

            '아쉬운점':
            - Areas for improvement content
            ```
            Furthermore, the following content includes company information and the applicant's self-introduction.
            {self.data_manager.get_userdata()}

            The question and the candidate's response are as follows:
            ```
            Interviewer`s Question:
            {self.question}
            Interviewee`s Answer:""" +
            remove_indent("""{input}```

            Please write in Korean.
            """)
        )

    def __make_router_chain(self, llm: ChatOpenAI, prompt_info_array: List[Dict]) -> LLMRouterChain:
        """

        Args:
            prompt_info_array: 프롬프트가 저장된 딕셔너리 배열

        Returns:

        """
        destinations = [f"{p['name']}: {p['description']}" for p in prompt_info_array]
        destinations_str = "\n".join(destinations)

        router_template = MULTI_PROMPT_ROUTER_TEMPLATE.format(
            destinations=destinations_str)

        router_prompt = PromptTemplate(
            template=router_template,
            input_variables=["input"],
            output_parser=RouterOutputParser(),
        )

        return LLMRouterChain.from_llm(llm, router_prompt)

    def __make_destination_chains(self, llm: ChatOpenAI, prompt_info_array: List[Dict]) -> Dict[str, LLMChain]:
        """

        Args:
            llm:
            prompt_info_array: 프롬프트가 저장된 딕셔너리 배열

        Returns:

        """
        destination_chains = {}

        for p_info in prompt_info_array:
            name = p_info["name"]
            prompt_template = p_info["prompt_template"]
            prompt = PromptTemplate(template=prompt_template,
                                    input_variables=["input"])
            destination_chains[name] = LLMChain(llm=llm, prompt=prompt)

        return destination_chains
