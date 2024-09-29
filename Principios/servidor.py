import json
import socket
import threading

def cargar_datos():
    try:
        with open('clientes_db.json', 'r') as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        print("Archivo de base de datos no encontrado, creando una nueva base de datos vacía.")
        return {}

clientes_db = cargar_datos()

# Manejo de conexiones de clientes
def manejar_cliente(cliente_socket, direccion):
    email = cliente_socket.recv(1024).decode().strip()
    if email in clientes_db:
        cliente_socket.send("Correo encontrado. Por favor ingrese su contraseña:".encode())
        password = cliente_socket.recv(1024).decode().strip()
        if clientes_db[email]["password"] == password:
            cliente_socket.send("Autenticación exitosa.".encode())
            manejar_sesiones(cliente_socket, email)
        else:
            cliente_socket.send("Error: Contraseña incorrecta.".encode())
    else:
        cliente_socket.send("Error: Correo no encontrado.".encode())

# Manejar sesiones individuales de cada cliente conectado
def manejar_sesiones(cliente_socket, email):
    while True:
        opcion = cliente_socket.recv(1024).decode().strip()
        if opcion == "1":
            nueva_contraseña = cliente_socket.recv(1024).decode().strip()
            clientes_db[email]["password"] = nueva_contraseña
            cliente_socket.send("Contraseña cambiada exitosamente.".encode())
        elif opcion == "7":
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

