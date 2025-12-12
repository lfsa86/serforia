"""
Conocimiento de dominio de SERFOR - Textos para usar en prompts
"""

# =============================================================================
# SINÓNIMOS - Cómo la gente pide cada entidad
# =============================================================================

ENTITY_SYNONYMS = """
SINÓNIMOS Y TÉRMINOS EQUIVALENTES:

V_AUTORIZACION_DESBOSQUE:
  permiso de desbosque, autorización para retirar bosque, permiso para limpiar terreno,
  licencia para deforestar, retiro de cobertura forestal, permiso para desmonte,
  permiso para tumbar monte, desbosque

V_CAMBIO_USO:
  cambio de uso, CUS, permiso para uso agrícola en zona de bosque,
  permiso para convertir terreno en chacra, cambio de clasificación de tierras,
  permiso para sembrar en el monte

V_AUTORIZACION_DEPOSITO:
  depósitos, lugares de venta de madera, lugares de venta de productos forestales,
  centros de comercialización, lugares de acopio

V_AUTORIZACION_CTP:
  CTP, centro de transformación primaria, planta de transformación,
  aserradero, laminadora, centro de procesamiento

V_LICENCIA_CAZA:
  licencias de caza, caza deportiva, permiso de caza

V_PLANTACION:
  plantaciones forestales, RNPF, registro de plantaciones, reforestación

V_INFRACTOR:
  infractores, sanciones, multas, infracciones, RNI, sancionados

V_TITULOHABILITANTE:
  títulos habilitantes, permisos forestales, concesiones, concesiones madereras,
  concesiones de castaña, concesiones de ecoturismo, cesiones en uso, bosque local
"""

# =============================================================================
# DESCRIPCIONES DE ENTIDADES
# =============================================================================

ENTITY_DESCRIPTIONS = """
DESCRIPCIÓN DE CADA VISTA:

V_AUTORIZACION_DESBOSQUE:
  Autorización para el retiro físico de cobertura forestal. Permite actividades no forestales
  como infraestructura, minería, hidrocarburos. NO confundir con tala o aprovechamiento forestal.

V_CAMBIO_USO:
  Autorización para cambiar clasificación de tierra de "uso forestal" a "uso agropecuario".
  Es PREVIO y OBLIGATORIO antes del desbosque para fines agrícolas.

V_AUTORIZACION_DEPOSITO:
  Autorización para lugares de acopio, depósitos y centros de comercialización
  de productos forestales y fauna silvestre.

V_AUTORIZACION_CTP:
  Autorización para Centros de Transformación Primaria (aserraderos, laminadoras, etc.)

V_LICENCIA_CAZA:
  Licencias de caza deportiva (sin fines de lucro). Otorgadas por ARFFS.

V_PLANTACION:
  Registro Nacional de Plantaciones Forestales. Incluye plantaciones de producción,
  protección y restauración.

V_INFRACTOR:
  Registro Nacional de Infractores con sanciones y multas.
  IMPORTANTE: Multas en UIT (usar WHERE Multa > 10 directamente).
  NOTA: No tiene Departamento/Provincia/Distrito. Si necesitas ubicación, hacer JOIN con V_TITULOHABILITANTE.

V_TITULOHABILITANTE:
  Títulos habilitantes: permisos, concesiones, autorizaciones, cesiones, bosque local.
  Campo TipoTh: AUTORIZACIONES, BOSQUE LOCAL, CAMBIO DE USO, CONCESIONES, PERMISOS.
  Campo Situacion: VIGENTE, NO VIGENTE, EXTINGUIDO, OBSERVADO.
  Contiene ubicación geográfica (Departamento, Provincia, Distrito).
"""

# =============================================================================
# RELACIONES ENTRE VISTAS
# =============================================================================

