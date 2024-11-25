import requests
import json

# URL del endpoint de registro
API_URL = "https://back-end-repify-340032812084.us-central1.run.app/usuario/login/Register/"

# Lista de usuarios (coloca aquí los JSON que te di anteriormente)
usuarios = [
  {
    "email": "emilio.castro11@uni.edu.pe",
    "password": "emilioPass123",
    "university": "Universidad Nacional de Ingeniería",
    "career": "Ingeniería Mecánica",
    "cycle": "IV",
    "biography": "Futuro ingeniero especializado en energía renovable.",
    "interests": ["Energías renovables", "Mecánica de fluidos"],
    "photo": "",
    "achievements": "Prototipo de turbina eólica casera",
    "first_name": "Emilio",
    "last_name": "Castro"
  },
  {
    "email": "lucia.santana12@pucp.edu.pe",
    "password": "luciaPass456",
    "university": "Pontificia Universidad Católica del Perú",
    "career": "Psicología",
    "cycle": "VII",
    "biography": "Enfocada en la psicología infantil.",
    "interests": ["Desarrollo infantil", "Psicología educativa"],
    "photo": "",
    "achievements": "Participé en campañas de salud mental",
    "first_name": "Lucía",
    "last_name": "Santana"
  },
  {
    "email": "eduardo.rios13@upe.edu.pe",
    "password": "eduPass789",
    "university": "Universidad Privada del Este",
    "career": "Ingeniería Ambiental",
    "cycle": "V",
    "biography": "Defensor del medio ambiente y recursos naturales.",
    "interests": ["Gestión ambiental", "Sostenibilidad"],
    "photo": "",
    "achievements": "Líder en proyectos de reciclaje",
    "first_name": "Eduardo",
    "last_name": "Ríos"
  },
  {
    "email": "paola.cano14@utp.edu.pe",
    "password": "paolaSecure001",
    "university": "Universidad Tecnológica del Perú",
    "career": "Ingeniería de Sistemas",
    "cycle": "VI",
    "biography": "Apasionada por la programación y los datos.",
    "interests": ["Data science", "Programación en Python"],
    "photo": "",
    "achievements": "Ganadora de hackathon universitaria",
    "first_name": "Paola",
    "last_name": "Cano"
  },
  {
    "email": "diego.silva15@unsa.edu.pe",
    "password": "silvaKey002",
    "university": "Universidad Nacional de San Agustín",
    "career": "Ingeniería de Minas",
    "cycle": "III",
    "biography": "Explorando los recursos minerales del Perú.",
    "interests": ["Minería sostenible", "Geología"],
    "photo": "",
    "achievements": "Prácticas en yacimientos mineros",
    "first_name": "Diego",
    "last_name": "Silva"
  },
  {
    "email": "valeria.zeballos16@ucp.edu.pe",
    "password": "valeriaPass123",
    "university": "Universidad Continental",
    "career": "Marketing",
    "cycle": "VIII",
    "biography": "Creativa y entusiasta del marketing digital.",
    "interests": ["Redes sociales", "Análisis de mercado"],
    "photo": "",
    "achievements": "Certificación en campañas publicitarias",
    "first_name": "Valeria",
    "last_name": "Zeballos"
  },
  {
    "email": "oscar.flores17@upe.edu.pe",
    "password": "oscarSecure456",
    "university": "Universidad Privada del Este",
    "career": "Administración de Negocios Internacionales",
    "cycle": "VII",
    "biography": "Interesado en la gestión de empresas globales.",
    "interests": ["Comercio internacional", "Gestión de proyectos"],
    "photo": "",
    "achievements": "Representante en conferencias de negocios",
    "first_name": "Óscar",
    "last_name": "Flores"
  },
  {
    "email": "daniela.mendoza18@upc.edu.pe",
    "password": "danielaKey789",
    "university": "Universidad Peruana de Ciencias Aplicadas",
    "career": "Comunicación Social",
    "cycle": "II",
    "biography": "Explorando el mundo de los medios y la sociedad.",
    "interests": ["Periodismo", "Producción audiovisual"],
    "photo": "",
    "achievements": "Productora de un cortometraje estudiantil",
    "first_name": "Daniela",
    "last_name": "Mendoza"
  },
  {
    "email": "miguel.rosales19@uap.edu.pe",
    "password": "rosalesPass123",
    "university": "Universidad Alas Peruanas",
    "career": "Ingeniería de Software",
    "cycle": "VIII",
    "biography": "Apasionado por la tecnología y la innovación.",
    "interests": ["Cloud computing", "Blockchain"],
    "photo": "",
    "achievements": "Creador de una plataforma de gestión escolar",
    "first_name": "Miguel",
    "last_name": "Rosales"
  },
  {
    "email": "carla.torres20@unsa.edu.pe",
    "password": "carlaSecure456",
    "university": "Universidad Nacional de San Agustín",
    "career": "Medicina",
    "cycle": "IX",
    "biography": "Futura doctora dedicada a la pediatría.",
    "interests": ["Salud infantil", "Nutrición"],
    "photo": "",
    "achievements": "Participación en brigadas médicas rurales",
    "first_name": "Carla",
    "last_name": "Torres"
  }
]

# Función para registrar un usuario
def registrar_usuario(usuario):
    try:
        # Enviar solicitud POST al endpoint
        response = requests.post(API_URL, json=usuario)
        if response.status_code == 201:
            print(f"[ÉXITO] Usuario registrado: {usuario['email']}")
            return response.json()
        else:
            print(f"[ERROR] No se pudo registrar el usuario: {usuario['email']}")
            print(f"Detalles: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[EXCEPCIÓN] Error al registrar usuario {usuario['email']}: {str(e)}")

# Registrar todos los usuarios
def registrar_todos():
    resultados = []
    for usuario in usuarios:
        resultado = registrar_usuario(usuario)
        resultados.append(resultado)
    return resultados

if __name__ == "__main__":
    print("Inicio de la carga masiva de usuarios...")
    resultados = registrar_todos()
    print("Carga masiva completada.")
