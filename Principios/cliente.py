# cliente.py - Código del Cliente (Modificado para asegurarse de que el cambio de contraseña funcione correctamente)
import socket
import json

# Función del cliente para conectarse al servidor
def cliente_terminal():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect(("localhost", 9999))  # Conectar al servidor local

    # Enviar el correo al servidor
    email = input("Ingrese su correo: ").strip().lower()
    print(f"[CLIENTE] Enviando correo: {email}")  # Depuración
    cliente.send(email.encode())

    # Esperar la respuesta del servidor
    respuesta = cliente.recv(1024).decode()
    print(f"[SERVIDOR]: {respuesta}")

    if "Correo encontrado" in respuesta:
        # Si el correo está registrado, enviar la contraseña
        password = input("Ingrese su contraseña: ").strip()
        print(f"[CLIENTE] Enviando contraseña.")  # Depuración
        cliente.send(password.encode())

        # Esperar respuesta del servidor para autenticación
        respuesta = cliente.recv(1024).decode()
        print(f"[SERVIDOR]: {respuesta}")

    # Si el registro o autenticación fue exitosa, proceder a mostrar el menú de opciones
    if "Autenticación exitosa" in respuesta or "Registro exitoso" in respuesta:
        while True:
            print("\nOpciones:")
            print("[1] Cambiar contraseña")
            print("[2] Ver historial de pedidos")
            print("[3] Comprar producto")
            print("[6] Contactar con un ejecutivo")
            print("[7] Salir")

            opcion = input("Ingrese una opción: ")

            if opcion == "1":
                # Cambiar contraseña
                nueva_contraseña = input("Ingrese su nueva contraseña: ").strip()
                confirmar_contraseña = input("Ingrese su nueva contraseña nuevamente: ").strip()

                # Verificar si ambas contraseñas coinciden antes de enviarlas
                if nueva_contraseña == confirmar_contraseña:
                    cliente.send(f"cambiar_contraseña:{nueva_contraseña}".encode())
                    respuesta = cliente.recv(1024).decode()
                    print(f"[SERVIDOR]: {respuesta}")
                else:
                    print("[CLIENTE] Error: Las contraseñas no coinciden. Intente nuevamente.")

            elif opcion == "2":
                # Ver historial de pedidos
                cliente.send("ver_historial".encode())
                respuesta = cliente.recv(1024).decode()
                print(f"[SERVIDOR]: {respuesta}")

            elif opcion == "3":
                # Comprar producto
                producto = input("Ingrese el producto que desea comprar: ").strip()
                cliente.send(f"comprar_producto:{producto}".encode())
                respuesta = cliente.recv(1024).decode()
                print(f"[SERVIDOR]: {respuesta}")

            elif opcion == "6":
                # Contactar con un ejecutivo
                cliente.send("contactar_ejecutivo".encode())
                respuesta = cliente.recv(1024).decode()
                print(f"[SERVIDOR]: {respuesta}")

            elif opcion == "7":
                # Salir
                cliente.send("7".encode())
                print("[CLIENTE] Desconectando...")
                cliente.close()
                break

            else:
                print("[CLIENTE] Opción inválida. Por favor, intente nuevamente.")

# Ejecutar el cliente
if __name__ == "__main__":
    cliente_terminal()