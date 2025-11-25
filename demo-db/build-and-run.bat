@echo off
echo === Construyendo imagen de SQL Server ===
docker build -t serfor-sqlserver:latest .

if %ERRORLEVEL% EQU 0 (
    echo.
    echo === Imagen construida exitosamente ===
    echo.
    echo === Deteniendo contenedor anterior si existe ===
    docker stop serfor-sqlserver 2>nul
    docker rm serfor-sqlserver 2>nul

    echo.
    echo === Iniciando contenedor ===
    docker run -d --name serfor-sqlserver -p 1433:1433 -v sqlserver_data:/var/opt/mssql serfor-sqlserver:latest

    if %ERRORLEVEL% EQU 0 (
        echo.
        echo === Contenedor iniciado exitosamente ===
        echo.
        echo Puedes ver los logs con: docker logs -f serfor-sqlserver
        echo Conexion: localhost,1433
        echo Usuario: sa
        echo Password: SerforDB@2025
        echo Base de datos: SERFOR_BDDWH
    ) else (
        echo Error al iniciar el contenedor
        exit /b 1
    )
) else (
    echo Error al construir la imagen
    exit /b 1
)
