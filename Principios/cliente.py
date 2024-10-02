import socket

def cliente_terminal():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect(("localhost", 9999))  # Conectar al servidor local

    while True:
        email = input("Ingrese su correo: ").strip().lower()
        cliente.send(email.encode())
        respuesta = cliente.recv(1024).decode()

        if "Correo encontrado" in respuesta:
            while True:
                password = input("Ingrese su contraseña: ").strip()
                cliente.send(password.encode())
                respuesta = cliente.recv(1024).decode()
                if "Autenticación" in respuesta:
                    print(f"[SERVIDOR]: {respuesta}")
                    break
                else:
                    print(f"[SERVIDOR]: {respuesta}")
            break
        else:
            print(f"{respuesta}")
            
            
    while "Autenticación exitosa" in respuesta:
        continuar = '1'
        while continuar == '1':
            print("\nOpciones:")
            print("[1] Cambiar contraseña")
            print("[2] Ver historial de pedidos")
            print("[3] Comprar producto")
            print("[4] Solicitar devolución")
            print("[5] Confirmar envío")
            print("[6] Contactarse con el ejecutivo")
            print("[7] Salir")

            opcion = input("Ingrese una opción: ").strip()
            cliente.send(opcion.encode())

            if opcion == "1":
                while True:
                    nueva_contraseña = input("Ingrese su nueva contraseña: ").strip()
                    repetir_contraseña = input("Repita su nueva contraseña: ").strip()
                    if nueva_contraseña == repetir_contraseña:
                        cliente.send(nueva_contraseña.encode())
                        respuesta = cliente.recv(1024).decode()
                        print(f"[SERVIDOR]: {respuesta}")
                        break
                    else:
                        print("Error: Las contraseñas no coinciden.")
            if opcion == "2":
                historial_compras = cliente.recv(1024).decode()
                print(f"[SERVIDOR]: {historial_compras}")
            if opcion == "3":
                producto = input("Ingrese el producto a comprar: ").strip()
                cliente.send(producto.encode())
                respuesta = cliente.recv(1024).decode()
                print(f"[SERVIDOR]: {respuesta}")
            if opcion == "4":
                producto = input("Ingrese el producto a devolver: ").strip()
                cliente.send(producto.encode())
                respuesta = cliente.recv(1024).decode()
                print(f"[SERVIDOR]: {respuesta}")
            if opcion == "5":
                producto = input("Ingrese el producto a confirmar envío: ").strip()
                cliente.send(producto.encode())
                respuesta = cliente.recv(1024).decode()
                print(f"[SERVIDOR]: {respuesta}")
            if opcion == "6":
                respuesta = cliente.recv(1024).decode()
                print(f"[SERVIDOR]: {respuesta}")
            if opcion == "7":
                print("[CLIENTE] Desconectando...")
                cliente.close()
                break

     
            continuar = input("¿Desea realizar otra operación? (1 = Sí, otro = No): ")
        break
if __name__ == "__main__":
    cliente_terminal()

