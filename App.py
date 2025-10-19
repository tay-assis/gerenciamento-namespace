from flask import Flask, request, jsonify
import mysql.connector
import subprocess
import os

app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="namespaces"
)

@app.route("/get_db", methods=["GET"])
def db_test():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM namespace;")
    result = cursor.fetchall()
    cursor.close()
    return str(result)

# @app.route("/put_db", methods=["PUT"])
# def get_db():
#     data = request.json
#     db_name = data["namespace"]
#     cursor = db.cursor()
#     cursor.execute(f"USE {db_name};")
#     cursor.execute("SHOW TABLES;")
#     cursor.execute(f"INSERT INTO {db_name} (namespace_cpu, namespace_mem, script) VALUES (50, 2048, 'init');")
#     result = cursor.fetchall()
#     cursor.close()
#     return str(result)

BASE_DIR = "/containers"

NAMESPACE_CLI = "/namespace.sh"  # caminho absoluto do script

@app.route("/")
def index():
    print("Testing database connection...")
    return "API de Gerenciamento de Namespaces"

@app.route("/create", methods=["POST"])
def create_namespace():
    data = request.json
    namespace_id = data["namespace_id"]
    cpu = str(data["cpu"])
    mem = str(data["mem"])
    script = data["script"]
    try:
        subprocess.run(
            [NAMESPACE_CLI, "create", namespace_id, cpu, mem, script],
            check=True
        )
        return jsonify({"status": "sucesso"}), 201
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "erro", "msg": str(e)}), 500


@app.route("/delete", methods=["POST"])
def delete_namespace():
    data = request.json
    namespace_id = data["namespace_id"]
    try:
        subprocess.run(
            [NAMESPACE_CLI, "delete", namespace_id],
            check=True
        )
        return jsonify({"status": "sucesso"})
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "erro", "msg": str(e)}), 500

@app.route("/list", methods=["GET"])
def list_namespaces():
    namespaces = []
    for name in os.listdir(BASE_DIR):
        pid_file = os.path.join(BASE_DIR, name, "pid")
        if not os.path.exists(pid_file):
            continue
        with open(pid_file) as f:
            pid = f.read().strip()
        status = "Em execução" if os.path.exists(f"/proc/{pid}") else "Terminado"
        namespaces.append({"name": name, "pid": pid, "status": status})
    return jsonify(namespaces)

if __name__ == "__main__":
    app.run(debug=True)
