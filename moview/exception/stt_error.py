class AudioTooShortError(Exception):
    def __init__(self):
        super().__init__("답변의 길이가 너무 짧습니다.\n1초 이상 대답해주세요!")


class AudioTooQuietError(Exception):
    def __init__(self):
        super().__init__("음성의 데시벨이 너무 작습니다.\n더 크게 대답해주세요!")
