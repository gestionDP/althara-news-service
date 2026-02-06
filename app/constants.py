"""
app/althara_constants_v2.py

Althara (Real Estate) — Pro taxonomy v2 + guardrails.

Goal:
- Categories are stable macro-topics (low ambiguity).
- Specific/niche topics become tags.
- Provide mapping from v1 categories to v2 to keep backwards compatibility.
- Provide allow/deny keyword guardrails to keep the feed strictly real-estate (no decor/lifestyle).
"""

from __future__ import annotations

from typing import Final


# ============================================================================
# V2 Categories (pro, low-noise)
# ============================================================================

class AltharaCategoryV2:
    """
    Pro categories for Althara (real estate / housing market).

    Keep this list relatively small and stable.
    """
    # Market
    MERCADO_COMPRAVENTA = "MERCADO_COMPRAVENTA"
    PRECIOS_VIVIENDA = "PRECIOS_VIVIENDA"
    ALQUILER_RESIDENCIAL = "ALQUILER_RESIDENCIAL"
    ALQUILER_VACACIONAL = "ALQUILER_VACACIONAL"
    OFERTA_Y_STOCK = "OFERTA_Y_STOCK"  # obra nueva, visados, stock, suelo disponible

    # Financing & Macro
    HIPOTECAS_Y_CREDITO = "HIPOTECAS_Y_CREDITO"
    TIPOS_Y_MACRO = "TIPOS_Y_MACRO"  # BCE, tipos, inflación (cuando aplica al housing)

    # Investment
    INVERSION_INSTITUCIONAL = "INVERSION_INSTITUCIONAL"  # fondos, SOCIMIs, capital
    OPERACIONES_CORPORATIVAS = "OPERACIONES_CORPORATIVAS"  # M&A, carteras, JV
    GRANDES_TENEDORES = "GRANDES_TENEDORES"

    # Regulation
    REGULACION_VIVIENDA = "REGULACION_VIVIENDA"  # ley vivienda, topes, fiscalidad, etc.
    URBANISMO_Y_PLANEAMIENTO = "URBANISMO_Y_PLANEAMIENTO"  # licencias, planeamiento, suelo
    BOE_SUBASTAS = "BOE_SUBASTAS"

    # Construction
    CONSTRUCCION_Y_COSTES = "CONSTRUCCION_Y_COSTES"  # materiales, mano de obra, plazos
    INDUSTRIALIZACION_MODULAR = "INDUSTRIALIZACION_MODULAR"

    # Social / Risk
    DESAHUCIOS_Y_VULNERABILIDAD = "DESAHUCIOS_Y_VULNERABILIDAD"
    OKUPACION_Y_SEGURIDAD_JURIDICA = "OKUPACION_Y_SEGURIDAD_JURIDICA"

    # Catch-all (last resort)
    SECTOR_INMOBILIARIO = "SECTOR_INMOBILIARIO"


VALID_CATEGORIES_V2: Final[list[str]] = [
    # Market
    AltharaCategoryV2.MERCADO_COMPRAVENTA,
    AltharaCategoryV2.PRECIOS_VIVIENDA,
    AltharaCategoryV2.ALQUILER_RESIDENCIAL,
    AltharaCategoryV2.ALQUILER_VACACIONAL,
    AltharaCategoryV2.OFERTA_Y_STOCK,
    # Financing & Macro
    AltharaCategoryV2.HIPOTECAS_Y_CREDITO,
    AltharaCategoryV2.TIPOS_Y_MACRO,
    # Investment
    AltharaCategoryV2.INVERSION_INSTITUCIONAL,
    AltharaCategoryV2.OPERACIONES_CORPORATIVAS,
    AltharaCategoryV2.GRANDES_TENEDORES,
    # Regulation
    AltharaCategoryV2.REGULACION_VIVIENDA,
    AltharaCategoryV2.URBANISMO_Y_PLANEAMIENTO,
    AltharaCategoryV2.BOE_SUBASTAS,
    # Construction
    AltharaCategoryV2.CONSTRUCCION_Y_COSTES,
    AltharaCategoryV2.INDUSTRIALIZACION_MODULAR,
    # Social / Risk
    AltharaCategoryV2.DESAHUCIOS_Y_VULNERABILIDAD,
    AltharaCategoryV2.OKUPACION_Y_SEGURIDAD_JURIDICA,
    # Catch-all
    AltharaCategoryV2.SECTOR_INMOBILIARIO,
]


