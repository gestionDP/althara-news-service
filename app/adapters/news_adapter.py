"""
Adapter to transform news to Althara tone.

Converts raw news (raw_summary) into content adapted to Althara's
analytical and professional style for social media use.
"""
from __future__ import annotations

import re
from datetime import datetime

from app.utils.html_utils import strip_html_tags
from textwrap import shorten
from typing import Optional, List, Dict, Any

ALTHARA_CLOSERS = [
    "Lo relevante no es el titular, sino quién ajusta posición antes de que el consenso llegue.",
    "La oportunidad aparece en el desfase entre el dato y la reacción del mercado visible.",
    "Donde el mercado ve ruido, Althara sólo registra el punto exacto del desplazamiento.",
    "Aquí importa menos el precio comunicado y más quién tiene acceso al siguiente movimiento.",
]


def _clean_html(text: str) -> str:
    """
    Clean HTML from text for Althara content adaptation.
    Uses base tag stripping, then removes metadata and applies accent fixes.
    """
    text = strip_html_tags(text)
    if not text:
        return ""
    
    patterns_to_remove = [
        r'[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]+\s+\d{1,2}\s+[A-Z]{3}\.\s+\d{4}\s*-\s*\d{2}:\d{2}',
        r'Compartir en (Facebook|Twitter|LinkedIn|WhatsApp)',
        r'Enviar por email',
        r'DREAMSTIME|GETTY|SHUTTERSTOCK|ISTOCK',
        r'EXPANSION|EL PAÍS|CINCO DÍAS',
        r'Vistas del|Imagen de|Foto de',
        r'\b\d{1,2}\s+[A-Z]{3}\.\s+\d{4}\s*-\s*\d{2}:\d{2}\b',
        r'Periodista y Coordinadora editorial',
        r'\d{2}/\d{2}/\d{4}',
    ]
    
    for pattern in patterns_to_remove:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if not re.match(r'^[A-ZÁÉÍÓÚÑ\s]{20,}$', line):
            cleaned_lines.append(line)
    text = ' '.join(cleaned_lines)
    
    text = text.replace('\ufffd', '')
    text = text.replace('', '')
    
    accent_fixes = [
        (r'\bneuropsicloga\b', 'neuropsicóloga'),
        (r'\bMnica\b', 'Mónica'),
        (r'\bcientfica\b', 'científica'),
        (r'\bdcadas\b', 'décadas'),
        (r'\bmbito\b', 'ámbito'),
        (r'\bpsicloga\b', 'psicóloga'),
        (r'\beducacin\b', 'educación'),
        (r'\bdiseñar\b', 'diseñar'),
        (r'\bsegn\b', 'según'),
        (r'\bcmo\b', 'cómo'),
        (r'\bqu\b', 'qué'),
        (r'\bdnde\b', 'dónde'),
        (r'\bcuando\b', 'cuándo'),
        (r'\barchitectura\b', 'arquitectura'),
    ]
    
    for pattern, replacement in accent_fixes:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    common_fixes = {
        'psicologa': 'psicóloga',
        'psicologo': 'psicólogo',
        'arquitecta': 'arquitecta',
        'arquitecto': 'arquitecto',
        'educacion': 'educación',
        'especializada': 'especializada',
        'especializado': 'especializado',
    }
    
    for wrong, correct in common_fixes.items():
        text = re.sub(r'\b' + wrong + r'\b', correct, text, flags=re.IGNORECASE)
    
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text


def _build_fact_line(title: str, raw_summary: Optional[str]) -> str:
    """
    Builds the first line: cold description of the fact.
    """
    base = title.strip()
    
    if raw_summary:
        cleaned_summary = _clean_html(raw_summary)
        combined = f"{title.strip()}. {cleaned_summary}"
        fact = shorten(combined, width=220, placeholder="…")
    else:
        fact = base
    
    lower = fact.lower()
    
    if lower.startswith("el ") or lower.startswith("la ") or lower.startswith("los ") or lower.startswith("las "):
        return fact
    if lower.startswith("en "):
        return fact
    
    return f"Los últimos datos apuntan a lo siguiente: {fact}"


def _build_strategic_line(category: Optional[str]) -> str:
    """
    Second line: strategic reading based on category.
    """
    if category is None:
        category = ""
    
    cat = category.upper()
    
    if cat in {"PRECIOS_VIVIENDA"}:
        return (
            "Detrás de la cifra, el patrón es un ajuste entre oferta limitada y demanda que aún no ha reprecificado del todo el riesgo del ciclo."
        )
    
    if cat in {"FONDOS_INVERSION_INMOBILIARIA", "MOVIMIENTOS_GRANDES_TENEDORES", "GRANDES_INVERSIONES_INMOBILIARIAS", "INVERSION_INSTITUCIONAL", "OPERACIONES_CORPORATIVAS", "GRANDES_TENEDORES"}:
        return (
            "El movimiento no es aislado: refleja una rotación silenciosa de capital hacia activos donde la asimetría de información sigue siendo aprovechable."
        )
    
    if cat in {"NOTICIAS_HIPOTECAS", "HIPOTECAS_Y_CREDITO", "TIPOS_Y_MACRO"}:
        return (
            "El repliegue y la reconfiguración del crédito redefinen quién puede seguir operando con ventaja en el próximo tramo del ciclo."
        )
    
    if cat in {"NOTICIAS_BOE_SUBASTAS", "NOTICIAS_DESAHUCIOS", "BOE_SUBASTAS", "DESAHUCIOS_Y_VULNERABILIDAD"}:
        return (
            "Estas entradas formalizan stock, pero sobre todo dibujan el mapa de activos donde el mercado aún no ha fijado un precio de consenso."
        )
    
    if cat in {"NOTICIAS_LEYES_OKUPAS", "NORMATIVAS_VIVIENDAS", "FALTA_VIVIENDA", "REGULACION_VIVIENDA", "OKUPACION_Y_SEGURIDAD_JURIDICA", "URBANISMO_Y_PLANEAMIENTO", "OFERTA_Y_STOCK"}:
        return (
            "La regulación no solo corrige desequilibrios aparentes, sino que reordena qué actores conservan acceso operativo real al mercado."
        )
    
    if cat in {"NOTICIAS_CONSTRUCCION", "PRECIOS_MATERIALES", "PRECIOS_SUELO", "NOVEDADES_CONSTRUCCION", "CONSTRUCCION_Y_COSTES"}:
        return (
            "Los costes y las reglas del juego de la obra redefinen la frontera entre proyectos viables y meros ejercicios teóricos de rentabilidad."
        )
    
    if cat in {"CONSTRUCCION_MODULAR", "NOTICIAS_URBANIZACION", "INDUSTRIALIZACION_MODULAR"}:
        return (
            "La industrialización y el planeamiento no solo cambian formas, comprimen plazos y riesgos allí donde el capital esté dispuesto a anticiparse."
        )
    
    if cat in {"FUTURO_SECTOR_INMOBILIARIO", "BURBUJA_INMOBILIARIA"}:
        return (
            "Más que un dato aislado, es una línea más en el gráfico de tensiones acumuladas que el consenso aún no ha terminado de asumir."
        )
    
    if cat in {"NOTICIAS_INMOBILIARIAS", "SECTOR_INMOBILIARIO", "MERCADO_COMPRAVENTA", "ALQUILER_RESIDENCIAL", "ALQUILER_VACACIONAL"}:
        return (
            "No es una noticia suelta: es otra pieza en la secuencia que reordena precios, actores y acceso efectivo a oportunidades reales."
        )
    
    return (
        "El dato no va solo: se suma a una secuencia de señales que reordenan quién tiene visibilidad real y quién llega tarde a cada movimiento."
    )


