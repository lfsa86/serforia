#!/bin/bash

# Esperar a que SQL Server esté listo
echo "Esperando a que SQL Server esté listo..."
sleep 30

# Ejecutar el script SQL
echo "Ejecutando el dump SQL..."
/opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P $SA_PASSWORD -i /docker-entrypoint-initdb.d/DataPilotoIA.sql

echo "Base de datos inicializada correctamente."