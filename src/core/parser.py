from .errors import InvalidSyntaxError, EmptyFileError
from .tokens import Token, TokenTypes


class NumberNode:
    def __init__(self, token):
        self.tok = token
        self.num = token.value

        self.pos_start = token.pos_start
        self.pos_end = token.pos_end

    def __repr__(self):
        return f"{self.num}"


class StringNode:
    def __init__(self, token):
        self.tok = token
        self.str_val = token.value

        self.pos_start = token.pos_start
        self.pos_end = token.pos_end

    def __repr__(self):
        return f'"{self.str_val}"'


class BinOpNode:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

        self.pos_start = left.pos_start
        self.pos_end = right.pos_end

    def __repr__(self):
        return f"({self.left}, {self.op}, {self.right})"


class UnaryOpNode:
    def __init__(self, op, node):
        self.op = op
        self.node = node

        self.pos_start = op.pos_start
        self.pos_end = node.pos_end

    def __repr__(self):
        return f"({self.op}, {self.node})"


class VarAsgnNode:
    def __init__(self, name_token, node):
        self.name_token = name_token
        self.name = name_token.value
        self.node = node

        self.pos_start = name_token.pos_start
        self.pos_end = node.pos_end

    def __repr__(self):
        return f"(assign {self.name}, {self.node})\n"


class VarGetNode:
    def __init__(self, name_token):
        self.name_token = name_token
        self.name = name_token.value

        self.pos_start = name_token.pos_start
        self.pos_end = name_token.pos_end

    def __repr__(self):
        return f"(get {self.name_token})"


class PrintNode:
    def __init__(self, nodes):
        self.nodes = nodes

        self.pos_start = nodes[0].pos_start
        self.pos_end = nodes[-1].pos_end

    def __repr__(self):
        return f"(say {self.nodes})\n"


class ExpressionNode:
    def __init__(self, statements):
        self.statements = statements

        self.pos_start = statements[0].pos_start
        self.pos_end = statements[-1].pos_end

    def __repr__(self):
        return f"ExpressionNode\n{"".join([str(i) for i in self.statements])}"


class IfNode:
    def __init__(self, condition_node, expression_node):
        self.condition_node = condition_node
        self.expression_node = expression_node

    def __repr__(self) -> str:
        return f"if {self.condition_node}: {self.expression_node}"


