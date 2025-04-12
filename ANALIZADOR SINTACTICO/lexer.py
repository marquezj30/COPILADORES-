# lexer.py
import re

token_exprs = [
    ("plus",      r"plus"),
    ("mul",       r"mul"),
    ("left_par",  r"\("),
    ("right_par", r"\)"),
    ("int",      r"int"),
    ("whitespace", r"\s+"),
]

def lexer(code):
    tokens = []
    line = 1
    column = 1
    while code:
        match = None
        for token_type, regex in token_exprs:
            regex_obj = re.compile(regex)
            match = regex_obj.match(code)
            if match:
                text = match.group(0)
                if token_type != "whitespace":
                    tokens.append((token_type, text, line, column))
                column += len(text)
                code = code[len(text):]
                break
        if not match:
            raise SyntaxError(f"caracter ilegal '{code[0]}' en la linea {line}, columna {column}")
    tokens.append(("$", "$", line, column))
    return tokens
