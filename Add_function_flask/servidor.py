from flask import Flask, request, jsonify
import os
import subprocess
import threading
import signal
from datetime import datetime

app = Flask(__name__)

FUNCIONES_DIR = "/home/nano/Desktop/util/flask/funciones"
os.makedirs(FUNCIONES_DIR, exist_ok=True)

# Proceso en ejecución
process = None

# Clave simple para autenticación
AUTH_KEY = "lsd2025"

# Función para registrar eventos
def log_event(mensaje):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {mensaje}"
    print(log_line)
    with open("log_ejecuciones.txt", "a") as f:
        f.write(log_line + "\n")

# Función de autenticación
def autenticado(req):
    return req.headers.get("X-Auth-Key") == AUTH_KEY

@app.route("/subir", methods=["POST"])
def subir_funcion():
    if not autenticado(request):
        return "No autorizado", 401

    if "file" not in request.files:
        return "No se envió archivo", 400

    archivo = request.files["file"]
    nombre_archivo = os.path.join(FUNCIONES_DIR, archivo.filename)
    archivo.save(nombre_archivo)

    log_event(f"Script subido: {archivo.filename}")
    return f"Archivo {archivo.filename} subido correctamente", 200

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
            universal_newlines=True,  # en lugar de 'text' para compatibilidad
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



