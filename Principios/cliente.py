import socket

def cliente_terminal():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect(("localhost", 9999))  # Conectar al servidor local

    email = input("Ingrese su correo: ").strip().lower()
    cliente.send(email.encode())
    respuesta = cliente.recv(1024).decode()
    print(f"[SERVIDOR]: {respuesta}")

    if "Correo encontrado" in respuesta:
        password = input("Ingrese su contraseña: ").strip()
        cliente.send(password.encode())
        respuesta = cliente.recv(1024).decode()
        print(f"[SERVIDOR]: {respuesta}")

    while "Autenticación exitosa" in respuesta:
        continuar = '1'
        while continuar == '1':
            print("\nOpciones:")
            print("[1] Cambiar contraseña")
            print("[2] Ver historial de pedidos")
            print("[3] Comprar producto")
            print("[6] Contactar con un ejecutivo")
            print("[7] Salir")

            opcion = input("Ingrese una opción: ").strip()
            cliente.send(opcion.encode())

            if opcion == "1":
                nueva_contraseña = input("Ingrese su nueva contraseña: ").strip()
                cliente.send(nueva_contraseña.encode())
                respuesta = cliente.recv(1024).decode()
                print(f"[SERVIDOR]: {respuesta}")

            elif opcion == "7":
                print("[CLIENTE] Desconectando...")
                cliente.close()
                break

            respuesta = cliente.recv(1024).decode()
            print(f"[SERVIDOR]: {respuesta}")
            if opcion != "7":
                continuar = input("¿Desea realizar otra operación? (1 = Sí, otro = No): ")

if __name__ == "__main__":
    cliente_terminal()

