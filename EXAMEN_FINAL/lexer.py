#lexer
import re

token_exprs = [
    # Palabras clave (prioridad alta)
    ("funk_ret", r"funk_ret"),
    ("funk_not_ret", r"funk_not_ret"),
    ("ret", r"ret"),
    ("if", r"if"),
    ("else", r"else"),
    ("while", r"while"),
    ("for", r"for"),
    
    # Operadores y símbolos (ordenar de mayor a menor longitud)
    ("<=", r"<="),
    (">=", r">="),
    ("<>", r"<>"),
    ("==", r"=="),
    ("//", r"//"),
    ("@", r"@"),
    ("=", r"="),
    ("<", r"<"),
    (">", r">"),
    ("+", r"\+"),
    ("-", r"-"),
    ("*", r"\*"),
    ("/", r"/"),
    ("(", r"\("),
    (")", r"\)"),
    ("{", r"\{"),
    ("}", r"\}"),
    (",", r","),
    ("#", r"#"),

    # Literales
    # Literales (nuevas definiciones)
    ("num", r"\d+"),                    # Números enteros
    ("string", r"\"[^\"]*\"?"),          # Cadenas entre comillas
    ("id", r"[a-zA-Z_][a-zA-Z0-9_]*"),   # Identificadores
    
    # Espacios (ignorar)
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
            raise SyntaxError(f"Carácter ilegal '{code[0]}' en línea {line}, columna {column}")
    tokens.append(('$', '$', line, column))  # Fin de entrada
    return tokens