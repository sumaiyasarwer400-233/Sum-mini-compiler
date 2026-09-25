from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer
from tac import TACGenerator
from optimizer import Optimizer
from backend import StackMachine
from interpreter import Interpreter


def run_compiler(source_code):
    print("================================")
    print("        MiniLang-233 Compiler")
    print("================================")

    # Step 1: Lexical Analysis
    print("\n[1] LEXICAL ANALYSIS")
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()

    for token in tokens:
        print(token)

    # Step 2: Parsing
    print("\n[2] PARSING")
    parser = Parser(tokens)
    ast = parser.parse()

    print("Parsing completed successfully.")

    # Step 3: Semantic Analysis
    print("\n[3] SEMANTIC ANALYSIS")
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)

    if analyzer.errors:
        print("Semantic errors found:")
        for error in analyzer.errors:
            print(" -", error)
        return

    print("Semantic analysis completed successfully.")

    # Step 4: Three Address Code
    print("\n[4] THREE ADDRESS CODE")
    tac_generator = TACGenerator()
    tac = tac_generator.generate(ast)

    for instruction in tac:
        print(instruction)

    # Step 5: Optimization
    print("\n[5] OPTIMIZATION")

    optimizer = Optimizer()

    print("\nBefore optimization:")
    for instruction in tac:
        print(instruction)

    optimized_tac = optimizer.optimize(tac)

    print("\nAfter optimization:")
    for instruction in optimized_tac:
        print(instruction)

    # Step 6: Backend
    print("\n[6] STACK MACHINE CODE")
    backend = StackMachine()
    machine_code = backend.generate(optimized_tac)

    for instruction in machine_code:
        print(instruction)

    # Step 7: Execution
    print("\n[7] EXECUTION")
    interpreter = Interpreter()
    result = interpreter.run(machine_code)

    print("Program result:", result)


if __name__ == "__main__":
    program = """
    mfunc factorial(mint n) {
        mif (n <= 1) {
            mreturn 1;
        }

        mreturn n * factorial(n - 1);
    }
    """

    run_compiler(program)
