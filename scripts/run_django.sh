#!/bin/bash

PORT=${PORT:-8000}

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --port) PORT="$2"; shift ;;
        *) echo "Opción desconocida: $1" ;;
    esac
    shift
done

echo "Realizando migraciones..."
python manage.py migrate

echo "Iniciando el servidor en el puerto $PORT..."
python manage.py runserver "0.0.0.0:$PORT"