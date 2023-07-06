import json
from typing import *

INPUT_FILE_NAME = "input"


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
                question_list[quest_idx] = temp_str[str_idx+1:].strip()
                break

    return question_list


def follow_up_question_parser(question: str) -> str:
    question.replace("\n", "")
    for str_idx in range(len(question)):
        if question[str_idx] == ":":
            return question[str_idx+1:].strip()
    return question


def remove_indent(string: str) -> str:
    return string.replace("    ", "").replace("\t", "")
