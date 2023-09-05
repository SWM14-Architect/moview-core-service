from langchain import LLMChain
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate
)

from moview.utils.prompt_loader import PromptLoader
from moview.environment.llm_factory import LLMModelFactory
from moview.config.loggers.mongo_logger import prompt_result_logger
from moview.utils.singleton_meta_class import SingletonMeta


class FollowUpQuestionGiver(metaclass=SingletonMeta):

    def __init__(self, prompt_loader: PromptLoader):
        self.prompt = prompt_loader.load_prompt_json(FollowUpQuestionGiver.__name__)

    def give_followup_question(self, question: str, answer: str, previous_question: str,
                               category: str, sub_category: str) -> str:
        """
        꼬리질문을 출제하는 메서드

        Args:
            question: 현재 질문
            answer: 현재 질문에 대한 답변
            previous_question: 이전 질문들
            category: 대분류
            sub_category: 중분류

        Returns:
            출제할 꼬리 질문

        """
        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    self.prompt.format(category=category, sub_category=sub_category,
                                       previous_question=previous_question)
                ),
                HumanMessagePromptTemplate.from_template(
                    """
                    면접 질문: {question}

                    지원자의 답변: {answer}     
                    """)
            ],
            input_variables=["question", "answer"],
        )

        llm = LLMModelFactory.create_chat_open_ai(temperature=0.7)

        chain = LLMChain(llm=llm, prompt=prompt)

        prompt_result = chain.run({
            "question": question,
            "answer": answer
        })

        prompt_result_logger("followup question prompt result", prompt_result=prompt_result)

        return prompt_result
