# MiniLang-233 Grammar

## 1. Overview

MiniLang-233 is a small programming language designed for the
Compiler Design Lab Assignment.

The grammar is written for a hand-written recursive-descent parser.

The grammar has been transformed to remove left recursion and is
left-factored where necessary.

---

## 2. Program Structure

```text
Program
    → DeclarationList EOF

DeclarationList
    → Declaration DeclarationList
    | ε

Declaration
    → FunctionDeclaration
    | Statement
