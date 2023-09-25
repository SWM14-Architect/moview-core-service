class InitialQuestionParseError(Exception):

    def __init__(self, message="INITIAL QUESTION PARSE ERROR"):
        self.message = message
        super().__init__(self.message)
