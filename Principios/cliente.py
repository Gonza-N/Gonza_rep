# Celda de Google Colab: Código del Cliente
import socket
import json

# Función del cliente para conectarse al servidor
def cliente_terminal():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect(("localhost", 9999))  # Conectar al servidor local

    email = input("Ingrese su correo: ")
    password = input("Ingrese su contraseña: ")
    
    # Enviar credenciales al servidor
    cliente.send(json.dumps((email, password)).encode())

    # Esperar respuesta del servidor
    respuesta = cliente.recv(1024).decode()
    print(f"[Servidor]: {respuesta}")

    if "Autenticación exitosa" in respuesta:
        while True:
            print("\nOpciones:")
            print("[1] Cambiar contraseña")
            print("[2] Ver historial de pedidos")
            print("[3] Comprar producto")
            print("[6] Contactar con un ejecutivo")
            print("[7] Salir")

            opcion = input("Ingrese una opción: ")

            if opcion == "7":
                cliente.send("7".encode())
                print("[Cliente] Desconectando...")
                cliente.close()
                break
            else:
                cliente.send(opcion.encode())
                respuesta = cliente.recv(1024).decode()
                print(f"[Servidor]: {respuesta}")

# Ejecutar el cliente
cliente_terminal()
