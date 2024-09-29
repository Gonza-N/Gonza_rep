import json
import socket
import threading
from collections import deque

def guardar_db():
    with open('clientes_db.json', 'w') as f:
        json.dump(clientes_db, f)

def cargar_db():
    try:
        with open('clientes_db.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "gonzalo@gmail.com": {"password": "1234", "historial_compras": []},
            "ammi@gmail.com": {"password": "5678", "historial_compras": []}
        }

clientes_db = cargar_db()
clientes_conectados = {}
cola_espera = deque()

def manejar_cliente(cliente_socket, direccion):
    email = cliente_socket.recv(1024).decode().strip()
    if email in clientes_db:
        cliente_socket.send("Correo encontrado. Por favor ingrese su contraseña:".encode())
        password = cliente_socket.recv(1024).decode().strip()
        if clientes_db[email]["password"] == password:
            cliente_socket.send("Autenticación exitosa.".encode())
            clientes_conectados[email] = cliente_socket
            manejar_sesiones(cliente_socket, email)
        else:
            cliente_socket.send("Error: Contraseña incorrecta.".encode())
    else:
        cliente_socket.send("Error: Correo no encontrado.".encode())

def manejar_sesiones(cliente_socket, email):
    while True:
        solicitud = cliente_socket.recv(1024).decode().strip()
        if solicitud == "1":
            nueva_contraseña = cliente_socket.recv(1024).decode().strip()
            clientes_db[email]["password"] = nueva_contraseña
            guardar_db()
            cliente_socket.send("Contraseña cambiada exitosamente.".encode())
        elif solicitud == "7":
            cliente_socket.send("Desconectado.".encode())
            break
        else:
            cliente_socket.send("Opción no válida.".encode())

def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(("localhost", 9999))
    servidor.listen(10)
    print("[SERVIDOR] Servidor iniciado y esperando conexiones...")
    while True:
        cliente_socket, direccion = servidor.accept()
        threading.Thread(target=manejar_cliente, args=(cliente_socket, direccion)).start()

if __name__ == "__main__":
    iniciar_servidor()
