class EvaluationParseError(Exception):

    def __init__(self, message="EVALUATION PARSE ERROR"):
        self.message = message
        super().__init__(self.message)
