"""
Constantes del microservicio Althara News Service

Este archivo contiene las categorías de noticias definidas para el sistema.
"""

# Categorías de noticias inmobiliarias
class NewsCategory:
    """Categorías de noticias definidas para el sistema"""
    
    # Fondos e inversión
    FONDOS_INVERSION_INMOBILIARIA = "FONDOS_INVERSION_INMOBILIARIA"
    GRANDES_INVERSIONES_INMOBILIARIAS = "GRANDES_INVERSIONES_INMOBILIARIAS"
    MOVIMIENTOS_GRANDES_TENEDORES = "MOVIMIENTOS_GRANDES_TENEDORES"
    TOKENIZATION_ACTIVOS = "TOKENIZATION_ACTIVOS"
    
    # Noticias generales
    NOTICIAS_INMOBILIARIAS = "NOTICIAS_INMOBILIARIAS"
    NOTICIAS_HIPOTECAS = "NOTICIAS_HIPOTECAS"
    NOTICIAS_LEYES_OKUPAS = "NOTICIAS_LEYES_OKUPAS"
    NOTICIAS_BOE_SUBASTAS = "NOTICIAS_BOE_SUBASTAS"
    NOTICIAS_DESAHUCIOS = "NOTICIAS_DESAHUCIOS"
    NOTICIAS_CONSTRUCCION = "NOTICIAS_CONSTRUCCION"
    
    # Precios y mercado
    PRECIOS_VIVIENDA = "PRECIOS_VIVIENDA"
    PRECIOS_MATERIALES = "PRECIOS_MATERIALES"
    PRECIOS_SUELO = "PRECIOS_SUELO"
    
    # Análisis y tendencias
    FUTURO_SECTOR_INMOBILIARIO = "FUTURO_SECTOR_INMOBILIARIO"
    BURBUJA_INMOBILIARIA = "BURBUJA_INMOBILIARIA"
    
    # Alquiler y normativas
    ALQUILER_VACACIONAL = "ALQUILER_VACACIONAL"
    NORMATIVAS_VIVIENDAS = "NORMATIVAS_VIVIENDAS"
    FALTA_VIVIENDA = "FALTA_VIVIENDA"
    
    # Construcción y urbanización
    NOTICIAS_URBANIZACION = "NOTICIAS_URBANIZACION"
    NOVEDADES_CONSTRUCCION = "NOVEDADES_CONSTRUCCION"
    CONSTRUCCION_MODULAR = "CONSTRUCCION_MODULAR"


# Lista de todas las categorías válidas (útil para validación)
VALID_CATEGORIES = [
    NewsCategory.FONDOS_INVERSION_INMOBILIARIA,
    NewsCategory.GRANDES_INVERSIONES_INMOBILIARIAS,
    NewsCategory.MOVIMIENTOS_GRANDES_TENEDORES,
    NewsCategory.TOKENIZATION_ACTIVOS,
    NewsCategory.NOTICIAS_INMOBILIARIAS,
    NewsCategory.NOTICIAS_HIPOTECAS,
    NewsCategory.NOTICIAS_LEYES_OKUPAS,
    NewsCategory.NOTICIAS_BOE_SUBASTAS,
    NewsCategory.NOTICIAS_DESAHUCIOS,
    NewsCategory.NOTICIAS_CONSTRUCCION,
    NewsCategory.PRECIOS_VIVIENDA,
    NewsCategory.PRECIOS_MATERIALES,
    NewsCategory.PRECIOS_SUELO,
    NewsCategory.FUTURO_SECTOR_INMOBILIARIO,
    NewsCategory.BURBUJA_INMOBILIARIA,
    NewsCategory.ALQUILER_VACACIONAL,
    NewsCategory.NORMATIVAS_VIVIENDAS,
    NewsCategory.FALTA_VIVIENDA,
    NewsCategory.NOTICIAS_URBANIZACION,
    NewsCategory.NOVEDADES_CONSTRUCCION,
    NewsCategory.CONSTRUCCION_MODULAR,
]

# Mapeo legible para humanos (para documentación y UI)
CATEGORY_LABELS = {
    NewsCategory.FONDOS_INVERSION_INMOBILIARIA: "Fondos de inversión inmobiliaria",
    NewsCategory.GRANDES_INVERSIONES_INMOBILIARIAS: "Noticias grandes inversiones inmobiliarias",
    NewsCategory.MOVIMIENTOS_GRANDES_TENEDORES: "Movimientos de grandes tenedores",
    NewsCategory.TOKENIZATION_ACTIVOS: "Tokenization activos",
    NewsCategory.NOTICIAS_INMOBILIARIAS: "Noticias inmobiliarias",
    NewsCategory.NOTICIAS_HIPOTECAS: "Noticias hipotecas",
    NewsCategory.NOTICIAS_LEYES_OKUPAS: "Noticias leyes okupas",
    NewsCategory.NOTICIAS_BOE_SUBASTAS: "Noticias BOE subastas inmobiliarias",
    NewsCategory.NOTICIAS_DESAHUCIOS: "Noticias desahucios",
    NewsCategory.NOTICIAS_CONSTRUCCION: "Noticias sobre construcción",
    NewsCategory.PRECIOS_VIVIENDA: "Precios de vivienda",
    NewsCategory.PRECIOS_MATERIALES: "Precios materiales",
    NewsCategory.PRECIOS_SUELO: "Precios del suelo",
    NewsCategory.FUTURO_SECTOR_INMOBILIARIO: "Futuro sector inmobiliario",
    NewsCategory.BURBUJA_INMOBILIARIA: "Burbuja inmobiliaria",
    NewsCategory.ALQUILER_VACACIONAL: "Alquiler vacacional",
    NewsCategory.NORMATIVAS_VIVIENDAS: "Normativas de viviendas",
    NewsCategory.FALTA_VIVIENDA: "Falta de vivienda",
    NewsCategory.NOTICIAS_URBANIZACION: "Noticias sobre urbanización",
    NewsCategory.NOVEDADES_CONSTRUCCION: "Novedades de construcción",
    NewsCategory.CONSTRUCCION_MODULAR: "Construcción modular",
}

