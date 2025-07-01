# symbol_table.py
class VariableSymbol:
    def __init__(self, name, var_type, line, column):
        self.name = name
        self.type = var_type
        self.line = line
        self.column = column

    def __str__(self):
        return f"<Variable {self.name}:{self.type}>"

class FunctionSymbol:
    def __init__(self, name, params, return_type, line, column):
        self.name = name
        self.params = params
        self.return_type = return_type
        self.locals = {}
        self.line = line
        self.column = column

    def add_local(self, var_name, var_type, line, column):
        self.locals[var_name] = VariableSymbol(var_name, var_type, line, column)

    def __str__(self):
        params_str = ', '.join([f"{p[0]}:{p[1]}" for p in self.params])
        return f"<Function {self.name}({params_str}) -> {self.return_type}>"

class SymbolTable:
    def __init__(self):
        self.global_vars = {}
        self.functions = {}
    
    def add_global_var(self, name, var_type, line, column):
        self.global_vars[name] = VariableSymbol(name, var_type, line, column)
    
    def add_function(self, name, params, return_type, line, column):
        self.functions[name] = FunctionSymbol(name, params, return_type, line, column)
    
    def add_local_var(self, func_name, var_name, var_type, line, column):
        if func_name in self.functions:
            self.functions[func_name].add_local(var_name, var_type, line, column)
    
    def get_public_view(self):
        public_table = SymbolTable()
        
        for name, var in self.global_vars.items():
            public_table.add_global_var(name, var.type, var.line, var.column)
        
        for name, func in self.functions.items():
            params = []
            for param_name, param_type in func.params:
                params.append((param_name, param_type))
            
            public_table.add_function(
                name, 
                params, 
                func.return_type, 
                func.line, 
                func.column
            )
        
        return public_table
    
    def to_string_full(self):
        output = "=== Tabla de Símbolos Completa ===\n"
        output += "\nVariables globales:\n"
        for name, var in self.global_vars.items():
            output += f"  {var}\n"
        
        output += "\nFunciones:\n"
        for name, func in self.functions.items():
            params_str = ', '.join([f"{p[0]}:{p[1]}" for p in func.params])
            output += f"  <Function {func.name}({params_str}) -> {func.return_type}>\n"
            if func.locals:
                output += "    Locales:\n"
                for var_name, var in func.locals.items():
                    output += f"      {var}\n"
        
        return output
    
    def to_string_public(self):
        output = "=== Tabla de Símbolos Pública ===\n"
        output += "\nVariables globales:\n"
        for name, var in self.global_vars.items():
            output += f"  {var}\n"
        
        output += "\nFunciones:\n"
        for name, func in self.functions.items():
            params_str = ', '.join([f"{p[0]}:{p[1]}" for p in func.params])
            output += f"  <Function {func.name}({params_str}) -> {func.return_type}>\n"
        
        return output
    
    def __str__(self):
        return self.to_string_public()
    
    def find_symbol(self, name, current_function=None):
        if current_function and current_function in self.functions:
            func = self.functions[current_function]
            
            if name in func.locals:
                return func.locals[name]
                
            for param_name, param_type in func.params:
                if param_name == name:
                    return VariableSymbol(name, param_type, 0, 0)
        
        if name in self.global_vars:
            return self.global_vars[name]
            
        if name in self.functions:
            return self.functions[name]
            
        return None

