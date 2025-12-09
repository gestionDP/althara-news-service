"""
Adapter para transformar noticias al tono Althara.

Convierte noticias crudas (raw_summary) en contenido adaptado al estilo
analítico y profesional de Althara para uso en redes sociales.
"""
from __future__ import annotations

import re
import html
from datetime import datetime
from textwrap import shorten
from typing import Optional, List

# Frases de cierre "genéricas" de Althara
ALTHARA_CLOSERS = [
    "Lo relevante no es el titular, sino quién ajusta posición antes de que el consenso llegue.",
    "La oportunidad aparece en el desfase entre el dato y la reacción del mercado visible.",
    "Donde el mercado ve ruido, Althara sólo registra el punto exacto del desplazamiento.",
    "Aquí importa menos el precio comunicado y más quién tiene acceso al siguiente movimiento.",
]


def _clean_html(text: str) -> str:
    """
    Limpia HTML de un texto, extrayendo solo el contenido de texto puro.
    
    Args:
        text: Texto que puede contener HTML
        
    Returns:
        Texto limpio sin tags HTML ni entidades HTML
    """
    if not text:
        return ""
    
    # Convertir entidades HTML a caracteres normales (&amp; -> &, etc.)
    text = html.unescape(text)
    
    # Remover tags HTML (ej: <p>, <a href="...">, etc.)
    # Regex: <[^>]+> busca cualquier cosa entre < y >
    text = re.sub(r'<[^>]+>', '', text)
    
    # Limpiar espacios múltiples y saltos de línea
    text = re.sub(r'\s+', ' ', text)
    
    # Limpiar espacios al inicio y final
    text = text.strip()
    
    return text


def _build_fact_line(title: str, raw_summary: Optional[str]) -> str:
    """
    Construye la primera línea: descripción fría del hecho.
    """
    base = title.strip()
    
    if raw_summary:
        # Limpiar HTML del raw_summary antes de combinarlo
        cleaned_summary = _clean_html(raw_summary)
        combined = f"{title.strip()}. {cleaned_summary}"
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


def _extract_key_data(raw_summary: Optional[str]) -> List[str]:
    """
    Extrae datos clave del raw_summary: números, porcentajes, precios, fechas importantes.
    
    Args:
        raw_summary: Resumen original de la noticia
        
    Returns:
        Lista de strings con datos clave encontrados (máximo 5)
    """
    if not raw_summary:
        return []
    
    key_data = []
    text = _clean_html(raw_summary)
    
    # Patrones para extraer datos relevantes
    patterns = [
        # Porcentajes: "5%", "12,5%", "aumentó un 15%"
        (r'(\d+[.,]?\d*\s*%)', 'Porcentaje'),
        # Precios: "€500.000", "1.2 millones", "€1.500/m²"
        (r'(€\s*\d+[.,]?\d*[.,]?\d*\s*(?:millones?|miles?|/m²)?)', 'Precio'),
        # Números grandes: "1.500 viviendas", "2 millones de euros"
        (r'(\d+[.,]?\d*[.,]?\d*\s*(?:millones?|miles?|millones? de|viviendas?|propiedades?|euros?))', 'Cantidad'),
        # Años: "2025", "en 2024"
        (r'(\b(?:20\d{2}|19\d{2})\b)', 'Año'),
        # Variaciones: "subió un 10%", "bajó 5 puntos"
        (r'((?:subió|bajó|aumentó|disminuyó|creció|descendió)\s+(?:un\s+)?\d+[.,]?\d*\s*(?:%|puntos?))', 'Variación'),
    ]
    
    found_data = set()  # Para evitar duplicados
    
    for pattern, label in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            data_point = match.group(1).strip()
            # Limpiar y formatear
            data_point = re.sub(r'\s+', ' ', data_point)
            if data_point and len(data_point) < 50:  # Evitar matches muy largos
                found_data.add(data_point)
    
    # Convertir a lista y limitar a 5 elementos más relevantes
    key_data = list(found_data)[:5]
    
    return key_data


