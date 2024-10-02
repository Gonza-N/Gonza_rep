import socket
import sys

def print_menu():
    print("""
    :status - Muestra la cantidad de clientes conectados y solicitudes de conexión.
    :details - Muestra los clientes conectados y su última acción.
    :history - Muestra el historial del cliente que está siendo atendido.
    :operations - Muestra todas las operaciones realizadas por un cliente.
    :connect - Conecta con el primer cliente en cola.
    :disconnect - Termina la conexión actual con el cliente.
    :exit - Salida del sistema.
    """)

def main():
    host = 'localhost'
    port = 12345
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))

        # Autenticación
        email = input("Ingrese su email: ")
        password = input("Ingrese su contraseña: ")
        s.send(f"login {email} {password}".encode())

        # Verificar respuesta del servidor
        response = s.recv(1024).decode()
        if response == "login_success":
            print("Autenticación exitosa.\n")
            print_menu()
        else:
            print("Error de autenticación.")
            return

        # Terminal interactiva
        while True:
            command = input("Ingrese un comando: ").strip().lower()
            if command == ":exit":
                s.send(command.encode())
                break
            elif command in [":status", ":details", ":history", ":operations", ":connect", ":disconnect"]:
                s.send(command.encode())
                response = s.recv(4096).decode()  # Asumiendo que se puede recibir una cantidad grande de datos.
                print(response)
            else:
                print("Comando no reconocido.")
                print_menu()

        print("Desconectado del servidor.")

if __name__ == "__main__":
    main()
