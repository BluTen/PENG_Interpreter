from string import ascii_letters, digits
from .errors import InvalidCharError, InvalidSyntaxError, UnknownCharError
from .position_manager import Position
from .tokens import TokenTypes, Token


DIGITS = digits
LETTERS = ascii_letters + digits + "_"


class Lexer:
    def __init__(self, code: str, file_name):
        self.code = code
        self.pos = Position(0, 1, 1, file_name, code)
        self.cur_char = self.code[self.pos.idx]
        self.indent_length = 0
        self.indent_using_space = True

    def advance(self):
        self.pos.advance(self.cur_char)
        self.cur_char = (
            self.code[self.pos.idx] if self.pos.idx < len(self.code) else None
        )

    def lex(self):
        parsed_tokens: list[Token] = []

        while self.cur_char is not None:
            if self.cur_char.isdigit():
                token = self._parse_num()
                parsed_tokens.append(token)

            elif self.cur_char in LETTERS:
                parsed_tokens.append(self._parse_letters())

            elif self.cur_char in " \t":
                self.advance()

            # elif self.cur_char in "\t":
            #     parsed_tokens.append(Token(TokenTypes.TOK_TAB, self.cur_char, pos_start=self.pos.copy()))
            #     self.advance()

            # elif self.cur_char in " ":
            #     parsed_tokens.append(Token(TokenTypes.TOK_SPACE, self.cur_char, pos_start=self.pos.copy()))
            #     self.advance()

            elif self.cur_char == '"':
                token = self._parse_string()
                parsed_tokens.append(token)

            elif self.cur_char == "+":
                parsed_tokens.append(
                    Token(TokenTypes.TOK_PLUS, self.cur_char, pos_start=self.pos.copy())
                )
                self.advance()

            elif self.cur_char == "-":
                parsed_tokens.append(
                    Token(
                        TokenTypes.TOK_MINUS, self.cur_char, pos_start=self.pos.copy()
                    )
                )
                self.advance()

            elif self.cur_char == "*":
                parsed_tokens.append(
                    Token(TokenTypes.TOK_MUL, self.cur_char, pos_start=self.pos.copy())
                )
                self.advance()

            elif self.cur_char == "/":
                parsed_tokens.append(
                    Token(TokenTypes.TOK_DIV, self.cur_char, pos_start=self.pos.copy())
                )
                self.advance()

            elif self.cur_char == "(":
                parsed_tokens.append(
                    Token(
                        TokenTypes.TOK_LPAREN, self.cur_char, pos_start=self.pos.copy()
                    )
                )
                self.advance()

            elif self.cur_char == ")":
                parsed_tokens.append(
                    Token(
                        TokenTypes.TOK_RPAREN, self.cur_char, pos_start=self.pos.copy()
                    )
                )
                self.advance()

            elif self.cur_char == ",":
                parsed_tokens.append(
                    Token(
                        TokenTypes.TOK_COMMA, self.cur_char, pos_start=self.pos.copy()
                    )
                )
                self.advance()

            elif self.cur_char == ".":
                parsed_tokens.append(
                    Token(
                        TokenTypes.TOK_FULLSTOP,
                        self.cur_char,
                        pos_start=self.pos.copy(),
                    )
                )
                self.advance()

            elif self.cur_char == "\n":
                parsed_tokens.append(
                    Token(
                        TokenTypes.TOK_NEWLINE, self.cur_char, pos_start=self.pos.copy()
                    )
                )
                self.advance()
                while self.cur_char is not None and self.cur_char in " \t":
                    parsed_tokens.append(
                        Token(
                            TokenTypes.TOK_SPACE
                            if self.cur_char == " "
                            else TokenTypes.TOK_TAB,
                            self.cur_char,
                            pos_start=self.pos.copy(),
                        )
                    )
                    self.advance()
                # if self.indent_length == 0:
                #     match self.cur_char:
                #         case " ":
                #             self.indent_using_space = True
                #             while self.cur_char == " ":
                #                 self.indent_length += 1
                #                 self.advance()
                #             parsed_tokens.append(Token)
                #         case "\t":
                #             self.indent_using_space = False
                #             while self.cur_char == "\t":
                #                 self.indent_length += 1
                #                 self.advance()
                #         case _:
                #             pass
                # else:

            elif self.cur_char == ".":
                parsed_tokens.append(
                    Token(
                        TokenTypes.TOK_FULLSTOP,
                        self.cur_char,
                        pos_start=self.pos.copy(),
                    )
                )
                self.advance()

            elif self.cur_char == "#":
                while self.cur_char not in ["\n", None]:
                    self.advance()

            else:
                raise UnknownCharError(
                    f"Unknown character '{self.cur_char}'", self.pos.copy()
                )

        parsed_tokens.append(Token(TokenTypes.TOK_EOF, pos_start=self.pos.copy()))
        return parsed_tokens

    def _parse_num(self):
        pos_start = self.pos.copy()
        num_str = ""
        is_float = False
        while self.cur_char is not None and self.cur_char in DIGITS + ".":
            if self.cur_char == ".":
                if is_float:
                    return Token(
                        TokenTypes.TOK_FLOAT,
                        float(num_str),
                        pos_start=pos_start,
                        pos_end=self.pos.copy(),
                    )
                else:
                    next_char = (
                        self.code[self.pos.idx + 1]
                        if self.pos.idx + 1 < len(self.code)
                        else None
                    )
                    if next_char == "\n" or next_char is None:
                        return Token(
                            TokenTypes.TOK_INT,
                            int(num_str),
                            pos_start=pos_start,
                            pos_end=self.pos.copy(),
                        )
                    elif next_char in DIGITS:
                        is_float = True
                    else:
                        start = pos_start.copy().advance()
                        end = start.copy().advance()
                        raise InvalidSyntaxError(
                            f"Expected integer not '{next_char}'",
                            start,
                            end,
                        )
            num_str += self.cur_char
            self.advance()
        if "." in num_str:
            return Token(
                TokenTypes.TOK_FLOAT,
                float(num_str),
                pos_start=pos_start,
                pos_end=self.pos.copy(),
            )
        else:
            return Token(
                TokenTypes.TOK_INT,
                int(num_str),
                pos_start=pos_start,
                pos_end=self.pos.copy(),
            )

    def _parse_letters(self):
        pos_start = self.pos.copy()
        word = ""
        while self.cur_char is not None and self.cur_char in LETTERS:
            word += self.cur_char
            self.advance()
        if word in TokenTypes.KEYWORDS:
            return Token(
                TokenTypes.TOK_KEYWORD,
                word,
                pos_start=pos_start,
                pos_end=self.pos.copy(),
            )
        else:
            return Token(
                TokenTypes.TOK_IDENTIFIER,
                word,
                pos_start=pos_start,
                pos_end=self.pos.copy(),
            )

    def _parse_string(self):
        pos_start = self.pos.copy()
        parsed_string = ""
        self.advance()
        while self.cur_char != "\n" and self.cur_char is not None:
            if self.cur_char == '"':
                self.advance()
                return Token(
                    TokenTypes.TOK_STRING, parsed_string, pos_start, self.pos.copy()
                )
            elif self.cur_char == "\\":
                self.advance()
                if self.cur_char == "\\":
                    self.advance()
                    parsed_string += "\\"
                elif self.cur_char == "t":
                    self.advance()
                    parsed_string += "\t"
                elif self.cur_char == "n":
                    self.advance()
                    parsed_string += "\n"
                elif self.cur_char == "r":
                    self.advance()
                    parsed_string += "\r"
                elif self.cur_char == "v":
                    self.advance()
                    parsed_string += "\v"
                elif self.cur_char == "f":
                    self.advance()
                    parsed_string += "\f"
            else:
                parsed_string += self.cur_char
                self.advance()
        raise InvalidSyntaxError("Expected closing '\"'", pos_start, self.pos.copy())


