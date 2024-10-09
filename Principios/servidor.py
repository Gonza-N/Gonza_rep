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
                if "exit" in password:
                    break
                elif clientes_db['usuarios']['clientes'][email]["password"] == password:
                    cliente_socket.send("Autenticación exitosa.".encode())
                    nombre = clientes_db['usuarios']['clientes'][email]["nombre"]
                    print(f"[SERVIDOR] {nombre} se ha conectado.")
                    clientes_conectados[email] = cliente_socket
                    accion = "Conexión"
                    clientes_db['usuarios']['clientes'][email]['acciones'].append(accion)
                    clientes_db['usuarios']['clientes'][email]["estado"] = "conectado"                  
                    manejar_sesiones(cliente_socket, email)
                else:
                    cliente_socket.send("Error: Contraseña incorrecta.".encode())
            break
        elif email in clientes_db['usuarios']['ejecutivos']:
            cliente_socket.send("Correo encontrado. Por favor ingrese su contraseña:".encode())
            while True:
                password = cliente_socket.recv(1024).decode().strip()
                if "exit" in password:
                    break
                elif clientes_db['usuarios']['ejecutivos'][email]["password"] == password:
                    cliente_socket.send("Autenticación exitosa.".encode())
                    nombre = clientes_db['usuarios']['ejecutivos'][email]["nombre"]
                    print(f"[SERVIDOR] {nombre} se ha conectado.")
                    clientes_conectados[email] = cliente_socket
                    manejar_ejecutivo(cliente_socket, email)
                else:
                    cliente_socket.send("Error: Contraseña incorrecta.".encode())
            break
    
        else:
            cliente_socket.send("Error: Correo no encontrado.".encode())
        break


def manejar_sesiones(cliente_socket, email):
    global sas
    global cola_espera
    while True:
        solicitud = cliente_socket.recv(1024).decode().strip()
        if solicitud == "1":
            nueva_contraseña = cliente_socket.recv(1024).decode().strip()
            clientes_db['usuarios']['clientes'][email]["password"] = nueva_contraseña
            guardar_db()
            nombre = clientes_db['usuarios']['clientes'][email]["nombre"]
            print(f"[SERVIDOR] Contraseña de {nombre} cambiada.")
            cliente_socket.send("Contraseña cambiada exitosamente.".encode())
            accion = "Cambio de contraseña"
            clientes_db['usuarios']['clientes'][email]['acciones'].append(accion)
            guardar_db()
        elif solicitud == "2":
            historial_2024 = []
            # Suponiendo que 'email' contiene el correo del cliente que estamos consultando
            for compra in clientes_db['usuarios']['clientes'][email]["historial_compras"]:
                if compra["fecha"].startswith("2024"):
                    historial_2024.append(compra)

            if historial_2024:
                cliente = clientes_db['usuarios']['clientes'][email]["nombre"]
                print(f"[SERVIDOR] {cliente} consultó su historial de compras.")
                accion = "Consulta de historial de compras"
                clientes_db['usuarios']['clientes'][email]['acciones'].append(accion)
                guardar_db()
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
                            print(f"[SERVIDOR] {nombre} compró {producto} [x{cantidad}].")
                            accion = f"Compra de producto {producto} [x{cantidad}]"
                            clientes_db['usuarios']['clientes'][email]['acciones'].append(accion)
                            guardar_db()
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
                cliente = clientes_db['usuarios']['clientes'][email]["nombre"]
                clientes_db["productos"][producto_a_eliminar]["stock"] += cantidad_a_eliminar
                guardar_db()
                print(f"[SERVIDOR] {cliente} devolvió {producto_a_eliminar} [x{cantidad_a_eliminar}].")
                cliente_socket.send("Devolución exitosa.".encode())
                accion = f"Devolución de producto {producto_a_eliminar} [x{cantidad_a_eliminar}]"
                clientes_db['usuarios']['clientes'][email]['acciones'].append(accion)
                guardar_db()
            else:
                cliente_socket.send("No se encontró el producto para devolución.".encode())
        elif solicitud == "5":
            producto = cliente_socket.recv(1024).decode().strip()
            if producto in clientes_db['usuarios']['clientes'][email]["historial_compras"]:
                clientes_db['usuarios']['clientes'][email]["historial_compras"].remove(producto)
                guardar_db()
                nombre = clientes_db['usuarios']['clientes'][email]["nombre"]
                print(f"[SERVIDOR] {nombre} confirmó envío de {producto}.")
                cliente_socket.send("Envío confirmado.".encode())
            else:
                cliente_socket.send("Error: Producto no encontrado.".encode())

        elif solicitud == "6":
            cola_espera.append([email,cliente_socket])
            cliente = clientes_db["usuarios"]["clientes"][email]["nombre"]
            print(f"[SERVIDOR] {cliente} en cola de espera.")
            cliente_socket.send("En cola de espera. Tiempo estimado: 1 minuto".encode())
            accion = "Derivado a ejecutivo"
            clientes_db['usuarios']['clientes'][email]['acciones'].append(accion)
            guardar_db()
            sas=0
            while True:
                if sas==1:
                    break

        elif solicitud == "7":
            nombre = clientes_db['usuarios']['clientes'][email]["nombre"]
            print(f"[SERVIDOR] {nombre} se ha desconectado.")
            accion = "Desconexión"
            clientes_db['usuarios']['clientes'][email]['acciones'].append(accion)
            clientes_db['usuarios']['clientes'][email]["estado"] = "desconectado"
            guardar_db()
            break
        else:
            cliente_socket.send("Opción no válida.".encode())