def _extract_keywords(title: str, raw_summary: Optional[str]) -> List[str]:
    """
    Extrae palabras clave relevantes del título y raw_summary.
    Se enfoca en términos inmobiliarios y económicos relevantes.
    
    Args:
        title: Título de la noticia
        raw_summary: Resumen original (opcional)
        
    Returns:
        Lista de palabras clave (máximo 8)
    """
    # Palabras comunes a excluir
    stop_words = {
        'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas',
        'de', 'del', 'en', 'a', 'al', 'con', 'por', 'para', 'sobre',
        'es', 'son', 'fue', 'fueron', 'ser', 'estar', 'tener', 'haber',
        'que', 'cual', 'cuales', 'quien', 'quienes', 'donde', 'cuando',
        'como', 'más', 'menos', 'muy', 'tan', 'tanto', 'también', 'tampoco',
        'este', 'esta', 'estos', 'estas', 'ese', 'esa', 'esos', 'esas',
        'año', 'años', 'mes', 'meses', 'día', 'días', 'vez', 'veces',
        'según', 'según', 'según', 'según', 'según', 'según', 'según',
    }
    
    # Términos inmobiliarios relevantes (prioridad)
    real_estate_terms = {
        'vivienda', 'viviendas', 'inmobiliario', 'inmobiliaria', 'inmobiliarias',
        'hipoteca', 'hipotecas', 'hipotecario', 'hipotecaria',
        'precio', 'precios', 'valor', 'valores', 'coste', 'costes',
        'alquiler', 'alquileres', 'renta', 'rentas',
        'compra', 'venta', 'comprar', 'vender',
        'mercado', 'mercados', 'sector', 'sectores',
        'propiedad', 'propiedades', 'inmueble', 'inmuebles',
        'construcción', 'construcciones', 'obra', 'obras',
        'promoción', 'promociones', 'desarrollo', 'desarrollos',
        'inversión', 'inversiones', 'inversor', 'inversores',
        'subasta', 'subastas', 'desahucio', 'desahucios',
        'okupación', 'okupaciones', 'okupa', 'okupas',
        'normativa', 'normativas', 'ley', 'leyes', 'regulación',
        'madrid', 'barcelona', 'valencia', 'sevilla', 'bilbao',
        'españa', 'español', 'europa', 'europeo',
    }
    
    # Combinar texto
    combined_text = title.lower()
    if raw_summary:
        cleaned = _clean_html(raw_summary).lower()
        combined_text += " " + cleaned
    
    # Extraer palabras (solo palabras de 4+ caracteres)
    words = re.findall(r'\b[a-záéíóúñü]{4,}\b', combined_text)
    
    # Filtrar y priorizar
    keywords = []
    seen = set()
    
    # Primero: términos inmobiliarios
    for word in words:
        if word in real_estate_terms and word not in seen:
            keywords.append(word)
            seen.add(word)
            if len(keywords) >= 8:
                break
    
    # Segundo: otras palabras relevantes (no stop words)
    if len(keywords) < 8:
        for word in words:
            if word not in stop_words and word not in seen and len(word) >= 4:
                # Priorizar sustantivos y adjetivos (terminaciones comunes)
                if any(word.endswith(suffix) for suffix in ['ción', 'sión', 'dad', 'tad', 'tud', 'aje', 'ismo']):
                    keywords.append(word)
                    seen.add(word)
                    if len(keywords) >= 8:
                        break
    
    # Si aún no tenemos suficientes, añadir otras palabras relevantes
    if len(keywords) < 8:
        for word in words:
            if word not in stop_words and word not in seen and len(word) >= 5:
                keywords.append(word)
                seen.add(word)
                if len(keywords) >= 8:
                    break
    
    return keywords[:8]


def _build_extended_summary(title: str, raw_summary: Optional[str]) -> str:
    """
    Construye un resumen ampliado del título y raw_summary.
    
    Args:
        title: Título de la noticia
        raw_summary: Resumen original (opcional)
        
    Returns:
        Resumen ampliado (hasta 500-600 caracteres)
    """
    if not raw_summary:
        return title.strip()
    
    cleaned_summary = _clean_html(raw_summary)
    
    # Combinar título y resumen
    combined = f"{title.strip()}. {cleaned_summary}"
    
    # Limitar a 550 caracteres (dejando margen para el placeholder)
    extended = shorten(combined, width=550, placeholder="…")
    
    return extended


def build_althara_summary(
    title: str,
    raw_summary: Optional[str],
    category: Optional[str],
    seed: Optional[int] = None,
) -> str:
    """
    Construye un resumen completo estructurado con el tono y estilo de Althara.
    
    Estructura:
    - RESUMEN: Contenido ampliado del raw_summary
    - ANÁLISIS ALTHARA: Lectura estratégica según categoría
    - DATOS CLAVE: Números, porcentajes, precios, fechas relevantes
    - PALABRAS CLAVE: Términos relevantes extraídos
    
    Args:
        title: Título de la noticia
        raw_summary: Resumen original de la fuente (opcional)
        category: Categoría de la noticia (opcional)
        seed: Semilla para rotar los cierres (opcional)
        
    Returns:
        Texto adaptado al tono Althara con estructura completa
    """
    sections = []
    
    # 1. RESUMEN ampliado
    extended_summary = _build_extended_summary(title, raw_summary)
    sections.append("📊 RESUMEN")
    sections.append(extended_summary)
    sections.append("")  # Línea en blanco
    
    # 2. ANÁLISIS ALTHARA
    strategic_line = _build_strategic_line(category)
    sections.append("💡 ANÁLISIS ALTHARA")
    sections.append(strategic_line)
    sections.append("")  # Línea en blanco
    
    # 3. DATOS CLAVE
    key_data = _extract_key_data(raw_summary)
    if key_data:
        sections.append("📈 DATOS CLAVE")
        for data in key_data:
            sections.append(f"- {data}")
        sections.append("")  # Línea en blanco
    
    # 4. PALABRAS CLAVE
    keywords = _extract_keywords(title, raw_summary)
    if keywords:
        sections.append("🔑 PALABRAS CLAVE")
        keywords_str = ", ".join(keywords)
        sections.append(keywords_str)
    
    return "\n".join(sections)
