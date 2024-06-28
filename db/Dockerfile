# Imagen de postgres
FROM postgres:latest

ENV POSTGRES_PASSWORD=myStrong#Password

# Copia el archivo de configuracion de postgres
COPY init_db.sql /docker-entrypoint-initdb.d/

# Copia el archivo de configuracion de postgres
COPY seeders.sql /docker-entrypoint-initdb.d/

EXPOSE 5432