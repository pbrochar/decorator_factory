class NoFunctionError(Exception):
    def __init__(self, decorator: callable) -> None:
        message = f"Need a Function class in decorator `{decorator}`"
        super().__init__(message)


class ConflictNameError(Exception):
    pass


class ArgumentValidationError(Exception):
    def __init__(self, message):
        super().__init__(message)