class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_count = 0

    def register_advancement(self):
        self.advance_count += 1

    def register(self, res: "ParseResult"):
        self.advance_count += res.advance_count
        if res.error:
            self.error = res.error
        return res.node

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if not self.error or self.advance_count == 0:
            self.error = error
        return self


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.idx = 0
        self.cur_tok = self.tokens[self.idx]

    def advance(self):
        self.idx += 1
        if self.idx < len(self.tokens):
            self.cur_tok = self.tokens[self.idx]
        return self.cur_tok

    def parse(self):
        # return self.tokens
        expression = self.expression()
        if expression.error:
            raise expression.error
        return expression.node

    def expression(self):
        res = ParseResult()
        expressions = []

        while True:
            if self.cur_tok.type == TokenTypes.TOK_NEWLINE:
                res.register_advancement()
                self.advance()
                continue

            elif self.cur_tok.match(TokenTypes.TOK_KEYWORD, "say"):
                print_values = []
                res.register_advancement()
                self.advance()
                statement = res.register(self.statement())
                if res.error:
                    return res
                print_values.append(statement)

                while self.cur_tok.type == TokenTypes.TOK_COMMA:
                    res.register_advancement()
                    self.advance()
                    statement = res.register(self.statement())
                    if res.error:
                        return res
                    print_values.append(statement)

                if self.cur_tok.type != TokenTypes.TOK_FULLSTOP:
                    if self.cur_tok.type in [
                        TokenTypes.TOK_IDENTIFIER,
                        TokenTypes.TOK_INT,
                        TokenTypes.TOK_FLOAT,
                    ]:
                        raise InvalidSyntaxError(
                            f"Expected '-', '+', '*', '/' or ',' before '{self.cur_tok.value}'",
                            self.cur_tok.pos_start,
                            self.cur_tok.pos_end,
                        )
                    else:
                        return res.failure(
                            InvalidSyntaxError(
                                "Sentences end with full stop/period (.)",
                                self.cur_tok.pos_start,
                                self.cur_tok.pos_end,
                            )
                        )
                else:
                    res.register_advancement()
                    self.advance()

                if self.cur_tok.type == TokenTypes.TOK_NEWLINE:
                    res.register_advancement()
                    self.advance()
                    expressions.append(PrintNode(print_values))
                elif self.cur_tok.type == TokenTypes.TOK_EOF:
                    expressions.append(PrintNode(print_values))
                    return res.success(ExpressionNode(expressions))
                else:
                    return res.failure(
                        InvalidSyntaxError(
                            f"Unexpected '{self.cur_tok.value}'",
                            self.cur_tok.pos_start,
                            self.cur_tok.pos_end,
                        )
                    )
            elif self.cur_tok.match(TokenTypes.TOK_KEYWORD, "if"):
                """TODO: complete this function"""
                res.register_advancement()
                self.advance()
                continue
            elif self.cur_tok.type == TokenTypes.TOK_IDENTIFIER:
                name = self.cur_tok
                value = None
                res.register_advancement()
                self.advance()

                if self.cur_tok.match(TokenTypes.TOK_KEYWORD, "is"):
                    res.register_advancement()
                    self.advance()
                    value = res.register(self.statement())
                    if res.error:
                        return res
                else:
                    return res.failure(
                        InvalidSyntaxError(
                            "Expected 'is' after identifier",
                            self.cur_tok.pos_start,
                            self.cur_tok.pos_end,
                        )
                    )

                if self.cur_tok.type != TokenTypes.TOK_FULLSTOP:
                    if self.cur_tok.type in [
                        TokenTypes.TOK_IDENTIFIER,
                        TokenTypes.TOK_INT,
                        TokenTypes.TOK_FLOAT,
                    ]:
                        raise InvalidSyntaxError(
                            f"Expected '-', '+', '*' or '/' before '{self.cur_tok.value}'",
                            self.cur_tok.pos_start,
                            self.cur_tok.pos_end,
                        )
                    else:
                        return res.failure(
                            InvalidSyntaxError(
                                "Sentences end with full stop/period (.)",
                                self.cur_tok.pos_start,
                                self.cur_tok.pos_end,
                            )
                        )
                else:
                    res.register_advancement()
                    self.advance()

                if self.cur_tok.type == TokenTypes.TOK_NEWLINE:
                    res.register_advancement()
                    self.advance()
                    expressions.append(VarAsgnNode(name, value))
                elif self.cur_tok.type == TokenTypes.TOK_EOF:
                    expressions.append(VarAsgnNode(name, value))
                    return res.success(ExpressionNode(expressions))
                else:
                    return res.failure(
                        InvalidSyntaxError(
                            f"Unexpected '{self.cur_tok.value}'",
                            self.cur_tok.pos_start,
                            self.cur_tok.pos_end,
                        )
                    )
            elif self.cur_tok.type == TokenTypes.TOK_EOF:
                if not expressions:
                    raise EmptyFileError()
                return res.success(ExpressionNode(expressions))
            else:
                return res.failure(
                    InvalidSyntaxError(
                        f"Expected 'say', 'if', variable or assignment not '{self.cur_tok.value}'",
                        self.cur_tok.pos_start,
                        self.cur_tok.pos_end,
                    )
                )

    def statement(self):
        res = ParseResult()
        node = res.register(self.math_op1())
        if res.error:
            return res
        return res.success(node)

    def math_op1(self):
        res = ParseResult()

        left = res.register(self.math_op2())
        if res.error:
            return res

        while self.cur_tok.type in (TokenTypes.TOK_PLUS, TokenTypes.TOK_MINUS):
            op_tok = self.cur_tok
            res.register_advancement()
            self.advance()

            right = res.register(self.math_op2())
            if res.error:
                return res

            left = BinOpNode(left, op_tok, right)

        return res.success(left)

    def math_op2(self):
        res = ParseResult()

        left = res.register(self.factor())
        if res.error:
            return res

        while self.cur_tok.type in (TokenTypes.TOK_MUL, TokenTypes.TOK_DIV):
            op_tok = self.cur_tok
            res.register_advancement()
            self.advance()

            right = res.register(self.factor())
            if res.error:
                return res

            left = BinOpNode(left, op_tok, right)

        return res.success(left)

    def factor(self):
        res = ParseResult()

        if self.cur_tok.type in (TokenTypes.TOK_MINUS, TokenTypes.TOK_PLUS):
            res.register_advancement()
            self.advance()

            atom = res.register(self.atom())
            if res.error:
                return res

            return res.success(UnaryOpNode(self.cur_tok, atom))

        else:
            atom = res.register(self.atom())
            if res.error:
                return res
            return res.success(atom)

    def atom(self):
        res = ParseResult()

        if self.cur_tok.type == TokenTypes.TOK_LPAREN:
            res.register_advancement()
            self.advance()

            expr = res.register(self.math_op1())
            if res.error:
                return res

            if self.cur_tok.type == TokenTypes.TOK_RPAREN:
                res.register_advancement()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(
                    InvalidSyntaxError(
                        "Expected ')'", self.cur_tok.pos_start, self.cur_tok.pos_end
                    )
                )
        elif self.cur_tok.type in (TokenTypes.TOK_INT, TokenTypes.TOK_FLOAT):
            tok = self.cur_tok
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))
        elif self.cur_tok.type == TokenTypes.TOK_IDENTIFIER:
            tok = self.cur_tok
            res.register_advancement()
            self.advance()
            return res.success(VarGetNode(tok))
        elif self.cur_tok.type == TokenTypes.TOK_STRING:
            tok = self.cur_tok
            res.register_advancement()
            self.advance()
            return res.success(StringNode(tok))
        else:
            return res.failure(
                InvalidSyntaxError(
                    "Expected int, float, identifier or '('",
                    self.cur_tok.pos_start,
                    self.cur_tok.pos_end,
                )
            )
