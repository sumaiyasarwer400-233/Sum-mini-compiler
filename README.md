# MiniLang Compiler - Variant 2

## Student Information

- Student ID: 233-006-042
- Roll: 42
- Language: MiniLang
- Personalized Variant: Variant 2

## Personalized Features

Since:

42 mod 4 = 2

This project implements **Variant 2**, which includes:

1. Structs / Records
2. Nested Functions
3. Static Scoping

---

# Project Description

MiniLang is a small custom programming language designed and implemented as a compiler project.

The compiler is completely hand-written and does not use compiler-generator tools such as:

- Lex
- Yacc
- Flex
- Bison
- ANTLR

The compiler contains both a front-end and a simple back-end.

---

# Compiler Architecture

```text
MiniLang Source Code
        |
        v
+------------------+
|      Lexer       |
+------------------+
        |
        v
+------------------+
|      Parser      |
+------------------+
        |
        v
+------------------+
|       AST        |
+------------------+
        |
        v
+----------------------+
| Semantic Analysis    |
| + Symbol Table       |
| + Static Scoping     |
+----------------------+
        |
        v
+------------------+
|       TAC        |
+------------------+
        |
        v
+----------------------+
| TAC Optimization     |
| 1. Constant Folding |
| 2. CSE               |
+----------------------+
        |
        v
+----------------------+
| Stack Machine        |
| Backend              |
+----------------------+
        |
        v
+----------------------+
| Stack Interpreter    |
+----------------------+
