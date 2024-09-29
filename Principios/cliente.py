import socket

def cliente_terminal():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect(("localhost", 9999))  # Conectar al servidor local

    # Autenticación inicial
    email = input("Ingrese su correo: ").strip().lower()
    cliente.send(email.encode())
    respuesta = cliente.recv(1024).decode()
    print(f"[SERVIDOR]: {respuesta}")

    if "Correo encontrado" in respuesta:
        password = input("Ingrese su contraseña: ").strip()
        cliente.send(password.encode())
        respuesta = cliente.recv(1024).decode()
        print(f"[SERVIDOR]: {respuesta}")

    if "Autenticación exitosa" in respuesta:
        while True:
            # Opciones disponibles para el usuario
            print("\nOpciones:")
            print("[1] Cambiar contraseña")
            print("[2] Ver historial de pedidos")
            print("[3] Comprar producto")
            print("[6] Contactar con un ejecutivo")
            print("[7] Salir")

            opcion = input("Ingrese una opción: ").strip()
            cliente.send(opcion.encode())

            # Esperar la respuesta del servidor a la acción realizada
            respuesta = cliente.recv(1024).decode()
            print(f"[SERVIDOR]: {respuesta}")

            if opcion == "7":
                print("[CLIENTE] Desconectando...")
                cliente.close()
                break

            # Preguntar si desea realizar otra operación
            continuar = input("¿Desea realizar otra operación? (1 = Sí, otro = No): ")
            if continuar != '1':
                cliente.send('7'.encode())  # Señal de desconexión
                print("[CLIENTE] Desconectando...")
                cliente.close()
                break

if __name__ == "__main__":
    cliente_terminal()

