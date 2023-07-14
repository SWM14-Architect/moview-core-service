import json
import os
from typing import *

INPUT_FILE_NAME = "input"


def write_log_in_txt(log: dict[str, str], class_name: str):
    # os.getcwd()는 현재 작업 디렉토리를 반환하는 함수입니다. 작업 디렉토리는 현재 실행 중인 프로그램이나 스크립트가 파일 시스템에서 작업을 수행하는 기준 디렉토리를 의미합니다.
    current_working_dir = os.getcwd()

    # os.environ.get('PYTHON_PROFILE')은 파이썬 프로파일을 가져오는 함수입니다. 테스트에는 test 프로파일을 지정해놨습니다.
    if os.environ.get('PYTHON_PROFILE') == 'test':
        log_dir = os.path.join(current_working_dir, 'logs')
        log_file_name = f'test_log-{class_name}.txt'
    else:
        log_dir = os.path.join(current_working_dir, 'logs')
        log_file_name = f'log-{class_name}.txt'

    # 기존 디렉토리가 없으면, 새로 만듭니다.
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, log_file_name)

    with open(log_file_path, "a") as outfile:
        json.dump(log, outfile)
        outfile.write("\n")


def input_user_info() -> Union[Dict, bool]:
    try:
        with open(f"{INPUT_FILE_NAME}.json", "r", encoding="UTF-8") as f:
            input_data = json.load(f)

    except FileNotFoundError:
        # input.json 파일이 없음.
        with open(f"{INPUT_FILE_NAME}.json", "w", encoding="UTF-8") as f:
            f.write(
                """{
                    "user_company" : "",
                    "user_job" : "",
                    "job_requirement" : "",
                    "cover_letter" : "",
                    "self_introduce" : ""
                }"""
            )
        print("input.json을 열고, 정보를 작성하세요.")
        return False

    return input_data


def create_question_parser(question: str) -> List:
    question_list = question.replace("\n\n", "\n").split("\n")

    for quest_idx in range(len(question_list)):
        temp_str = question_list[quest_idx]
        for str_idx in range(len(temp_str)):
            if temp_str[str_idx] == ".":
                question_list[quest_idx] = temp_str[str_idx + 1:].strip()
                break

    return question_list


def follow_up_question_parser(question: str) -> str:
    question.replace("\n", "")
    for str_idx in range(len(question)):
        if question[str_idx] == ":":
            return question[str_idx + 1:].strip()
    return question


def remove_indent(string: str) -> str:
    return string.replace("    ", "").replace("\t", "")
