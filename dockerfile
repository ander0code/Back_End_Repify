FROM python:3.12.7-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para algunas librerías
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && apt-get clean

# Actualizar pip
RUN pip install --upgrade pip

# Copiar el archivo de requerimientos y luego instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código del proyecto
COPY . .

# Exponer el puerto 8000
EXPOSE 8000

# Comando para ejecutar la aplicación (desarrollo o producción)
CMD ["gunicorn", "repo.wsgi:application", "--bind", "0.0.0.0:8000"]