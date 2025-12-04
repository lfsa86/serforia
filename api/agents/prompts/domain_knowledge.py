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
  IMPORTANTE: NO tiene Departamento/Provincia/Distrito - hacer JOIN con V_TITULOHABILITANTE.

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

V_INFRACTOR ↔ V_TITULOHABILITANTE:
  - JOIN por: TituloHabilitante, NumeroDocumento o Titular
  - Usar para: obtener ubicación geográfica del infractor
  - Ejemplo: SELECT i.*, th.Departamento FROM V_INFRACTOR i
             JOIN V_TITULOHABILITANTE th ON i.TituloHabilitante = th.TituloHabilitante

V_CAMBIO_USO → V_AUTORIZACION_DESBOSQUE:
  - El cambio de uso es PREVIO al desbosque para fines agrícolas

Todas las vistas → V_INFRACTOR:
  - Incumplir cualquier autorización puede generar infracción
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

SOBRE UBICACIÓN GEOGRÁFICA:
  - V_INFRACTOR NO tiene Departamento, Provincia, Distrito
  - Para ubicación de infractores: JOIN con V_TITULOHABILITANTE
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
