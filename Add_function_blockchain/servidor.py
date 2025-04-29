from flask import Flask, request, jsonify
import os
import subprocess
import threading
import signal
import hashlib
import json
from time import time
from datetime import datetime

app = Flask(__name__)

FUNCIONES_DIR = "/home/nano/Desktop/util/flask/funciones_server002"
os.makedirs(FUNCIONES_DIR, exist_ok=True)

AUTH_KEY = "lsd2025"
process = None

# Blockchain clases
class UpdateBlock:
    def __init__(self, index, timestamp, version, script_name, script_hash, previous_hash, hash=None):
        self.index = index
        self.timestamp = timestamp
        self.version = version
        self.script_name = script_name
        self.script_hash = script_hash
        self.previous_hash = previous_hash
        self.hash = hash if hash else self.calculate_hash()

    def calculate_hash(self):
        block_content = f"{self.index}{self.timestamp}{self.version}{self.script_name}{self.script_hash}{self.previous_hash}"
        return hashlib.sha256(block_content.encode()).hexdigest()

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "version": self.version,
            "script_name": self.script_name,
            "script_hash": self.script_hash,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class UpdateBlockchain:
    def __init__(self):
        self.chain = []

    def load_chain(self, filename="update_chain.json"):
        if os.path.exists(filename):
            with open(filename, "r") as f:
                data = json.load(f)
                self.chain = [UpdateBlock.from_dict(b) for b in data]
        else:
            self.chain = []
            self.save_chain()

    def get_last_block(self):
        return self.chain[-1] if self.chain else None

    def is_valid_new_block(self, new_block):
        last_block = self.get_last_block()
        if last_block:
            expected_index = last_block.index + 1
            expected_prev_hash = last_block.hash
            expected_hash = new_block.calculate_hash()

            return (
                new_block.index == expected_index and
                new_block.previous_hash == expected_prev_hash and
                new_block.hash == expected_hash
            )
        return False

    def add_block(self, block):
        self.chain.append(block)

    def save_chain(self, filename="update_chain.json"):
        with open(filename, "w") as f:
            json.dump([b.to_dict() for b in self.chain], f, indent=4)

    def save_last_block(self, filename="last_update.json"):
        if self.chain:
            with open(filename, "w") as f:
                json.dump(self.get_last_block().to_dict(), f, indent=4)

# Utilidades
def log_event(mensaje):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {mensaje}"
    print(log_line)
    with open("log_ejecuciones.txt", "a") as f:
        f.write(log_line + "\n")

def autenticado(req):
    return req.headers.get("X-Auth-Key") == AUTH_KEY

@app.route("/genesis", methods=["POST"])
def recibir_genesis():
    if not autenticado(request):
        return "No autorizado", 401

    if "json" not in request.files:
        return "Falta el bloque Genesis JSON", 400

    bloque_json = request.files["json"]

    # Cargar bloque desde el JSON
    bloque_data = json.load(bloque_json)
    nuevo_bloque = UpdateBlock.from_dict(bloque_data)

    # Cargar y validar blockchain
    bc = UpdateBlockchain()
    bc.load_chain()

    # Si no hay cadena (es decir, no se ha recibido el bloque génesis aún), agregar el bloque génesis
    if not bc.chain:
        bc.add_block(nuevo_bloque)
        bc.save_chain()
        bc.save_last_block()
        log_event(f"✅ Bloque génesis recibido y almacenado: {nuevo_bloque.version}")
        return f"Bloque génesis recibido y almacenado", 200
    else:
        log_event("❌ Bloque génesis ya existe, no es necesario recibirlo de nuevo.")
        return "Bloque génesis ya existe", 400

@app.route("/subir", methods=["POST"])
def subir_funcion_y_bloque():
    if not autenticado(request):
        return "No autorizado", 401

    if "file" not in request.files or "json" not in request.files:
        return "Faltan archivo o bloque JSON", 400

    archivo = request.files["file"]
    bloque_json = request.files["json"]

    # Cargar bloque desde el JSON
    bloque_data = json.load(bloque_json)
    nuevo_bloque = UpdateBlock.from_dict(bloque_data)

    # Calcular hash del contenido del archivo recibido (sin guardarlo)
    contenido = archivo.read()
    script_hash = hashlib.sha256(contenido).hexdigest()

    if script_hash != nuevo_bloque.script_hash:
        log_event("❌ Hash del script no coincide con el del bloque.")
        return "Hash del script no válido", 400

    # Cargar y validar blockchain
    bc = UpdateBlockchain()
    bc.load_chain()

    if not bc.is_valid_new_block(nuevo_bloque):
        log_event("❌ El bloque no es válido según la cadena.")
        return "Bloque inválido", 400

    # Si todo es válido, guardar el archivo en disco
    nombre_script = os.path.join(FUNCIONES_DIR, archivo.filename)
    with open(nombre_script, "wb") as f:
        f.write(contenido)
    log_event(f"Script recibido: {archivo.filename}")

    # Añadir bloque
    bc.add_block(nuevo_bloque)
    bc.save_chain()
    bc.save_last_block()
    log_event(f"✅ Bloque válido añadido: {nuevo_bloque.version}")

    return f"Script y bloque {nuevo_bloque.version} subidos y validados", 200

@app.route("/ejecutar/<nombre>", methods=["POST"])
def ejecutar_funcion(nombre):
    global process

    if not autenticado(request):
        return "No autorizado", 401

    archivo = os.path.join(FUNCIONES_DIR, nombre)
    if not os.path.exists(archivo):
        return "Archivo no encontrado", 404

    if process:
        return "Ya hay un proceso en ejecución. Detenelo antes de ejecutar otro.", 400

    def run_script():
        global process
        local_process = subprocess.Popen(
            ["python3", archivo],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            preexec_fn=os.setsid
        )
        process = local_process
        log_event(f"Script iniciado: {nombre}")

        for line in local_process.stdout:
            print(line, end="")

        local_process.wait()
        log_event(f"Script terminado: {nombre}")
        process = None

    threading.Thread(target=run_script).start()
    return f"Ejecución de {nombre} iniciada", 200

@app.route("/detener", methods=["POST"])
def detener_script():
    global process

    if not autenticado(request):
        return "No autorizado", 401

    if process:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        log_event("Script detenido manualmente")
        process = None
        return "Proceso detenido", 200
    else:
        return "No hay un proceso en ejecución", 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)



