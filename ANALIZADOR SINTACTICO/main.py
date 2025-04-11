# main.py
from lexer import lexer
from parser import BottomUpParser

# Archivo CSV convertido (recuerda modificar los símbolos por nombres de tokens: + a plus, * a mul, etc.)
PARSING_TABLE_FILE = 'tablaSintactica.csv'

# Entrada de ejemplo
code = "( # ) + #"

try:
    tokens = lexer(code)
    print("Tokens:", tokens)

    parser = BottomUpParser(PARSING_TABLE_FILE)

    # Si quieres, puedes definir reglas de gramática aquí para validación cruzada
    # parser.set_grammar_rules({ ... })

    parser.parse(tokens)

except SyntaxError as e:
    print(e)
