from core.errors import Error
from core.interpreter import Interpreter, Context, SymbolTable
from core.lexer import Lexer
from core.parser import Parser

__version__ = "0.1.0"

def compile_and_run(code_source, file_name):
    lexer = Lexer(code_source, file_name)
    tokens = lexer.lex()
    if isinstance(tokens, Error):
        print(tokens)
        return

    parser = Parser(tokens)
    ast = parser.parse()
    if isinstance(ast, Error):
        print(ast)
        return

    context = Context("<main>")
    context.symbol_table = SymbolTable()
    interpreter = Interpreter()
    interpreter.interpret(ast, context)

def get_help():
    print("Text version of help coming soon for now please go to https://bluten.tk/project/peng/wiki")

if __name__ == "__main__":

    import argparse
    import os

    arg_parser = argparse.ArgumentParser(
        description="A Interpreter for the language PENG(Programming ENGlish) by BluTen",
        usage="peng.py [options] [file | -]",
        epilog="For more information, visit https://bluten.tk/project/peng/wiki"
    )

    arg_parser.add_argument("--version", action="version", version=f"%(prog)s v{__version__}")
    arg_parser.add_argument("file", nargs="?", default="-", help="The file to run. Defaults to stdin.")

    args = arg_parser.parse_args()

    if args.file == "-":
        print(f"PENG v{__version__}\n\nREPL Coming Soon!\n\n")
        # while True:
        #     try:
        #         code_source = input(">>> ")
        #         if code_source == "":
        #             continue
        #         elif code_source == "exit":
        #             break
        #         elif code_source == "help":
        #             get_help()
        #         else: 
        #             compile_and_run(code_source)
        #     except EOFError:
        #         break
        #     except KeyboardInterrupt:
        #         print("\nKeyboardInterrupt")
    else:
        source = None

        try:
            with open(args.file, "r") as f:
                source = f.read()
            if source != "":
                compile_and_run(source, args.file)
        except FileNotFoundError:
            print(f"{arg_parser.prog}: can't open file '{os.path.abspath(args.file)}': [Errno 2] No such file or directory")
