"""
Adapter para transformar noticias al tono Althara.

Convierte noticias crudas (raw_summary) en contenido adaptado al estilo
analítico y profesional de Althara para uso en redes sociales.
"""
from __future__ import annotations

from datetime import datetime
from textwrap import shorten
from typing import Optional

# Frases de cierre "genéricas" de Althara
ALTHARA_CLOSERS = [
    "Lo relevante no es el titular, sino quién ajusta posición antes de que el consenso llegue.",
    "La oportunidad aparece en el desfase entre el dato y la reacción del mercado visible.",
    "Donde el mercado ve ruido, Althara sólo registra el punto exacto del desplazamiento.",
    "Aquí importa menos el precio comunicado y más quién tiene acceso al siguiente movimiento.",
]


def _build_fact_line(title: str, raw_summary: Optional[str]) -> str:
    """
    Construye la primera línea: descripción fría del hecho.
    """
    base = title.strip()
    
    if raw_summary:
        combined = f"{title.strip()}. {raw_summary.strip()}"
        # recortamos para no generar un bloque eterno
        fact = shorten(combined, width=220, placeholder="…")
    else:
        fact = base
    
    # Algunos prefijos neutros que suavizan titulares muy periodísticos
    lower = fact.lower()
    
    if lower.startswith("el ") or lower.startswith("la ") or lower.startswith("los ") or lower.startswith("las "):
        return fact
    if lower.startswith("en "):
        return fact
    
    # Si no empieza con algo neutro, añadimos un marco
    return f"Los últimos datos apuntan a lo siguiente: {fact}"


def _build_strategic_line(category: Optional[str]) -> str:
    """
    Segunda línea: lectura estratégica en función de la categoría.
    """
    if category is None:
        category = ""
    
    cat = category.upper()
    
    if cat in {"PRECIOS_VIVIENDA"}:
        return (
            "Detrás de la cifra, el patrón es un ajuste entre oferta limitada y demanda que aún no ha reprecificado del todo el riesgo del ciclo."
        )
    
    if cat in {"FONDOS_INVERSION_INMOBILIARIA", "MOVIMIENTOS_GRANDES_TENEDORES", "GRANDES_INVERSIONES_INMOBILIARIAS"}:
        return (
            "El movimiento no es aislado: refleja una rotación silenciosa de capital hacia activos donde la asimetría de información sigue siendo aprovechable."
        )
    
    if cat in {"NOTICIAS_HIPOTECAS"}:
        return (
            "El repliegue y la reconfiguración del crédito redefinen quién puede seguir operando con ventaja en el próximo tramo del ciclo."
        )
    
    if cat in {"NOTICIAS_BOE_SUBASTAS", "NOTICIAS_DESAHUCIOS"}:
        return (
            "Estas entradas formalizan stock, pero sobre todo dibujan el mapa de activos donde el mercado aún no ha fijado un precio de consenso."
        )
    
    if cat in {"NOTICIAS_LEYES_OKUPAS", "NORMATIVAS_VIVIENDAS", "FALTA_VIVIENDA"}:
        return (
            "La regulación no solo corrige desequilibrios aparentes, sino que reordena qué actores conservan acceso operativo real al mercado."
        )
    
    if cat in {"NOTICIAS_CONSTRUCCION", "PRECIOS_MATERIALES", "PRECIOS_SUELO", "NOVEDADES_CONSTRUCCION"}:
        return (
            "Los costes y las reglas del juego de la obra redefinen la frontera entre proyectos viables y meros ejercicios teóricos de rentabilidad."
        )
    
    if cat in {"CONSTRUCCION_MODULAR", "NOTICIAS_URBANIZACION"}:
        return (
            "La industrialización y el planeamiento no solo cambian formas, comprimen plazos y riesgos allí donde el capital esté dispuesto a anticiparse."
        )
    
    if cat in {"FUTURO_SECTOR_INMOBILIARIO", "BURBUJA_INMOBILIARIA"}:
        return (
            "Más que un dato aislado, es una línea más en el gráfico de tensiones acumuladas que el consenso aún no ha terminado de asumir."
        )
    
    if cat in {"NOTICIAS_INMOBILIARIAS"}:
        return (
            "No es una noticia suelta: es otra pieza en la secuencia que reordena precios, actores y acceso efectivo a oportunidades reales."
        )
    
    # fallback genérico
    return (
        "El dato no va solo: se suma a una secuencia de señales que reordenan quién tiene visibilidad real y quién llega tarde a cada movimiento."
    )


def _pick_closer(index_seed: Optional[int] = None) -> str:
    """
    Tercera línea: cierre Althara. Puedes usar una rotación simple en lugar de random puro,
    para que sea más determinista si quieres.
    """
    if index_seed is None:
        # muy simple: usa el timestamp actual para variar un poco
        index_seed = int(datetime.utcnow().timestamp())
    
    idx = index_seed % len(ALTHARA_CLOSERS)
    return ALTHARA_CLOSERS[idx]


def build_althara_summary(
    title: str,
    raw_summary: Optional[str],
    category: Optional[str],
    seed: Optional[int] = None,
) -> str:
    """
    Construye un texto breve en tres líneas con el tono y estructura de Althara.
    
    - Línea 1: hecho frío.
    - Línea 2: lectura estratégica según categoría.
    - Línea 3: cierre en clave de asimetría / acceso / timing.
    
    Args:
        title: Título de la noticia
        raw_summary: Resumen original de la fuente (opcional)
        category: Categoría de la noticia (opcional)
        seed: Semilla para rotar los cierres (opcional)
        
    Returns:
        Texto adaptado al tono Althara (3 líneas)
    """
    fact_line = _build_fact_line(title, raw_summary)
    strategic_line = _build_strategic_line(category)
    closer_line = _pick_closer(seed)
    
    return "\n".join([fact_line, strategic_line, closer_line])