def manejar_ejecutivo(ejecutivo_socket, email):
    global sas
    global cola_espera
    while True:
        solicitud = ejecutivo_socket.recv(1024).decode().strip()
        if solicitud == "1":
            clientes_conectados = []
            clientes_derivados = []
            for cliente_id, cliente_info in clientes_db["usuarios"]["clientes"].items():
                if cliente_info["estado"] == "conectado":
                    clientes_conectados.append(cliente_info['nombre'])  # Añadir cliente a la lista
                if cliente_info["acciones"] and cliente_info["acciones"][-1] == "Derivado a ejecutivo":
                    clientes_derivados.append(cliente_info['nombre'])

            # Convertir la lista en un string para enviar al ejecutivo
            if clientes_conectados:
                mensaje = f"Hay {len(clientes_conectados)} clientes conectados:"
                ejecutivo_socket.send(mensaje.encode())
                if clientes_derivados:
                    mensaje = f"Clientes derivados: {', '.join(clientes_derivados)}"
                    ejecutivo_socket.send(mensaje.encode())
                else:
                    mensaje = "No hay clientes derivados."
                    ejecutivo_socket.send(mensaje.encode())
            else:
                mensaje = "No hay clientes conectados."
                ejecutivo_socket.send(mensaje.encode())
        elif solicitud == "2":
            clientes_conectados = []
            for cliente_id, cliente_info in clientes_db["usuarios"]["clientes"].items():
                if cliente_info["estado"] == "conectado":
                    # Agregar una tupla (nombre, última acción) a la lista
                    ultima_accion = cliente_info["acciones"][-1]  # Última acción del cliente
                    clientes_conectados.append((cliente_info['nombre'], ultima_accion))
            
            if clientes_conectados:
                mensaje = f"Clientes conectados y su última acción: {clientes_conectados}"
                ejecutivo_socket.send(mensaje.encode())
            else:
                mensaje = "No hay clientes conectados."
                ejecutivo_socket.send(mensaje.encode())

        elif solicitud == "3":
            clientes_conectados = []  # Lista para almacenar los clientes conectados con todas sus acciones

            # Iterar sobre los clientes para encontrar los que están conectados
            for cliente_id, cliente_info in clientes_db["usuarios"]["clientes"].items():
                if cliente_info["estado"] == "conectado":
                    # Agregar una tupla (nombre, todas las acciones) a la lista
                    todas_las_acciones = cliente_info["acciones"]  # Todas las acciones del cliente
                    clientes_conectados.append((cliente_info['nombre'], todas_las_acciones))
            if clientes_conectados:
                mensaje = f"Historial de acciones: {(clientes_conectados)}"
                ejecutivo_socket.send(mensaje.encode())

        elif solicitud == "5":
            if len(cola_espera) > 0:
                accion = "Conectado con el Ejecutivo"
                email_c = cola_espera[0][0]
                clientes_db['usuarios']['clientes'][email_c]['acciones'].append(accion)
                guardar_db()
                ejecutivo = clientes_db["usuarios"]["ejecutivos"][email]["nombre"]
                cliente_email = clientes_db["usuarios"]["clientes"][cola_espera[0][0]]["nombre"]
                print(f"[SERVIDOR] {ejecutivo} conectado con {cliente_email}.")
                cliente_socket = cola_espera[0][1]              
                cola_espera.popleft()
                ejecutivo_socket.send(f"Conectado con {cliente_email}.".encode())
                while True:
                    mensaje_de_ejecutivo = ejecutivo_socket.recv(1024).decode()  # recibir del ejecutivo
                    if mensaje_de_ejecutivo == "disconnect":
                        cliente_socket.send("Ejecutivo desconectado".encode())
                        ejecutivo_socket.send("Cliente desconectado".encode())
                        sas=1
                        break
                    elif mensaje_de_ejecutivo == "operations":
                        cliente = clientes_db["usuarios"]["clientes"][email_c]["nombre"]
                        historial_operaciones = clientes_db["usuarios"]["clientes"][email_c]["acciones"]
                        mensaje = f"Historial de operaciones de {cliente}: {historial_operaciones}"
                        cliente_socket.send(mensaje.encode())
                    elif mensaje_de_ejecutivo == "history":
                        cliente = clientes_db["usuarios"]["clientes"][email_c]["nombre"]
                        historial_compras = clientes_db["usuarios"]["clientes"][email_c]["historial_compras"]
                        mensaje = f"Historial de compras de {cliente}: {historial_compras}"
                        ejecutivo_socket.send(mensaje.encode())

                    elif mensaje_de_ejecutivo:
                        cliente_socket.send(mensaje_de_ejecutivo.encode())  # enviar al cliente
                        respuesta_de_cliente = cliente_socket.recv(1024).decode()  # recibir respuesta del cliente
                        ejecutivo_socket.send(respuesta_de_cliente.encode())  # enviar respuesta al ejecutivo
            else:
                ejecutivo_socket.send("No hay clientes en cola.".encode())
        
        elif solicitud == "7":
            nombre = clientes_db['usuarios']['ejecutivos'][email]["nombre"]
            print(f"[SERVIDOR] {nombre} se ha desconectado.")
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
