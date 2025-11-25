#!/bin/bash

# Iniciar SQL Server en segundo plano
/opt/mssql/bin/sqlservr &

# Esperar a que SQL Server esté listo
echo "Esperando a que SQL Server inicie..."
sleep 30s

# Intentar conectar hasta que SQL Server esté listo
for i in {1..50};
do
    /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P $SA_PASSWORD -C -Q "SELECT 1" > /dev/null 2>&1
    if [ $? -eq 0 ]
    then
        echo "SQL Server está listo"
        break
    else
        echo "Esperando a SQL Server... intento $i"
        sleep 2s
    fi
done

# Ejecutar script de setup (crear base de datos y schema)
echo "Ejecutando setup.sql..."
/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P $SA_PASSWORD -C -i /usr/config/setup.sql

# Ejecutar script de datos
echo "Ejecutando DataPilotoIA.sql..."
/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P $SA_PASSWORD -C -i /usr/config/DataPilotoIA.sql

# Ejecutar script de datos
echo "Ejecutando scriptBDIA29102025.sql..."
/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P $SA_PASSWORD -C -i /usr/config/scriptBDIA29102025.sql

# Ejecutar script de parche para vistas
echo "Ejecutando PATCH_correccion_vistas.sql..."
/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P $SA_PASSWORD -C -i /usr/config/PATCH_correccion_vistas.sql

echo "Inicialización completada"

# Mantener el contenedor en ejecución
wait
