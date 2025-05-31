# mainNodo.py
from lexer import lexer
from parserNodo import LL1Parser
from symbol_table import SymbolTable, FunctionSymbol, VariableSymbol

def extract_parameters(params_node):
    """Extrae nombres de parámetros del nodo PARAMS"""
    params = []
    if not params_node.children:
        return params
    
    # El primer hijo debe ser un id (primer parámetro)
    if params_node.children[0].symbol == 'id':
        params.append(params_node.children[0].value)
    
    # Si hay más parámetros, estarán en PARAMS'
    if len(params_node.children) > 1:
        current = params_node.children[1]  # PARAMS'
        while current.children:
            # Buscamos coma seguida de id
            if len(current.children) >= 3 and current.children[0].symbol == ',' and current.children[1].symbol == 'id':
                params.append(current.children[1].value)
                current = current.children[2]  # siguiente PARAMS'
            else:
                break
    
    return params

def build_symbol_table(syntax_tree):
    symbol_table = SymbolTable()
    
    # Procesar declaraciones globales primero
    for node in syntax_tree.children:
        if node.symbol == 'DECLARACION':
            # Buscar patron: # -> id
            for i in range(len(node.children)-1):
                if node.children[i].symbol == '#' and node.children[i+1].symbol == 'id':
                    var_name = node.children[i+1].value
                    # Usar valores temporales para línea/columna
                    line = getattr(node, 'line', 0)
                    column = getattr(node, 'column', 0)
                    symbol_table.add_global_var(var_name, "auto", line, column)
    
    # Procesar funciones
    for func_type in ['FUNK_NOT_RET', 'FUNK_RET']:
        for func_node in find_nodes(syntax_tree, func_type):
            # Extraer nombre de función
            func_name = next(child.value for child in func_node.children #buscamos el nodo hijo con simbolo id
                           if child.symbol == 'id')
            
            # Extraer parámetros
            params_node = find_first_child(func_node, 'PARAMS')
            params = []
            if params_node:
                param_names = extract_parameters(params_node)
                params = [(name, "auto") for name in param_names]  # (nombre, tipo)
            
            # Determinar tipo de retorno
            return_type = 'no_return' if func_type == 'FUNK_NOT_RET' else 'return'
            
            # Crear símbolo de función (usar posición del nodo)
            line = getattr(func_node, 'line', 0)
            column = getattr(func_node, 'column', 0)
            symbol_table.add_function(func_name, params, return_type, line, column)
            
            # Procesar variables locales
            instr_node = find_first_child(func_node, 'INSTRUCCIONES')
            if instr_node:
                for decl in find_nodes(instr_node, 'DECLARACION'):
                    for i in range(len(decl.children)-1):
                        if decl.children[i].symbol == '#' and decl.children[i+1].symbol == 'id':
                            var_name = decl.children[i+1].value
                            if var_name not in [p[0] for p in params]:  # No es parámetro
                                # Usar posición del nodo si está disponible
                                line = getattr(decl, 'line', 0)
                                column = getattr(decl, 'column', 0)
                                symbol_table.add_local_var(func_name, var_name, "auto", line, column)
    
    return symbol_table

# Funciones auxiliares para buscar nodos
def find_nodes(root, symbol):
    nodes = []
    if root.symbol == symbol:# Agrega a la lista al sybol si coincide
        nodes.append(root)
    for child in root.children:#para cada hijo del nodo actual 
        nodes.extend(find_nodes(child, symbol))
    return nodes

def find_first_child(root, symbol):#
    for child in root.children:#buscamos el simblo que coincide
        if child.symbol == symbol:
            return child#retornams el que coincida con symbol 
    return None

