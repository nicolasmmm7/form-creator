# Usar una imagen base oficial de Python
FROM python:3.11-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Establecer variables de entorno
# Evita que Python genere archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
# Evita que Python guarde en búfer stdout y stderr
ENV PYTHONUNBUFFERED=1

# Instalar dependencias del sistema si son necesarias
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requerimientos
COPY backend/requirements.txt /app/backend/requirements.txt

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Instalar gunicorn explícitamente para producción
RUN pip install gunicorn

# Copiar el resto del código del proyecto
COPY . /app/

# Recolectar archivos estáticos (opcional, depende de si usas whitenoise o similar, 
# pero es buena práctica tenerlo si Django maneja estáticos)
# RUN python manage.py collectstatic --noinput

# Exponer el puerto que usará la aplicación (Railway usa PORT dinámico, pero documentamos 8000)
EXPOSE 8000

# Comando para correr la aplicación usando gunicorn
# Se usa la variable de entorno PORT que Railway provee automáticamente
CMD gunicorn formCreatorApp.wsgi:application --bind 0.0.0.0:$PORT
