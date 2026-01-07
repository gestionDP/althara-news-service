"""
Adapter to transform news to Althara tone.

Converts raw news (raw_summary) into content adapted to Althara's
analytical and professional style for social media use.
"""
from __future__ import annotations

import re
import html
from datetime import datetime
from textwrap import shorten
from typing import Optional, List

ALTHARA_CLOSERS = [
    "Lo relevante no es el titular, sino quién ajusta posición antes de que el consenso llegue.",
    "La oportunidad aparece en el desfase entre el dato y la reacción del mercado visible.",
    "Donde el mercado ve ruido, Althara sólo registra el punto exacto del desplazamiento.",
    "Aquí importa menos el precio comunicado y más quién tiene acceso al siguiente movimiento.",
]


def _clean_html(text: str) -> str:
    """
    Cleans HTML from text, extracting only pure text content.
    Also removes metadata like authors, dates, share buttons, etc.
    Handles UTF-8 encoding and HTML entities correctly.
    
    Args:
        text: Text that may contain HTML
        
    Returns:
        Clean text without HTML tags or entities, with correct encoding
    """
    if not text:
        return ""
    
    if isinstance(text, bytes):
        try:
            text = text.decode('utf-8')
        except UnicodeDecodeError:
            try:
                text = text.decode('latin-1')
            except UnicodeDecodeError:
                text = text.decode('utf-8', errors='replace')
    
    text = html.unescape(text)
    
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")
    text = text.replace('&nbsp;', ' ')
    
    text = re.sub(r'<[^>]+>', '', text)
    
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
