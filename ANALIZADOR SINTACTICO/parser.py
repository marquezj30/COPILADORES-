# parser.py
import csv
from collections import deque

class BottomUpParser:
    def __init__(self, parsing_table_file):
        self.parsing_table = self.load_parsing_table(parsing_table_file)
        self.grammar_rules = {}

    def load_parsing_table(self, file):
        table = {}
        with open(file, newline='') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)
            terminals = headers[1:]
            for row in reader:
                non_terminal = row[0]
                table[non_terminal] = dict(zip(terminals, row[1:]))
        return table

    def set_grammar_rules(self, rules):
        self.grammar_rules = rules

    def parse(self, tokens):
        stack = deque(["$"])
        input_tokens = deque(token[0] for token in tokens)
        while True:
            top = stack[-1]
            current = input_tokens[0]

            if top == current == "$":
                print("Input is syntactically correct.")
                return

            elif top in self.parsing_table and current in self.parsing_table[top]:
                rule = self.parsing_table[top][current]
                if rule:
                    stack.pop()
                    if rule != "epsilon":
                        for sym in reversed(rule.split()):
                            stack.append(sym)
                else:
                    self.error(current, tokens)
            elif top == current:
                stack.pop()
                input_tokens.popleft()
            else:
                self.error(current, tokens)

    def error(self, token, tokens):
        for ttype, tval, line, col in tokens:
            if ttype == token:
                raise SyntaxError(f"Syntax error at token '{ttype}' (value: '{tval}') at line {line}, column {col}")
