import datetime
from moview.utils.data_manager import *
from moview.utils.util import write_log_in_txt


class QuestionPrompter:
    """
    질문을 던지고, 답변을 받아서 QuestionEntity에 저장합니다.
    """

    def prompt_question(self, question_entity: QuestionEntity) -> bool:
        """
        Args:
            question_entity: 면접자가 받았던 질문(question_entity.question)과 면접자의 답변(question_entity.answer) 쌍을 담고 있는 객체

        Returns:
            True: 종료
            False: 계속 진행
        """

        question = question_entity.question

        log = {"time": str(datetime.datetime.now()), "message": "Start of QuestionPrompter. question is : " + question}
        write_log_in_txt(log, QuestionPrompter.__name__)

        # TODO: 나중에 면접자의 답변을 프론트에서 받아와야함.
        print(f"면접관: {question}")
        answer = input("면접자:  ...질문에 답변하세요.\n")
        question_entity.add_answer(answer)

        log = {"time": str(datetime.datetime.now()), "message": "End of QuestionPrompter. answer is : " + answer}
        write_log_in_txt(log, QuestionPrompter.__name__)

        # 입력이 "exit" 또는 "c"이면 종료 (True 반환)
        if answer in ["exit", "c"]:
            return True
        return False
