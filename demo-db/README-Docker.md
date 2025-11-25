# SERFOR Database Docker Setup

Este setup de Docker Compose configura una base de datos SQL Server con los datos del dump `DataPilotoIA.sql`.

## Estructura

```
├── docker-compose.yml          # Configuración principal
├── init/
│   ├── DataPilotoIA.sql       # Dump de la base de datos
│   └── init-db.sh             # Script de inicialización
└── README-Docker.md           # Este archivo
```

## Base de Datos

- **Nombre**: `SERFOR_BDDWH`
- **Esquema principal**: `Dir`
- **Tablas principales**:
  - `T_GEP_INFRACTORES` - Datos de infractores
  - `T_GEP_TITULOHABILITANTE` - Datos de títulos habilitantes

## Configuración

### Credenciales
- **Usuario**: `sa`
- **Contraseña**: `SerforDB@2025`
- **Puerto**: `1433`

### Uso

1. **Iniciar la base de datos**:
   ```bash
   docker-compose up -d
   ```

2. **Configurar la base de datos** (solo la primera vez):
   ```bash
   docker exec serfor-sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "SerforDB@2025" -C -i /tmp/setup.sql
   ```

3. **Cargar los datos del dump** (solo la primera vez):
   ```bash
   docker exec serfor-sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "SerforDB@2025" -C -i /tmp/DataPilotoIA.sql
   ```

4. **Verificar que los datos se cargaron**:
   ```bash
   docker exec serfor-sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "SerforDB@2025" -C -Q "USE SERFOR_BDDWH; SELECT COUNT(*) AS TotalInfractores FROM Dir.T_GEP_INFRACTORES;"
   ```

5. **Conectar a la base de datos**:
   ```bash
   docker exec -it serfor-sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "SerforDB@2025" -C
   ```

6. **Usar la base de datos** (dentro de sqlcmd):
   ```sql
   USE SERFOR_BDDWH;
   GO
   SELECT COUNT(*) FROM Dir.T_GEP_INFRACTORES;
   SELECT COUNT(*) FROM Dir.T_GEP_TITULOHABILITANTE;
   GO
   ```

7. **Ver logs**:
   ```bash
   docker-compose logs -f sqlserver
   ```

8. **Detener**:
   ```bash
   docker-compose down
   ```

9. **Limpiar completamente** (elimina datos):
   ```bash
   docker-compose down -v
   ```

## Notas

- Los datos se persisten en el volumen `sqlserver_data`
- La inicialización de la base de datos se hace manualmente con los comandos de los pasos 2 y 3
- Si necesitas reinicializar, elimina el volumen con `docker-compose down -v` y vuelve a ejecutar los pasos de configuración
- El parámetro `-C` en sqlcmd es necesario para confiar en el certificado auto-firmado de SQL Server