CATEGORY_LABELS_V2: Final[dict[str, str]] = {
    # Market
    AltharaCategoryV2.MERCADO_COMPRAVENTA: "Mercado: compraventa y actividad",
    AltharaCategoryV2.PRECIOS_VIVIENDA: "Mercado: precios de vivienda",
    AltharaCategoryV2.ALQUILER_RESIDENCIAL: "Mercado: alquiler residencial",
    AltharaCategoryV2.ALQUILER_VACACIONAL: "Mercado: alquiler vacacional",
    AltharaCategoryV2.OFERTA_Y_STOCK: "Oferta: stock, obra nueva y suelo",
    # Financing & Macro
    AltharaCategoryV2.HIPOTECAS_Y_CREDITO: "Financiación: hipotecas y crédito",
    AltharaCategoryV2.TIPOS_Y_MACRO: "Macro: tipos y condiciones financieras",
    # Investment
    AltharaCategoryV2.INVERSION_INSTITUCIONAL: "Inversión: institucional y capital",
    AltharaCategoryV2.OPERACIONES_CORPORATIVAS: "Inversión: operaciones y carteras",
    AltharaCategoryV2.GRANDES_TENEDORES: "Mercado: grandes tenedores",
    # Regulation
    AltharaCategoryV2.REGULACION_VIVIENDA: "Regulación: vivienda y fiscalidad",
    AltharaCategoryV2.URBANISMO_Y_PLANEAMIENTO: "Regulación: urbanismo y planeamiento",
    AltharaCategoryV2.BOE_SUBASTAS: "BOE: subastas",
    # Construction
    AltharaCategoryV2.CONSTRUCCION_Y_COSTES: "Construcción: costes y ejecución",
    AltharaCategoryV2.INDUSTRIALIZACION_MODULAR: "Construcción: industrialización/modular",
    # Social / Risk
    AltharaCategoryV2.DESAHUCIOS_Y_VULNERABILIDAD: "Riesgo social: desahucios y vulnerabilidad",
    AltharaCategoryV2.OKUPACION_Y_SEGURIDAD_JURIDICA: "Riesgo jurídico: okupación y seguridad",
    # Catch-all
    AltharaCategoryV2.SECTOR_INMOBILIARIO: "Sector inmobiliario (general)",
}


# ============================================================================
# Category priority (used for relevance scoring / UI ordering)
# Higher = more editorially important
# ============================================================================

CATEGORY_PRIORITY_V2: Final[dict[str, int]] = {
    # Very high signal
    AltharaCategoryV2.PRECIOS_VIVIENDA: 90,
    AltharaCategoryV2.HIPOTECAS_Y_CREDITO: 88,
    AltharaCategoryV2.MERCADO_COMPRAVENTA: 85,
    AltharaCategoryV2.INVERSION_INSTITUCIONAL: 82,
    AltharaCategoryV2.OPERACIONES_CORPORATIVAS: 80,
    AltharaCategoryV2.REGULACION_VIVIENDA: 78,
    # High
    AltharaCategoryV2.OFERTA_Y_STOCK: 75,
    AltharaCategoryV2.CONSTRUCCION_Y_COSTES: 72,
    AltharaCategoryV2.URBANISMO_Y_PLANEAMIENTO: 70,
    # Medium
    AltharaCategoryV2.ALQUILER_RESIDENCIAL: 68,
    AltharaCategoryV2.ALQUILER_VACACIONAL: 62,
    AltharaCategoryV2.GRANDES_TENEDORES: 60,
    # Lower / specialised
    AltharaCategoryV2.BOE_SUBASTAS: 55,
    AltharaCategoryV2.INDUSTRIALIZACION_MODULAR: 52,
    AltharaCategoryV2.DESAHUCIOS_Y_VULNERABILIDAD: 50,
    AltharaCategoryV2.OKUPACION_Y_SEGURIDAD_JURIDICA: 50,
    # Catch-all
    AltharaCategoryV2.SECTOR_INMOBILIARIO: 30,
}


