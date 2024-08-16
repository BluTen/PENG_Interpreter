class PengError(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, name, msg, pos_start, pos_end=None):
        self.name = name
        self.msg = msg
        self.pos_start = pos_start
        self.pos_end = pos_end
        super().__init__()

    def __str__(self):
        error_string = (
            f"\n{self.name}: {self.msg}\n\nFrom {self.pos_start}\nto {self.pos_end}"
        )
        return error_string


class UnknownCharError(PengError):
    def __init__(self, msg, pos_start):
        super().__init__(
            "Unknown Charecter Error", msg, pos_start, pos_start.copy().advance()
        )


class InvalidCharError(PengError):
    def __init__(self, msg, pos_start):
        super().__init__(
            "Invalid Charecter Error", msg, pos_start, pos_start.copy().advance()
        )


class InvalidSyntaxError(PengError):
    def __init__(self, msg, pos_start, pos_end):
        super().__init__("Invalid Syntax Error", msg, pos_start, pos_end)


class InvalidOperationError(PengError):
    def __init__(self, msg, pos_start, pos_end):
        super().__init__("Invalid Operation Error", msg, pos_start, pos_end)


class DivisionByZeroError(PengError):
    def __init__(self, msg, pos_start, pos_end):
        super().__init__("Division By Zero Error", msg, pos_start, pos_end)


class IdentifierError(PengError):
    def __init__(self, msg, pos_start, pos_end, context):
        super().__init__("Identifier Error", msg, pos_start, pos_end)
        self.context = context


class EmptyFileError(PengError):
    """When file contains only comments, random index errors popup.
    To stop them we detect if the file is empty after lexical analysis in parser.py"""

    def __init__(self):
        super().__init__("some file", "which is empty", 0, 0)
