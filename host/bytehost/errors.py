class HostError(Exception):
    def __init__(self, code, message, **details):
        super().__init__(message)
        self.code = code
        self.details = details

    def record(self):
        return {"status": "FAIL", "error": self.code,
                "message": str(self), "details": self.details}


def require(condition, code, message, **details):
    if not condition:
        raise HostError(code, message, **details)
