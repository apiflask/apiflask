class ValidationError(Exception):
    def __init__(self, status_code, messages):
        self.status_code = status_code
        self.messages = messages
