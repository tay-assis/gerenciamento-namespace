from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import subprocess, os, time, json, logging, sys


app = Flask(__name__)

#CONFIGURAÇÕES DE LOG
log_path = "namespace.log"
log_format = "%(asctime)s - %(levelname)s - %(message)s"

#Configuração base (grava em arquivo)
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler(sys.stdout)  # 👈 mantém saída no terminal
    ]
)

werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.INFO)
werkzeug_logger.addHandler(logging.FileHandler(log_path))
werkzeug_logger.addHandler(logging.StreamHandler(sys.stdout))

#CONEXÃO COM BANCO DE DADOS
db = mysql.connector.connect(

    host="localhost",
    user="user",
    password="password",
    database="namespace"
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
        script_path = os.path.join(os.getcwd(), "create_namespace.sh")
        # Executa o script bash
        process = subprocess.Popen(
        ["sudo", "bash", script_path, nome, cpu, memoria, io, script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
        )
        # Procura pid no arquivo gerado
        pid_file = f"./containers/namespaces/{nome}/pid"
        timeout = 10  # segundos
        start_time = time.time()
        pid = None

        while time.time() - start_time < timeout:
            if os.path.exists(pid_file) and os.path.getsize(pid_file) > 0:
                with open(pid_file) as f:
                    pid = f.read().strip()
                break
            time.sleep(0.5)

        if not pid:
            return f"❌ Erro: arquivo de PID não encontrado após {timeout}s. Saída do script:\n{process.stderr.read()}", 500
      

        # Verifica status do namespace
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
    app.logger.info(f"Namespace '{nome}' criado (PID {pid}) pelo IP {request.remote_addr}")


    

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



@app.route('/encerrar/<int:ns_id>', methods=['POST'])
def encerrar_namespace(ns_id):
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT namespace_name, pid FROM namespace WHERE id = %s", (ns_id,))
        result = cursor.fetchone()
        cursor.close()

        if not result:
            return f" Namespace com ID {ns_id} não encontrado.", 404

        nome = result["namespace_name"]
        pid = result["pid"]

        #  Tenta encerrar o processo
        try:
            subprocess.run(["sudo", "kill", "-TERM", str(pid)], check=False)
            subprocess.run(["sudo", "pkill", "-TERM", "-P", str(pid)], check=False)
            subprocess.run(["sudo", "pkill", "-9", "-P", str(pid)], check=False)
            status = "terminated"

        except subprocess.CalledProcessError:
            status = "already stopped"

        # Atualiza o status no banco
        cursor = db.cursor()
        cursor.execute("UPDATE namespace SET status = %s WHERE id = %s", (status, ns_id))
        db.commit()
        cursor.close()
        app.logger.info(f"Namespace '{nome}' (PID {pid}) encerrado pelo IP {request.remote_addr}")
        return redirect(url_for('monitorar'))

    except mysql.connector.Error as err:
        return f"Erro ao encerrar namespace: {err}", 500

@app.route('/remover/<int:ns_id>', methods=['POST'])
def remover_namespace(ns_id):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT namespace_name FROM namespace WHERE id = %s", (ns_id,))
        result = cursor.fetchone()

        if not result:
            cursor.close()
            return f" Namespace com ID {ns_id} não encontrado no banco.", 404

        namespace_name = result[0]
        cursor.close()
        script_path = os.path.join(os.getcwd(), "delete_namespace.sh")
        result = subprocess.run(
            ["sudo", "bash", script_path, namespace_name],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return f" Erro ao remover namespace físico:<br><pre>{result.stderr}</pre>", 500
        cursor = db.cursor()
        cursor.execute("DELETE FROM namespace WHERE id = %s", (ns_id,))
        db.commit()
        cursor.close()

        print(f" Namespace '{namespace_name}' (ID={ns_id}) removido do sistema e do banco.")
        app.logger.info(f"Namespace '{namespace_name}' (ID {ns_id}) removido pelo IP {request.remote_addr}")
        return redirect(url_for('monitorar'))

    except mysql.connector.Error as err:
        return f" Erro MySQL: {err}", 500

    except Exception as e:
        return f" Erro inesperado: {e}", 500
    
@app.route('/ver_status/<int:ns_id>', methods=['GET'])
def ver_status(ns_id):
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT pid, namespace_name FROM namespace WHERE id = %s", (ns_id,))
        result = cursor.fetchone()
        cursor.close()

        if not result:
            return f" Namespace com ID {ns_id} não encontrado."

        pid = result["pid"]
        nome = result["namespace_name"]

        if os.path.exists(f"/proc/{pid}"):
            status = "running"
        else:
            status = "terminated"
        return f"Status do namespace '{nome}' (PID {pid}): {status}"

    except mysql.connector.Error as err:
        return f"Erro ao consultar status: {err}"

@app.route('/ver_log/<string:nome>')
def ver_log(nome):
    log_file= f"./containers/namespaces/{nome}/log.txt"
    if not log_file:
        return f"Nenhum log encontrado para '{nome}'"

    with open(log_file, "r") as f:
        conteudo = f.read()
    return f"<pre>{conteudo}</pre>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)



