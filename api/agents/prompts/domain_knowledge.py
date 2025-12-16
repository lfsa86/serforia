"""
Conocimiento de dominio de SERFOR - Textos para usar en prompts
"""

# =============================================================================
# SINÓNIMOS - Cómo la gente pide cada entidad
# =============================================================================

ENTITY_SYNONYMS = """
CÓMO IDENTIFICAR QUÉ BUSCA EL USUARIO:

V_AUTORIZACION_DESBOSQUE:
  Cuando pregunten por REMOVER o QUITAR cobertura forestal para otro uso (infraestructura, minería, hidrocarburos)
  Términos: desbosque, desmontar, tumbar monte, limpiar terreno, quitar el bosque, retiro de cobertura

V_CAMBIO_USO:
  Cuando pregunten por CONVERTIR tierra de uso forestal/protección a uso agropecuario
  Términos: cambio de uso, CUS, legalizar terreno para agricultura, sembrar en zona de bosque

V_AUTORIZACION_DEPOSITO:
  Cuando pregunten por LUGARES de acopio, depósitos o comercialización de productos forestales Y de fauna silvestre
  Términos: depósitos, lugares de venta, acopio, comercialización, tiendas de madera, venta de fauna

V_AUTORIZACION_CTP:
  Cuando pregunten por CENTROS que TRANSFORMAN productos forestales Y de fauna silvestre (aserraderos, laminadoras, etc.)
  Términos: CTP, centro de transformación primaria, aserradero, planta de procesamiento

V_LICENCIA_CAZA:
  Cuando pregunten por CAZA deportiva (sin fines de lucro)
  Términos: licencias de caza, caza deportiva, permiso para cazar

V_PLANTACION:
  Cuando pregunten por PLANTACIONES forestales registradas (producción, protección, restauración)
  Términos: plantaciones, RNPF, registro de plantaciones, reforestación

V_INFRACTOR:
  Cuando pregunten por SANCIONES, MULTAS o personas/empresas SANCIONADAS
  Términos: infractores, sanciones, multas, RNI, sancionados, infracciones

V_TITULOHABILITANTE:
  Esta vista contiene VARIOS tipos de títulos habilitantes. Identificar cuál buscan:

  → PERMISOS (TipoTh='PERMISOS'): Aprovechamiento en predios privados o comunidades
    Forestales: madera, castaña en predios privados
    Fauna: aprovechamiento de animales silvestres

  → CONCESIONES (TipoTh='CONCESIONES'): Derechos en tierras del Estado (40 años renovables)
    Maderables, conservación, ecoturismo, castaña, fauna silvestre

  → AUTORIZACIONES FORESTALES (TipoTh='AUTORIZACIONES'): Extracción de productos DIFERENTES a la madera
    Plantas medicinales, uña de gato, totora, sangre de grado
    Especies arbustivas, herbáceas, vegetación acuática
    Términos: PFDM, PFNM, productos no maderables, extracción de plantas

  → CESIONES EN USO (TipoTh='CESIÓN EN USO'): Contratos para sistemas agroforestales en tierras públicas
    Términos: agroforestal, SAF, sembrar en terreno del Estado

  → BOSQUE LOCAL (TipoTh='BOSQUE LOCAL'): Bosques administrados por municipalidades
    Términos: bosques municipales, gestión municipal de bosques
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
# DATOS NO DISPONIBLES
# =============================================================================

DATOS_NO_DISPONIBLES = """
DATOS QUE NO EXISTEN EN LA BASE DE DATOS:

ESPECIES (no hay columna de especie en ninguna vista):
  - Árboles: pino, eucalipto, cedro, caoba, tornillo, shihuahuaco, mohena, etc.
  - Productos no maderables: uña de gato, sangre de grado, totora, palo santo, tara, aguaje, etc.
  - Fauna: venado, sajino, taricaya, lagarto, loro, guacamayo, etc.

VOLÚMENES (no hay columnas de volumen en ninguna vista):
  - Metros cúbicos de madera
  - Toneladas de producto
  - Cantidad de especímenes de fauna

  Solo existe Superficie (hectáreas)