# ============================================================================
# V1 -> V2 mapping (backwards compatibility)
# Adjust keys to match your existing app/constants.py v1 names.
# ============================================================================
# NOTE: Importing NewsCategory directly would create coupling; keep it string-based.
# If you prefer, replace keys with NewsCategory.* references inside your codebase.

V1_TO_V2_MAP: Final[dict[str, str]] = {
    # Investment
    "FONDOS_INVERSION_INMOBILIARIA": AltharaCategoryV2.INVERSION_INSTITUCIONAL,
    "GRANDES_INVERSIONES_INMOBILIARIAS": AltharaCategoryV2.OPERACIONES_CORPORATIVAS,
    "MOVIMIENTOS_GRANDES_TENEDORES": AltharaCategoryV2.GRANDES_TENEDORES,
    "TOKENIZATION_ACTIVOS": AltharaCategoryV2.INVERSION_INSTITUCIONAL,  # better as a tag "tokenizacion"

    # General / Market
    "NOTICIAS_INMOBILIARIAS": AltharaCategoryV2.SECTOR_INMOBILIARIO,
    "PRECIOS_VIVIENDA": AltharaCategoryV2.PRECIOS_VIVIENDA,
    "FUTURO_SECTOR_INMOBILIARIO": AltharaCategoryV2.SECTOR_INMOBILIARIO,  # better as tag "perspectiva"
    "BURBUJA_INMOBILIARIA": AltharaCategoryV2.PRECIOS_VIVIENDA,  # better as tag "burbuja"/"riesgo"

    # Financing
    "NOTICIAS_HIPOTECAS": AltharaCategoryV2.HIPOTECAS_Y_CREDITO,

    # Regulation / Urbanism
    "NORMATIVAS_VIVIENDAS": AltharaCategoryV2.REGULACION_VIVIENDA,
    "NOTICIAS_URBANIZACION": AltharaCategoryV2.URBANISMO_Y_PLANEAMIENTO,
    "NOTICIAS_BOE_SUBASTAS": AltharaCategoryV2.BOE_SUBASTAS,

    # Social / Risk
    "NOTICIAS_DESAHUCIOS": AltharaCategoryV2.DESAHUCIOS_Y_VULNERABILIDAD,
    "NOTICIAS_LEYES_OKUPAS": AltharaCategoryV2.OKUPACION_Y_SEGURIDAD_JURIDICA,
    "FALTA_VIVIENDA": AltharaCategoryV2.OFERTA_Y_STOCK,

    # Construction
    "NOTICIAS_CONSTRUCCION": AltharaCategoryV2.CONSTRUCCION_Y_COSTES,
    "NOVEDADES_CONSTRUCCION": AltharaCategoryV2.CONSTRUCCION_Y_COSTES,
    "CONSTRUCCION_MODULAR": AltharaCategoryV2.INDUSTRIALIZACION_MODULAR,

    # Costs / land
    "PRECIOS_MATERIALES": AltharaCategoryV2.CONSTRUCCION_Y_COSTES,
    "PRECIOS_SUELO": AltharaCategoryV2.URBANISMO_Y_PLANEAMIENTO,
    "ALQUILER_VACACIONAL": AltharaCategoryV2.ALQUILER_VACACIONAL,
}


def map_category_v1_to_v2(category_v1: str | None) -> str:
    """
    Map a v1 category string to the new v2 taxonomy.
    Falls back to SECTOR_INMOBILIARIO if unknown.
    """
    if not category_v1:
        return AltharaCategoryV2.SECTOR_INMOBILIARIO
    return V1_TO_V2_MAP.get(category_v1, AltharaCategoryV2.SECTOR_INMOBILIARIO)


# ============================================================================
# Editorial guardrails (relevance filters)
# ============================================================================
# Purpose: keep Althara feed strictly "real estate market/investment/regulation"
# and reject decor/lifestyle/clickbait.

# If STRICT_REQUIRE_ALLOW=True: content must match at least one allow keyword
# (unless source is whitelisted in your ingestion layer).
STRICT_REQUIRE_ALLOW: Final[bool] = True

