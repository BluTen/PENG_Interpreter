from webbrowser import get
from core.errors import DivisionByZeroError, IdentifierError, InvalidOperationError, Error
from core.tokens import TOK_DIV, TOK_MINUS, TOK_MUL, TOK_PLUS

class Number:
    def __init__(self, value) -> None:
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    def set_pos(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context):
        self.context = context
        return self

    def copy(self):
        return Number(self.value)

    def add(self, num):
        if not isinstance(num, Number):
            return InvalidOperationError(f"Cant add Num with {type(num).__name__}!", self.pos_start, num.pos_end)
        return Number(self.value + num.value)

    def sub(self, num):
        if not isinstance(num, Number):
            return InvalidOperationError(f"Cant add Num with {type(num).__name__}!", self.pos_start, num.pos_end)
        return Number(self.value - num.value)

    def mul(self, num):
        if isinstance(num, String):
            return String(num.value * self.value)
        if not isinstance(num, Number):
            return InvalidOperationError(f"Cant add Num with {type(num).__name__}!", self.pos_start, num.pos_end)
        return Number(self.value * num.value)

    def div(self, num):
        if num.value == 0:
            return DivisionByZeroError("Bruh...", self.token.pos_start, num.token.pos_end)
        return Number(self.value / num.value)


class String:
    def __init__(self, value) -> None:
        self.value = value

    def __str__(self) -> str:
        return self.value

    def set_pos(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context):
        self.context = context
        return self

    def copy(self):
        return String(self.value)

    def add(self, string):
        if not isinstance(string, String):
            return InvalidOperationError(f"Cant concatenate String with {type(string).__name__}!", self.pos_start, string.pos_end)
        return String(self.value + string.value)

    def sub(self, node):
        return InvalidOperationError("'-' is not supported for type String", self.pos_start, node.pos_end)

    def mul(self, num):
        if not isinstance(num, Number):
            return InvalidOperationError(f"Cant multiply String with {type(num).__name__}", self.pos_start, num.pos_end)
        return String(self.value * num.value)

    def div(self, node):
        return InvalidOperationError("'/' is not supported for type String", self.pos_start, node.pos_end)





class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = None


class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.parent = None

    def get(self, name):
        value, _ = self._get(name)
        return value

    def _get(self, name):
        value = self.symbols.get(name, None)
        if value == None and self.parent:
            return self.parent.get(name)
        return value, self

    def set(self, name, value):
        return_val, table = self._get(name)
        if return_val:
            table.symbols[name] = value
        else:
            self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]


class RTResult:
    def __init__(self) -> None:
        self.error = None
        self.value = None

    def register(self, res):
        if hasattr(res, "value"):
            return res.value
        return res

    def success(self, node):
        self.value = node
        return self

    def failure(self, error):
        self.error = error
        return self

class Interpreter:

    def interpret(self, ast, context):
        res = RTResult()
        res.register(self.visit(ast, context, res))
        if res.error:
            print(res.error)
            exit(1)

    def visit(self, node, context, res):
        def visit_error(): raise RuntimeError(f"Visit Method Not Available for node {type(node).__name__}")
        func = getattr(self, f"visit_{type(node).__name__}", visit_error)
        return func(node, context, res)

    def visit_NumberNode(self, node, context, res):
        return res.success(
            Number(node.num).set_pos(node.pos_start, node.pos_end).set_context(context)
        )

    def visit_StringNode(self, node, context, res):
        return res.success(
            String(node.str_val).set_pos(node.pos_start, node.pos_end).set_context(context)
        )

    def visit_BinOpNode(self, node, context, res):
        left = res.register(self.visit(node.left, context, res))
        if res.error: return res
        right = res.register(self.visit(node.right, context, res))
        if res.error: return res

        if node.op.type == TOK_PLUS:
            val = left.add(right)
        elif node.op.type == TOK_MINUS:
            val = left.sub(right)
        elif node.op.type == TOK_MUL:
            val = left.mul(right)
        elif node.op.type == TOK_DIV:
            val = left.div(right)

        if isinstance(val, Error):
            return res.failure(val)
        return res.success(val.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node, context, res):
        number = res.register(self.visit(node.node, context, res))
        if res.error: return res

        if (node.op.type == TOK_MINUS and number.value < 0) \
            or (node.op.type == TOK_PLUS and number.value > 0):
            val = number.mul(Number(-1))

        if isinstance(val, Error):
            return res.failure(val)
        return res.success(val.set_pos(node.pos_start, node.pos_end))

    def visit_VarAsgnNode(self, node, context, res):
        name = node.name
        value = res.register(self.visit(node.node, context, res))
        if res.error: return res

        context.symbol_table.set(name, value)
        return res.success(value)

    def visit_VarGetNode(self, node, context, res):
        name = node.name
        value = context.symbol_table.get(name)

        if not value:
            return res.failure(IdentifierError(
                f"Identifier {name} not defined!",
                node.name_token.pos_start,
                node.name_token.pos_end,
                context
            ))

        value = value.copy().set_pos(node.pos_start, node.pos_end)
        return res.success(value)

    def visit_PrintNode(self, print_node, context, res):
        for i, node in enumerate(print_node.nodes):
            value = res.register(self.visit(node, context, res))
            if res.error: return res
            print(value, end="\n" if i == len(print_node.nodes) - 1 else " ")

    def visit_ExpressionNode(self, expression, context, res):
        for statement in expression.statements:
            res.register(self.visit(statement, context, res))
            if res.error: return res
