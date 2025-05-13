# main.py
from lexer import lexer
from parserNodo import LL1Parser

def main():
    # Cargar el parser con la tabla
    parser = LL1Parser("tablaSintactica.csv", start_symbol="S")
    # Después de crear el parser, verifica la tabla cargada
    print("Tabla cargada:")
    for non_terminal, productions in parser.parsing_table.items():
        print(f"{non_terminal}: {productions}")
    
    # Leer cadena del usuario
    code = input("Ingresa una expresión (usa int para representar enteros): ")

    try:
        tokens = lexer(code)
        print("Tokens:", tokens)
        syntax_tree = parser.parse(tokens)
        
        # Imprimir el árbol sintáctico
        print("\n=== Árbol Sintáctico ===")
        print(syntax_tree.print_tree())
        
        # Exportar árbol a formato TXT
        tree_txt = syntax_tree.export_tree_format()
        print("\n=== Árbol en formato TXT ===")
        print(tree_txt)
        
        # Guardar en archivo
        with open("arbol_sintactico.txt", "w", encoding="utf-8") as f:
            f.write(tree_txt)
        print("\nEl árbol sintáctico ha sido guardado en 'arbol_sintactico.txt'")
        
        # Exportar árbol a formato DOT para Graphviz
        dot_code = syntax_tree.export_graphviz()
        with open("arbol_sintactico.dot", "w", encoding="utf-8") as f:
            f.write(dot_code)
        print("El código Graphviz ha sido guardado en 'arbol_sintactico.dot'")
        print("\nPuedes visualizar el árbol en https://dreampuf.github.io/GraphvizOnline/ o cualquier herramienta compatible con Graphviz")

    except SyntaxError as e:
        print(e)

if __name__ == "__main__":
    main()