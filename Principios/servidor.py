# Celda de Google Colab: Código del Servidor
import socket
import threading
import json
from collections import deque

# Base de datos en memoria
clientes_db = {
    "gonzalo@gmail.com": {"password": "1234", "historial_compras": []},
    "ammi@gmail.com": {"password": "5678", "historial_compras": []}
}
ejecutivos_db = {
    "cristobal@gmail.com": {"password": "abcd"},
    "diego@gmail.com": {"password": "efgh"}
}

# Conexiones activas y cola de espera
clientes_conectados = {}
ejecutivos_conectados = {}
cola_espera = deque()  # Cola para los clientes esperando ejecutivos

# Función para manejar clientes y ejecutivos
# Inicia el servidor
def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(("localhost", 9999))
    servidor.listen(10)  # Capacidad para 10 usuarios
    print("[SERVIDOR] Esperando conexiones...")

    while True:
        cliente_socket, direccion = servidor.accept()
        print(f"[SERVIDOR] Conexión entrante desde {direccion}")
        hilo_cliente = threading.Thread(target=manejar_cliente, args=(cliente_socket, direccion))
        hilo_cliente.start()

# Ejecutar el servidor
hilo_servidor = threading.Thread(target=iniciar_servidor)
hilo_servidor.start()
