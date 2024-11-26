from flask import Flask, render_template, request, jsonify, send_file
import ast
from graphviz import Digraph
import os
import time
import ply.lex as lex
import math  # Añadido para funciones matemáticas

app = Flask(__name__)

# Configuración de tokens para PLY
tokens = (
    'INTEGER',
    'DECIMAL',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'LPAREN',
    'RPAREN',
    'EULER',
    'SQRT',
    'POWER'  # Añadido para potencia
)

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_EULER = r'e'
t_SQRT = r'sqrt'
t_POWER = r'\^'
t_ignore = ' \t'

def t_DECIMAL(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_INTEGER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()

def sanitize_expression(expression):
    allowed_chars = set('0123456789+-*/().esqrt^ ')
    return ''.join(c for c in expression if c in allowed_chars)

def generate_tree(expression):
    try:
        clean_expr = sanitize_expression(expression)
        if not clean_expr:
            return False

        timestamp = str(int(time.time() * 1000))
        filename = f'output_tree_{timestamp}'
        os.makedirs('trees', exist_ok=True)

        tree = ast.parse(clean_expr, mode='eval').body
        graph = Digraph()
        graph.attr(rankdir='TB')
        graph.node_attr['color'] = 'black'
        graph.graph_attr['bgcolor'] = 'white'
        graph.node_attr['fontcolor'] = 'black'
        build_graph(tree, graph)

        output_path = os.path.join('trees', filename)
        graph.render(output_path, format='png', cleanup=True)
        return filename
    except Exception as e:
        print(f"Error generating tree: {e}")
        return False

def build_graph(node, graph, parent=None):
    node_id = str(id(node))

    if isinstance(node, ast.BinOp):
        op_name = type(node.op).__name__
        op_symbols = {
            'Add': '+',
            'Sub': '-',
            'Mult': '×',
            'Div': '÷',
            'Pow': '^'
        }
        display_name = op_symbols.get(op_name, op_name)
        graph.node(node_id, display_name, color='black')
        if parent:
            graph.edge(parent, node_id, color='black')
        build_graph(node.left, graph, node_id)
        build_graph(node.right, graph, node_id)

    elif isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            graph.node(node_id, func_name)
            if parent:
                graph.edge(parent, node_id, color='black')
            for arg in node.args:
                build_graph(arg, graph, node_id)

    elif isinstance(node, ast.Num):
        graph.node(node_id, str(node.n))
        if parent:
            graph.edge(parent, node_id, color='black')
    elif isinstance(node, ast.Name) and node.id == 'e':
        graph.node(node_id, 'e')
        if parent:
            graph.edge(parent, node_id, color='black')        
    elif isinstance(node, ast.Expression):
        build_graph(node.body, graph, parent)
    else:
        raise ValueError(f"Unsupported node type: {type(node).__name__}")


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
def calculate():
    expression = request.form.get("expression", "").strip()
    if not expression:
        return jsonify({"error": "Empty expression"}), 400

    try:
        # Tokenize the expression
        lexer.input(expression)
        tokens_list = list(lexer)
        
        # Count tokens
        total_tokens = len(tokens_list)
        total_integers = sum(1 for tok in tokens_list if tok.type == 'INTEGER')
        total_decimals = sum(1 for tok in tokens_list if tok.type == 'DECIMAL')
        total_operators = sum(1 for tok in tokens_list if tok.type in ('PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'POWER'))

        # Calculate result with safe context
        safe_eval_globals = {
            'e': math.e, 
            'sqrt': math.sqrt, 
            '^': lambda x, y: x**y  # Añadido soporte para potencia
        }
        result = eval(sanitize_expression(expression), safe_eval_globals)

        tree_filename = generate_tree(expression)

        return jsonify({
            "result": result,
            "tree": f"/trees/{tree_filename}.png" if tree_filename else None,
            "tokens": [tok.value for tok in tokens_list],
            "total_tokens": total_tokens,
            "total_integers": total_integers,
            "total_decimals": total_decimals,
            "total_operators": total_operators
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/trees/<filename>")
def get_tree(filename):
    try:
        return send_file(f"trees/{filename}", mimetype='image/png')
    except Exception:
        return "Tree not found", 404

if __name__ == "__main__":
    app.run(debug=True)