from mvp.data_manager import *


def question_prompter(
    question_entity: QuestionEntity,
):
    question = question_entity.question

    # TODO: 나중에 면접자의 답변을 프론트에서 받아와야함.
    print(f"면접관: {question}")
    answer = input("면접자:  ...질문에 답변하세요.\n")
    question_entity.add_answer(answer)

    if answer in ["exit", "c"]:
        return True
    return False