def check_undeclared_variables(node, symbol_table, current_function=None):
    """
    Recorre el AST y verifica que todos los identificadores usados estén declarados.
    Devuelve una lista de mensajes de error.
    """
    errors = []
    
    # Si encontramos una definición de función, actualizamos el ámbito actual
    if node.symbol in ['FUNK_NOT_RET', 'FUNK_RET']:
        # Buscar el nombre de la función
        for child in node.children:
            if child.symbol == 'id':
                current_function = child.value
                break
    
    # Verificar si este nodo es un uso de variable (identificador)
    if node.symbol == 'id':
        var_name = node.value
        symbol = symbol_table.find_symbol(var_name, current_function)
        
        if symbol is None:
            # Obtener posición para el mensaje de error
            line = getattr(node, 'line', 'desconocida')
            column = getattr(node, 'column', 'desconocida')
            scope = f"en la función '{current_function}'" if current_function else "global"
            errors.append(f"ERROR: Variable '{var_name}' no declarada {scope} (Línea {line}, Columna {column})")
    
    # Recorrer recursivamente los hijos
    for child in node.children:
        child_errors = check_undeclared_variables(child, symbol_table, current_function)
        errors.extend(child_errors)
    
    return errors

def main():
    # Cargar el parser con la tabla
    parser = LL1Parser("tablaSintactica.csv", start_symbol="S")
    # Después de crear el parser, verifica la tabla cargada
    # print("Tabla cargada:")
    #for non_terminal, productions in parser.parsing_table.items():
    #    print(f"{non_terminal}: {productions}")
    
    # Leer cadena del usuario
    code = input("Ingresa una expresión (usa int para representar enteros): ")

    try:
        tokens = lexer(code)
        print("Tokens:", tokens)
        syntax_tree = parser.parse(tokens)

        # Construir tabla de símbolos COMPLETA (incluye locales)
        full_symbol_table = build_symbol_table(syntax_tree)
        
        # Crear vista pública (sin variables locales)
        public_symbol_table = full_symbol_table.get_public_view()
        
        # --- VERIFICAR VARIABLES NO DECLARADAS ---
        undeclared_errors = check_undeclared_variables(syntax_tree, full_symbol_table)
        
        if undeclared_errors:
            print("\n=== ERRORES DE VARIABLES NO DECLARADAS ===")
            for error in undeclared_errors:
                print(error)
            print("Compilación interrumpida debido a errores.")
            return  # Termina la ejecución aquí sin generar archivos
        else:
            print("\n✓ Todas las variables están correctamente declaradas")
        # -----------------------------------------
                
        # Guardar ambas tablas de símbolos
        with open("tabla_simbolos_completa.txt", "w") as f:
            f.write(full_symbol_table.to_string_full())
        
        with open("tabla_simbolos_publica.txt", "w") as f:
            f.write(public_symbol_table.to_string_public())
        
        # Imprimir ambas tablas
        #print("\n=== Tabla de Símbolos  ===")
        print(full_symbol_table.to_string_full())
        
        #print("\n=== Tabla de Símbolos eliminando  ===")
        print(public_symbol_table.to_string_public())
        
        # Imprimir el árbol sintáctico
        #print("\n=== Árbol Sintáctico ===")
        #print(syntax_tree.print_tree())
        
        # Exportar árbol a formato TXT
        tree_txt = syntax_tree.export_tree_format()
        #print("\n=== Árbol en formato TXT ===")
        #print(tree_txt)
        
        # Guardar en archivo
        with open("arbol_sintactico.txt", "w", encoding="utf-8") as f:
            f.write(tree_txt)
        print("\nEl árbol sintáctico ha sido guardado en 'arbol_sintactico.txt'")
        
        # Exportar árbol a formato DOT para Graphviz
        dot_code = syntax_tree.export_graphviz()
        with open("arbol_sintactico.dot", "w", encoding="utf-8") as f:
            f.write(dot_code)
        print("El código Graphviz ha sido guardado en 'arbol_sintactico.dot'")
       

    except SyntaxError as e:
        print(e)

if __name__ == "__main__":
    main()