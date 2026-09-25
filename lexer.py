def tokenize(code):
    tokens = []
    
    for word in code.split():
        if word.isdigit():
            tokens.append(("NUMBER", word))
        elif word.isidentifier():
            tokens.append(("IDENTIFIER", word))
        else:
            tokens.append(("SYMBOL", word))
    
    return tokens


if __name__ == "__main__":
    code = "x = 10 + 20"
    print(tokenize(code))