# Fix ending string
# (.venv) PS E:\Nayan_Folder\PythonProjects\peng_compiler> python peng.py code.peng
# Traceback (most recent call last):
#   File "E:\Nayan_Folder\PythonProjects\peng_compiler\peng.py", line 72, in <module>
#     compile_and_run(source, args.file)
#   File "E:\Nayan_Folder\PythonProjects\peng_compiler\peng.py", line 16, in compile_and_run
#     ast = parser.parse()
#   File "E:\Nayan_Folder\PythonProjects\peng_compiler\core\parser.py", line 119, in parse
#     expression = self.expression()
#   File "E:\Nayan_Folder\PythonProjects\peng_compiler\core\parser.py", line 146, in expression
#     statement = res.register(self.statement())
#   File "E:\Nayan_Folder\PythonProjects\peng_compiler\core\parser.py", line 201, in statement
#     node = res.register(self.math_op1())
#   File "E:\Nayan_Folder\PythonProjects\peng_compiler\core\parser.py", line 208, in math_op1
#     left = res.register(self.math_op2())
#   File "E:\Nayan_Folder\PythonProjects\peng_compiler\core\parser.py", line 227, in math_op2
#     left = res.register(self.factor())
#   File "E:\Nayan_Folder\PythonProjects\peng_compiler\core\parser.py", line 248, in factor
#     if self.cur_tok.type in (TOK_MINUS, TOK_PLUS):
# AttributeError: 'InvalidSyntaxError' object has no attribute 'type'
