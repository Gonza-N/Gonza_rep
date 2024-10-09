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
def ejecutivo_terminal():
    ejecutivo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ejecutivo.connect(("localhost", 9999))  # Conectar al servidor local

    while True:
        email = input("Ingrese su correo: ").strip().lower()
        ejecutivo.send(email.encode())
        respuesta = ejecutivo.recv(1024).decode()
        if "Correo encontrado" in respuesta:
            while True:
                password = input("Correo encontrado. Por favor ingrese su contraseña: ").strip()
                ejecutivo.send(password.encode())
                respuesta = ejecutivo.recv(1024).decode()
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
            clientes_db = cargar_db()
            print("\nOpciones para ejecutivo:")
            print("[1] .status - Ver cantidad de clientes conectados y solicitudes")
            print("[2] .details - Ver clientes conectados y su última acción")
            print("[3] .history - Ver historial del cliente actual")
            print("[4] .operations - Ver todo el historial de operaciones del cliente")
            print("[5] .connect - Conectarse con el primer cliente en cola")
            print("[6] .disconnect - Terminar la conexión con el cliente")
            print("[7] .exit - Desconectarse del servidor")

            opcion = input("Seleccione una opción: ")
            if opcion not in ['1', '2', '3', '4', '5', '6', '7']:
                print("Opción no válida. Ingrese una opción válida.")
                continue
            ejecutivo.send(opcion.encode())
            if opcion == '1':
                mensaje = ejecutivo.recv(1024).decode()
                print(f"[SERVIDOR]: {mensaje}")
                mensaje2 = ejecutivo.recv(1024).decode()
                print(f"[SERVIDOR]: {mensaje2}")

            elif opcion == '2':
                # Mostrar detalles de los clientes conectados
                mensaje = ejecutivo.recv(1024).decode()
                print(f"[SERVIDOR]: {mensaje}")
            elif opcion == '3':
                # Mostrar el historial del cliente que está siendo atendido
                mensaje = ejecutivo.recv(1024).decode()
                print(f"[SERVIDOR]: {mensaje}")
                
            elif opcion == '5':
                mensaje = ejecutivo.recv(1024).decode()
                if "No hay clientes" in mensaje:
                    print("[SERVIDOR]: No hay clientes en cola.")
                else:
                    while True:
                        mensaje = input("Ejecutivo, ingresa tu mensaje: ").strip()
                        ejecutivo.send(mensaje.encode())  # enviar al servidor
                        respuesta = ejecutivo.recv(1024).decode()  # recibir respuesta del servidor
                        if respuesta == "history":
                            mensaje = ejecutivo.recv(1024).decode()
                            print(f"[SERVIDOR]: {mensaje}")
                        if respuesta == "Cliente desconectado":
                            break
                        print(f"[Cliente] {respuesta}")
            elif opcion == '7':                # Salir del sistema
                print("Desconectando del servidor...")
                ejecutivo.send("exit".encode())
                ejecutivo.close()
                break    
            continuar = input("¿Desea realizar otra acción? [1] Sí [otro] No: ").strip()
        if continuar != '1':
            print("[CLIENTE] Desconectando...")      
                
        break


if __name__ == "__main__":
    ejecutivo_terminal()