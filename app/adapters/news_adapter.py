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
