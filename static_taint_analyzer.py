from pycparser import c_parser, c_ast
import re

# regular expression to match #include statements
include_pattern = re.compile(r'^\s*#include\s*.*$')

class TaintAnalyzer(c_ast.NodeVisitor):
    def __init__(self):
        self.tainted_variables = set()

    #Function which can be used to manually taint some variables
    def set_taint(self, var):
        self.tainted_variables.add(var)

    def remove_includes_from_c_code(self,code):
        lines = code.split('\n')
        lines = [line for line in lines if not include_pattern.match(line)]
        return '\n'.join(lines)

    def visit_Assignment(self, node):
        # self.visit(node.rvalue)
        if isinstance(node.rvalue, c_ast.ID) and node.rvalue.name in self.tainted_variables:
            self.tainted_variables.add(node.lvalue.name)
            print("Tainted variable:",node.lvalue.name)
        elif self.trav(node.rvalue):
        # elif isinstance(node.rvalue, c_ast.BinaryOp) and ((isinstance(node.rvalue.right,c_ast.ID) and node.rvalue.right.name in self.tainted_variables) or (isinstance(node.rvalue.left,c_ast.ID) and node.rvalue.left.name in self.tainted_variables)) :
            self.tainted_variables.add(node.lvalue.name)
            print("Tainted variable:", node.lvalue.name)
        elif isinstance(node.lvalue, c_ast.ID) and node.lvalue.name in self.tainted_variables:
            self.tainted_variables.discard(node.lvalue.name)
            print("Discared taint from:", node.lvalue.name)
        # self.visit(node.lvalue)

    # def visit_ID(self, node):
    #     if node.name in self.tainted_variables:
    #         print("Tainted variable used:", node.name)

    def trav(self,node):
        # print(node)
        if type(node) is not c_ast.BinaryOp and type(node) is c_ast.ID:
             if node.name in self.tainted_variables: return True
             else : return False
        elif type(node) is not c_ast.BinaryOp: return False
        leftAns = self.trav(node.left)
        rightAns = self.trav(node.right)
        return leftAns or rightAns

    def visit_If(self,node):
        if self.trav(node.cond):
            # print(node.iftrue.block_items[0])
            for assignment in node.iftrue.block_items:
                self.tainted_variables.add(assignment.lvalue.name)

    def visit_FuncCall(self, node):
        # print(node.name.name)
        if isinstance(node.name, c_ast.ID) and node.name.name == "gets":
            for arg in node.args.exprs:
                if isinstance(arg, c_ast.ID):
                    self.tainted_variables.add(arg.name)
        elif isinstance(node.name, c_ast.ID) and node.name.name == "scanf":
            for arg in node.args.exprs[1:]:
                if isinstance(arg, c_ast.UnaryOp) and isinstance(arg.expr, c_ast.ID):
                    self.tainted_variables.add(arg.expr.name)
                    print("Tainted variable:",arg.expr.name)
        elif isinstance(node.name, c_ast.ID) and node.name.name == "printf":
            for arg in node.args.exprs[1:]:
                if isinstance(arg, c_ast.ID) and arg.name in self.tainted_variables:
                    print("Tainted variable:",arg.name,", possibly reaching sink - printf")
        self.generic_visit(node)

    def analyze(self, file_path):
        try:
            with open(file_path, 'r') as f:
                code = f.read()
        except FileNotFoundError:
            print("Error: file not found")
        parser = c_parser.CParser()
        filtered_code = self.remove_includes_from_c_code(code)
        try:
            ast = parser.parse(filtered_code)
        except any:
            print("Error parsing the C code, please check if it's syntactically correct")
        # print(ast.ext[0].body.block_items)
        self.visit(ast)

analyzer = TaintAnalyzer()
analyzer.analyze("input.c")
print("Final tainted variables are : ",analyzer.tainted_variables)

#TODO -(DONE) Add logic to remove includes from c code if there
#TODO - Add logic if input to function is tainted then taint it's return value(Implicit tainting in function call)
#TODO - Have customizable source sink options for TaintAnalyzer class
#TODO - Ask ma'am if we need to support python code as well
#TODO - (Done) Use file to read code, Pass file name to analyze function
#TODO - 2 modes, self tainting using set_taint function, use scanf and gets function to taint manually
