import re
from moview.utils.singleton_meta_class import SingletonMeta
from typing import Optional


class PromptParser(metaclass=SingletonMeta):

    @staticmethod
    def parse_question(question: str) -> Optional[str]:
        colon_pattern = ":"

        if re.search(colon_pattern, question):  # 문자열에 : 이 있다면,
            pattern = ":(.*?)(?=#)"  # : 뒤에 #이 나오기 전까지의 문자열을 추출
            match = re.search(pattern, question)

            if match:
                return match.group(1).strip()
            else:
                return None
        else:
            pattern = r"\d+\.(.*?)(?=#)"  # 숫자. 뒤에 #이 나오기 전까지의 문자열을 추출
            match = re.search(pattern, question)
            if match:
                return match.group(1).strip()
            else:
                return None
