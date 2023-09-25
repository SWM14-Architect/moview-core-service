class RetryExecutionError(Exception):

    def __init__(self, message="RETRY EXECUTION ERROR"):
        self.message = message
        super().__init__(self.message)
