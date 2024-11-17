from flask import Flask, render_template, request, jsonify, send_file
import ast
from graphviz import Digraph
import os
import time

app = Flask(__name__)

def sanitize_expression(expression):
    """Sanitiza la expresión para hacerla segura para ast.parse"""
    allowed_chars = set('0123456789+-*/(). ')
    return ''.join(c for c in expression if c in allowed_chars)

def generate_tree(expression):
    try:
        # Sanitizar la expresión
        clean_expr = sanitize_expression(expression)
        if not clean_expr:
            return False

        # Generar un nombre único para el archivo
        timestamp = str(int(time.time() * 1000))
        filename = f'output_tree_{timestamp}'
        
        # Crear el directorio trees si no existe
        os.makedirs('trees', exist_ok=True)
        
        # Generar el árbol
        tree = ast.parse(clean_expr, mode='eval').body
        graph = Digraph()
        graph.attr(rankdir='TB')  # Top to Bottom direction
        build_graph(tree, graph)
        
        # Renderizar con el nombre único
        output_path = os.path.join('trees', filename)
        graph.render(output_path, format='png', cleanup=True)
        
        return filename
    except Exception as e:
        print(f"Error al generar el árbol: {e}")
        return False

def build_graph(node, graph, parent=None):
    node_id = str(id(node))
    
    if isinstance(node, ast.BinOp):
        op_name = type(node.op).__name__
        # Mapear nombres de operadores a símbolos
        op_symbols = {
            'Add': '+',
            'Sub': '-',
            'Mult': '×',
            'Div': '÷'
        }
        display_name = op_symbols.get(op_name, op_name)
        graph.node(node_id, display_name)
        if parent:
            graph.edge(parent, node_id)
        build_graph(node.left, graph, node_id)
        build_graph(node.right, graph, node_id)
    
    elif isinstance(node, ast.Num):
        graph.node(node_id, str(node.n))
        if parent:
            graph.edge(parent, node_id)
    
    elif isinstance(node, ast.Expression):
        build_graph(node.body, graph, parent)
    
    else:
        raise ValueError(f"Tipo de nodo no soportado: {type(node).__name__}")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
def calculate():
    expression = request.form.get("expression", "").strip()
    if not expression:
        return jsonify({"error": "Expresión vacía"}), 400
    
    try:
        # Calcular el resultado
        result = eval(sanitize_expression(expression))
        
        # Generar el árbol
        tree_filename = generate_tree(expression)
        if tree_filename:
            # Devolver la ruta al nuevo archivo
            return jsonify({
                "result": result,
                "tree": f"/trees/{tree_filename}.png"
            })
        else:
            return jsonify({"error": "No se pudo generar el árbol"}), 500
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/trees/<filename>")
def get_tree(filename):
    try:
        return send_file(f"trees/{filename}", mimetype='image/png')
    except Exception:
        return "Árbol no encontrado", 404

if __name__ == "__main__":
    app.run(debug=True)