def _pick_closer(index_seed: Optional[int] = None) -> str:
    """
    Third line: Althara closer. Uses simple rotation instead of pure random for determinism.
    """
    if index_seed is None:
        index_seed = int(datetime.utcnow().timestamp())
    
    idx = index_seed % len(ALTHARA_CLOSERS)
    return ALTHARA_CLOSERS[idx]


def _extract_key_data(raw_summary: Optional[str]) -> List[str]:
    """
    Extracts key data from raw_summary: numbers, percentages, prices, important dates.
    
    Args:
        raw_summary: Original news summary
        
    Returns:
        List of strings with found key data (maximum 5)
    """
    if not raw_summary:
        return []
    
    key_data = []
    text = _clean_html(raw_summary)
    
    patterns = [
        (r'(\d+[.,]?\d*\s*%)', 'Porcentaje'),
        (r'(€\s*\d+[.,]?\d*[.,]?\d*\s*(?:millones?|miles?|/m²)?)', 'Precio'),
        (r'(\d+[.,]?\d*[.,]?\d*\s*(?:millones?|miles?|millones? de|viviendas?|propiedades?|euros?))', 'Cantidad'),
        (r'(\b(?:20\d{2}|19\d{2})\b)', 'Año'),
        (r'((?:subió|bajó|aumentó|disminuyó|creció|descendió)\s+(?:un\s+)?\d+[.,]?\d*\s*(?:%|puntos?))', 'Variación'),
    ]
    
    found_data = set()
    
    for pattern, label in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            data_point = match.group(1).strip()
            data_point = re.sub(r'\s+', ' ', data_point)
            if data_point and len(data_point) < 50:
                found_data.add(data_point)
    
    key_data = list(found_data)[:5]
    
    return key_data


def _extract_keywords(title: str, raw_summary: Optional[str]) -> List[str]:
    """
    Extracts relevant and coherent keywords from title and raw_summary.
    Focuses on real estate terms, locations, and key concepts.
    
    Args:
        title: News title
        raw_summary: Original summary (optional)
        
    Returns:
        List of relevant keywords (maximum 6-8)
    """
    stop_words = {
        'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas',
        'de', 'del', 'en', 'a', 'al', 'con', 'por', 'para', 'sobre',
        'es', 'son', 'fue', 'fueron', 'ser', 'estar', 'tener', 'haber',
        'que', 'cual', 'cuales', 'quien', 'quienes', 'donde', 'cuando',
        'como', 'más', 'menos', 'muy', 'tan', 'tanto', 'también', 'tampoco',
        'este', 'esta', 'estos', 'estas', 'ese', 'esa', 'esos', 'esas',
        'año', 'años', 'mes', 'meses', 'día', 'días', 'vez', 'veces',
        'según', 'todos', 'todas', 'cada', 'todo', 'toda',
        'puede', 'pueden', 'debe', 'deben', 'hace', 'hacen',
        'sido', 'estado', 'estado', 'sido',
    }
    
    real_estate_terms = {
        'vivienda', 'viviendas', 'inmobiliario', 'inmobiliaria', 'inmobiliarias',
        'hipoteca', 'hipotecas', 'hipotecario', 'hipotecaria',
        'precio', 'precios', 'valor', 'valores', 'coste', 'costes',
        'alquiler', 'alquileres', 'renta', 'rentas',
        'compra', 'venta', 'comprar', 'vender', 'compraventa', 'compraventas',
        'mercado', 'mercados', 'sector', 'sectores',
        'propiedad', 'propiedades', 'inmueble', 'inmuebles',
        'construcción', 'construcciones', 'obra', 'obras',
        'promoción', 'promociones', 'desarrollo', 'desarrollos',
        'inversión', 'inversiones', 'inversor', 'inversores',
        'subasta', 'subastas', 'desahucio', 'desahucios',
        'okupación', 'okupaciones', 'okupa', 'okupas',
        'normativa', 'normativas', 'ley', 'leyes', 'regulación',
    }
    
    locations = {
        'madrid', 'barcelona', 'valencia', 'sevilla', 'bilbao', 'zaragoza',
        'málaga', 'murcia', 'palma', 'las palmas', 'granada', 'alicante',
        'valladolid', 'córdoba', 'vigo', 'gijón', 'hospitalet', 'vitoria',
        'castilla', 'león', 'andalucía', 'cataluña', 'comunidad valenciana',
        'galicia', 'país vasco', 'asturias', 'cantabria', 'navarra',
        'españa', 'español', 'europa', 'europeo',
    }
    
    combined_text = title.lower()
    if raw_summary:
        cleaned = _clean_html(raw_summary).lower()
        combined_text += " " + cleaned
    
    words = re.findall(r'\b[a-záéíóúñü]{4,}\b', combined_text)
    
    word_freq = {}
    for word in words:
        if word not in stop_words:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    keywords = []
    seen = set()
    
    for word in sorted(word_freq.keys(), key=lambda x: word_freq[x], reverse=True):
        if word in real_estate_terms and word not in seen:
            keywords.append(word)
            seen.add(word)
            if len(keywords) >= 5:
                break
    
    if len(keywords) < 8:
        for word in sorted(word_freq.keys(), key=lambda x: word_freq[x], reverse=True):
            if word in locations and word not in seen:
                keywords.append(word)
                seen.add(word)
                if len(keywords) >= 8:
                    break
    
    if len(keywords) < 8:
        for word in sorted(word_freq.keys(), key=lambda x: word_freq[x], reverse=True):
            if word not in seen and len(word) >= 5:
                if any(word.endswith(suffix) for suffix in ['ción', 'sión', 'dad', 'tad', 'tud', 'aje', 'ismo', 'miento']):
                    keywords.append(word)
                    seen.add(word)
                    if len(keywords) >= 8:
                        break
    
    if len(keywords) < 6:
        for word in sorted(word_freq.keys(), key=lambda x: word_freq[x], reverse=True):
            if word not in stop_words and word not in seen and len(word) >= 5 and word_freq[word] >= 2:
                keywords.append(word)
                seen.add(word)
                if len(keywords) >= 6:
                    break
    
    return keywords[:8]


