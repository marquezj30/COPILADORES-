# parser.py
import csv
from tabulate import tabulate 


class LL1Parser:
    def __init__(self, parsing_table_file, start_symbol='S'):
        self.start_symbol = start_symbol
        self.parsing_table = self.load_parsing_table(parsing_table_file)
        print("\nTabla cargada:")
        for non_terminal, productions in self.parsing_table.items():
            print(f"{non_terminal}: {productions}")

    def load_parsing_table(self, file):
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
        print("\nTabla cargada (verificación):")
        for nt in table:
            print(f"{nt}: {table[nt]}")
        
        return table


    def parse(self, tokens):#RECIVIMOS LA LISTA DE TOKENS
        stack = ['$', self.start_symbol]#INICIAMOS LA PILA CON $ Y CON "S"
        index = 0
        tokens.append(('$', '$', -1, -1))  # EOF marker

        output_rows = []#ABRIMOS ESTA LISTA PARA GUARDAR LOS PASOS DEL ANALISIS
        step = 1

        while stack:#INICIAMOS EL BUCLE SI LA PILA NO ESTA VACÍA
            top = stack.pop()#saca el simbolo de la cima de la pila
            current_token = tokens[index]
            token_type = current_token[0]#toma el token actual y su tipo

            stack_str = ' '.join(reversed(stack + [top]))  # Incluye el top que se sacó
            input_str = ' '.join([tok[0] for tok in tokens[index:]])#  los tokens que aún no han sido consumidos.
            action = '' # se usara para el mensaje de la acción

            if top == 'e':
                action = 'Epsilon (e), se omite'
            elif top == token_type:
                action = f"[Match] {top}"
                index += 1#si top coincide con el token actual se aanza el indice
            elif top in self.parsing_table:
                production = self.parsing_table[top].get(token_type, None)
                if production:
                    action = f"[Expand] {top} → {production}"
                    stack.extend(reversed(production.split()))#se colocan al reves los simbolos a la pila
                else:
                    raise SyntaxError(#Error sintactico
                        f"Error en línea {current_token[2]}, columna {current_token[3]}: "
                        f"No hay producción para {top} → {token_type}"
                    )
            else:
                raise SyntaxError(#no es ni terminal, ni no terminal, ni epsilon. se considera error 
                    f"Error en línea {current_token[2]}, columna {current_token[3]}: "
                    f"Símbolo inesperado '{token_type}'"
                )

            output_rows.append([step, stack_str, input_str, action]) #GUARDAMOS EL PASO REALIZADO EN LA TABLA
            step += 1

        if index != len(tokens) - 1:# verificamos que los tokens se consuman, si no es error
            current_token = tokens[index]
            raise SyntaxError(
                f"Error: entrada no completamente consumida. "
                f"Símbolo inesperado '{current_token[0]}'"
            )

        print("\n¡Análisis sintáctico exitoso!\n")
        print(tabulate(output_rows, headers=["Paso", "Pila", "Entrada", "Acción"], tablefmt="grid"))
