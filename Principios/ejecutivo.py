# ejecutivo.py - Código del Ejecutivo
import socket
import json

# Función del ejecutivo para conectarse al servidor
def ejecutivo_terminal():
    ejecutivo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ejecutivo.connect(("localhost", 9999))  # Conectar al servidor local

    email = input("Ingrese su correo (ejecutivo): ")
    password = input("Ingrese su contraseña: ")
    
    # Enviar credenciales al servidor
    ejecutivo.send(json.dumps((email, password)).encode())

    # Esperar respuesta del servidor
    try:
        respuesta = ejecutivo.recv(1024).decode()
        print(f"[Servidor]: {respuesta}")

        if "Autenticación exitosa" in respuesta:
            while True:
                print("\nComandos disponibles:")
                print("[1] Ver estado de clientes conectados")
                print("[2] Desconectar cliente")
                print("[7] Salir")

                opcion = input("Ingrese un comando: ")

                if opcion == "7":
                    ejecutivo.send("7".encode())
                    print("[Ejecutivo] Desconectando...")
                    ejecutivo.close()
                    break
                else:
                    ejecutivo.send(opcion.encode())
                    respuesta = ejecutivo.recv(1024).decode()
                    print(f"[Servidor]: {respuesta}")

    except Exception as e:
        print(f"[Ejecutivo] Error durante la comunicación: {e}")
        ejecutivo.close()

# Ejecutar el ejecutivo
if __name__ == "__main__":
    ejecutivo_terminal()
