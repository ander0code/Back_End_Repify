
# 🐍 Backend Repify con Django REST Framework

Backend construido con Django REST Framework (DRF), utilizando PostgreSQL como base de datos y desplegado en Google Cloud Run con Docker.

## 🚀 Características

- API RESTful construida con **Django REST Framework**.
- Base de datos PostgreSQL.
- Contenedorizado con **Docker**.
- Desplegado en Google Cloud Run para escalabilidad y alta disponibilidad.
- Autenticación basada en tokens (JWT o similar).

## 📚 Stack Tecnológico

### 🖥️ Backend
- **Lenguaje:** Python
- **Framework:** Django REST Framework (DRF)
- **Base de Datos:** PostgreSQL
- **Serialización:** DRF serializers
- **Validaciones y lógica de negocio:** Utilizando DRF y módulos nativos de Python.

### 🔒 Autenticación
- **Protocolo:** JSON Web Tokens (JWT) para autenticación basada en tokens.
- **Gestión de usuarios:** Implementación de modelos personalizados de usuarios con DRF.

### ☁️ Despliegue
- **Contenerización:** Docker para empaquetar la aplicación.
- **Servicio Cloud:** Google Cloud Run para el despliegue serverless.

### 🧩 API y Documentación
- **Documentación de la API:** DRF + herramientas como Swagger o Redoc.


## 🛠 Instalación

1. Clona este repositorio:

   ```bash
   git clone https://github.com/usuario/proyecto-backend.git
   cd proyecto-backend
   ```

2. Configura las variables de entorno. Crea un archivo `.env` basado en el ejemplo:

   ```bash
   cp .env.example .env
   ```

3. Construye el contenedor Docker:

   ```bash
   docker-compose build
   ```

4. Inicia los servicios:

   ```bash
   docker-compose up
   ```

   Esto levantará el backend junto con la base de datos PostgreSQL.

5. Aplica las migraciones de Django:

   ```bash
   docker-compose exec web python manage.py migrate
   ```

6. (Opcional) Crea un superusuario para acceder al panel de administración:

   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

## ▶️ Uso

El servidor estará disponible en:

```
http://localhost:8000
```

- La documentación de la API, si está habilitada, estará en `http://localhost:8000/api/docs/`.

## 📂 Estructura del Proyecto

```plaintext
BACK_END_REPIFY/
├── usuario/                  # Aplicaciones Django
|   ├── admin.py 
|   ├── apps.py  
│   ├── models.py         # Modelos de datos
│   ├── serializers.py    # Serializadores de DRF
│   ├── views.py          # Vistas de la API
│   ├── urls.py           # Rutas de la aplicación
│   └── tests/            # Pruebas unitarias
├── repo/             # Configuración principal de Django
│   ├── settings.py       # Configuración general
│   ├── urls.py           # Rutas principales
│   └── wsgi.py           # Configuración para WSGI
├── manage.py             # Herramienta de administración de Django
├── Dockerfile            # Configuración para construir el contenedor Docker
├── .dockerignore         # Configuración de Docker Compose
└── requirements.txt      # Dependencias del proyecto
```

## 🌍 Variables de Entorno

El proyecto utiliza un archivo `.env` para gestionar las variables sensibles. Aquí están las principales:

- `DJANGO_SECRET_KEY`: Clave secreta de Django.
- `DATABASE_URL`: URI de conexión a la base de datos PostgreSQL.
- `DEBUG`: Modo de depuración (True/False).
- `ALLOWED_HOSTS`: Hosts permitidos para servir el backend.
- `CLOUD_RUN_SERVICE`: Nombre del servicio desplegado en Cloud Run.

Ejemplo de `.env`:

```env
DJANGO_SECRET_KEY=supersecreto123
DATABASE_URL=postgres://user:password@db:5432/nombre_bd
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CLOUD_RUN_SERVICE=my-cloud-run-service
```

## 📡 API Endpoints

Documentación básica de los endpoints principales:

| Método | Endpoint               | Descripción                  | Autenticación |
|--------|------------------------|------------------------------|---------------|
| `GET`  | `/api/v1/items/`       | Lista todos los ítems        | No            |
| `POST` | `/api/v1/items/`       | Crea un nuevo ítem           | Sí            |
| `GET`  | `/api/v1/items/<id>/`  | Detalles de un ítem específico | No          |
| `PUT`  | `/api/v1/items/<id>/`  | Actualiza un ítem específico | Sí            |
| `DELETE` | `/api/v1/items/<id>/` | Elimina un ítem específico   | Sí            |

(O proporciona un enlace a una documentación más completa como Swagger o Postman.)

## 🧪 Pruebas

Ejecuta las pruebas utilizando Django:

```bash
docker-compose exec web python manage.py test
```

## 🚀 Despliegue

1. Construye la imagen Docker:

   ```bash
   docker build -t mi-backend:latest .
   ```

2. Sube la imagen a un registro de contenedores (por ejemplo, Google Container Registry):

   ```bash
   docker tag mi-backend gcr.io/tu-proyecto/mi-backend
   docker push gcr.io/tu-proyecto/mi-backend
   ```

3. Despliega la imagen en Google Cloud Run:

   ```bash
   gcloud run deploy mi-backend        --image gcr.io/tu-proyecto/mi-backend        --platform managed        --region tu-region        --allow-unauthenticated
   ```

## 🤝 Contribuir

1. Haz un fork del proyecto.
2. Crea una nueva rama para tu contribución:
   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```
3. Haz tus cambios y realiza commits:
   ```bash
   git commit -m "Añadida nueva funcionalidad"
   ```
4. Envía un Pull Request.

## 📄 Licencia

Este proyecto está bajo la licencia [MIT](./LICENSE).

---

### ¡Listo para usar! 🎉
