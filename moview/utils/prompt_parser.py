import re
from moview.utils.singleton_meta_class import SingletonMeta
from typing import Optional, List


class PromptParser(metaclass=SingletonMeta):

    @staticmethod
    def parse_question(questions_string: str) -> Optional[List[str]]:
        results = []

        colon_pattern = ":"
        if re.search(colon_pattern, questions_string):  # 문자열에 : 이 있다면,
            pattern = re.compile(":(.*?)(?=#)")  # : 뒤에 #이 나오기 전까지의 문자열을 추출
            matches = pattern.findall(questions_string)
            for match in matches:
                results.append(match.strip())
        else:
            pattern = re.compile(r"\d+\.(.*?)(?=#)")  # 숫자. 뒤에 #이 나오기 전까지의 문자열을 추출
            matches = pattern.findall(questions_string)
            for match in matches:
                results.append(match.strip())

        return results if results else None