VIEW_RELATIONSHIPS = """
RELACIONES ENTRE VISTAS (JOINs):

IMPORTANTE: Solo usar JOINs cuando la consulta EXPLÍCITAMENTE requiere cruzar datos.
Para consultas simples de una sola tabla, NO agregar JOINs.

⚠️ REGLA CRÍTICA - LIKE vs IGUALDAD:
  - LIKE es para BÚSQUEDAS del usuario: WHERE Titular LIKE '%Juan Pérez%'
  - IGUALDAD (=) es para JOINs entre vistas: ON a.NumeroDocumento = b.NumeroDocumento
  - ❌ NUNCA usar LIKE en JOINs: ON a.Col LIKE '%' + b.Col + '%' (causa timeout)
  - ✅ SIEMPRE usar = en JOINs: ON a.NumeroDocumento = b.NumeroDocumento

COLUMNAS DE RELACIÓN (usar con =):
  - NumeroDocumento: identificador principal para relacionar titulares entre vistas
  - TituloHabilitante: código del título habilitante (solo V_INFRACTOR ↔ V_TITULOHABILITANTE)

JOINs DISPONIBLES (todas por NumeroDocumento con =):

V_INFRACTOR puede cruzarse con:
  - V_TITULOHABILITANTE: para obtener ubicación (Departamento, Provincia, Distrito)
  - V_PLANTACION: para encontrar plantaciones de infractores
  - V_LICENCIA_CAZA: para encontrar licencias de caza de infractores
  - V_AUTORIZACION_CTP: para encontrar CTPs de infractores
  - V_AUTORIZACION_DEPOSITO: para encontrar depósitos de infractores

V_TITULOHABILITANTE puede cruzarse con:
  - V_PLANTACION, V_LICENCIA_CAZA, V_AUTORIZACION_CTP, V_AUTORIZACION_DEPOSITO,
    V_AUTORIZACION_DESBOSQUE, V_CAMBIO_USO (todo por NumeroDocumento)

CASO ESPECIAL - V_INFRACTOR ↔ V_TITULOHABILITANTE:
  - Usar SOLO cuando necesitas ubicación geográfica (V_INFRACTOR no tiene Departamento)
  - Si solo necesitas datos del infractor, consultar V_INFRACTOR directamente SIN JOIN

RELACIÓN DE NEGOCIO:
  V_CAMBIO_USO → V_AUTORIZACION_DESBOSQUE:
  - El cambio de uso es PREVIO al desbosque para fines agrícolas
"""

# =============================================================================
# NOTAS IMPORTANTES
# =============================================================================

IMPORTANT_NOTES = """
NOTAS IMPORTANTES:

SOBRE MULTAS:
  - El campo Multa en V_INFRACTOR ya está en UIT (Unidad Impositiva Tributaria)
  - Para "multas mayores a 10 UIT" usar: WHERE Multa > 10
  - NO buscar tablas de conversión, el valor ya está en UIT

SOBRE FECHAS (MUY IMPORTANTE):
  - Los campos de fecha pueden tener datos inconsistentes
  - NO usar BETWEEN con fechas directamente (puede fallar)
  - SIEMPRE usar YEAR() para filtrar por año: WHERE YEAR(FechaResolucion) = 2024
  - Para rango de años: WHERE YEAR(FechaResolucion) BETWEEN 2024 AND 2025
  - Para mes: WHERE YEAR(FechaResolucion) = 2024 AND MONTH(FechaResolucion) = 6

SOBRE UBICACIÓN GEOGRÁFICA:
  - V_INFRACTOR no tiene Departamento, Provincia, Distrito
  - Si necesitas ubicación de infractores: JOIN con V_TITULOHABILITANTE
  - Si NO necesitas ubicación: consultar V_INFRACTOR directamente SIN JOIN
  - Las demás vistas SÍ tienen campos de ubicación

SOBRE DESBOSQUE vs TALA:
  - Desbosque: remueve el bosque para otra actividad (no forestal)
  - Tala/Aprovechamiento: usa la madera manteniendo el bosque
  - Son conceptos diferentes, no confundir

SOBRE TIPOS DE TÍTULO (V_TITULOHABILITANTE.TipoTh):
  - AUTORIZACIONES: autorizaciones forestales
  - BOSQUE LOCAL: bosques administrados por municipalidades
  - CAMBIO DE USO: cambios de uso de suelo
  - CONCESIONES: concesiones forestales y de fauna
  - PERMISOS: permisos forestales y de fauna
"""

# =============================================================================
# GLOSARIO
# =============================================================================

GLOSSARY = """
GLOSARIO DE TÉRMINOS:

SERFOR: Servicio Nacional Forestal y de Fauna Silvestre de Perú
ARFFS: Autoridad Regional Forestal y de Fauna Silvestre
ATFFS: Administración Técnica Forestal y de Fauna Silvestre
OSINFOR: Organismo de Supervisión de los Recursos Forestales
UIT: Unidad Impositiva Tributaria (unidad para multas)
RNI: Registro Nacional de Infractores
RNPF: Registro Nacional de Plantaciones Forestales
CTP: Centro de Transformación Primaria
CUS: Cambio de Uso de Suelo
"""