EDAD DE PLANTACIONES (V_PLANTACION no tiene edad ni año de siembra):
  AnioRegistro es el año en que se registró en SERFOR, NO cuando se plantó

PRECIOS Y VALORES ECONÓMICOS (no hay columnas de precio):
  - Precio de productos
  - Valor de concesiones
  - Montos de contratos

  El único dato monetario es Multa en V_INFRACTOR (en UIT)

UBICACIÓN GEOGRÁFICA (limitaciones por vista):
  - V_INFRACTOR: no tiene Departamento, Provincia, Distrito
  - V_LICENCIA_CAZA: no tiene Departamento, Provincia, Distrito

COORDENADAS GPS:
  - Solo V_AUTORIZACION_CTP y V_AUTORIZACION_DEPOSITO tienen CoordenadaX, CoordenadaY
  - Las demás vistas no tienen coordenadas

FISCALIZACIÓN:
  - No hay información de inspecciones, auditorías ni planes de manejo
  - Solo existen sanciones impuestas (V_INFRACTOR)
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
CONCEPTO CLAVE - DESAGREGACIÓN PARA USUARIOS EJECUTIVOS:

Este sistema provee información a usuarios del área ejecutiva que NO conocen la estructura
de la base de datos. Sus preguntas suelen ser generales porque no saben cómo están organizados
los datos.

Por eso, las consultas SQL deben SIEMPRE desagregar por columnas clave para entregar un
"pantallazo ordenado" que permita al usuario entender los datos y hacer preguntas más específicas.

Esto NO es filtrar (WHERE), es MOSTRAR la información organizada (SELECT + GROUP BY).

COLUMNAS DE DESAGREGACIÓN OBLIGATORIAS:

  V_TITULOHABILITANTE:
    - Situacion (VIGENTE, NO VIGENTE, EXTINGUIDO)
    - OtorgaPermiso (tipo de tenencia)

  V_PLANTACION:
    - FinalidadPlantacion (PRODUCCION, PROTECCION, RESTAURACION)

  Tablas con columna de estado (V_CAMBIO_USO, V_AUTORIZACION_DESBOSQUE, etc.):
    - Su respectiva columna de estado/situación

CÓMO APLICAR:
  - Incluir las columnas de desagregación en SELECT
  - Si hay agregación (COUNT, SUM, etc.), incluirlas también en GROUP BY

EXCEPCIÓN: Si el usuario YA especificó un valor de alguna columna de desagregación en su pregunta,
filtrar por ese valor y no desagregar por esa columna (pero sí por las demás si aplica).

Ejemplo - V_TITULOHABILITANTE, pregunta general: "¿Cuántos títulos hay en Loreto?"
  SELECT Situacion, OtorgaPermiso, COUNT(*) as Cantidad
  FROM V_TITULOHABILITANTE
  WHERE Departamento = 'LORETO'
  GROUP BY Situacion, OtorgaPermiso

Ejemplo - V_TITULOHABILITANTE, con estado específico: "¿Cuántos títulos vigentes hay en Loreto?"
  SELECT OtorgaPermiso, COUNT(*) as Cantidad
  FROM V_TITULOHABILITANTE
  WHERE Departamento = 'LORETO' AND Situacion = 'VIGENTE'
  GROUP BY OtorgaPermiso

Ejemplo - V_PLANTACION, pregunta general: "¿Cuántas plantaciones hay en Cusco?"
  SELECT FinalidadPlantacion, COUNT(*) as Cantidad
  FROM V_PLANTACION
  WHERE Departamento = 'CUSCO'
  GROUP BY FinalidadPlantacion

Ejemplo - Listado: "Listado de concesiones en Madre de Dios"
  SELECT TituloHabilitante, Titular, TipoConcesion, Situacion, OtorgaPermiso, FechaDocumento
  FROM V_TITULOHABILITANTE
  WHERE Departamento = 'MADRE DE DIOS' AND TipoTh = 'CONCESIONES'


REGLA - TipoTh vs TipoConcesion/CategoriaPermiso EN V_TITULOHABILITANTE:

