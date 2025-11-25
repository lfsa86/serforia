#!/bin/bash

# Script para construir y ejecutar el contenedor de SQL Server

echo "=== Construyendo imagen de SQL Server ==="
docker build -t serfor-sqlserver:latest .

if [ $? -eq 0 ]; then
    echo ""
    echo "=== Imagen construida exitosamente ==="
    echo ""
    echo "=== Deteniendo contenedor anterior si existe ==="
    docker stop serfor-sqlserver 2>/dev/null
    docker rm serfor-sqlserver 2>/dev/null

    echo ""
    echo "=== Iniciando contenedor ==="
    docker run -d \
        --name serfor-sqlserver \
        -p 1433:1433 \
        -v sqlserver_data:/var/opt/mssql \
        serfor-sqlserver:latest

    if [ $? -eq 0 ]; then
        echo ""
        echo "=== Contenedor iniciado exitosamente ==="
        echo ""
        echo "Puedes ver los logs con: docker logs -f serfor-sqlserver"
        echo "Conexión: localhost,1433"
        echo "Usuario: sa"
        echo "Password: SerforDB@2025"
        echo "Base de datos: SERFOR_BDDWH"
    else
        echo "Error al iniciar el contenedor"
        exit 1
    fi
else
    echo "Error al construir la imagen"
    exit 1
fi