# For safety, use lowercase matching on title + summary + url.
DENY_KEYWORDS: Final[list[str]] = [
    # Decor / lifestyle
    "decoración", "decoracion", "interiorismo", "muebles", "ikea", "salón", "salon",
    "cocina", "baño", "bano", "jardín", "jardin", "bricolaje", "diy", "manualidades",
    "ideas para", "antes y después", "antes y despues",
    # Celebrity / soft content
    "casa de", "mansión", "mansion", "famoso", "influencer",
    # Promotions / commerce
    "rebaja", "descuento", "chollo", "black friday", "prime day",
    # Off-topic: transport, crime, sport, etc.
    "bici", "bicicleta", "bicipalma", "rebalanceo", "flota entre estaciones",
    "coche", "coches", "robo", "robos", "detenidos", "detenido", "policía", "policia",
    "fútbol", "futbol", "deporte", "deportes", "partido", "gol", "liga",
    "sanidad", "hospital", "covid", "vacuna", "elecciones", "político", "politico",
]

ALLOW_KEYWORDS: Final[list[str]] = [
    # Market & prices
    "vivienda", "inmueble", "inmobiliario", "compraventa", "tasación", "tasacion",
    "precio", "precios", "obra nueva", "visados", "promotor", "promotora",
    # Rent
    "alquiler", "renta", "arrendamiento",
    # Financing
    "hipoteca", "hipotecas", "euríbor", "euribor", "crédito", "credito", "morosidad",
    # Regulation / planning
    "ley de vivienda", "regulación", "regulacion", "topes", "licencia", "licencias",
    "planeamiento", "urbanismo", "suelo", "fiscalidad", "impuestos", "boe", "subasta", "subastas",
    # Construction
    "construcción", "construccion", "arquitect", "cscae", "observatorio 2030",
    # Investment
    "fondo", "fondos", "socimi", "cartera", "yield", "cap rate", "rentabilidad",
    "inversión", "inversion", "inversiones inmobiliarias",
]

# Optional: category hints to strengthen classification (use in classifier).
CATEGORY_HINTS: Final[dict[str, list[str]]] = {
    AltharaCategoryV2.PRECIOS_VIVIENDA: ["precio", "precios", "tasación", "tasacion", "índice", "indice"],
    AltharaCategoryV2.MERCADO_COMPRAVENTA: ["compraventa", "ventas", "operaciones", "transacciones"],
    AltharaCategoryV2.ALQUILER_RESIDENCIAL: ["alquiler", "renta", "arrendamiento"],
    AltharaCategoryV2.HIPOTECAS_Y_CREDITO: ["hipoteca", "euríbor", "euribor", "crédito", "credito", "tipo de interés"],
    AltharaCategoryV2.REGULACION_VIVIENDA: ["ley", "regulación", "regulacion", "topes", "fiscalidad", "impuestos"],
    AltharaCategoryV2.URBANISMO_Y_PLANEAMIENTO: ["urbanismo", "planeamiento", "licencia", "licencias", "suelo"],
    AltharaCategoryV2.BOE_SUBASTAS: ["boe", "subasta", "subastas"],
    AltharaCategoryV2.CONSTRUCCION_Y_COSTES: ["construcción", "construccion", "materiales", "costes", "obra nueva", "plazos"],
    AltharaCategoryV2.INDUSTRIALIZACION_MODULAR: ["modular", "industrialización", "industrializacion", "offsite"],
    AltharaCategoryV2.INVERSION_INSTITUCIONAL: ["fondo", "fondos", "socimi", "yield", "cap rate", "rentabilidad"],
    AltharaCategoryV2.OPERACIONES_CORPORATIVAS: ["cartera", "carteras", "adquiere", "compra", "venta", "joint venture", "m&a"],
    AltharaCategoryV2.GRANDES_TENEDORES: ["gran tenedor", "grandes tenedores"],
    AltharaCategoryV2.DESAHUCIOS_Y_VULNERABILIDAD: ["desahucio", "desahucios", "vulnerabilidad"],
    AltharaCategoryV2.OKUPACION_Y_SEGURIDAD_JURIDICA: ["okupa", "okupas", "okupación", "okupacion"],
}


# ============================================================================
# Tags (pro) — use these as consistent labels (do NOT overfit categories)
# ============================================================================
# These are suggestions; your classifier can emit these as tags when matched.

