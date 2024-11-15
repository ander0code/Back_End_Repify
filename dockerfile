# Usa una imagen base oficial de Python
FROM python:3.11-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia el archivo de requerimientos al directorio de trabajo
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el archivo .env al directorio de trabajo
COPY .env .env

# Copia el resto del código de la aplicación al directorio de trabajo
COPY . .

# Establece las variables de entorno necesarias
ENV DJANGO_SETTINGS_MODULE=repo.settings
ENV PYTHONUNBUFFERED=1

# Ejecuta las migraciones y recopila los archivos estáticos
RUN python manage.py migrate
RUN python manage.py collectstatic --noinput

# Expone el puerto en el que la aplicación correrá
EXPOSE 8000

# Comando para correr la aplicación
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "repo.wsgi:application"]