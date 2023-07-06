import util
from data_manager import *
from core.init_question_generator import init_question_generator
from core.input_info_analyzer import input_info_analyzer
from core.question_prompter import question_prompter
from core.answer_analyzer import answer_analyzer
from core.follow_up_question_generator import follow_up_question_generator


def input_process(manager: DataManager):
    # input.json에서 데이터를 가져옵니다.
    input_data = util.input_user_info()
    if input_data is False:
        return False
    manager.set_data(input_data)


if __name__ == "__main__":
    # 전역으로 관리하기 위해 생성된 Manager
    key_manager = KeyManager()
    data_manager = DataManager()
    evaluation_manager = EvaluationManager()

    # input_process에서 사용자의 데이터(input.json)를 읽어서, DataManager에 저장함.
    input_process(data_manager)

    # Input으로 받은 회사모집공고와 자소서, 1분 자기소개를 바탕으로 평가를 생성합니다.
    input_info_analyzer(data_manager, evaluation_manager)

    # init_question_generator 함수에서 초기질문을 생성합니다.
    question_list = init_question_generator(data_manager)
    # 생성된 질문리스트를 QuestionManager에 저장합니다.
    question_manager = QuestionManager(question_list)

    quit_flag = False
    for _ in range(6):
        if quit_flag is True:
            break

        # 생성된 question_list에서 질문을 1개씩 가져와서, 질문을 던집니다.
        next_question = question_manager.get_question()

        # 질문을 entity에 넣고, question_prompter 함수를 실행합니다.
        question_entity = QuestionEntity(next_question)
        quit_flag = question_prompter(question_entity)

        # answer_analyzer 함수는 인자로 받은 질문을 던지고, 답변 내용을 평가합니다.
        answer_analyzer(
            data_manager,
            question_entity,
            evaluation_manager
        )

        for _ in range(3):
            if quit_flag is True:
                break
            # answer_analyzer 함수의 결과가 나왔다면, 심화질문 생성함수를 실행합니다.
            # 생성결과 심화질문이 필요없다고 판단되면 "Very nice good!"을 return 합니다.
            followup_question = follow_up_question_generator(
                data_manager,
                evaluation_manager
            )
            # followup_question 안에 "very", "nice", "good"이 포함되어있다면, 반복문을 종료합니다.
            exit_flag = 0
            for word in ["very", "nice", "good"]:
                if word in followup_question.lower():
                    exit_flag += 1

            if exit_flag >= 2:
                break

            # 심화질문이 생성되었다면, 다시 question_prompter 함수로 질문을 던집니다.
            followup_entity = QuestionEntity(followup_question)
            quit_flag = question_prompter(followup_entity)

            # 심화질문에 대한 평가가 EvaluationManager에 저장되어서 다음 반복문에서 이 결과를
            # 이용해서 심화질문을 또 생성하게 됩니다. 일단, 최대 3회 반복합니다.
            answer_analyzer(
                data_manager,
                followup_entity,
                evaluation_manager
            )

    print("최종 평가 결과입니다.")
    from pprint import pprint
    pprint(evaluation_manager.get_all_evaluation())
