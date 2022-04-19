#############################
#          TOKENS           #
#############################

TOK_INT = "INT"
TOK_FLOAT = "FLOAT"
TOK_STRING = "STRING"

TOK_PLUS = "PLUS"
TOK_MINUS = "MIN"
TOK_MUL = "MUL"
TOK_DIV = "DIV"
TOK_POV = "POV"

TOK_LPAREN = "LPAREN"
TOK_RPAREN = "RPAREN"

TOK_COMMA = "COMMA"

TOK_KEYWORD = "KEYWORD"
TOK_IDENTIFIER = "IDENTIFIER"

TOK_NEWLINE = "NEWLINE"
TOK_EOF = "EOF"

KEYWORDS = [
    "say",
    "is"
]


class Token:
    
    def __init__(self, type:str, value=None, pos_start=None, pos_end=None):
        self.type = type
        self.value = value
        if pos_start is not None:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()
        if pos_end:
            self.pos_end = pos_end.copy()
    
    def __repr__(self):
        return f"{self.type}" if self.value is None else f"{self.type}:{self.value}"

    def match(self, type, value = None):
        return self.type == type and self.value == value