class SemanticAnalyzer:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_index = 0
        self.symbol_table = SymbolTable()
        self.current_function = None
        self.in_function = False
        self.error_occurred = False
        self.error_message = ""

    def analyze(self):
        try:
            while self.current_token()[0] != '$':
                token_type, token_value, line, col = self.current_token()
                
                if token_type == 'funk_ret' or token_type == 'funk_not_ret':
                    self.analyze_function_declaration()
                elif token_type == '#':
                    self.analyze_variable_declaration()
                else:
                    self.advance()
            
            return self.symbol_table
        
        except Exception as e:
            self.error_occurred = True
            self.error_message = str(e)
            return self.symbol_table

    def report_results(self):
        if self.error_occurred:
            print(f"\n ERROR SEMÁNTICO: {self.error_message}")
            print("\nTabla de símbolos parcial:")
            print(self.symbol_table.to_string_public())
        else:
            print("\n ¡ANÁLISIS SEMÁNTICO COMPLETADO CON ÉXITO!")
            print("No se encontraron errores en el programa.")
            self.report_variables()
            print("\nTabla de símbolos completa:")
            print(self.symbol_table.to_string_full())

    def current_token(self):
        return self.tokens[self.current_index] if self.current_index < len(self.tokens) else ('$', '$', 0, 0)

    def advance(self):
        self.current_index += 1

    def match(self, expected_type):
        if self.current_token()[0] == expected_type:
            token = self.current_token()
            self.advance()
            return token
        return None
    
    def infer_type_from_value(self, token_value):
        """Infiere el tipo de una variable basándose en su valor literal"""
        if token_value.startswith('"') and token_value.endswith('"'):
            return 'string'
        
        try:
            if '.' in token_value:
                float(token_value)
                return 'float'
            else:
                int(token_value)
                return 'int'
        except ValueError:
            pass
        
        if token_value.lower() in ['true', 'false']:
            return 'bool'
        
        return 'unknown'

    def analyze_function_declaration(self):
        ret_token = self.current_token()
        self.advance()
        
        func_name_token = self.match('id')
        if not func_name_token:
            raise SyntaxError("Se esperaba nombre de función")
        func_name = func_name_token[1]
        
        if not self.match('('):
            raise SyntaxError("Se esperaba '(' después del nombre de la función")
        
        params = []
        while self.current_token()[0] != ')':
            param_type = self.analyze_type()
            param_name = self.match('id')
            if not param_name:
                raise SyntaxError("Se esperaba nombre de parámetro")
            params.append((param_name[1], param_type))
            
            if self.current_token()[0] == ',':
                self.advance()
            else:
                break
        
        if not self.match(')'):
            raise SyntaxError("Se esperaba ')' después de los parámetros")
        
        return_type = 'void' if ret_token[0] == 'funk_not_ret' else self.analyze_type()
        
        self.symbol_table.add_function(
            func_name, 
            params, 
            return_type, 
            func_name_token[2], 
            func_name_token[3]
        )
        
        self.current_function = func_name
        self.in_function = True
        
        if self.match('{'):
            while self.current_token()[0] != '}':
                if self.current_token()[0] == '#':
                    self.analyze_variable_declaration()
                else:
                    self.advance()
            
            if not self.match('}'):
                raise SyntaxError("Se esperaba '}' al final de la función")
        
        self.current_function = None
        self.in_function = False

    def analyze_variable_declaration(self):
        """Analiza declaraciones de variables con validación de tipos en asignaciones"""
        decl_token = self.current_token()
        self.advance()
        
        var_name_token = self.match('id')
        if not var_name_token:
            raise SyntaxError("Se esperaba nombre de variable después de '#'")
        
        var_name = var_name_token[1]
        
        if self.current_token()[0] == '=':
            self.advance()
            
            # Analizar la expresión completa del lado derecho
            try:
                inferred_type, _, _ = self.analyze_expression()
            except (TypeError, NameError, SyntaxError) as e:
                # Re-lanzar el error para que sea capturado por el analizador principal
                raise e
        else:
            inferred_type = 'undefined'
        
        # Agregar la variable a la tabla de símbolos
        if self.in_function:
            self.symbol_table.add_local_var(
                self.current_function,
                var_name,
                inferred_type,
                var_name_token[2],
                var_name_token[3]
            )
        else:
            self.symbol_table.add_global_var(
                var_name,
                inferred_type,
                var_name_token[2],
                var_name_token[3]
            )
        
        print(f"✓ Variable '{var_name}' declarada como tipo '{inferred_type}'")

    def are_types_compatible_for_arithmetic(self, type1, type2):
        """Verifica si dos tipos son compatibles para operaciones aritméticas"""
        # Solo permitir operaciones entre tipos numéricos idénticos
        numeric_types = {'int', 'float'}
        return type1 == type2 and type1 in numeric_types

    def are_types_compatible_for_comparison(self, type1, type2):
        """Verifica si dos tipos son compatibles para comparaciones"""
        # Solo permitir comparaciones entre tipos idénticos
        return type1 == type2

    def get_result_type_for_arithmetic(self, type1, type2, operator):
        """Determina el tipo resultante de una operación aritmética"""
        if not self.are_types_compatible_for_arithmetic(type1, type2):
            return None
        return type1  # El resultado es del mismo tipo que los operandos

    def analyze_expression(self):
        """Analiza expresiones con validación estricta de tipos"""
        # Analizar primer operando
        left_type, left_line, left_col = self.analyze_operand()
        
        # Verificar si hay un operador binario
        current_token = self.current_token()
        
        if current_token[0] in ['+', '-', '*', '/']:
            # Operación aritmética
            op_token = current_token
            self.advance()
            
            # Analizar segundo operando
            right_type, right_line, right_col = self.analyze_operand()
            
            # VALIDACIÓN ESTRICTA: Solo permitir operaciones entre tipos compatibles
            if not self.are_types_compatible_for_arithmetic(left_type, right_type):
                raise TypeError(
                    f"ERROR DE TIPOS: No se puede realizar la operación '{op_token[1]}' entre "
                    f"'{left_type}' y '{right_type}' en línea {op_token[2]}, columna {op_token[3]}. "
                    f"Las operaciones aritméticas solo están permitidas entre tipos numéricos idénticos (int con int, float con float)."
                )
            
            # Determinar tipo resultante
            result_type = self.get_result_type_for_arithmetic(left_type, right_type, op_token[1])
            if result_type is None:
                raise TypeError(
                    f"ERROR DE TIPOS: Operación '{op_token[1]}' no válida para tipos "
                    f"'{left_type}' y '{right_type}' en línea {op_token[2]}, columna {op_token[3]}."
                )
            
            print(f"✓ Operación aritmética válida: {left_type} {op_token[1]} {right_type} → {result_type}")
            return result_type, op_token[2], op_token[3]
            
        elif current_token[0] in ['==', '<', '>', '<=', '>=', '<>']:
            # Operación de comparación
            op_token = current_token
            self.advance()
            
            right_type, right_line, right_col = self.analyze_operand()
            
            # VALIDACIÓN ESTRICTA: Solo permitir comparaciones entre tipos idénticos
            if not self.are_types_compatible_for_comparison(left_type, right_type):
                raise TypeError(
                    f"ERROR DE TIPOS: No se puede realizar la comparación '{op_token[1]}' entre "
                    f"'{left_type}' y '{right_type}' en línea {op_token[2]}, columna {op_token[3]}. "
                    f"Las comparaciones solo están permitidas entre tipos idénticos."
                )
            
            print(f"✓ Comparación válida: {left_type} {op_token[1]} {right_type} → bool")
            return 'bool', op_token[2], op_token[3]
        else:
            # Expresión simple (un solo operando)
            return left_type, left_line, left_col

    def analyze_operand(self):
        """Analiza un operando individual y retorna su tipo"""
        token_type, token_value, line, col = self.current_token()
        self.advance()
        
        if token_type == 'num':
            inferred_type = self.infer_type_from_value(token_value)
            return inferred_type, line, col
            
        elif token_type == 'string':
            return 'string', line, col
            
        elif token_type == 'id':
            # Buscar la variable en la tabla de símbolos
            symbol = self.symbol_table.find_symbol(token_value, self.current_function)
            if not symbol:
                raise NameError(
                    f"ERROR: Variable '{token_value}' no declarada en línea {line}, columna {col}"
                )
            return symbol.type, line, col
        else:
            raise SyntaxError(
                f"ERROR: Token inesperado en expresión: '{token_value}' en línea {line}, columna {col}"
            )

    def analyze_type(self):
        """Analiza y retorna el tipo de una declaración explícita"""
        token_type, token_value, line, col = self.current_token()
        
        if token_type == 'id':
            if token_value in ['int', 'float', 'string', 'bool', 'void']:
                self.advance()
                return token_value
            else:
                return None
        else:
            self.advance()
            if token_type == 'num':
                return 'float' if '.' in token_value else 'int'
            elif token_type == 'string':
                return 'string'
            elif token_value in ['true', 'false']:
                return 'bool'
        
        return None
    
    def report_variables(self):
        """Genera un reporte detallado de las variables declaradas"""
        print("\n" + "="*50)
        print("REPORTE DE VARIABLES DECLARADAS")
        print("="*50)
        
        if self.symbol_table.global_vars:
            print("\n VARIABLES GLOBALES:")
            for name, var in self.symbol_table.global_vars.items():
                print(f"  • {name}: {var.type} (línea {var.line}, columna {var.column})")
        else:
            print("\n VARIABLES GLOBALES: Ninguna")
        
        if self.symbol_table.functions:
            for func_name, func in self.symbol_table.functions.items():
                if func.locals:
                    print(f"\n VARIABLES LOCALES EN '{func_name}':")
                    for var_name, var in func.locals.items():
                        print(f"  • {var_name}: {var.type} (línea {var.line}, columna {var.column})")
        
        # Estadisticas de tipos
        all_vars = list(self.symbol_table.global_vars.values())
        for func in self.symbol_table.functions.values():
            all_vars.extend(func.locals.values())
        
        if all_vars:
            type_count = {}
            for var in all_vars:
                type_count[var.type] = type_count.get(var.type, 0) + 1
            
            print(f"\n RESUMEN DE TIPOS:")
            for var_type, count in type_count.items():
                print(f"  • {var_type}: {count} variable(s)")
        
        print("="*50)