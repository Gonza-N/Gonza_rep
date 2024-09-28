# servidor.py - Código del Servidor Modificado para primero verificar las credenciales y luego registrar si es necesario
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

# Función para manejar cada cliente
def manejar_cliente(cliente_socket, direccion):
    while True:
        email = cliente_socket.recv(1024).decode().strip()
        if email in clientes_db:
            print(f"[SERVIDOR] Correo recibido: {email}")  # Depuración
            # Si el correo está registrado, pedir la contraseña
            cliente_socket.send("Correo encontrado. Por favor ingrese su contraseña:".encode())
            password = cliente_socket.recv(1024).decode().strip()
            print(f"[SERVIDOR] Intentando autenticar al usuario: {email}") 

            # Verificar la contraseña
            if clientes_db[email]["password"] == password:
                clientes_conectados[email] = cliente_socket
                autenticado = True
                cliente_socket.send(f"Autenticación exitosa. Bienvenido {email}".encode())
                print(f"[SERVIDOR] Cliente {email} conectado.")
            else:
                cliente_socket.send("Error: Contraseña incorrecta. Intente nuevamente.".encode())
        
            registro_datos = cliente_socket.recv(1024).decode().strip()
        if registro_datos:
                try:
                    # Descomponer los datos ingresados (correo y contraseña)
                    nuevo_email, nueva_password = json.loads(registro_datos)
                    nuevo_email = nuevo_email.strip().lower()  # Limpiar y convertir a minúsculas
                    nueva_password = nueva_password.strip()
                    print(f"[SERVIDOR] Registrando nuevo usuario: {nuevo_email}")  # Depuración

                    if nuevo_email in clientes_db:
                        cliente_socket.send("Error: El correo ya está registrado. Intente nuevamente.".encode())
                    else:
                        # Registrar el nuevo usuario en la base de datos
                        clientes_db[nuevo_email] = {"password": nueva_password, "historial_compras": []}
                        cliente_socket.send(f"Registro exitoso. Por favor inicie sesión con su nuevo correo y contraseña.".encode())
                        print(f"[SERVIDOR] Cliente {nuevo_email} registrado, redirigiendo a inicio de sesión.")
                except json.JSONDecodeError:
                    cliente_socket.send("Error: Formato inválido al registrar el usuario. Asegúrese de ingresar correo y contraseña correctamente.".encode())
    while True:
        try:
            mensaje = cliente_socket.recv(1024).decode().strip()
            print(f"[SERVIDOR] Mensaje recibido de {email}: {mensaje}")  # Depuración

            if mensaje.lower() == "7":  # El cliente desea salir
                print(f"[SERVIDOR] {email} se ha desconectado.")
                clientes_conectados.pop(email, None)
                cliente_socket.close()
                break
            elif mensaje.startswith("cambiar_contraseña:"):
                # Cambiar contraseña
                nueva_contraseña = mensaje.split(":")[1]
                clientes_db[email]["password"] = nueva_contraseña
                cliente_socket.send("Contraseña cambiada exitosamente.".encode())
                print(f"[SERVIDOR] Contraseña cambiada para el usuario: {email}")
            elif mensaje == "ver_historial":
                # Ver historial de pedidos
                historial = clientes_db[email].get("historial_compras", [])
                cliente_socket.send(f"Historial de pedidos: {historial}".encode())
            elif mensaje.startswith("comprar_producto:"):
                # Comprar producto
                producto = mensaje.split(":")[1]
                clientes_db[email]["historial_compras"].append(producto)
                cliente_socket.send(f"Producto '{producto}' comprado exitosamente.".encode())
            elif mensaje == "contactar_ejecutivo":
                # Contactar con un ejecutivo (lógica de ejemplo)
                cliente_socket.send("Todos los ejecutivos están ocupados. Usted está en espera.".encode())
                cola_espera.append((email, cliente_socket))
                print(f"[SERVIDOR] Cliente {email} añadido a la cola de espera.")
            else:
                cliente_socket.send(f"Comando '{mensaje}' no reconocido.".encode())

        except Exception as e:
            print(f"[SERVIDOR] Error manejando cliente {direccion}: {e}")
            clientes_conectados.pop(email, None)
            cliente_socket.close()
            break
# Función para iniciar el chat entre cliente y ejecutivo
def iniciar_chat(cliente_socket, ejecutivo_socket):
    print("[SERVIDOR] Iniciando chat entre cliente y ejecutivo.")

    def recibir_mensajes(desde_socket, hacia_socket):
        while True:
            try:
                mensaje = desde_socket.recv(1024).decode().strip()
                if mensaje.lower() == "salir":
                    hacia_socket.send("El otro participante se ha desconectado.".encode())
                    desde_socket.close()
                    hacia_socket.close()
                    break
                hacia_socket.send(f"Mensaje: {mensaje}".encode())
            except:
                desde_socket.close()
                hacia_socket.close()
                break

    # Crear hilos para permitir el envío y la recepción de mensajes simultáneamente
    hilo_cliente = threading.Thread(target=recibir_mensajes, args=(cliente_socket, ejecutivo_socket))
    hilo_ejecutivo = threading.Thread(target=recibir_mensajes, args=(ejecutivo_socket, cliente_socket))

    hilo_cliente.start()
    hilo_ejecutivo.start()

# Configuración del servidor
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

# Ejecutar el servidor en un hilo
if __name__ == "__main__":
    iniciar_servidor()
