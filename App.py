from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

db = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "password",
    database = "namespace"
)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/criar_namespace', methods=['POST'])
def criar_namespace():
    nome = request.form.get('nome')
    cpu = request.form.get('cores')
    memoria = request.form.get('memoria')
    io = request.form.get('io')
    script = request.form.get('script')

    print(nome, cpu, memoria, io, script) 

    try:
        cursor = db.cursor()

        query = """
            INSERT INTO namespace (namespace_name, namespace_cpu, namespace_mem, namespace_io, script)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (nome, cpu, memoria, io, script))
        # armazena as mudanças no banco de maneira permanente (usada no insert, update, delete)
        # se não utilizar o commit, as mudanças não serão salvas quando o programa terminar
        db.commit()
        cursor.close()

        return f"Namespace inserido com sucesso! Script: {script}"

    except mysql.connector.Error as err:
        return f"Erro ao inserir no banco: {err}"
    

@app.route('/monitorar', methods=['GET'])
def monitorar():
    try:
        cursor = db.cursor(dictionary=True)  # retorna dicionários
        cursor.execute("SELECT * FROM namespace")
        results = cursor.fetchall()
        cursor.close()

        return render_template('monitorar.html', namespaces=results)

    except mysql.connector.Error as err:
        return f"Erro ao listar no banco: {err}"


@app.route('/ver_log/<int:ns_id>')
def ver_log(ns_id):
    # Aqui futuramente você pode abrir o arquivo de log correspondente
    print(f"Visualizando log do namespace {ns_id}")
    return f"Exibindo log do namespace {ns_id}"

@app.route('/encerrar/<int:ns_id>', methods=['POST'])
def encerrar_namespace(ns_id):
    for ns in namespaces:
        if ns["id"] == ns_id:
            ns["status"] = "terminado"
    return redirect(url_for('monitorar'))

@app.route('/remover/<int:ns_id>', methods=['POST'])
def remover_namespace(ns_id):
    try:
        cursor = db.cursor()
        query = "DELETE FROM namespace WHERE namespace_id = %s"
        cursor.execute(query, (ns_id,))
        db.commit()
        cursor.close()
        return redirect(url_for('monitorar'))
    except mysql.connector.Error as err:
        return f"Erro ao remove do banco: {err}"
    
@app.route('/ver_status/<int:ns_id>', methods=['GET'])
def ver_status(ns_id):
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT status FROM namespace WHERE namespace_id = %s", (ns_id,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            status = result["status"]
            return f"Status do namespace {ns_id}: {status}"
        else:
            return f"Namespace {ns_id} não encontrado."
    except mysql.connector.Error as err:
        return f"Erro ao consultar status: {err}"
    


# PARTE DO PEDRO ----------------------------------------------------------------

# from flask import Flask, request, jsonify
# import subprocess
# import os

# app = Flask(__name__)
# BASE_DIR = "/containers"

# NAMESPACE_CLI = "/namespace.sh"  # caminho absoluto do script

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

# if __name__ == "__main__":
#     app.run(debug=True)



