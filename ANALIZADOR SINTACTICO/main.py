# main.py
from lexer import lexer
from parser import LL1Parser

# Cargar el parser con la tabla
parser = LL1Parser("tablaSintactica.csv", start_symbol="S")
# Después de crear el parser, verifica la tabla cargada
print("Tabla cargada:")
for non_terminal, productions in parser.parsing_table.items():
    print(f"{non_terminal}: {productions}")
# Leer cadena del usuario
code = input("Ingresa una expresión (usa # para representar int): ")

try:
    tokens = lexer(code)
    print("Tokens:", tokens)
    parser.parse(tokens)

except SyntaxError as e:
    print(e)
