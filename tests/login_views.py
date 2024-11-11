import requests
from concurrent.futures import ThreadPoolExecutor
import time

# Lista de usuarios y contraseñas de prueba con las nuevas contraseñas
usuarios = [
    {"email": "MTTITOP@autonoma.edu.pe", "password": "123456789"},
    {"email": "sanchezdeyes16@autonoma.edu.pe", "password": "123456789"},
    {"email": "dingas@autonoma.edu.pe", "password": "123456789"},
    {"email": "abner.7.gonzales@gmail.com", "password": "123456789"},
    {"email": "tito@autonoma.edu.pe", "password": "123456789"},
    {"email": "daaaa@autonoma.edu.pe", "password": "123456789"},
    {"email": "minaya@autonoma.edu.pe", "password": "123456789"},
    {"email": "epittmanm@autonoma.edu.pe", "password": "123456789"},
    {"email": "masami@superlearnerperu.com", "password": "123456789"},
    {"email": "maxxd814@gmail.com", "password": "123456789"},
]

# URL de inicio de sesión
url_login = "http://127.0.0.1:8000/usuario/login/Login/"

# Función para hacer una solicitud de inicio de sesión
def iniciar_sesion(usuario):
    response = requests.post(url_login, json=usuario)
    return {"email": usuario["email"], "status_code": response.status_code, "response": response.json()}

# Función principal para ejecutar las pruebas
def realizar_pruebas(min_respuestas):
    respuestas = 0
    while respuestas < min_respuestas:
        with ThreadPoolExecutor(max_workers=50) as executor:
            # Ejecutar las pruebas de manera concurrente
            resultados = list(executor.map(iniciar_sesion, usuarios))
            
            # Imprimir los resultados de esta tanda de pruebas
            for resultado in resultados:
                print(f"Usuario: {resultado['email']}, Código de estado: {resultado['status_code']}, Respuesta: {resultado['response']}")
                respuestas += 1
                if respuestas >= min_respuestas:
                    break
        # Espera un poco antes de enviar otra tanda de solicitudes
        time.sleep(2)  # Ajusta el tiempo de espera si es necesario

# Llamada a la función principal para ejecutar las pruebas hasta obtener al menos 100 respuestas
realizar_pruebas(min_respuestas=100)
