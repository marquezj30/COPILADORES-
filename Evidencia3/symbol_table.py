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
        """
        Crea una copia de la tabla que solo contiene:
        - Variables globales
        - Funciones (sin variables locales)
        """
        public_table = SymbolTable()
        
        # Clonar variables globales
        for name, var in self.global_vars.items():
            public_table.add_global_var(name, var.type, var.line, var.column)
        
        # Clonar funciones (sin variables locales)
        for name, func in self.functions.items():
            # Clonar parámetros
            params = []
            for param_name, param_type in func.params:
                params.append((param_name, param_type))
            
            # Crear función clonada sin locales
            public_table.add_function(
                name, 
                params, 
                func.return_type, 
                func.line, 
                func.column
            )
        
        return public_table
    
    def to_string_full(self):
        """
        Representación completa con variables locales
        """
        output = "=== Tabla de Símbolos Completa ===\n"
        output += "\nVariables globales:\n"
        for name, var in self.global_vars.items():
            output += f"  {var}\n"
        
        output += "\nFunciones:\n"
        for name, func in self.functions.items():
            # Mostrar función con sus locales
            params_str = ', '.join([f"{p[0]}:{p[1]}" for p in func.params])
            output += f"  <Function {func.name}({params_str}) -> {func.return_type}>\n"
            if func.locals:
                output += "    Locales:\n"
                for var_name, var in func.locals.items():
                    output += f"      {var}\n"
        
        return output
    
    def to_string_public(self):
        """
        Representación pública sin variables locales
        """
        output = "=== ELIMINANDO LOCALES ===\n"
        output += "\nVariables globales:\n"
        for name, var in self.global_vars.items():
            output += f"  {var}\n"
        
        output += "\nFunciones:\n"
        for name, func in self.functions.items():
            # Solo mostrar parámetros y tipo de retorno
            params_str = ', '.join([f"{p[0]}:{p[1]}" for p in func.params])
            output += f"  <Function {func.name}({params_str}) -> {func.return_type}>\n"
        
        return output
    
    def __str__(self):
        """Por defecto muestra la vista pública"""
        return self.to_string_public()
    
    def find_symbol(self, name, current_function=None):
        """
        Busca un símbolo por nombre en el ámbito actual.
        - Si estamos dentro de una función, busca primero en locales y parámetros
        - Luego busca en variables globales
        - Finalmente busca en funciones globales
        """
        # Buscar en el ámbito de la función actual (si existe)
        if current_function and current_function in self.functions:
            func = self.functions[current_function]
            
            # Buscar en variables locales
            if name in func.locals:
                return func.locals[name]
                
            # Buscar en parámetros
            for param_name, _ in func.params:
                if param_name == name:
                    # Devolver un símbolo ficticio para parámetros
                    return VariableSymbol(name, "param", 0, 0)
        
        # Buscar en variables globales
        if name in self.global_vars:
            return self.global_vars[name]
            
        # Buscar en funciones globales
        if name in self.functions:
            return self.functions[name]
            
        return None  # No encontrado