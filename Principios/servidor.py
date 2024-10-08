import json
import socket
import threading
from collections import deque
import random
import datetime

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
        if email in clientes_db['usuarios']['clientes']:
            cliente_socket.send("Correo encontrado. Por favor ingrese su contraseña:".encode())
            while True:
                password = cliente_socket.recv(1024).decode().strip()
                if clientes_db['usuarios']['clientes'][email]["password"] == password:
                    cliente_socket.send("Autenticación exitosa.".encode())
                    nombre = clientes_db['usuarios']['clientes']["gonza@gmail.com"]["nombre"]
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
            clientes_db['usuarios']['clientes'][email]["password"] = nueva_contraseña
            guardar_db()
            print(f"Contraseña de {email} cambiada.")
            cliente_socket.send("Contraseña cambiada exitosamente.".encode())
        elif solicitud == "2":
            historial_2024 = []
            for compra in clientes_db['usuarios']['clientes'][email]["historial_compras"]:
                if compra["fecha"].startswith("2024"):
                    historial_2024.append(compra)

            if historial_2024:
                respuesta = f"Historial de compras de {clientes_db['usuarios']['clientes'][email]['nombre']} en 2024: {historial_2024}"
            else:
                respuesta = "No hay compras registradas en el año 2024."
            
            cliente_socket.send(respuesta.encode())
        elif solicitud == "3":
            while True:
                # Recibir el nombre del producto que el cliente quiere comprar
                producto = cliente_socket.recv(1024).decode().strip()
                print(producto)
                
                # Verificar si el producto está en la base de datos
                if producto in clientes_db["productos"]:
                    stock = clientes_db["productos"][producto]["stock"]
                    cliente_socket.send(f"Producto encontrado. stock disponible {stock} Ingrese la cantidad a comprar:".encode())
                    while True:
                        # Recibir la cantidad solicitada
                        cantidad = int(cliente_socket.recv(1024).decode().strip())
                        if cantidad <= stock:
                            # Actualizar stock y añadir al historial de compras
                            clientes_db["productos"][producto]["stock"] = stock - cantidad
                            fecha_aleatoria = datetime.date(2020, 1, 1) + datetime.timedelta(days=random.randint(0, (datetime.date(2024, 1, 1) - datetime.date(2020, 1, 1)).days))
                            
                            nuevo_historial = {
                                "fecha": str(fecha_aleatoria),
                                "producto": producto,
                                "cantidad": cantidad
                            }
                            
                            clientes_db['usuarios']['clientes'][email]["historial_compras"].append(nuevo_historial)
                            guardar_db()
                            
                            # Confirmación de la compra
                            cliente_socket.send("Compra Exitosa. Gracias por su compra.".encode())
                            nombre = clientes_db['usuarios']['clientes'][email]["nombre"]
                            print(f"{nombre} compró {producto} [x{cantidad}].")
                            break
                        else:
                            # Notificar al cliente que el stock es insuficiente
                            cliente_socket.send(f"Stock insuficiente. Stock actual: {stock}.".encode())
                        
                        # Salir del bucle después de procesar la compra o notificar stock insuficiente
                    break
                else:
                    # Notificar que el producto no se encontró y continuar el bucle
                    cliente_socket.send("Producto no encontrado. Por favor, intente nuevamente.".encode())


        elif solicitud == "4":
            # Recibimos el producto a eliminar y la cantidad del cliente
            producto_a_eliminar = cliente_socket.recv(1024).decode().strip()
            cantidad_a_eliminar = int(cliente_socket.recv(1024).decode().strip())
              # Cambia esto según cómo identifiques al cliente

            # Verificamos y eliminamos la compra del historial
            encontrado = False  # Definimos la variable para controlar si se encontró la compra
            
            for compra in clientes_db['usuarios']['clientes'][email]["historial_compras"]:
                if compra["producto"] == producto_a_eliminar and compra["cantidad"] == cantidad_a_eliminar:
                    clientes_db['usuarios']['clientes'][email]["historial_compras"].remove(compra)
                    encontrado = True
                    break  # Eliminamos solo la primera coincidencia y salimos del bucle

            # Guardamos la base de datos si se realizó una eliminación
            if encontrado:
                clientes_db["productos"][producto_a_eliminar]["stock"] += cantidad_a_eliminar
                guardar_db()
                print(f"{email} devolvió {producto_a_eliminar}.")
                cliente_socket.send("Devolución exitosa.".encode())
            else:
                cliente_socket.send("No se encontró el producto para devolución.".encode())
        elif solicitud == "5":
            producto = cliente_socket.recv(1024).decode().strip()
            if producto in clientes_db['usuarios']['clientes'][email]["historial_compras"]:
                clientes_db['usuarios']['clientes'][email]["historial_compras"].remove(producto)
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
            print(f"{email} se ha desconectado.")
            cliente_socket.send("Desconectado.".encode())
            break
        conitnuar = cliente_socket.recv(1024).decode().strip()
        if continuar != "si":
            print(f"{email} se ha desconectado.")
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
