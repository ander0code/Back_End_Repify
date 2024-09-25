#!/bin/bash
set -e

# Instalar dependencias
pip install -r requirements.txt

# Realizar migraciones (opcional, dependiendo de tu flujo de trabajo)
python manage.py migrate

# Recopilar archivos estáticos
python manage.py collectstatic --noinput