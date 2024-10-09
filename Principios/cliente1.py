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
def cliente_terminal():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect(("localhost", 9999))  # Conectar al servidor local

    while True:
        email = input("Ingrese su correo: ").strip().lower()
        cliente.send(email.encode())
        respuesta = cliente.recv(1024).decode()

        if "Correo encontrado" in respuesta:
            while True:
                password = input("Correo encontrado. Por favor ingrese su contraseña: ").strip()
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
            clientes_db = cargar_db()
            print("\nOpciones:")
            print("[1] Cambiar contraseña")
            print("[2] Ver historial de pedidos")
            print("[3] Comprar producto")
            print("[4] Solicitar devolución")
            print("[5] Confirmar envío")
            print("[6] Contactarse con el ejecutivo")
            print("[7] Salir")

            opcion = input("Ingrese una opción: ").strip()
            if opcion not in ['1', '2', '3', '4', '5', '6', '7']:
                print("Opción no válida. Ingrese una opción válida.")
                continue
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
                while True:
                    respuesta = cliente.recv(1024).decode()

                    if "Historial de compras" in respuesta:
                        print(f"[SERVIDOR]: {respuesta}")
                        break  # Salir del bucle después de recibir la respuesta correcta
                    elif "No hay compras registradas" in respuesta:
                        print(f"[SERVIDOR]: {respuesta}")
                        break  # Salir del bucle si no hay compras registradas
                    else:
                        # Si el cliente no fue encontrado, volver a intentar
                        print(f"[SERVIDOR]: {respuesta}")
                        intentar_otra_vez = input("¿Desea intentar nuevamente? (s/n): ").strip().lower()
                        if intentar_otra_vez != 's':
                            break

            if opcion == "3":
                while True:
                    for producto, info in clientes_db['productos'].items():
                        print(f"{info['nombre']}: stock {info['stock']}")
                    # Solicitar el nombre del producto al usuario
                    producto = input("Ingrese el producto a comprar: ").strip().lower()
                    cliente.send(producto.encode())
                    # Recibir respuesta del servidor sobre el producto
                    respuesta = cliente.recv(1024).decode()  
                    if "Producto encontrado" in respuesta:
                        print(f"[SERVIDOR]: {respuesta}")
                        while True:
                            # Solicitar la cantidad de producto a comprar
                            cantidad = input("Ingrese la cantidad a comprar: ").strip()
                            # Enviar la cantidad al servidor
                            cliente.send(cantidad.encode())
                            # Recibir respuesta del servidor sobre la cantidad y el stock disponible
                            respuesta = cliente.recv(1024).decode()
                            if "Compra Exitosa" in respuesta:
                                print(f"[SERVIDOR]: {respuesta}")
                                break  # Salir del bucle ya que la compra fue exitosa
                            else:
                                # Si el stock es insuficiente, se muestra el mensaje del servidor
                                print(f"[SERVIDOR]: {respuesta}")
                        break
                    else:
                        # Producto no encontrado, pedir al usuario intentar nuevamente
                        print(f"[SERVIDOR]: Producto no encontrado.")
                        

                    
            if opcion == "4":
                if clientes_db['usuarios']['clientes'][email]['historial_compras']:  # Verificar si el historial no está vacío
                    for compra in clientes_db['usuarios']['clientes'][email]['historial_compras']:
                        print(f"  Fecha: {compra['fecha']}, Producto: {compra['producto']}, Cantidad: {compra['cantidad']}")
                else:
                    print("  No hay historial de compras.")
                producto = input("Ingrese el producto a devolver: ").strip()
                cliente.send(producto.encode())
                cantidad = input("Ingrese la cantidad a devolver: ").strip()
                cliente.send(cantidad.encode())
                respuesta = cliente.recv(1024).decode()
                print(f"[SERVIDOR]: {respuesta}")
            if opcion == "5":
                producto = input("Ingrese el producto a confirmar envío: ").strip()
                cliente.send(producto.encode())
                respuesta = cliente.recv(1024).decode()
                print(f"[SERVIDOR]: {respuesta}")
            if opcion == "6":
                msg = cliente.recv(1024).decode()
                print(f"[SERVIDOR]: {msg}")
                while True:
                    mensaje = cliente.recv(1024).decode()  # recibir mensaje del servidor
                    if mensaje == "history":
                        mensaje = cliente.recv(1024).decode()
                        print(f"[SERVIDOR]: {mensaje}")
                    elif mensaje == "Ejecutivo desconectado":
                        break
                    elif "historial de operaciones" in mensaje:
                        print("Historial de operaciones del cliente:")
                        respuesta = cliente.recv(1024).decode()
                        print(f"[SERVIDOR]: {respuesta}")
                    else:
                        print(f"[Ejecutivo] {mensaje}")
                        respuesta = input(">:").strip()
                        cliente.send(respuesta.encode())  # enviar respuesta al servidor
                
            if opcion == "7":               
                print("[CLIENTE] Desconectando...")
                cliente.send("exit".encode())
                cliente.close()
                break 
            continuar = input("¿Desea realizar otra acción? [1] Sí [otro] No: ").strip()
        if continuar != '1':
            print("[CLIENTE] Desconectando...")
                        
        break
if __name__ == "__main__":
    cliente_terminal()