import datetime
from langchain import LLMChain
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate
)

from moview.utils.data_manager import *
from moview.utils.util import remove_indent, follow_up_question_parser, write_log_in_txt


class FollowUpQuestionGenerator:
    def __init__(
            self,
            data_manager: DataManager,
            evaluation_manager: EvaluationManager
    ):
        self.data_manager = data_manager
        self.evaluation_manager = evaluation_manager

    def generate_follow_up_question(self) -> str:
        log = {"time": str(datetime.datetime.now()), "message": "Start of FollowUpQuestionGenerator"}
        write_log_in_txt(log, FollowUpQuestionGenerator.__name__)

        chat_manager = ChatManager()

        prompt = self.__make_follow_up_question_prompt()

        log = {"time": str(datetime.datetime.now()),
               "message": "FollowUpQuestionGenerator made a prompt. prompt is : " + str(prompt)}
        write_log_in_txt(log, FollowUpQuestionGenerator.__name__)

        followup_chain = LLMChain(llm=chat_manager.get_chat_model(),
                                  prompt=prompt)
        output = followup_chain(self.evaluation_manager.get_answer_evaluation())

        result = follow_up_question_parser(output['text'])
        log = {"time": str(datetime.datetime.now()),
               "message": "End of FollowUpQuestionGenerator. result is : " + result}
        write_log_in_txt(log, FollowUpQuestionGenerator.__name__)

        return result

    def __make_follow_up_question_prompt(self) -> ChatPromptTemplate:
        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    remove_indent(
                        f"""You are an interviewer at {self.data_manager.company}.

                            {self.data_manager.get_userdata()}
                            """)),

                HumanMessagePromptTemplate.from_template(
                    remove_indent(
                        """You are an interviewer. Please read the interview question and response. If you determine that a `Follow up Question` is necessary, write the additional question you would like to ask in the areas for improvement. If you determine that it is not necessary, write `Very nice good!`. Also, please follow the format below when creating the questions:

                        ```
                        '심화질문':
                        - Content of follow up question
                        ```
                        And below is the interviewee's response to the interviewer's question, including the interviewer's evaluation:
                        {evaluation}

                        REMEMBER! Please write in Korean.
                        REMEMBER! Please create only 1 question.
                        """))
            ],
            input_variables=["evaluation"],
        )
        return prompt