# =============================================================================
# REGLAS DE NEGOCIO
# =============================================================================

BUSINESS_RULES_QUERIES = """
REGLA - TÍTULOS HABILITANTES (QUERIES):

Para consultas sobre V_TITULOHABILITANTE:
  - SIEMPRE incluir en SELECT y GROUP BY:
    * Situacion
    * OtorgaPermiso
  - Esto aplica incluso si el usuario no lo pide explícitamente

Ejemplo: "¿Cuántos títulos habilitantes hay en Loreto?"
  SELECT Situacion, OtorgaPermiso, COUNT(*) as Cantidad
  FROM V_TITULOHABILITANTE
  WHERE Departamento = 'LORETO'
  GROUP BY Situacion, OtorgaPermiso


REGLA - CONSULTAS CON PERIODOS DE TIEMPO (QUERIES):

Cuando la consulta involucre un rango de tiempo:
  - Incluir la columna de año/mes en SELECT y GROUP BY
  - Usar YEAR() o MONTH() según la granularidad del periodo

Ejemplo: "¿Cuántas infracciones hubo entre 2020 y 2023?"
  SELECT YEAR(FechaResolucion) as Anio, COUNT(*) as Cantidad
  FROM V_INFRACTOR
  WHERE YEAR(FechaResolucion) BETWEEN 2020 AND 2023
  GROUP BY YEAR(FechaResolucion)


REGLA - ORDENAMIENTO DE RESULTADOS:

Los resultados de las queries deben ordenarse de forma coherente:
  - Consultas con conteos: ORDER BY cantidad DESC (mostrar primero los más relevantes)
  - Consultas con fechas: ORDER BY fecha DESC (mostrar primero los más recientes)
  - Consultas con montos/superficies: ORDER BY monto DESC (mostrar primero los mayores)
  - Consultas con nombres/titulares: ORDER BY nombre ASC (orden alfabético)

Ejemplo: "¿Cuántos títulos hay por departamento?"
  SELECT Departamento, COUNT(*) as Cantidad
  FROM V_TITULOHABILITANTE
  GROUP BY Departamento
  ORDER BY Cantidad DESC


REGLA - SUPERFICIES EN CAMBIO DE USO Y DESBOSQUE (QUERIES):

En V_CAMBIO_USO y V_AUTORIZACION_DESBOSQUE, cuando consulten sobre área, superficie o hectáreas:
  - SIEMPRE incluir las tres columnas: Superficie, SuperficieConservar, SuperficieDesbosque

Ejemplo: "¿Cuál es la superficie autorizada para cambio de uso en San Martín?"
  SELECT Titular, Superficie, SuperficieConservar, SuperficieDesbosque
  FROM V_CAMBIO_USO
  WHERE Departamento = 'SAN MARTIN'


REGLA - PLANTACIONES (QUERIES):

En consultas sobre V_PLANTACION, SIEMPRE desagregar por FinalidadPlantacion:
  - Valores posibles: PRODUCCION, PROTECCION, RESTAURACION
  - Incluir en SELECT y GROUP BY aunque el usuario no lo pida explícitamente

Ejemplo: "¿Cuántas plantaciones hay en Cusco?"
  SELECT FinalidadPlantacion, COUNT(*) as Cantidad
  FROM V_PLANTACION
  WHERE Departamento = 'CUSCO'
  GROUP BY FinalidadPlantacion


REGLA - LICENCIAS DE CAZA (QUERIES):

En V_LICENCIA_CAZA, la columna EstadoLicencia siempre dice "APROBADA", pero eso no significa que esté vigente.
La columna CausalExtincion determina el estado real:
  - CausalExtincion IS NULL: licencia vigente/activa
  - CausalExtincion IS NOT NULL: licencia extinta (no vigente)

Cuando pregunten por:
  - Licencias vigentes/activas/aprobadas: WHERE CausalExtincion IS NULL
  - Licencias extintas/canceladas/vencidas: WHERE CausalExtincion IS NOT NULL

Ejemplo: "¿Cuántas licencias de caza están vigentes?"
  SELECT COUNT(*) as Cantidad
  FROM V_LICENCIA_CAZA
  WHERE CausalExtincion IS NULL

Ejemplo: "¿Cuántas licencias de caza están extintas?"
  SELECT CausalExtincion, COUNT(*) as Cantidad
  FROM V_LICENCIA_CAZA
  WHERE CausalExtincion IS NOT NULL
  GROUP BY CausalExtincion


REGLA - FECHAS EN TÍTULOS HABILITANTES (QUERIES):

En V_TITULOHABILITANTE:
  - FechaDocumento: fecha de EMISIÓN del título
  - FechaInicio/FechaFin: PERIODO de vigencia habilitado

Cuando pregunten por:
  - "¿Cuándo se emitió/otorgó?": usar FechaDocumento
  - "¿Cuándo empieza/termina la vigencia?": usar FechaInicio/FechaFin
  - "Títulos emitidos en 2023": WHERE YEAR(FechaDocumento) = 2023
  - "Títulos vigentes en 2024": WHERE FechaInicio <= '2024-12-31' AND FechaFin >= '2024-01-01'


REGLA - VALORES DE COLUMNAS CATEGÓRICAS:

V_TITULOHABILITANTE:
  - TipoTh: AUTORIZACIONES, BOSQUE LOCAL, CAMBIO DE USO, CESIÓN EN USO, CONCESIONES, DESBOSQUE, PERMISOS
  - TipoConcesion: CONSERVACIÓN, ECOTURISMO, FAUNA SILVESTRE, FINES MADERABLES, FORESTACIÓN Y/O REFORESTACIÓN, NO APLICA, PLANTACIONES FORESTALES, PRODUCTOS FORESTALES DIFERENTES A LA MADERA
  - Categoriapermiso: BOSQUE SECO, FAUNA SILVESTRE, MADERABLE, NO APLICA, NO MADERABLE
  - OtorgaPermiso: COMUNIDAD CAMPESINA, COMUNIDAD NATIVA, NO APLICA, PREDIO PRIVADO, TIERRAS DE DOMINIO PÚBLICO

V_PLANTACION:
  - FinalidadPlantacion: PRODUCCION, PROTECCION, RESTAURACION
  - Region: COSTA, SELVA, SIERRA
  - TipoPersona: PERSONA JURIDICA, PERSONA NATURAL
  - RegimenTenencia: COMUNIDAD CAMPESINA, COMUNIDAD NATIVA, NO APLICA, PREDIO PRIVADO, TIERRAS DE DOMINIO PÚBLICO
  - TipoComunidad: CAMPESINA, NATIVA

V_AUTORIZACION_DEPOSITO:
  - TipoDeposito: DEPOSITO, ESTABLECIMIENTO COMERCIAL, LUGAR DE ACOPIO

V_AUTORIZACION_CTP:
  - TipoRecurso: FAUNA SILVESTRE, FORESTAL
  - LineaProduccionGiro: ASERRADERO, LAMINADORA, PRODUCCION DE CARBON VEGETAL, TRIPLAYERA, otros

Usar estos valores exactos en las queries (respetando mayúsculas).
"""

