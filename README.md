from lexer import tokenize
from parser import Parser


def main():
    print("MiniLang 233")
    print("----------------")

    code = input("Enter MiniLang code: ")

    tokens = tokenize(code)

    print("\nTokens:")
    for token in tokens:
        print(token)

    parser = Parser(tokens)

    try:
        tree = parser.parse()
        print("\nParsing successful!")
        print(tree)
    except Exception as error:
        print("\nParsing error:", error)


if __name__ == "__main__":
    main()
