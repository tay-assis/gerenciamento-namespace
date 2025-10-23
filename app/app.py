from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import subprocess, os, time

app = Flask(__name__)

db = mysql.connector.connect(

    host="localhost",
    user="user",
    password="password",
    database="namespace"
)

@app.route('/')
def index():
    return render_template('index.html')


import os
import subprocess
import json
from flask import Flask, request
import mysql.connector

app = Flask(__name__)

@app.route('/criar_namespace', methods=['POST'])
def criar_namespace():
    nome = request.form.get('nome')
    cpu = request.form.get('cores')
    memoria = request.form.get('memoria')
    io = request.form.get('io')
    script = request.form.get('script')

    print(nome, cpu, memoria, io, script)
    try:
        script_path = os.path.join(os.getcwd(), "create_namespace.sh")
        print("📂 Caminho do script:", script_path)

        # Executa o script bash
        process = subprocess.Popen(
        ["sudo", "bash", script_path, nome, cpu, memoria, io, script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
        )

        # Espera alguns segundos pra capturar logs iniciais
        time.sleep(2)

        # Captura o que foi impresso até agora
        stdout = process.stdout.read()
        stderr = process.stderr.read()

        # Procura pid no arquivo gerado
        pid_file = f"./containers/namespaces/{nome}/pid"
        for i in range(10):  # tenta por até ~10 segundos
            if os.path.exists(pid_file) and os.path.getsize(pid_file) > 0:
                with open(pid_file) as f:
                    pid = f.read().strip()
                break 

        time.sleep(1)
        # NÃO espera o processo terminar — ele continua rodando
        stdout, stderr = process.communicate(timeout=5)
        print("⚙️ STDOUT:", stdout)
        print("⚠️ STDERR:", stderr)
        print("🐧 PID capturado:", pid) 

        # Verifica erro de execução
        if os.path.exists(f"/proc/{pid}"):
            status = "running"
        else:
            status = "terminated"

        # Insere no banco
        try:
            cursor = db.cursor()
            query = """
                INSERT INTO namespace (namespace_name, namespace_cpu, namespace_mem, namespace_io, script, pid, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (nome, cpu, memoria, io, script, pid, status))
            db.commit()
            cursor.close()

            return f"✅ Namespace '{nome}' criado com sucesso! PID={pid}, Status={status}"

        except mysql.connector.Error as err:
            print("❌ Erro MySQL:", err)
            return f"Erro ao inserir no banco: {err}", 500

    except Exception as e:
        print("❌ Erro geral:", e)
        return f"Erro inesperado: {e}", 500

    

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
        cursor.execute("SELECT namespace_name FROM namespace WHERE id = %s", (ns_id,))
        result = cursor.fetchone()

        if not result:
            cursor.close()
            return f"❌ Namespace com ID {ns_id} não encontrado no banco.", 404

        namespace_name = result[0]
        cursor.close()
        script_path = os.path.join(os.getcwd(), "delete_namespace.sh")
        result = subprocess.run(
            ["sudo", "bash", script_path, namespace_name],
            capture_output=True,
            text=True
        )

        print("⚙️ STDOUT:", result.stdout)
        print("⚠️ STDERR:", result.stderr)

        if result.returncode != 0:
            return f"❌ Erro ao remover namespace físico:<br><pre>{result.stderr}</pre>", 500
        cursor = db.cursor()
        cursor.execute("DELETE FROM namespace WHERE id = %s", (ns_id,))
        db.commit()
        cursor.close()

        print(f"✅ Namespace '{namespace_name}' (ID={ns_id}) removido do sistema e do banco.")
        return redirect(url_for('monitorar'))

    except mysql.connector.Error as err:
        return f"❌ Erro MySQL: {err}", 500

    except Exception as e:
        return f"❌ Erro inesperado: {e}", 500
    
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


