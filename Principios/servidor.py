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
                    nombre = clientes_db['usuarios']['clientes'][email]["nombre"]
                    print(f"{nombre} se ha conectado.")
                    clientes_conectados[email] = cliente_socket
                    manejar_sesiones(cliente_socket, email)
                else:
                    cliente_socket.send("Error: Contraseña incorrecta.".encode())
        elif email in clientes_db['usuarios']['ejecutivos']:
            cliente_socket.send("Correo encontrado. Por favor ingrese su contraseña:".encode())
            while True:
                password = cliente_socket.recv(1024).decode().strip()
                if clientes_db['usuarios']['ejecutivos'][email]["password"] == password:
                    cliente_socket.send("Autenticación exitosa.".encode())
                    nombre = clientes_db['usuarios']['ejecutivos'][email]["nombre"]
                    print(f"{nombre} se ha conectado.")
                    clientes_conectados[email] = cliente_socket
                    manejar_ejectivo(cliente_socket, email)
                else:
                    cliente_socket.send("Error: Contraseña incorrecta.".encode())
    
        else:
            cliente_socket.send("Error: Correo no encontrado.".encode())


def manejar_sesiones(cliente_socket, email):
    global sas
    global cola_espera
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
            # Suponiendo que 'email' contiene el correo del cliente que estamos consultando
            for compra in clientes_db['usuarios']['clientes'][email]["historial_compras"]:
                if compra["fecha"].startswith("2024"):
                    historial_2024.append(compra)

            if historial_2024:
                cliente = clientes_db['usuarios']['clientes'][email]["nombre"]
                print(f"{cliente} consultó su historial de compras.")
                # Crear una respuesta formateada con los detalles de cada compra incluyendo el estado
                detalles_compras = []
                for compra in historial_2024:
                    detalle = f"Fecha: {compra['fecha']}, Producto: {compra['producto']}, Cantidad: {compra['cantidad']}, Estado: {compra['estado']}"
                    detalles_compras.append(detalle)
                respuesta = f"Historial de compras de {clientes_db['usuarios']['clientes'][email]['nombre']} en 2024:\n" + "\n".join(detalles_compras)
            else:
                respuesta = "No hay compras registradas en el año 2024."
            
            cliente_socket.send(respuesta.encode())
        elif solicitud == "3":
            while True:
                # Recibir el nombre del producto que el cliente quiere comprar
                producto = cliente_socket.recv(1024).decode().strip()
                
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
                            #fecha_aleatoria = datetime.date(2020, 1, 1) + datetime.timedelta(days=random.randint(0, (datetime.date(2024, 1, 1) - datetime.date(2020, 1, 1)).days))
                            fecha_aleatoria = datetime.datetime.now() 
                            nuevo_historial = {
                                "fecha": str(fecha_aleatoria),
                                "producto": producto,
                                "cantidad": cantidad,
                                "estado": "pagado"
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
            cola_espera.append([email,cliente_socket])
            cliente = clientes_db["usuarios"]["clientes"][email]["nombre"]
            print(f"{cliente} en cola de espera.")
            cliente_socket.send("En cola de espera.".encode())
            sas=0
            while True:
                if sas==1:
                    break

        elif solicitud == "7":
            print(f"{email} se ha desconectado.")
            cliente_socket.send("Desconectado.".encode())
            break
        else:
            cliente_socket.send("Opción no válida.".encode())

def manejar_ejectivo(ejecutivo_socket, email):
    global sas
    global cola_espera
    while True:
        solicitud = ejecutivo_socket.recv(1024).decode().strip()
        if solicitud == "1":
            clientes_conectados[email].send(f"Hola {email}".encode())
            ejecutivo_socket.send(f"Mensaje enviado a {email}".encode())
        #elif solicitud == "2":

        #elif solicitud == "3":

        #elif solicitud == "4":   

        elif solicitud == "5":

            if len(cola_espera) > 0:
                ejecutivo = clientes_db["usuarios"]["ejecutivos"][email]["nombre"]
                cliente_email = clientes_db["usuarios"]["clientes"][cola_espera[0][0]]["nombre"]
                print(f"{ejecutivo} conectado con {cliente_email}.")
                cliente_socket = cola_espera[0][1]
                if len(cola_espera) > 1:
                    cola_espera = cola_espera[1:]
                else:
                    cola_espera = deque()
                ejecutivo_socket.send(f"Conectado con {cliente_email}.".encode())
                while True:

                    mensaje_de_ejecutivo = ejecutivo_socket.recv(1024).decode()  # recibir del ejecutivo
                    if mensaje_de_ejecutivo == "disconnect":
                        cliente_socket.send("Ejecutivo desconectado".encode())
                        ejecutivo_socket.send("Cliente desconectado".encode())
                        sas=1
                        break

                    cliente_socket.send(mensaje_de_ejecutivo.encode())  # enviar al cliente
                    respuesta_de_cliente = cliente_socket.recv(1024).decode()  # recibir respuesta del cliente
                    ejecutivo_socket.send(respuesta_de_cliente.encode())  # enviar respuesta al ejecutivo
            else:
                ejecutivo_socket.send("No hay clientes en cola.".encode())
        
        elif solicitud == "7":
            ejecutivo_socket.send("Desconectado.".encode())
            ejecutivo.close()
            break
    

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