La columna TipoTh indica el tipo de título habilitante, pero su implementación
es INCONSISTENTE para CONCESIONES y PERMISOS. Usar las columnas específicas:

  TipoTh = 'CONCESIONES' → Usar TipoConcesion para el tipo específico:
    - CONSERVACIÓN
    - ECOTURISMO
    - FAUNA SILVESTRE
    - FINES MADERABLES
    - FORESTACIÓN Y/O REFORESTACIÓN
    - PLANTACIONES FORESTALES
    - PRODUCTOS FORESTALES DIFERENTES A LA MADERA

  TipoTh = 'PERMISOS' → Usar CategoriaPermiso para el tipo específico:
    - MADERABLE
    - NO MADERABLE
    - BOSQUE SECO
    - FAUNA SILVESTRE

  Para los demás valores, usar TipoTh directamente (funciona bien):
    - AUTORIZACIONES
    - BOSQUE LOCAL
    - CAMBIO DE USO
    - CESIÓN EN USO
    - DESBOSQUE

Ejemplos:
  "Concesiones de ecoturismo"     → WHERE TipoConcesion = 'ECOTURISMO'
  "Concesiones maderables"        → WHERE TipoConcesion = 'FINES MADERABLES'
  "Permisos maderables"           → WHERE CategoriaPermiso = 'MADERABLE'
  "Permisos forestales"           → WHERE CategoriaPermiso IN ('MADERABLE', 'NO MADERABLE', 'BOSQUE SECO')
  "Cesiones en uso"               → WHERE TipoTh = 'CESIÓN EN USO'
  "Bosques locales"               → WHERE TipoTh = 'BOSQUE LOCAL'


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


REGLA GENERAL - NO ASUMIR FILTROS:

El sistema PROVEE información, NO interpreta intenciones.

PRINCIPIO:
  - Aplicar ÚNICAMENTE los filtros (WHERE) que el usuario pidió explícitamente
  - Consulta general → sin filtros adicionales
  - Consulta específica → con filtros explícitos
  - La desagregación (SELECT + GROUP BY) NO es un filtro, siempre aplica

Ejemplo:
  ❌ Usuario: "¿Concesiones en Loreto?"
     Query: WHERE Situacion = 'VIGENTE' AND Departamento = 'LORETO'
     Error: Asumió que querían solo vigentes

  ✅ Usuario: "¿Concesiones en Loreto?"
     Query: WHERE Departamento = 'LORETO' (desagregando por Situacion, OtorgaPermiso)
     Correcto: Solo filtró lo pedido explícitamente

  ✅ Usuario: "¿Concesiones vigentes en Loreto?"
     Query: WHERE Situacion = 'VIGENTE' AND Departamento = 'LORETO'
     Correcto: El usuario SÍ pidió "vigentes"


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


REGLA - BÚSQUEDA DE TIPOS DE EMPRESA:

No existe campo "tipo de empresa" en la base de datos.
Para buscar por tipo de empresa, usar LIKE en el nombre del titular/infractor:

Ejemplo: "¿Empresas de transporte con infracciones?"
  SELECT COUNT(DISTINCT NumeroDocumento) as Cantidad
  FROM V_INFRACTOR
  WHERE TipoDocumento = 'RUC'
    AND Infractor LIKE '%TRANSPORTE%'

Ejemplo: "¿Empresas madereras sancionadas?"
  SELECT Infractor, Multa
  FROM V_INFRACTOR
  WHERE TipoDocumento = 'RUC'
    AND Infractor LIKE '%MADERER%'


REGLA - VALORES COMPUESTOS EN COLUMNAS CATEGÓRICAS:

Algunas columnas pueden tener valores compuestos (múltiples valores separados por coma).
Cuando el usuario busque por un valor específico, considerar también los valores compuestos que lo contengan.

V_AUTORIZACION_DEPOSITO.TipoDeposito tiene estos valores:
  - 'DEPOSITO'
  - 'ESTABLECIMIENTO COMERCIAL'
  - 'LUGAR DE ACOPIO'
  - 'LUGAR DE ACOPIO, DEPOSITO, ESTABLECIMIENTO COMERCIAL' (valor compuesto)

Para buscar "lugares de acopio":
  WHERE TipoDeposito IN ('LUGAR DE ACOPIO', 'LUGAR DE ACOPIO, DEPOSITO, ESTABLECIMIENTO COMERCIAL')
  -- O usar LIKE: WHERE TipoDeposito LIKE '%LUGAR DE ACOPIO%'