SUGGESTED_TAGS: Final[dict[str, list[str]]] = {
    # Market structure
    "demanda": ["demanda"],
    "oferta": ["oferta", "stock"],
    "obra_nueva": ["obra nueva", "visados"],
    "suelo": ["suelo"],
    # Prices
    "tasacion": ["tasación", "tasacion"],
    "descuento": ["descuento"],
    "tension_precios": ["tensión", "tension", "presión", "presion"],
    # Financing
    "euribor": ["euríbor", "euribor"],
    "tipo_fijo": ["tipo fijo"],
    "tipo_variable": ["tipo variable"],
    "credito": ["crédito", "credito"],
    # Investment
    "socimi": ["socimi"],
    "cap_rate": ["cap rate"],
    "yield": ["yield", "rentabilidad"],
    "carteras": ["cartera", "carteras"],
    # Regulation
    "topes_alquiler": ["tope", "topes"],
    "licencias": ["licencia", "licencias"],
    "fiscalidad": ["fiscalidad", "impuestos"],
    # Social / risk
    "desahucios": ["desahucio", "desahucios"],
    "okupacion": ["okupa", "okupas", "okupación", "okupacion"],
    # Niche (tags, not categories)
    "tokenizacion": ["tokenización", "tokenizacion"],
    "burbuja": ["burbuja"],
    "riesgo": ["riesgo"],
}


# ============================================================================
# Backwards compatibility (consumers: rss_ingestor, idealista_client, ui)
# ============================================================================

VALID_CATEGORIES: Final[list[str]] = VALID_CATEGORIES_V2
CATEGORY_LABELS: Final[dict[str, str]] = CATEGORY_LABELS_V2


class NewsCategory:
    """V1 aliases -> V2 category values for backwards compatibility."""
    FONDOS_INVERSION_INMOBILIARIA = AltharaCategoryV2.INVERSION_INSTITUCIONAL
    GRANDES_INVERSIONES_INMOBILIARIAS = AltharaCategoryV2.OPERACIONES_CORPORATIVAS
    MOVIMIENTOS_GRANDES_TENEDORES = AltharaCategoryV2.GRANDES_TENEDORES
    TOKENIZATION_ACTIVOS = AltharaCategoryV2.INVERSION_INSTITUCIONAL
    NOTICIAS_INMOBILIARIAS = AltharaCategoryV2.SECTOR_INMOBILIARIO
    PRECIOS_VIVIENDA = AltharaCategoryV2.PRECIOS_VIVIENDA
    FUTURO_SECTOR_INMOBILIARIO = AltharaCategoryV2.SECTOR_INMOBILIARIO
    BURBUJA_INMOBILIARIA = AltharaCategoryV2.PRECIOS_VIVIENDA
    NOTICIAS_HIPOTECAS = AltharaCategoryV2.HIPOTECAS_Y_CREDITO
    NORMATIVAS_VIVIENDAS = AltharaCategoryV2.REGULACION_VIVIENDA
    NOTICIAS_URBANIZACION = AltharaCategoryV2.URBANISMO_Y_PLANEAMIENTO
    NOTICIAS_BOE_SUBASTAS = AltharaCategoryV2.BOE_SUBASTAS
    NOTICIAS_DESAHUCIOS = AltharaCategoryV2.DESAHUCIOS_Y_VULNERABILIDAD
    NOTICIAS_LEYES_OKUPAS = AltharaCategoryV2.OKUPACION_Y_SEGURIDAD_JURIDICA
    FALTA_VIVIENDA = AltharaCategoryV2.OFERTA_Y_STOCK
    PRECIOS_MATERIALES = AltharaCategoryV2.CONSTRUCCION_Y_COSTES
    PRECIOS_SUELO = AltharaCategoryV2.URBANISMO_Y_PLANEAMIENTO
    NOTICIAS_CONSTRUCCION = AltharaCategoryV2.CONSTRUCCION_Y_COSTES
    NOVEDADES_CONSTRUCCION = AltharaCategoryV2.CONSTRUCCION_Y_COSTES
    CONSTRUCCION_MODULAR = AltharaCategoryV2.INDUSTRIALIZACION_MODULAR
    ALQUILER_VACACIONAL = AltharaCategoryV2.ALQUILER_VACACIONAL
