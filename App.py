from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)
BASE_DIR = "/containers"

NAMESPACE_CLI = "/namespace.sh"  # caminho absoluto do script

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
