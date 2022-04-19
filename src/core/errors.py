class Error:
    """Base class for exceptions in this module."""
    def __init__(self, name, msg, pos_start, pos_end = None):
        self.name = name
        self.msg = msg
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __str__(self):
        error_string = f"{self.name}: {self.msg}.\n{self.pos_start}\n{self.pos_end}"

        return error_string


class UnknownCharError(Error):
    def __init__(self, msg, pos_start):
        super().__init__("Unknown Charecter Error", msg, pos_start, pos_start.copy().advance())

class InvalidCharError(Error):
    def __init__(self, msg, pos_start):
        super().__init__("Invalid Charecter Error", msg, pos_start, pos_start.copy().advance())

class InvalidSyntaxError(Error):
    def __init__(self, msg, pos_start, pos_end):
        super().__init__("Invalid Syntax Error", msg, pos_start, pos_end)

class InvalidOperationError(Error):
    def __init__(self, msg, pos_start, pos_end):
        super().__init__("Invalid Operation Error", msg, pos_start, pos_end)

class DivisionByZeroError(Error):
    def __init__(self, msg, pos_start, pos_end):
        super().__init__("Division By Zero Error", msg, pos_start, pos_end)

class IdentifierError(Error):
    def __init__(self, msg, pos_start, pos_end, context):
        super().__init__(f"Identifier Error", msg, pos_start, pos_end)
        self.context = context
