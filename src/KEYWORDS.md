# MiniLang-233 Keywords

## Roll Number

Roll Number: 233-006-042

## Variant Calculation

233 mod 4 = 1

Therefore, MiniLang-233 uses Variant 1.

Variant 1 features:

- Arrays
- Array bounds checking
- While loop
- Switch-case-default

---

## Keyword Naming Rule

MiniLang-233 uses a custom keyword set.

The language keywords use the prefix `m` to make them different
from normal programming-language keywords.

---

## Keyword Mapping

| Normal Keyword | MiniLang-233 Keyword | Purpose |
|---|---|---|
| if | `mif` | Conditional statement |
| else | `melse` | Alternative condition |
| while | `mwhile` | While loop |
| switch | `mswitch` | Switch statement |
| case | `mcase` | Switch case |
| default | `mdefault` | Default switch case |
| break | `mbreak` | Exit loop or switch |
| function | `mfunc` | Function declaration |
| return | `mreturn` | Return a value |
| int | `mint` | Integer data type |
| bool | `mbool` | Boolean data type |
| true | `mtrue` | Boolean true |
| false | `mfalse` | Boolean false |

---

## Arrays

MiniLang-233 supports arrays.

Example:

    mint numbers[5];

This creates an integer array with 5 elements.

Valid indexes:

    0
    1
    2
    3
    4

Invalid indexes:

    -1
    5
    6

The compiler performs array bounds checking.

---

## While Loop

The `mwhile` keyword is used for loops.

Example:

    mwhile (i < 5) {
        i = i + 1;
    }

---

## Switch Statement

The `mswitch` keyword is used for multiple choices.

Example:

    mswitch (x) {

        mcase 1:
            x = 10;
            mbreak;

        mcase 2:
            x = 20;
            mbreak;

        mdefault:
            x = 0;
    }

---

## Reserved Keywords

The following words are reserved:

    mif
    melse
    mwhile
    mswitch
    mcase
    mdefault
    mbreak
    mfunc
    mreturn
    mint
    mbool
    mtrue
    mfalse

Reserved keywords cannot be used as variable names.

---

## MiniLang-233 Variant

Roll number:

    233

Calculation:

    233 mod 4 = 1

Therefore:

    Variant 1

Main features:

    Arrays
    Array Bounds Checking
    While Loop
    Switch-Case-Default
