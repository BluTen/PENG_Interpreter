from sys import exit as sys_exit
from core.errors import EmptyFileError, PengError
from core.interpreter import Interpreter, Context, SymbolTable
from core.lexer import Lexer
from core.parser import Parser

__version__ = "0.1.0"


def compile_and_run(code_source, file_name, context=None, verbose=False):
    lexer = Lexer(code_source, file_name)
    tokens = lexer.lex()
    if verbose:
        print("Tokens *******************************************")
        print("".join([str(token) for token in tokens]), "\n")

    parser = Parser(tokens)
    ast = parser.parse()
    if verbose:
        print("Parsed code **************************************")
        print(ast, end="**************************************************\n")

    if context is None:
        context = Context("<main>")
        context.symbol_table = SymbolTable()
    interpreter = Interpreter()
    interpreter.interpret(ast, context)


def get_help():
    print(
        "Text version of help coming soon for now please go to https://bluten.github.io/project/peng/wiki"
    )


def main():
    import argparse
    import os

    arg_parser = argparse.ArgumentParser(
        description="A Interpreter for the language PENG(Programming ENGlish) by BluTen",
        usage="peng.py [options] [file | -]",
        epilog="For more information, visit https://bluten.github.io/project/peng/wiki",
    )

    arg_parser.add_argument(
        "--version",
        "-V",
        action="version",
        version=f"PENG - Programming ENGlish v{__version__}",
    )
    arg_parser.add_argument(
        "-v",
        action="store_true",
        help="Setting this flag will enable verbose output (Cannot be used in REPL)",
    )
    arg_parser.add_argument(
        "file",
        nargs="?",
        default="-",
        type=argparse.FileType("r"),
        help="The file to run. run without this argument to start REPL.",
    )

    args = arg_parser.parse_args()

    if args.file.name == "<stdin>":
        # print(f"PENG v{__version__}\n\nREPL Coming Soon!\n\n")
        print(f"PENG v{__version__}")
        context = Context("<main>")
        context.symbol_table = SymbolTable()
        while True:
            try:
                code_source = input(">>> ")
                if code_source == "":
                    continue
                elif code_source == "exit":
                    break
                elif code_source == "help":
                    get_help()
                else:
                    compile_and_run(code_source, "<stdin>", context)
            except EOFError:
                break
            except KeyboardInterrupt:
                print("\nKeyboardInterrupt")
            except Exception as err:
                if isinstance(err, PengError):
                    print(err)
                else:
                    raise

    else:
        source = None

        try:
            # print(args.file.name)
            with args.file as f:
                source = f.read()
            if source != "":
                compile_and_run(source, args.file.name, verbose=args.v)
        except FileNotFoundError:
            print(
                f"{arg_parser.prog}: can't open file '{os.path.abspath(args.file)}': [Errno 2] No such file or directory"
            )
        except EmptyFileError:
            pass
        except Exception as err:
            if isinstance(err, PengError):
                sys_exit(err)
            raise


if __name__ == "__main__":
    # import timeit

    # print(timeit.timeit("main()", setup="from __main__ import main", number=1))
    # 0.008815239499999733 n=1000
    main()
