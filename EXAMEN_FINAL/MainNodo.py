from lexer import lexer
from parserNodo import LL1Parser
from symbol_table import SymbolTable, FunctionSymbol, VariableSymbol, SemanticAnalyzer


def extract_parameters(params_node):
    params = []
    if not params_node.children:
        return params
    if params_node.children[0].symbol == 'id':
        params.append(params_node.children[0].value)
    if len(params_node.children) > 1:
        current = params_node.children[1]
        while current.children:
            if len(current.children) >= 3 and current.children[0].symbol == ',' and current.children[1].symbol == 'id':
                params.append(current.children[1].value)
                current = current.children[2]
            else:
                break
    return params


def build_symbol_table(syntax_tree):
    symbol_table = SymbolTable()
    for node in syntax_tree.children:
        if node.symbol == 'DECLARACION':
            for i in range(len(node.children) - 1):
                if node.children[i].symbol == '#' and node.children[i + 1].symbol == 'id':
                    var_name = node.children[i + 1].value
                    line = getattr(node, 'line', 0)
                    column = getattr(node, 'column', 0)
                    symbol_table.add_global_var(var_name, "auto", line, column)

    for func_type in ['FUNK_NOT_RET', 'FUNK_RET']:
        for func_node in find_nodes(syntax_tree, func_type):
            func_name = next(child.value for child in func_node.children if child.symbol == 'id')
            params_node = find_first_child(func_node, 'PARAMS')
            params = []
            if params_node:
                param_names = extract_parameters(params_node)
                params = [(name, "auto") for name in param_names]
            return_type = 'no_return' if func_type == 'FUNK_NOT_RET' else 'return'
            line = getattr(func_node, 'line', 0)
            column = getattr(func_node, 'column', 0)
            symbol_table.add_function(func_name, params, return_type, line, column)

            instr_node = find_first_child(func_node, 'INSTRUCCIONES')
            if instr_node:
                for decl in find_nodes(instr_node, 'DECLARACION'):
                    for i in range(len(decl.children) - 1):
                        if decl.children[i].symbol == '#' and decl.children[i + 1].symbol == 'id':
                            var_name = decl.children[i + 1].value
                            if var_name not in [p[0] for p in params]:
                                line = getattr(decl, 'line', 0)
                                column = getattr(decl, 'column', 0)
                                symbol_table.add_local_var(func_name, var_name, "auto", line, column)
    return symbol_table


def find_nodes(root, symbol):
    nodes = []
    if root.symbol == symbol:
        nodes.append(root)
    for child in root.children:
        nodes.extend(find_nodes(child, symbol))
    return nodes


def find_first_child(root, symbol):
    for child in root.children:
        if child.symbol == symbol:
            return child
    return None


def check_undeclared_variables(node, symbol_table, current_function=None):
    errors = []
    if node.symbol in ['FUNK_NOT_RET', 'FUNK_RET']:
        for child in node.children:
            if child.symbol == 'id':
                current_function = child.value
                break
    if node.symbol == 'id':
        var_name = node.value
        symbol = symbol_table.find_symbol(var_name, current_function)
        if symbol is None:
            line = getattr(node, 'line', 'desconocida')
            column = getattr(node, 'column', 'desconocida')
            scope = f"en la función '{current_function}'" if current_function else "global"
            errors.append(f"ERROR: Variable '{var_name}' no declarada {scope} (Línea {line}, Columna {column})")
    for child in node.children:
        errors.extend(check_undeclared_variables(child, symbol_table, current_function))
    return errors


def main():
    parser = LL1Parser("tablaSintactica.csv", start_symbol="S")
# Ejemplos de código para probar
    test_codes = [
        "# x = 5",
        "# y = 3.14", 
        "# nombre = \"Juan\"",
        "# x = 5 # y = 10 # resultado = x + y",
        "# texto = \"hola\" # numero = 42 # suma = texto + numero"  # Esto debe dar error
    ]
    
    print("Selecciona un ejemplo o ingresa tu código:")
    for i, code in enumerate(test_codes, 1):
        print(f"{i}. {code}")
    
    choice = input("\nIngresa el número del ejemplo (1-5) o tu código: ")
    
    if choice.isdigit() and 1 <= int(choice) <= len(test_codes):
        code = test_codes[int(choice) - 1]
    else:
        code = choice
    
    try:
        tokens = lexer(code)
        print(f"\nCódigo analizado: {code}")
        print("Tokens:", tokens)
        
        # Análisis semántico mejorado
        analyzer = SemanticAnalyzer(tokens)
        analyzer.analyze()
        analyzer.report_results()
        
    except SyntaxError as e:
        print(f"Error de sintaxis: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    main()