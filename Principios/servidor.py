import json
import socket
import threading
from collections import deque

def guardar_db():
    with open('clientes_db.json', 'w') as f:
        json.dump(clientes_db, f)

def cargar_db():
        with open('clientes_db.json', 'r') as f:
            return json.load(f)

clientes_db = cargar_db()
clientes_conectados = {}
cola_espera = deque()

def manejar_cliente(cliente_socket, direccion):
    while True:
        email = cliente_socket.recv(1024).decode().strip()
        if email in clientes_db:
            cliente_socket.send("Correo encontrado. Por favor ingrese su contraseña:".encode())
            while True:
                password = cliente_socket.recv(1024).decode().strip()
                if clientes_db[email]["password"] == password:
                    cliente_socket.send("Autenticación exitosa.".encode())
                    nombre = clientes_db[email]["nombre"]
                    print(f"{nombre} se ha conectado.")
                    clientes_conectados[email] = cliente_socket
                    manejar_sesiones(cliente_socket, email)
                else:
                    cliente_socket.send("Error: Contraseña incorrecta.".encode())
        if not email in clientes_db:
            cliente_socket.send("Error: Correo no encontrado.".encode())


def manejar_sesiones(cliente_socket, email):
    while True:
        solicitud = cliente_socket.recv(1024).decode().strip()
        if solicitud == "1":
            nueva_contraseña = cliente_socket.recv(1024).decode().strip()
            clientes_db[email]["password"] = nueva_contraseña
            guardar_db()
            print(f"Contraseña de {email} cambiada.")
            cliente_socket.send("Contraseña cambiada exitosamente.".encode())
        elif solicitud == "2":
            historial_compras = clientes_db[email]["historial_compras"]
            cliente_socket.send(json.dumps(historial_compras).encode())
        elif solicitud == "3":
            while True:
                producto = cliente_socket.recv(1024).decode().strip()
                if producto in clientes_db[productos]:
                    cantidad = cliente_socket.recv(1024).decode().int()
                    stock = clientes_db[producto][stock]
                    while True:
                        if cantidad <= stock:
                            clientes_db[producto][stock] = stock - cantidad
                            guardar_db()
                            print(f"{email} compró {producto} [x{cantidad}].")
                            cliente_socket.send("Compra exitosa.".encode())
                        else:
                            cliente_socket.send("Error: Stock insuficiente.".encode())
                else:
                    cliente_socket.send("Error: Producto no encontrado. Porfavor ingrese otro producto.".encode())
        elif solicitud == "4":
            producto = cliente_socket.recv(1024).decode().strip()
            if producto in clientes_db[email]["historial_compras"]:
                clientes_db[email]["historial_compras"].remove(producto)
                guardar_db()
                print(f"{email} devolvió {producto}.")
                cliente_socket.send("Devolución exitosa.".encode())
            else:
                cliente_socket.send("Error: Producto no encontrado.".encode())
        elif solicitud == "5":
            producto = cliente_socket.recv(1024).decode().strip()
            if producto in clientes_db[email]["historial_compras"]:
                clientes_db[email]["historial_compras"].remove(producto)
                guardar_db()
                print(f"{email} confirmó envío de {producto}.")
                cliente_socket.send("Envío confirmado.".encode())
            else:
                cliente_socket.send("Error: Producto no encontrado.".encode())
        elif solicitud == "6":
            cola_espera.append(email)
            print(f"{email} en cola de espera.")
            cliente_socket.send("En cola de espera.".encode())
            if len(cola_espera) == 1:
                ejecutivo = cola_espera.popleft()
                print(f"Conectando a {ejecutivo} con un ejecutivo.")
                ejecutivo_socket = clientes_conectados[ejecutivo]
                ejecutivo_socket.send("Conectado con un ejecutivo.".encode())
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
