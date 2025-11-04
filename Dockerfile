FROM mcr.microsoft.com/mssql/server:2022-latest

# Configurar variables de entorno
ENV ACCEPT_EULA=Y
ENV SA_PASSWORD=SerforDB@2025
ENV MSSQL_PID=Developer

# Crear directorio para scripts
USER root
RUN mkdir -p /usr/config
WORKDIR /usr/config

# Copiar scripts SQL
COPY init/DataPilotoIA.sql /usr/config/DataPilotoIA.sql
COPY init/setup.sql /usr/config/setup.sql

# Copiar script de inicialización
COPY init/entrypoint.sh /usr/config/entrypoint.sh
RUN chmod +x /usr/config/entrypoint.sh

# Exponer puerto
EXPOSE 1433

# Ejecutar script de inicialización
ENTRYPOINT ["/usr/config/entrypoint.sh"]