Para buscar "depósitos":
  WHERE TipoDeposito IN ('DEPOSITO', 'LUGAR DE ACOPIO, DEPOSITO, ESTABLECIMIENTO COMERCIAL')
  -- O usar LIKE: WHERE TipoDeposito LIKE '%DEPOSITO%'


REGLA - COLUMNAS CATEGÓRICAS (ENUMERACIONES CON VALORES FIJOS):

Las siguientes columnas son ENUMERACIONES con un conjunto CERRADO de valores.
NO existen otros valores. NO usar LIKE para buscar valores que no estén en esta lista.

V_TITULOHABILITANTE:
  - TipoTh: AUTORIZACIONES, BOSQUE LOCAL, CAMBIO DE USO, CESIÓN EN USO, CONCESIONES, DESBOSQUE, PERMISOS
  - TipoConcesion: CONSERVACIÓN, ECOTURISMO, FAUNA SILVESTRE, FINES MADERABLES, FORESTACIÓN Y/O REFORESTACIÓN, NO APLICA, PLANTACIONES FORESTALES, PRODUCTOS FORESTALES DIFERENTES A LA MADERA
  - Categoriapermiso: BOSQUE SECO, FAUNA SILVESTRE, MADERABLE, NO APLICA, NO MADERABLE
  - OtorgaPermiso: COMUNIDAD CAMPESINA, COMUNIDAD NATIVA, NO APLICA, PREDIO PRIVADO, TIERRAS DE DOMINIO PÚBLICO
  - Situacion: VIGENTE, NO VIGENTE, EXTINGUIDO

V_PLANTACION:
  - FinalidadPlantacion: PRODUCCION, PROTECCION, RESTAURACION
    (NO contiene especies, nombres de árboles, ni tipos de plantas)
  - Region: COSTA, SELVA, SIERRA
  - TipoPersona: PERSONA JURIDICA, PERSONA NATURAL
  - RegimenTenencia: COMUNIDAD CAMPESINA, COMUNIDAD NATIVA, NO APLICA, PREDIO PRIVADO, TIERRAS DE DOMINIO PÚBLICO
  - TipoComunidad: CAMPESINA, NATIVA

V_AUTORIZACION_DEPOSITO:
  - TipoDeposito: ver regla de VALORES COMPUESTOS arriba
  - TipoRecurso: FAUNA SILVESTRE, FORESTAL
    (NO contiene especies específicas como "palo santo", "tara", etc.)

V_AUTORIZACION_CTP:
  - TipoRecurso: FAUNA SILVESTRE, FORESTAL
  - LineaProduccionGiro: ASERRADERO, LAMINADORA, PRODUCCION DE CARBON VEGETAL, TRIPLAYERA, otros

IMPORTANTE:
  - Usar ÚNICAMENTE estos valores exactos (respetando mayúsculas)
  - Si el usuario pide algo que no está en esta lista, NO existe en la base de datos
  - NO usar WHERE columna LIKE '%valor_inexistente%' en columnas categóricas
"""

BUSINESS_RULES_ESTADOS = """
REFERENCIA - COLUMNAS DE ESTADO POR TABLA:

Los términos "Estado" y "Situación" son sinónimos en el contexto de SERFOR.

Columnas de estado:
  - V_TITULOHABILITANTE.Situacion: VIGENTE, NO VIGENTE, EXTINGUIDO
  - V_CAMBIO_USO.Situacion: VIGENTE, NO VIGENTE, EXTINGUIDO
  - V_AUTORIZACION_DESBOSQUE.Situacion: VIGENTE, NO VIGENTE
  - V_AUTORIZACION_CTP.Estado: VIGENTE
  - V_AUTORIZACION_DEPOSITO.Estado: VIGENTE
  - V_LICENCIA_CAZA.EstadoLicencia: APROBADA
    NOTA: Para licencias extintas, verificar CausalExtincion (si no es NULL, está extinta)

Tablas SIN columna de estado:
  - V_PLANTACION
  - V_INFRACTOR
"""
