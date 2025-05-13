# parser.py
import csv
from tabulate import tabulate 

class Node:
    def __init__(self, symbol, value=None, line=-1, column=-1):
        self.symbol = symbol  # Símbolo no terminal o terminal
        self.value = value    # Valor real para terminales
        self.children = []    # Nodos hijos
        self.line = line      # Número de línea en el código fuente
        self.column = column  # Número de columna en el código fuente
        self.id = None        # ID único para Graphviz
    
    def add_child(self, node):
        self.children.append(node)
        
    def __str__(self):
        return f"{self.symbol}" + (f"({self.value})" if self.value else "")
    
    def print_tree(self, level=0):
        indent = "  " * level
        result = f"{indent}{self}\n"
        for child in self.children:
            result += child.print_tree(level + 1)
        return result
    
    def export_tree_format(self):
        """Genera una representación del árbol en formato de reglas de producción."""
        result = []
        
        def traverse(node, parent_id=None):
            node_id = f"{node.symbol}"
            if parent_id:
                result.append(f"{parent_id} -> {node_id};")
            
            for child in node.children:
                traverse(child, node_id)
        
        traverse(self)
        return "\n".join(result)
    
    def export_graphviz(self):
        """Genera una representación del árbol en formato DOT para Graphviz."""
        # Iniciar el grafo
        dot = ['digraph G {']
        
        # Contador para asignar IDs únicos a los nodos
        node_counter = [0]
        node_ids = {}
        
        def assign_ids(node):
            # Asignar un ID único al nodo
            node_id = f"node{node_counter[0]}"
            node_counter[0] += 1
            node_ids[node] = node_id
            
            # Asignar IDs a todos los hijos
            for child in node.children:
                assign_ids(child)
        
        def build_dot(node):
            node_id = node_ids[node]
            # Añadir el nodo al grafo
            label = node.symbol
            dot.append(f'  {node_id} [label="{label}", shape=ellipse];')
            
            # Añadir aristas a los hijos
            for child in node.children:
                child_id = node_ids[child]
                dot.append(f'  {node_id} -> {child_id};')
                build_dot(child)
        
        # Asignar IDs a todos los nodos
        assign_ids(self)
        
        # Construir el DOT
        build_dot(self)
        
        # Cerrar el grafo
        dot.append('}')
        
        return '\n'.join(dot)


class LL1Parser:
    def __init__(self, parsing_table_file, start_symbol='S'):
        self.start_symbol = start_symbol
        self.parsing_table = self.load_parsing_table(parsing_table_file)
        ## print("\nTabla cargada:")
        ##for non_terminal, productions in self.parsing_table.items():
           ## print(f"{non_terminal}: {productions}")

    def load_parsing_table(self, file, debug=False):
        table = {} # iniciar diccionario vacío
        with open(file, newline='', encoding='utf-8') as csvfile: #leer csv
            # Leer todas las líneas ignorando vacías
            lines = [line.strip() for line in csvfile if line.strip()]
            
            # Procesar headers
            headers = [h.strip() for h in lines[0].split(';')[1:]]#simbolos terminales 
            
            # Procesar cada fila de producción
            for line in lines[1:]:
                parts = [p.strip() for p in line.split(';')]#LECTURA DEL CSV ";"
                if not parts:#ELIMINACIÓN DE LINEAS VACÍAS
                    continue
                    
                non_terminal = parts[0]
                table[non_terminal] = {}#guardamos el no terminal izquierdo "S"
                
                for i in range(1, len(parts)):
                    if i-1 < len(headers):  # Asegurar que hay header correspondiente
                        token = headers[i-1] # 
                        production = parts[i]
                        if production and production != 'NaN':
                            table[non_terminal][token] = production
        
        # Verificación de carga
        if debug:
            print("\nTabla cargada (verificación):")
            for nt in table:
                print(f"{nt}: {table[nt]}")
        
        return table

    def parse(self, tokens):
        # Primero verificamos si ya hay un token $ al final
        tokens_copy = tokens.copy()  # Hacemos una copia para no modificar el original
        if not tokens_copy or tokens_copy[-1][0] != '$':
            # Si no hay token $ al final, lo añadimos
            last_token = tokens_copy[-1] if tokens_copy else (None, None, 1, 1)
            tokens_copy.append(('$', '$', last_token[2], last_token[3]))#añade el token de fin de entrada

        stack = ['$', self.start_symbol] #pila
        index = 0

        output_rows = []
        step = 1
        
        # Diccionario para almacenar nodos para cada símbolo de la pila
        node_stack = [Node('$')]  #pila paralela que usaremos para el arbol Comenzamos con el nodo $
        root_node = Node(self.start_symbol)
        node_stack.append(root_node)

        while stack and index < len(tokens_copy):#mientras tengamos simbolos por analizar y tokens por consumir el while sigue
            top = stack.pop() #
            top_node = node_stack.pop() # se saca el tope de la pila
            current_token = tokens_copy[index] #
            token_type, token_value, line, column = current_token # se obtiene el toker actual

            stack_str = ' '.join(reversed(stack + [top]))
            input_str = ' '.join([tok[0] for tok in tokens_copy[index:]])
            action = ''

            if top == 'e':
                action = 'Epsilon (e), se omite'
                
            elif top == token_type:#se avanza al siguiente token y se guarda el valor real match int = int
                action = f"[Match] {top}"
                # En lugar de crear un nuevo nodo, completa el nodo actual (top_node)
                top_node.value = token_value
                top_node.line = line
                top_node.column = column
                index += 1

            elif top in self.parsing_table:# si el tope es un no terminal
                production = self.parsing_table[top].get(token_type, None)
                if production:
                    action = f"[Expand] {top} → {production}"
                    # Dividir la producción en símbolos
                    symbols = production.split()
                    
                    # Crear nodos para cada símbolo en la producción
                    new_nodes = []
                    for symbol in symbols:
                        new_node = Node(symbol)
                        top_node.add_child(new_node)
                        new_nodes.append(new_node)
                    
                    # Añadir los nodos a la pila en orden inverso
                    for node in reversed(new_nodes):
                        node_stack.append(node)
                    
                    stack.extend(reversed(symbols))
                else:
                    raise SyntaxError(
                        f"Error en línea {line}, columna {column}: "
                        f"No hay producción para {top} → {token_type}"
                    )
            else:
                raise SyntaxError(
                    f"Error en línea {line}, columna {column}: "
                    f"Símbolo inesperado '{token_type}'"
                )

            output_rows.append([step, stack_str, input_str, action])
            step += 1

        # Verificar si la pila y entrada están vacías (excepto por $)
        if index < len(tokens_copy) - 1:  # Si no hemos consumido todos los tokens
            current_token = tokens_copy[index]
            raise SyntaxError(
                f"Error: entrada no completamente consumida. "
                f"Símbolo inesperado '{current_token[0]}'"
            )

        print("\n¡Análisis sintáctico exitoso!\n")
        print(tabulate(output_rows, headers=["Paso", "Pila", "Entrada", "Acción"], tablefmt="grid"))
        
        # Devolver la raíz del árbol sintáctico
        return root_node