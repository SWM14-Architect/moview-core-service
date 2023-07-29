from langchain import LLMChain
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate
)
from moview.modules.prompt_loader.prompt_loader import PromptLoader
from moview.utils.llm_interface import LLMModelFactory


class FollowUpQuestionGiver:

    def __init__(self):
        prompt_loader = PromptLoader()
        self.prompt = prompt_loader.load_prompt_json(FollowUpQuestionGiver.__name__)

    def give_followup_question(self, job_group: str, question: str, answer: str, previous_questions: str,
                               categories_ordered_pair: str) -> str:
        """
        꼬리질문을 출제하는 메서드

        Args:
            job_group: 직군
            question: 현재 질문
            answer: 현재 질문에 대한 답변
            previous_questions: 이전 질문들
            categories_ordered_pair: 대분류, 중분류 순서쌍

        Returns:

        """
        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    self.prompt.format(job_group=job_group, categories_ordered_pair=categories_ordered_pair,
                                       previous_question=previous_questions)
                ),
                HumanMessagePromptTemplate.from_template(
                    """
                    interview question: {question}

                    candidate's answer : {answer}    
                    """)
            ],
            input_variables=["question", "answer"],
        )

        llm = LLMModelFactory.create_chat_open_ai(temperature=0.7)

        chain = LLMChain(llm=llm, prompt=prompt)

        return chain.run({"question": question, "answer": answer})
