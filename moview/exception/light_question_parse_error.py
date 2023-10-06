class LightQuestionParseError(Exception):

    def __init__(self, message="Light QUESTION PARSE ERROR"):
        self.message = message
        super().__init__(self.message)
