import ply.lex as lex

# Lista de tokens
tokens = ("IGUAL", "NUMBER", "ADD", "LESS", "MULT", "DIV", "LEFT_POR", "RIGHT_POR","INICIO", "FIN", "VAR", "WHILE","FOR","IF","ELSE_IF", "COMMENT","BREAK","PUNTO_COMA", "MENOR", "MAYOR", "MAYOR_IGUAL", "MENOR_IGUAL", "IGUAL_QUE","DIFERENTE", "AND", "OR", "FUNK_RET", "FUNK_NOT_RET", "MAIN", "RETURN", "IMPRIMIR", "ID")

# Expresiones regulares para tokens simples
t_IGUAL = r'\='
t_ADD       = r'\+'
t_LESS      = r'\-'
t_MULT      = r'\.'
t_DIV       = r'/'
t_LEFT_POR  = r'\('
t_RIGHT_POR = r'\)'
t_DIFERENTE = r'<>'
t_INICIO = r'{'
t_FIN = r'}'
t_MENOR = r'<'
t_MAYOR = r'>'
t_MENOR_IGUAL = r'<='
t_MAYOR_IGUAL = r'>='
t_PUNTO_COMA = r';'
t_IGUAL_QUE = r'=='
t_AND = r'@'
t_OR = r'//'

#imprimir
def t_IMPRIMIR(t):
    r"imprimir\s*\(\s*'([a-zA-Z0-9_ ]*)'\s*\)\s*;"
    return t

#retornar
def t_RETURN(t):
    r'ret'
    return t

#funciones
def t_FUNK_RET(t):
    r'funk_ret'
    return t

def t_FUNK_NOT_RET(t):
    r'funk_not_ret'
    return t

#main
def t_MAIN(t):
    r'main'
    return t

#Expresión para BREAK
def t_BROKEN(t):
    r'break'
    return t


#Expresión para ELSE_IF
def t_ELSE_IF(t):
    r'else'
    return t


#Expresión para IF
def t_IF(t):
    r'if'
    return t


#Expresión para FOR
def t_FOR(t):
    r'for'
    return t


# Expresión regular while
def t_WHILE(t):
    r'while'
    return t

# Expresión regular para variables que empiezan con #
def t_VAR(t):
    r'\#[a-zA-Z_][a-zA-Z0-9_]*'
    return t

# COMENTARIOS VDM
def t_COMMENT(t):
    r'\<--.*?-->'
    return t

# Expresión regular para números
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)  
    return t

# Identificadores para funciones o variables (como factorial, num, etc.)
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    return t


# Manejo de saltos de línea
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Caracteres a ignorar (espacios y tabulaciones)
t_ignore = ' \t'

# Manejo de errores
def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

# Construcción del analizador léxico
lexer = lex.lex()

# Leer el archivo de entrada
archivo = input("Ingrese el nombre del archivo de código fuente: ")  # Pedir el archivo al usuario

try:
    with open(archivo, "r", encoding="utf-8") as file:
        data = file.read()  # Leer el contenido del archivo
except FileNotFoundError:
    print(f"Error: No se encontró el archivo '{archivo}'")
    exit(1)

# Pasar la entrada al lexer
lexer.input(data)

#almacenando los tokens en una lista
tokens_list = []

# Obtener los tokens
print("\nTokens detectados:")
for tok in lexer:
    print(tok)
    tokens_list.append({"tipo": tok.type, "valor": tok.value, "linea": tok.lineno})


# Mostrar los tokens en formato de lista
print("\nTokens detectados en formato de diccionario:")
print(tokens_list)