BUSINESS_RULES_ESTADOS = """
REGLA - ESTADOS Y SITUACIONES:

Los términos "Estado" y "Situación" son sinónimos en el contexto de SERFOR.

Columnas de estado por tabla:
  - V_TITULOHABILITANTE.Situacion: VIGENTE, NO VIGENTE, EXTINGUIDO
  - V_CAMBIO_USO.Situacion: VIGENTE, NO VIGENTE, EXTINGUIDO
  - V_AUTORIZACION_DESBOSQUE.Situacion: VIGENTE, NO VIGENTE
  - V_AUTORIZACION_CTP.Estado: VIGENTE
  - V_AUTORIZACION_DEPOSITO.Estado: VIGENTE
  - V_LICENCIA_CAZA.EstadoLicencia: APROBADA
    NOTA: Para licencias extintas, verificar columna CausalExtincion (si no es NULL, la licencia está extinta aunque EstadoLicencia diga APROBADA)

Tablas SIN columna de estado:
  - V_PLANTACION (no aplica esta regla)
  - V_INFRACTOR (no aplica esta regla)

Comportamiento cuando el usuario NO especifica un estado:
  - La query debe incluir la columna de estado en el SELECT
  - Agregar GROUP BY por la columna de estado
  - La respuesta debe mostrar los resultados desglosados por cada estado

Ejemplo: Si preguntan "¿Cuántos títulos habilitantes hay en Lima?"
  - NO hacer: SELECT COUNT(*) FROM V_TITULOHABILITANTE WHERE Departamento = 'LIMA'
  - SÍ hacer: SELECT Situacion, COUNT(*) as Cantidad FROM V_TITULOHABILITANTE WHERE Departamento = 'LIMA' GROUP BY Situacion
"""
