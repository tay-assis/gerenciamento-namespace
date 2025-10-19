from flask import Flask, render_template_string, request, jsonify
import mysql.connector
import subprocess
import os

app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="namespace"
)

# --- Rota principal (formulário) ---
@app.route("/", methods=["POST", "GET"])
def index():
    # Pega os dados do formulário
    pid = request.form.get("namespace_pid") or None
    cpu = request.form.get("namespace_cpu")
    mem = request.form.get("namespace_mem")
    script = request.form.get("script")

    if request.method == "POST":
        try:
            cursor = db.cursor()

            query = """
                INSERT INTO namespace (namespace_pid, namespace_cpu, namespace_mem, script)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (pid, cpu, mem, script))
            # armazena as mudanças no banco de maneira permanente (usada no insert, update, delete)
            # se não utilizar o commit, as mudanças não serão salvas quando o programa terminar
            db.commit()
            cursor.close()

            return f"Namespace inserido com sucesso! Script: {script}"

        except mysql.connector.Error as err:
            return f"Erro ao inserir no banco: {err}"

    # HTML simples do formulário
    html_form = """
    <h2>Inserir Namespace</h2>
    <form method="POST">

        <label>CPU (%):</label><br>
        <input type="number" name="namespace_cpu" min="0" max="255" required><br><br>

        <label>Memória (MB):</label><br>
        <input type="number" name="namespace_mem" min="1" max="9999" required><br><br>

        <label>Script:</label><br>
        <input type="text" name="script" maxlength="500" required><br><br>

        <button type="submit">Enviar</button>
    </form>
    <br>
    <form action="/lista" method="GET">
        <button type="submit">Lista</button>
    </form>
    """
    return render_template_string(html_form)

@app.route("/lista", methods=["GET"])
def lista():
    try:
        # cursor é o que faz a comunicação com o banco
        cursor = db.cursor()

        query = """
            SELECT * FROM namespace
        """
        # cursor aqui executa a query direto no banco
        cursor.execute(query)
        # cursor traz os resultados das querys e guarda na variável results de maneira temporaria usando fetchall()
        results = cursor.fetchall()
        # fecha a conexão com o banco após o uso
        cursor.close()

        # Construir uma resposta HTML simples para exibir os resultados
        response_html = "<h2>Lista de Namespaces</h2><ul>"
        for row in results:
            response_html += f"<li>ID: {row[0]}, PID: {row[1]}, CPU: {row[2]}%, Memória: {row[3]}MB, Script: {row[4]}</li>"
        response_html += "</ul><a href='/'>Voltar</a>"

        return response_html

    except mysql.connector.Error as err:
        return f" Erro ao listar no banco: {err}"

@app.route("/get_db", methods=["GET"])
def db_test():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM namespace;")
    result = cursor.fetchall()
    cursor.close()
    return str(result)

# BASE_DIR = "/containers"

# NAMESPACE_CLI = "/namespace.sh"  # caminho absoluto do script

# @app.route("/")
# def index():
#     print("Testing database connection...")
#     return "API de Gerenciamento de Namespaces"

# @app.route("/create", methods=["POST"])
# def create_namespace():
#     data = request.json
#     namespace_id = data["namespace_id"]
#     cpu = str(data["cpu"])
#     mem = str(data["mem"])
#     script = data["script"]
#     try:
#         subprocess.run(
#             [NAMESPACE_CLI, "create", namespace_id, cpu, mem, script],
#             check=True
#         )
#         return jsonify({"status": "sucesso"}), 201
#     except subprocess.CalledProcessError as e:
#         return jsonify({"status": "erro", "msg": str(e)}), 500


# @app.route("/delete", methods=["POST"])
# def delete_namespace():
#     data = request.json
#     namespace_id = data["namespace_id"]
#     try:
#         subprocess.run(
#             [NAMESPACE_CLI, "delete", namespace_id],
#             check=True
#         )
#         return jsonify({"status": "sucesso"})
#     except subprocess.CalledProcessError as e:
#         return jsonify({"status": "erro", "msg": str(e)}), 500

# @app.route("/list", methods=["GET"])
# def list_namespaces():
#     namespaces = []
#     for name in os.listdir(BASE_DIR):
#         pid_file = os.path.join(BASE_DIR, name, "pid")
#         if not os.path.exists(pid_file):
#             continue
#         with open(pid_file) as f:
#             pid = f.read().strip()
#         status = "Em execução" if os.path.exists(f"/proc/{pid}") else "Terminado"
#         namespaces.append({"name": name, "pid": pid, "status": status})
#     return jsonify(namespaces)

if __name__ == "__main__":
    app.run(debug=True)
