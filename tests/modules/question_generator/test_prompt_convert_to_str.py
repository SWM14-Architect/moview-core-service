import unittest
from moview.utils.data_manager import *
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate
)


# prompt template.dict가 str인지 테스트
class TestPromptTemplateConvertToString(unittest.TestCase):

    def setUp(self) -> None:
        self.company = 'test'
        self.user_data = 'test-data'
        os.environ['PYTHON_PROFILE'] = 'test'
        self.prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    remove_indent(
                        f"""You are an interviewer at {self.company}.

                                {self.user_data}
                                """)),

                HumanMessagePromptTemplate.from_template(
                    remove_indent(
                        """As an interviewer, you need to generate {question_count} interview questions based on the applicant's desired position, their cover letter. Additionally, consider the qualities and skills the company is looking for in candidates based on the job posting. Please follow the format below when creating the questions:

                        ```
                        1. Question content
                        2. Question content
                        3. Question content
                        ...
                        ```

                        Please write in Korean.
                        """))
            ],
            input_variables=["question_count"],
        )

    def test_prompt_dict_convert_string(self):
        with self.assertRaises(NotImplementedError):  # 특정 예외가 발생하는지 확인하고 예외를 잡아내는 데 사용됩니다.
            log_data = str(self.prompt.dict())

    def test_prompt_convert_string(self):
        log_data = str(self.prompt)

        self.assertEqual(type(log_data), str)
        print(log_data)