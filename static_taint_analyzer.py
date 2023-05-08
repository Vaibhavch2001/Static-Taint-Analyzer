from pycparser import c_parser, c_ast
import re

# regular expression to match #include statements
include_pattern = re.compile(r'^\s*#include\s*.*$')

# Taint Analyzer class inheriting from NodeVisitor class to define our taints while the AST is being visited
class TaintAnalyzer(c_ast.NodeVisitor):
    def __init__(self):
        self.tainted_variables = set()

    #Function which can be used to manually taint some variables
    def set_taint(self, var):
        self.tainted_variables.add(var)

    #Function which removes include statements from the c code since it is not supported by pycparser
    def remove_includes_from_c_code(self,code):
        lines = code.split('\n')
        lines = [line for line in lines if not include_pattern.match(line)]
        return '\n'.join(lines)

    #Overrinding visit_Assignment Function which sets taint to left operand on basis of right operand
    def visit_Assignment(self, node):
        if isinstance(node.rvalue, c_ast.ID) and node.rvalue.name in self.tainted_variables:
            self.tainted_variables.add(node.lvalue.name)
            print("Tainted variable:",node.lvalue.name)
        elif self.trav(node.rvalue):
            self.tainted_variables.add(node.lvalue.name)
            print("Tainted variable:", node.lvalue.name)
        elif isinstance(node.lvalue, c_ast.ID) and node.lvalue.name in self.tainted_variables:
            self.tainted_variables.discard(node.lvalue.name)
            print("Discared taint from:", node.lvalue.name)

    #Helper function to find out if a complex statement has a tainted variable or not
    #Returns true is some variable is tainted else false
    def trav(self,node):
        if type(node) is not c_ast.BinaryOp and type(node) is c_ast.ID:
             return node.name in self.tainted_variables
        elif type(node) is c_ast.FuncCall:
            self.visit(node)
            for arg in node.args.exprs:
                if type(arg) is c_ast.ID and arg.name in self.tainted_variables: return True
            return False
        elif type(node) is not c_ast.BinaryOp: return False
        leftAns = self.trav(node.left)
        rightAns = self.trav(node.right)
        return leftAns or rightAns

    #Overrinding visit_If Function which sets taint to left hand value of all assignment statements inside the if, else
    # block if the condition in the if contains a tainted variable
    def visit_If(self,node):
        print(node.show)
        if self.trav(node.cond):
            for statement in node.iftrue.block_items + node.iffalse.block_items:
                if type(statement) is c_ast.Assignment:
                    self.tainted_variables.add(statement.lvalue.name)
                    print("Tainted Variable:",statement.lvalue.name)

    #Overrinding visit_FuncCall Function to identify sources and sinks on basis of functions invoked
    def visit_FuncCall(self, node):
        if isinstance(node.name, c_ast.ID) and node.name.name == "gets":
            for arg in node.args.exprs:
                if isinstance(arg, c_ast.ID):
                    self.tainted_variables.add(arg.name)
                    print("Tainted variable:",arg.name)

        elif isinstance(node.name, c_ast.ID) and node.name.name == "scanf":
            for arg in node.args.exprs[1:]:
                if isinstance(arg, c_ast.UnaryOp) and isinstance(arg.expr, c_ast.ID):
                    self.tainted_variables.add(arg.expr.name)
                    print("Tainted variable:",arg.expr.name)

        elif isinstance(node.name, c_ast.ID) and node.name.name == 'fgets':
            self.tainted_variables.add(node.args.exprs[0].name)
            print("Tainted variable:",node.args.exprs[0].name)

        elif isinstance(node.name, c_ast.ID) and node.name.name == "printf":
            for arg in node.args.exprs[1:]:
                if isinstance(arg, c_ast.ID) and arg.name in self.tainted_variables:
                    print("Tainted variable:",arg.name,", possibly reaching sink - printf()")

        elif isinstance(node.name, c_ast.ID) and node.name.name == "system":
            if isinstance(node.args.exprs[0], c_ast.ID) and node.args.exprs[0].name in self.tainted_variables:
                print("Tainted variable:",node.args.exprs[0].name,", possibly reaching sink - system()")

        self.generic_visit(node)

    #Analyze function of class which should be invoked with input C file name for analysis
    def analyze(self, file_path):
        try:
            with open(file_path, 'r') as f:
                code = f.read()
        except FileNotFoundError:
            print("Error: file not found")
            return
        parser = c_parser.CParser()
        filtered_code = self.remove_includes_from_c_code(code)
        try:
            ast = parser.parse(filtered_code)
        except:
            print("Error parsing the C code, please check if it's syntactically correct")
            return
        self.visit(ast)

analyzer = TaintAnalyzer()
analyzer.analyze("input.c")
print("Final tainted variables are : ",analyzer.tainted_variables)