def _build_extended_summary(title: str, raw_summary: Optional[str]) -> str:
    """
    Builds the complete news content, cleaning metadata but keeping all relevant information.
    Does not truncate content, only cleans it.
    
    Args:
        title: News title
        raw_summary: Original summary (optional)
        
    Returns:
        Complete clean news content
    """
    if not raw_summary:
        return title.strip()
    
    cleaned_summary = _clean_html(raw_summary)
    
    title_lower = title.lower().strip()
    cleaned_lower = cleaned_summary.lower().strip()
    
    if cleaned_lower.startswith(title_lower):
        cleaned_summary = cleaned_summary[len(title):].strip()
        cleaned_summary = re.sub(r'^[.,\s]+', '', cleaned_summary)
    
    title_words = title_lower.split()
    if len(title_words) > 3:
        title_start = ' '.join(title_words[:min(5, len(title_words))])
        if cleaned_lower.startswith(title_start):
            idx = cleaned_summary.lower().find(title_start)
            if idx == 0:
                remaining = cleaned_summary[len(title_start):].strip()
                next_space = remaining.find(' ')
                if next_space > 0:
                    cleaned_summary = remaining[next_space:].strip()
                else:
                    cleaned_summary = remaining
                cleaned_summary = re.sub(r'^[.,\s]+', '', cleaned_summary)
    
    words = cleaned_summary.split()
    if len(words) > 15:
        for i in range(3, min(8, len(words))):
            first_phrase = ' '.join(words[:i]).lower()
            remaining_text = ' '.join(words[i:]).lower()
            if first_phrase in remaining_text:
                cleaned_summary = ' '.join(words[i:])
                break
    
    section_phrases = ['mercado inmobiliario', 'noticias inmobiliarias', 'economía inmobiliaria']
    for phrase in section_phrases:
        if cleaned_summary.lower().startswith(phrase):
            cleaned_summary = cleaned_summary[len(phrase):].strip()
            cleaned_summary = re.sub(r'^[.,\s]+', '', cleaned_summary)
    
    words = cleaned_summary.split()
    if len(words) > 20:
        first_10_words = ' '.join(words[:10]).lower()
        remaining_text = ' '.join(words[10:]).lower()
        if first_10_words in remaining_text:
            idx = remaining_text.find(first_10_words)
            if idx > 0:
                cleaned_summary = ' '.join(words[:10 + idx // 2])
            else:
                cleaned_summary = ' '.join(words[10:])
    
    combined = f"{title.strip()}. {cleaned_summary}"
    
    sentences = re.split(r'([.!?])\s+', combined)
    
    reconstructed_sentences = []
    for i in range(0, len(sentences) - 1, 2):
        if i + 1 < len(sentences):
            sentence = sentences[i] + sentences[i + 1]
            sentence = sentence.strip()
            if sentence:
                reconstructed_sentences.append(sentence)
    
    if not reconstructed_sentences:
        sentences = re.split(r'\.\s+', combined)
        reconstructed_sentences = [s.strip() + '.' for s in sentences if s.strip()]
    
    paragraphs = []
    current_paragraph = []
    
    for sentence in reconstructed_sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        if not sentence.endswith(('.', '!', '?', '…')):
            sentence += '.'
        
        current_paragraph.append(sentence)
        
        if len(current_paragraph) >= 3 or (len(sentence) > 120 and len(current_paragraph) >= 2):
            paragraphs.append(' '.join(current_paragraph))
            current_paragraph = []
    
    if current_paragraph:
        paragraphs.append(' '.join(current_paragraph))
    
    if not paragraphs:
        if len(combined) > 5000:
            truncated = combined[:5000]
            last_period = truncated.rfind('. ')
            if last_period > 4500:
                combined = combined[:last_period + 1] + "…"
            else:
                combined = truncated + "…"
        return combined
    
    formatted_text = '\n\n'.join(paragraphs)
    
    if len(formatted_text) > 5000:
        truncated_paragraphs = []
        total_length = 0
        for para in paragraphs:
            if total_length + len(para) + 2 > 5000:
                break
            truncated_paragraphs.append(para)
            total_length += len(para) + 2
        formatted_text = '\n\n'.join(truncated_paragraphs) + "…"
    
    return formatted_text


def build_althara_summary(
    title: str,
    raw_summary: Optional[str],
    category: Optional[str],
    seed: Optional[int] = None,
) -> str:
    """
    Builds a complete structured summary with Althara tone and style.
    
    Structure:
    - SUMMARY: Extended content from raw_summary
    - ALTHARA ANALYSIS: Strategic reading based on category
    - KEY DATA: Numbers, percentages, prices, relevant dates
    - KEY WORDS: Extracted relevant terms
    
    Args:
        title: News title
        raw_summary: Original source summary (optional)
        category: News category (optional)
        seed: Seed for rotating closers (optional)
        
    Returns:
        Text adapted to Althara tone with complete structure
    """
    sections = []
    
    full_content = _build_extended_summary(title, raw_summary)
    sections.append("Content Summary")
    sections.append("")
    sections.append(full_content)
    sections.append("")
    sections.append("")
       
    key_data = _extract_key_data(raw_summary)
    if key_data:
        sections.append("Key Data")
        sections.append("")
        for data in key_data:
            sections.append(f"• {data}")
        sections.append("")
        sections.append("")
    
    keywords = _extract_keywords(title, raw_summary)
    if keywords:
        sections.append("Key Words")
        sections.append("")
        keywords_str = " • ".join(keywords)
        sections.append(keywords_str)
    
    return "\n".join(sections)


def build_instagram_post(
    title: str,
    raw_summary: Optional[str],
    category: Optional[str],
    source: Optional[str] = None,
    url: Optional[str] = None,
    key_data: Optional[List[str]] = None,
    seed: Optional[int] = None,
) -> str:
    """
    Genera un post de Instagram en el tono Althara: minimalista, reflexivo y estratégico.
    
    Estructura:
    - Pregunta provocadora o insight estratégico
    - Dato clave (si hay)
    - Título breve
    - Reflexión estratégica
    - Fuente y URL (con tono Althara)
    - Hashtags mínimos
    
    Args:
        title: Título de la noticia
        raw_summary: Resumen original
        category: Categoría de la noticia
        source: Fuente de la noticia (opcional)
        url: URL de la noticia (opcional)
        key_data: Lista de datos clave extraídos
        seed: Seed para determinismo
        
    Returns:
        Post formateado para Instagram (máximo 2200 caracteres, idealmente 300-500)
    """
    if not key_data:
        key_data = _extract_key_data(raw_summary)
    
    # Preguntas provocadoras por categoría (estilo Althara)
    provocative_questions = {
        "PRECIOS_VIVIENDA": [
            "¿El precio comunica valor o solo VISIBILIDAD?",
            "¿Quién ajusta posición antes de que el consenso llegue?",
            "¿El dato refleja realidad o anticipa movimiento?",
        ],
        "FONDOS_INVERSION_INMOBILIARIA": [
            "¿El capital sigue al consenso o lo anticipa?",
            "¿Quién tiene acceso al siguiente movimiento?",
            "¿La rotación de capital construye valor o solo VISIBILIDAD?",
        ],
        "GRANDES_INVERSIONES_INMOBILIARIAS": [
            "¿La inversión comunica oportunidad o solo VISIBILIDAD?",
            "¿Quién lee las señales antes del consenso?",
            "¿El movimiento refleja estrategia o reacción?",
        ],
        "NOTICIAS_HIPOTECAS": [
            "¿El crédito redefine acceso o solo VISIBILIDAD?",
            "¿Quién opera con ventaja en el próximo tramo?",
            "¿La reconfiguración del crédito construye valor o solo VISIBILIDAD?",
        ],
        "NOTICIAS_CONSTRUCCION": [
            "¿El proyecto comunica viabilidad o solo VISIBILIDAD?",
            "¿Quién anticipa la frontera entre viable y teórico?",
            "¿La obra construye valor o solo VISIBILIDAD?",
        ],
        "NORMATIVAS_VIVIENDAS": [
            "¿La regulación reordena acceso o solo VISIBILIDAD?",
            "¿Quién conserva acceso operativo real?",
            "¿La normativa construye valor o solo VISIBILIDAD?",
        ],
        "BURBUJA_INMOBILIARIA": [
            "¿El consenso ha asumido las tensiones acumuladas?",
            "¿Quién lee el gráfico antes del ajuste?",
            "¿El dato comunica corrección o solo VISIBILIDAD?",
        ],
        "NOTICIAS_BOE_SUBASTAS": [
            "¿El mercado ha fijado precio de consenso?",
            "¿Quién lee el mapa de activos antes del consenso?",
            "¿La subasta comunica oportunidad o solo VISIBILIDAD?",
        ],
        "NOTICIAS_DESAHUCIOS": [
            "¿El proceso formaliza stock o solo VISIBILIDAD?",
            "¿Quién lee el mapa de activos donde no hay consenso?",
        ],
        "NOTICIAS_LEYES_OKUPAS": [
            "¿La ley reordena acceso o solo VISIBILIDAD?",
            "¿Quién conserva acceso operativo real?",
        ],
        "ALQUILER_VACACIONAL": [
            "¿El alquiler comunica oportunidad o solo VISIBILIDAD?",
            "¿Quién lee la tendencia antes del consenso?",
        ],
    }
    
    # Insights estratégicos (alternativa a preguntas)
    strategic_insights = {
        "PRECIOS_VIVIENDA": [
            "Detrás de la cifra, el patrón es un ajuste entre oferta limitada y demanda que aún no ha reprecificado del todo el riesgo del ciclo.",
            "Lo relevante no es el precio comunicado, sino quién tiene acceso al siguiente movimiento.",
        ],
        "FONDOS_INVERSION_INMOBILIARIA": [
            "El movimiento no es aislado: refleja una rotación silenciosa de capital hacia activos donde la asimetría de información sigue siendo aprovechable.",
            "La oportunidad aparece en el desfase entre el dato y la reacción del mercado visible.",
        ],
        "GRANDES_INVERSIONES_INMOBILIARIAS": [
            "El movimiento no es aislado: refleja una rotación silenciosa de capital hacia activos donde la asimetría de información sigue siendo aprovechable.",
        ],
        "NOTICIAS_HIPOTECAS": [
            "El repliegue y la reconfiguración del crédito redefinen quién puede seguir operando con ventaja en el próximo tramo del ciclo.",
            "Donde el mercado ve ajuste, Althara registra el punto exacto del desplazamiento.",
        ],
        "NOTICIAS_CONSTRUCCION": [
            "Los costes y las reglas del juego redefinen la frontera entre proyectos viables y meros ejercicios teóricos de rentabilidad.",
        ],
        "NORMATIVAS_VIVIENDAS": [
            "La regulación no solo corrige desequilibrios aparentes, sino que reordena qué actores conservan acceso operativo real al mercado.",
        ],
        "BURBUJA_INMOBILIARIA": [
            "Más que un dato aislado, es una línea más en el gráfico de tensiones acumuladas que el consenso aún no ha terminado de asumir.",
        ],
        "NOTICIAS_BOE_SUBASTAS": [
            "Estas entradas formalizan stock, pero sobre todo dibujan el mapa de activos donde el mercado aún no ha fijado un precio de consenso.",
        ],
        "NOTICIAS_DESAHUCIOS": [
            "Estas entradas formalizan stock, pero sobre todo dibujan el mapa de activos donde el mercado aún no ha fijado un precio de consenso.",
        ],
    }
    
    # Usar seed para determinismo
    if seed is None:
        seed = hash(title) % 1000
    
    post_lines = []
    
    # Decidir si usar pregunta o insight (50/50)
    use_question = (seed % 2 == 0)
    
    if use_question and category in provocative_questions:
        questions = provocative_questions[category]
        selected_question = questions[seed % len(questions)]
        post_lines.append(selected_question)
    elif category in strategic_insights:
        insights = strategic_insights[category]
        selected_insight = insights[seed % len(insights)]
        post_lines.append(selected_insight)
    else:
        # Fallback genérico
        post_lines.append("¿El dato comunica valor o solo VISIBILIDAD?")
    
    post_lines.append("")  # Espacio en blanco (estilo minimalista)
    
    # Dato clave (si hay, máximo 1-2 datos)
    if key_data:
        # Tomar solo el dato más relevante
        main_data = key_data[0]
        post_lines.append(main_data)
        post_lines.append("")
    
    # Título adaptado (muy breve, máximo 1 línea)
    title_clean = _clean_html(title)
    # Simplificar título si es muy largo
    if len(title_clean) > 80:
        words = title_clean.split()
        title_short = ""
        for word in words[:10]:  # Máximo 10 palabras
            if len(title_short + " " + word) <= 80:
                title_short += " " + word if title_short else word
            else:
                break
        title_clean = title_short
    
    post_lines.append(title_clean)
    post_lines.append("")  # Espacio en blanco
    
    # Insight estratégico breve (1 línea, estilo Althara)
    strategic_line = _build_strategic_line(category)
    # Acortar si es muy largo
    if len(strategic_line) > 150:
        sentences = strategic_line.split('. ')
        strategic_line = sentences[0] + "." if sentences else strategic_line[:150]
    
    post_lines.append(strategic_line)
    
    # Espacio en blanco antes de fuente
    post_lines.append("")
    
    # Fuente y URL con tono Althara (minimalista, no promocional)
    if source or url:
        post_lines.append("—")
        post_lines.append("")
        
        if source:
            # Formato minimalista: solo el nombre de la fuente
            post_lines.append(f"Fuente: {source}")
        
        if url:
            # URL sin formato promocional, solo el link
            post_lines.append(url)
    
    # Espacio antes de hashtags
    post_lines.append("")
    
    # Hashtags mínimos y relevantes (máximo 5-7, estilo minimalista)
    hashtags = _generate_minimal_hashtags(category, title)
    if hashtags:
        post_lines.append(" ".join(hashtags))
    
    # Unir todo
    post = "\n".join(post_lines)
    
    # Asegurar que no exceda 2200 caracteres
    if len(post) > 2200:
        # Truncar manteniendo estructura
        lines = post.split('\n')
        truncated = []
        current_length = 0
        for line in lines:
            if current_length + len(line) + 1 <= 2100:
                truncated.append(line)
                current_length += len(line) + 1
            else:
                break
        post = "\n".join(truncated)
        if hashtags:
            post += "\n\n" + " ".join(hashtags[:3])
    
    return post


def _generate_minimal_hashtags(
    category: Optional[str],
    title: str
) -> List[str]:
    """
    Genera hashtags mínimos y relevantes (estilo Althara: máximo 5-7).
    """
    hashtags = []
    
    # Hashtags base por categoría (mínimos)
    category_hashtags = {
        "PRECIOS_VIVIENDA": ["#preciosvivienda", "#mercadoinmobiliario"],
        "FONDOS_INVERSION_INMOBILIARIA": ["#fondosinversion", "#inversioninmobiliaria"],
        "NOTICIAS_HIPOTECAS": ["#hipotecas", "#financiacion"],
        "NOTICIAS_CONSTRUCCION": ["#construccion", "#desarrolloinmobiliario"],
        "ALQUILER_VACACIONAL": ["#alquilervacacional"],
        "NORMATIVAS_VIVIENDAS": ["#normativa", "#leyvivienda"],
    }
    
    hashtags.extend(category_hashtags.get(category, ["#inmobiliaria"]))
    
    # Hashtag de marca (siempre)
    hashtags.append("#althara")
    
    # Máximo 5-7 hashtags total (estilo minimalista)
    return hashtags[:7]


def build_all_content(
    title: str,
    raw_summary: Optional[str],
    category: Optional[str],
    source: Optional[str] = None,
    url: Optional[str] = None,
    seed: Optional[int] = None,
) -> tuple[str, str]:
    """
    Genera tanto el resumen de Althara como el post de Instagram.
    
    Returns:
        Tuple (althara_summary, instagram_post)
    """
    althara_summary = build_althara_summary(title, raw_summary, category, seed)
    
    key_data = _extract_key_data(raw_summary)
    instagram_post = build_instagram_post(
        title=title,
        raw_summary=raw_summary,
        category=category,
        source=source,
        url=url,
        key_data=key_data,
        seed=seed
    )
    
    return althara_summary, instagram_post


# ============================================================================
# FUNCIONES PARA CONTENIDO ESTRUCTURADO (FORMATO JSON)
# ============================================================================

def build_structured_content(
    title: str,
    raw_summary: Optional[str],
    category: Optional[str],
    source: Optional[str] = None,
    url: Optional[str] = None,
    published_at: Optional[datetime] = None,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Genera contenido estructurado en formato JSON según el spec de Althara.
    Completamente determinista, sin LLM.
    
    Returns:
        Dict con estructura completa: source, web, instagram, qa
    """
    if seed is None:
        seed = hash(title) % 1000
    
    # Extraer información base
    key_data = _extract_key_data(raw_summary)
    keywords = _extract_keywords(title, raw_summary)
    
    # Construir título Althara (interpretativo)
    althara_title = _build_althara_title(title, category, seed)
    
    # Construir "hecho" (1-2 líneas, factual)
    hecho = _build_hecho(title, raw_summary, key_data)
    
    # Construir "lectura Althara" (3-6 líneas)
    lectura = _build_lectura_althara(title, raw_summary, category, key_data, keywords, seed)
    
    # Construir "implicaciones" (3-5 bullets)
    implicaciones = _build_implicaciones(category, key_data, keywords, seed)
    
    # Construir "señales a vigilar" (2-4 bullets)
    senales = _build_senales_a_vigilar(category, key_data, keywords, seed)
    
    # Construir deck (subtítulo breve)
    deck = _build_deck(title, hecho, category)
    
    # Construir disclaimer
    disclaimer = _build_disclaimer(source, url)
    
    # Construir Instagram
    instagram = _build_instagram_structured(
        title, raw_summary, category, source, url, key_data, seed
    )
    
    # QA: verificar datos
    qa = _build_qa(key_data, keywords, raw_summary, title)
    
    # Formato de fecha
    published_date_str = None
    if published_at:
        if isinstance(published_at, datetime):
            published_date_str = published_at.strftime("%Y-%m-%d")
        else:
            published_date_str = str(published_at)[:10]
    
    return {
        "version": "2.0",
        "source": {
            "name": source or "Fuente no especificada",
            "url": url or "",
            "published_date": published_date_str or ""
        },
        "web": {
            "title": althara_title,
            "deck": deck,
            "hecho": hecho,
            "lectura": lectura,
            "implicaciones": implicaciones,
            "senales_a_vigilar": senales,
            "disclaimer": disclaimer
        },
        "instagram": instagram,
        "qa": qa,
        "metadata": {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "category": category or "NOTICIAS_INMOBILIARIAS",
            "seed": seed
        }
    }


def _build_althara_title(title: str, category: Optional[str], seed: int) -> str:
    """
    Construye título interpretativo Althara (no sensacionalista).
    Usa templates por categoría o transforma el título original.
    """
    title_clean = _clean_html(title)
    
    # Templates por categoría para títulos interpretativos
    title_templates = {
        "PRECIOS_VIVIENDA": [
            "El precio no comunica valor, comunica posición",
            "Detrás de la cifra, el ajuste del ciclo",
            "El dato no es el precio, es quién ajusta primero"
        ],
        "FONDOS_INVERSION_INMOBILIARIA": [
            "El capital no sigue al consenso, lo anticipa",
            "La rotación silenciosa de capital",
            "Quién tiene acceso al siguiente movimiento"
        ],
        "NOTICIAS_HIPOTECAS": [
            "El crédito redefine acceso, no solo condiciones",
            "Quién opera con ventaja en el próximo tramo",
            "La reconfiguración del crédito"
        ],
        "NORMATIVAS_VIVIENDAS": [
            "La regulación reordena acceso, no solo corrige",
            "Quién conserva acceso operativo real",
            "La normativa no corrige, reordena"
        ],
        "NOTICIAS_CONSTRUCCION": [
            "La frontera entre viable y teórico",
            "Los costes redefinen la viabilidad",
            "El proyecto no comunica viabilidad, comunica umbral"
        ],
        "NOTICIAS_INMOBILIARIAS": [
            "La fricción no está en el acuerdo, sino en la integración",
            "No es una noticia suelta: es otra pieza en la secuencia",
            "El dato no va solo: se suma a una secuencia de señales"
        ]
    }
    
    # Si hay template para la categoría, usarlo
    if category and category in title_templates:
        templates = title_templates[category]
        selected = templates[seed % len(templates)]
        
        # Intentar personalizar con palabras clave del título
        title_words = set(title_clean.lower().split())
        location_words = {'palma', 'madrid', 'barcelona', 'valencia', 'sevilla', 'bilbao'}
        found_location = title_words.intersection(location_words)
        
        if found_location:
            location = found_location.pop().capitalize()
            return f"{location}: {selected.lower()}"
        
        return selected
    
    # Fallback: transformar título original
    # Eliminar palabras sensacionalistas
    sensacionalistas = ['impactante', 'brutal', 'bomba', 'escándalo', 'shock', 
                       'revelación', 'exclusiva', 'última hora']
    words = title_clean.split()
    filtered_words = [w for w in words if w.lower() not in sensacionalistas]
    
    if len(filtered_words) < len(words):
        title_clean = ' '.join(filtered_words)
    
    # Si es muy largo, acortar manteniendo esencia
    if len(title_clean) > 80:
        # Intentar mantener sujeto + verbo + complemento clave
        sentences = re.split(r'[.!?]', title_clean)
        if sentences:
            title_clean = sentences[0].strip()
            if len(title_clean) > 80:
                words = title_clean.split()
                title_clean = ' '.join(words[:12])
    
    return title_clean


def _build_hecho(title: str, raw_summary: Optional[str], key_data: List[str]) -> str:
    """
    Construye el "hecho" (1-2 líneas, factual, sin opinión).
    """
    if not raw_summary:
        return title.strip()
    
    cleaned = _clean_html(raw_summary)
    
    # Extraer primera oración factual
    sentences = re.split(r'([.!?])\s+', cleaned)
    factual_sentences = []
    
    for i in range(0, len(sentences) - 1, 2):
        if i + 1 < len(sentences):
            sentence = (sentences[i] + sentences[i + 1]).strip()
            if sentence and len(sentence) > 20:
                # Evitar oraciones con opinión
                opinion_words = ['considera', 'cree', 'opina', 'piensa', 'sugiere']
                if not any(word in sentence.lower() for word in opinion_words):
                    factual_sentences.append(sentence)
                    if len(factual_sentences) >= 2:
                        break
    
    if factual_sentences:
        hecho = ' '.join(factual_sentences[:2])
        # Asegurar máximo 2 líneas (aprox 220 caracteres)
        if len(hecho) > 220:
            hecho = hecho[:220].rsplit('.', 1)[0] + '.'
        return hecho
    
    # Fallback: usar título + inicio del resumen
    combined = f"{title.strip()}. {cleaned[:150]}"
    return shorten(combined, width=220, placeholder="…")


def _build_lectura_althara(
    title: str, 
    raw_summary: Optional[str], 
    category: Optional[str],
    key_data: List[str],
    keywords: List[str],
    seed: int
) -> str:
    """
    Construye "lectura Althara" (3-6 líneas: causalidad + fricción + "qué cambia").
    """
    # Usar la función existente _build_strategic_line como base
    strategic_base = _build_strategic_line(category)
    
    # Expandir con contexto específico de la noticia
    lectura_parts = [strategic_base]
    
    # Añadir línea sobre causalidad si hay datos clave
    if key_data:
        data_line = _build_causalidad_line(category, key_data[0])
        if data_line:
            lectura_parts.append(data_line)
    
    # Añadir línea sobre fricción/umbral
    friccion_line = _build_friccion_line(category, title)
    if friccion_line:
        lectura_parts.append(friccion_line)
    
    # Añadir línea sobre "qué cambia"
    cambio_line = _build_cambio_line(category, keywords)
    if cambio_line:
        lectura_parts.append(cambio_line)
    
    # Unir y asegurar 3-6 líneas
    lectura = ' '.join(lectura_parts[:4])  # Máximo 4 partes = ~6 líneas
    
    # Asegurar longitud razonable (3-6 líneas = ~300-600 caracteres)
    if len(lectura) > 600:
        sentences = re.split(r'([.!?])\s+', lectura)
        truncated = []
        current_len = 0
        for i in range(0, len(sentences) - 1, 2):
            if i + 1 < len(sentences):
                sentence = (sentences[i] + sentences[i + 1]).strip()
                if current_len + len(sentence) <= 600:
                    truncated.append(sentence)
                    current_len += len(sentence)
                else:
                    break
        lectura = ' '.join(truncated)
    
    return lectura


def _build_causalidad_line(category: Optional[str], key_data: str) -> Optional[str]:
    """Construye línea sobre causalidad basada en datos."""
    causalidad_templates = {
        "PRECIOS_VIVIENDA": [
            "El dato {data} refleja un ajuste entre oferta limitada y demanda que aún no ha reprecificado el riesgo del ciclo.",
            "Detrás de {data}, el patrón es una reconfiguración de acceso antes de que el consenso llegue."
        ],
        "FONDOS_INVERSION_INMOBILIARIA": [
            "El movimiento {data} no es aislado: refleja una rotación silenciosa de capital.",
            "La cifra {data} comunica quién tiene acceso al siguiente movimiento."
        ]
    }
    
    if category and category in causalidad_templates:
        templates = causalidad_templates[category]
        template = templates[hash(key_data) % len(templates)]
        return template.format(data=key_data)
    
    return None


def _build_friccion_line(category: Optional[str], title: str) -> Optional[str]:
    """Construye línea sobre fricción/umbral."""
    friccion_templates = {
        "NORMATIVAS_VIVIENDAS": [
            "La fricción aparece cuando la regulación reordena acceso sin definir umbrales operativos claros.",
            "El umbral crítico: quién conserva acceso operativo real tras la reconfiguración."
        ],
        "NOTICIAS_CONSTRUCCION": [
            "La fricción está en la frontera entre proyectos viables y ejercicios teóricos de rentabilidad.",
            "El umbral: costes y reglas del juego que redefinen la viabilidad real."
        ],
        "NOTICIAS_INMOBILIARIAS": [
            "La fricción no está en el acuerdo, sino en la integración operativa posterior.",
            "El umbral crítico: el desfase entre anuncio e implementación efectiva."
        ]
    }
    
    if category and category in friccion_templates:
        templates = friccion_templates[category]
        return templates[hash(title) % len(templates)]
    
    return None


def _build_cambio_line(category: Optional[str], keywords: List[str]) -> Optional[str]:
    """Construye línea sobre 'qué cambia'."""
    cambio_templates = {
        "PRECIOS_VIVIENDA": [
            "Lo que cambia: quién puede seguir operando con ventaja en el próximo tramo del ciclo.",
            "El desplazamiento real: acceso efectivo a oportunidades antes de que el consenso llegue."
        ],
        "NORMATIVAS_VIVIENDAS": [
            "Lo que cambia: qué actores conservan acceso operativo real al mercado.",
            "El desplazamiento: reordenamiento de acceso, no solo corrección de desequilibrios."
        ]
    }
    
    if category and category in cambio_templates:
        templates = cambio_templates[category]
        return templates[hash(' '.join(keywords[:3]) if keywords else '') % len(templates)]
    
    return None


def _build_implicaciones(
    category: Optional[str], 
    key_data: List[str], 
    keywords: List[str],
    seed: int
) -> List[str]:
    """
    Construye "implicaciones" (3-5 bullets: efectos de 1er y 2º orden).
    """
    # Templates base por categoría
    implicaciones_templates = {
        "PRECIOS_VIVIENDA": [
            "Riesgo de ajuste de posición si el mercado no ha reprecificado el riesgo del ciclo.",
            "El coste real aparece después: acceso diferencial para quienes leen las señales antes del consenso.",
            "Señal de mercado: la calidad del dato se mide por anticipación, no por consenso.",
            "Efecto de segundo orden: reconfiguración de acceso a oportunidades antes de que el precio se estabilice."
        ],
        "FONDOS_INVERSION_INMOBILIARIA": [
            "Riesgo de rotación silenciosa de capital hacia activos con asimetría de información aprovechable.",
            "El coste real: acceso diferencial para quienes anticipan el movimiento antes del consenso.",
            "Señal institucional: el capital no sigue al consenso, lo anticipa.",
            "Efecto de segundo orden: reordenamiento de acceso a activos donde el mercado aún no ha fijado precio de consenso."
        ],
        "NORMATIVAS_VIVIENDAS": [
            "Riesgo de tensión si el encaje operativo no queda definido con trazabilidad.",
            "El coste real aparece después: ajustes, reclamaciones y pérdida de continuidad operativa.",
            "Señal institucional: la calidad del proceso se mide por implementación, no por anuncio.",
            "Efecto de segundo orden: reordenamiento de qué actores conservan acceso operativo real."
        ],
        "NOTICIAS_CONSTRUCCION": [
            "Riesgo de redefinición de la frontera entre proyectos viables y ejercicios teóricos.",
            "El coste real: compresión de plazos y riesgos allí donde el capital esté dispuesto a anticiparse.",
            "Señal de mercado: los costes y reglas del juego redefinen la viabilidad real.",
            "Efecto de segundo orden: industrialización y planeamiento que cambian formas y comprimen riesgos."
        ],
        "NOTICIAS_HIPOTECAS": [
            "Riesgo de repliegue y reconfiguración del crédito que redefine acceso operativo.",
            "El coste real: quién puede seguir operando con ventaja en el próximo tramo del ciclo.",
            "Señal de mercado: el crédito reordena acceso, no solo condiciones.",
            "Efecto de segundo orden: reconfiguración de quién tiene acceso efectivo a financiación."
        ],
        "NOTICIAS_INMOBILIARIAS": [
            "Riesgo de fricción si la integración no queda definida con trazabilidad operativa.",
            "El coste real aparece después: ajustes y pérdida de continuidad operativa.",
            "Señal institucional: la calidad se mide por implementación, no por anuncio.",
            "Efecto de segundo orden: reordenamiento de acceso a oportunidades reales."
        ]
    }
    
    # Seleccionar 3-5 implicaciones según seed
    if category and category in implicaciones_templates:
        templates = implicaciones_templates[category]
        num_implicaciones = 3 + (seed % 3)  # 3-5 implicaciones
        selected = []
        for i in range(num_implicaciones):
            idx = (seed + i) % len(templates)
            selected.append(templates[idx])
        return selected[:5]
    
    # Fallback genérico
    return [
        "Riesgo de ajuste si el mercado no ha asumido las tensiones acumuladas.",
        "El coste real: acceso diferencial para quienes leen las señales antes del consenso.",
        "Señal de mercado: la calidad se mide por anticipación, no por consenso."
    ]


def _build_senales_a_vigilar(
    category: Optional[str],
    key_data: List[str],
    keywords: List[str],
    seed: int
) -> List[str]:
    """
    Construye "señales a vigilar" (2-4 bullets: métricas/decisiones verificables).
    """
    senales_templates = {
        "PRECIOS_VIVIENDA": [
            "Ajuste de posición de actores clave antes de que el consenso llegue.",
            "Reprecificación del riesgo del ciclo en próximos movimientos de mercado.",
            "Acceso diferencial a oportunidades antes de estabilización de precios."
        ],
        "FONDOS_INVERSION_INMOBILIARIA": [
            "Rotación de capital hacia activos con asimetría de información.",
            "Movimientos de grandes tenedores antes del consenso del mercado.",
            "Fijación de precio de consenso en activos objetivo."
        ],
        "NORMATIVAS_VIVIENDAS": [
            "Apertura de mesa efectiva con calendario y actas de negociación.",
            "Documento final con definición concreta de umbrales operativos (no solo adscripción).",
            "Implementación real vs. anuncio: métricas de continuidad operativa."
        ],
        "NOTICIAS_CONSTRUCCION": [
            "Redefinición de frontera entre proyectos viables y teóricos.",
            "Compresión de plazos y riesgos en proyectos con capital anticipado.",
            "Cambios en reglas del juego que redefinen viabilidad real."
        ],
        "NOTICIAS_HIPOTECAS": [
            "Reconfiguración de acceso a crédito en próximos tramos del ciclo.",
            "Ajuste de posición de actores con ventaja operativa.",
            "Reprecificación de riesgo crediticio antes del consenso."
        ],
        "NOTICIAS_INMOBILIARIAS": [
            "Implementación efectiva vs. anuncio: métricas de continuidad operativa.",
            "Definición concreta de umbrales operativos (no solo adscripción).",
            "Ajuste de posición de actores clave antes del consenso."
        ]
    }
    
    if category and category in senales_templates:
        templates = senales_templates[category]
        num_senales = 2 + (seed % 3)  # 2-4 señales
        selected = []
        for i in range(num_senales):
            idx = (seed + i) % len(templates)
            selected.append(templates[idx])
        return selected[:4]
    
    # Fallback
    return [
        "Ajuste de posición de actores clave antes del consenso.",
        "Métricas de implementación efectiva vs. anuncio."
    ]


def _build_deck(title: str, hecho: str, category: Optional[str]) -> str:
    """
    Construye deck (subtítulo breve, 1 línea).
    """
    # Usar hecho pero más corto, o primera parte del título
    if len(hecho) <= 120:
        return hecho
    
    # Acortar hecho
    sentences = hecho.split('. ')
    if sentences:
        deck = sentences[0]
        if len(deck) > 120:
            words = deck.split()
            deck = ' '.join(words[:15])
        return deck + '.'
    
    # Fallback: título acortado
    title_clean = _clean_html(title)
    if len(title_clean) > 120:
        words = title_clean.split()
        return ' '.join(words[:15])
    return title_clean


def _build_disclaimer(source: Optional[str], url: Optional[str]) -> str:
    """
    Construye disclaimer de atribución (en inglés).
    """
    source_name = source or "the original source"
    url_text = f" Read the original article here: {url}." if url else ""
    
    return (
        f"Restructured by Althara from information published in {source_name}, "
        f"for analysis and signal reading purposes.{url_text}"
    )


def _build_instagram_structured(
    title: str,
    raw_summary: Optional[str],
    category: Optional[str],
    source: Optional[str],
    url: Optional[str],
    key_data: List[str],
    seed: int
) -> Dict[str, Any]:
    """
    Construye estructura completa de Instagram: hook, carousel, caption, cta.
    """
    # Hook (1 frase) - usar pregunta provocadora existente
    provocative_questions = {
        "PRECIOS_VIVIENDA": [
            "¿El precio comunica valor o solo VISIBILIDAD?",
            "¿Quién ajusta posición antes de que el consenso llegue?",
        ],
        "FONDOS_INVERSION_INMOBILIARIA": [
            "¿El capital sigue al consenso o lo anticipa?",
            "¿Quién tiene acceso al siguiente movimiento?",
        ],
        "NORMATIVAS_VIVIENDAS": [
            "¿La regulación reordena acceso o solo VISIBILIDAD?",
            "¿Quién conserva acceso operativo real?",
        ],
        "NOTICIAS_INMOBILIARIAS": [
            "¿El riesgo no es el acuerdo, sino la integración?",
            "¿Quién lee las señales antes del consenso?",
        ]
    }
    
    if category and category in provocative_questions:
        questions = provocative_questions[category]
        hook = questions[seed % len(questions)]
    else:
        hook = "¿El dato comunica valor o solo VISIBILIDAD?"
    
    # Carrusel slides (6-8 slides, 1 idea/slide, máximo 2 líneas)
    carousel_slides = _build_carousel_slides(
        title, raw_summary, category, key_data, seed
    )
    
    # Caption (100-180 palabras)
    caption = _build_instagram_caption(
        title, raw_summary, category, source, url, key_data, seed
    )
    
    # CTA (pregunta o "qué vigilar")
    cta = _build_instagram_cta(category, seed)
    
    return {
        "hook": hook,
        "carousel_slides": carousel_slides,
        "caption": caption,
        "cta": cta
    }


def _build_carousel_slides(
    title: str,
    raw_summary: Optional[str],
    category: Optional[str],
    key_data: List[str],
    seed: int
) -> List[str]:
    """
    Construye slides del carrusel (6-8 slides, 1 idea/slide, máximo 2 líneas).
    """
    slides = []
    
    # Slide 1: Título/contexto
    title_clean = _clean_html(title)
    if len(title_clean) > 80:
        words = title_clean.split()
        title_clean = ' '.join(words[:10])
    slides.append(title_clean)
    
    # Slide 2: Dato clave (si hay)
    if key_data:
        slides.append(f"Dato clave: {key_data[0]}")
    
    # Slide 3-5: Insights estratégicos
    strategic_points = _build_strategic_line(category)
    # Dividir en puntos
    sentences = re.split(r'[.!?]', strategic_points)
    for sentence in sentences[:3]:
        sentence = sentence.strip()
        if sentence and len(sentence) > 10:
            if len(sentence) > 100:
                words = sentence.split()
                sentence = ' '.join(words[:15])
            slides.append(sentence)
            if len(slides) >= 5:
                break
    
    # Slide 6-7: Implicaciones clave (breves)
    keywords = _extract_keywords(title, raw_summary)
    implicaciones = _build_implicaciones(category, key_data, keywords, seed)
    for impl in implicaciones[:2]:
        # Acortar a máximo 2 líneas
        if len(impl) > 120:
            words = impl.split()
            impl = ' '.join(words[:15])
        slides.append(impl)
        if len(slides) >= 7:
            break
    
    # Slide 8: Señal a vigilar
    senales = _build_senales_a_vigilar(category, key_data, keywords, seed)
    if senales:
        senal = senales[0]
        if len(senal) > 120:
            words = senal.split()
            senal = ' '.join(words[:15])
        slides.append(senal)
    
    # Asegurar 6-8 slides
    return slides[:8] if len(slides) >= 6 else slides + ["Vigilar implementación efectiva."] * (6 - len(slides))


def _build_instagram_caption(
    title: str,
    raw_summary: Optional[str],
    category: Optional[str],
    source: Optional[str],
    url: Optional[str],
    key_data: List[str],
    seed: int
) -> str:
    """
    Construye caption de Instagram (100-180 palabras).
    """
    caption_parts = []
    
    # Primera parte: contexto breve
    hecho = _build_hecho(title, raw_summary, key_data)
    if len(hecho) > 150:
        hecho = hecho[:150].rsplit('.', 1)[0] + '.'
    caption_parts.append(hecho)
    
    # Segunda parte: lectura Althara (breve)
    keywords = _extract_keywords(title, raw_summary)
    lectura = _build_lectura_althara(title, raw_summary, category, key_data, keywords, seed)
    # Acortar lectura para caption
    sentences = re.split(r'[.!?]', lectura)
    lectura_short = '. '.join(sentences[:2]) + '.' if len(sentences) >= 2 else lectura[:200]
    caption_parts.append(lectura_short)
    
    # Tercera parte: qué vigilar
    senales = _build_senales_a_vigilar(category, key_data, keywords, seed)
    if senales:
        vigilar_text = f"Qué vigilar: {senales[0].lower()}"
        caption_parts.append(vigilar_text)
    
    # Cuarta parte: fuente
    if source:
        caption_parts.append(f"Fuente: {source}")
    if url:
        caption_parts.append(url)
    
    caption = '\n\n'.join(caption_parts)
    
    # Asegurar 100-180 palabras (aprox 600-1100 caracteres)
    words = caption.split()
    if len(words) > 180:
        caption = ' '.join(words[:180])
    elif len(words) < 100:
        # Añadir más contenido si es muy corto
        if category:
            strategic = _build_strategic_line(category)
            caption += f"\n\n{strategic[:200]}"
    
    return caption


def _build_instagram_cta(category: Optional[str], seed: int) -> str:
    """
    Construye CTA (pregunta o "qué vigilar").
    """
    cta_templates = [
        "¿Qué señal te parece más determinante?",
        "¿Qué vigilar ahora?",
        "¿Qué cambia realmente?",
        "¿Quién lee las señales antes del consenso?",
        "¿Qué umbral es crítico aquí?"
    ]
    
    return cta_templates[seed % len(cta_templates)]


def _build_qa(
    key_data: List[str],
    keywords: List[str],
    raw_summary: Optional[str],
    title: str
) -> Dict[str, List[str]]:
    """
    Construye QA: facts_used y unknown_or_missing.
    Verifica que los datos extraídos estén en el texto original.
    """
    facts_used = []
    unknown_or_missing = []
    
    # Verificar que key_data esté en el texto original
    full_text = (title + " " + (raw_summary or "")).lower()
    
    for data in key_data:
        # Limpiar el dato para buscar
        data_clean = re.sub(r'[^\w\s]', '', data.lower())
        if data_clean in full_text or any(word in full_text for word in data_clean.split() if len(word) > 3):
            facts_used.append(data)
        else:
            unknown_or_missing.append(f"Dato no verificado en fuente: {data}")
    
    # Añadir keywords relevantes a facts_used
    if keywords:
        facts_used.extend([f"Término clave: {kw}" for kw in keywords[:3]])
    
    # Si no hay datos verificados, indicarlo
    if not facts_used:
        facts_used.append("Información extraída del título y resumen general")
    
    # Indicar qué podría faltar según la categoría
    if not key_data:
        unknown_or_missing.append("Datos numéricos específicos no presentes en la fuente")
    
    return {
        "facts_used": facts_used[:10],  # Máximo 10
        "unknown_or_missing": unknown_or_missing[:5]  # Máximo 5
    }


def build_all_content_structured(
    title: str,
    raw_summary: Optional[str],
    category: Optional[str],
    source: Optional[str] = None,
    url: Optional[str] = None,
    published_at: Optional[datetime] = None,
    seed: Optional[int] = None,
) -> tuple[str, str, Dict[str, Any]]:
    """
    Genera TODO: resumen legacy, post legacy, Y contenido estructurado JSON.
    
    Returns:
        Tuple (althara_summary, instagram_post, structured_content_dict)
    """
    # Generar contenido legacy (compatibilidad)
    althara_summary, instagram_post = build_all_content(
        title, raw_summary, category, source, url, seed
    )
    
    # Generar contenido estructurado
    structured = build_structured_content(
        title, raw_summary, category, source, url, published_at, seed
    )
    
    return althara_summary, instagram_post, structured
