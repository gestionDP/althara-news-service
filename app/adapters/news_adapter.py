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
    También elimina metadatos como autores, fechas, botones de compartir, etc.
    Maneja correctamente la codificación UTF-8 y las entidades HTML.
    
    Args:
        text: Texto que puede contener HTML
        
    Returns:
        Texto limpio sin tags HTML ni entidades HTML, con codificación correcta
    """
    if not text:
        return ""
    
    # Asegurar que el texto está en UTF-8
    if isinstance(text, bytes):
        try:
            text = text.decode('utf-8')
        except UnicodeDecodeError:
            try:
                text = text.decode('latin-1')
            except UnicodeDecodeError:
                text = text.decode('utf-8', errors='replace')
    
    # Convertir entidades HTML a caracteres normales (&amp; -> &, &aacute; -> á, etc.)
    # html.unescape maneja entidades estándar, pero también necesitamos manejar casos especiales
    text = html.unescape(text)
    
    # Decodificar entidades HTML adicionales que html.unescape podría no manejar
    # Reemplazar entidades comunes manualmente si es necesario
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")
    text = text.replace('&nbsp;', ' ')
    
    # Remover tags HTML (ej: <p>, <a href="...">, etc.)
    # Regex: <[^>]+> busca cualquier cosa entre < y >
    text = re.sub(r'<[^>]+>', '', text)
    
    # Eliminar metadatos comunes de artículos
    # Patrones para eliminar: "AUTOR FECHA - HORA", "Compartir en...", etc.
    patterns_to_remove = [
        r'[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]+\s+\d{1,2}\s+[A-Z]{3}\.\s+\d{4}\s*-\s*\d{2}:\d{2}',  # "BEATRIZ AMIGOT 27 NOV. 2025 - 09:39"
        r'Compartir en (Facebook|Twitter|LinkedIn|WhatsApp)',  # Botones de compartir
        r'Enviar por email',
        r'DREAMSTIME|GETTY|SHUTTERSTOCK|ISTOCK',  # Fuentes de imágenes
        r'EXPANSION|EL PAÍS|CINCO DÍAS',  # Nombres de medios repetidos
        r'Vistas del|Imagen de|Foto de',  # Descripciones de imágenes
        r'\b\d{1,2}\s+[A-Z]{3}\.\s+\d{4}\s*-\s*\d{2}:\d{2}\b',  # Fechas sueltas
        r'Periodista y Coordinadora editorial',  # Cargos editoriales
        r'\d{2}/\d{2}/\d{4}',  # Fechas en formato DD/MM/YYYY
    ]
    
    for pattern in patterns_to_remove:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Eliminar líneas que solo contienen mayúsculas (títulos de sección)
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        # Si la línea tiene más de 3 palabras en mayúsculas consecutivas, probablemente es un título
        if not re.match(r'^[A-ZÁÉÍÓÚÑ\s]{20,}$', line):
            cleaned_lines.append(line)
    text = ' '.join(cleaned_lines)
    
    # Limpiar caracteres de reemplazo Unicode () - estos indican problemas de codificación
    # Intentar reparar caracteres comunes mal codificados
    text = text.replace('\ufffd', '')  # Eliminar caracteres de reemplazo Unicode
    text = text.replace('', '')  # Eliminar caracteres de reemplazo si están presentes
    
    # Reparar caracteres acentuados comunes que se hayan perdido por problemas de codificación
    # Patrones comunes donde se pierden acentos en español
    accent_fixes = [
        (r'\bneuropsicloga\b', 'neuropsicóloga'),
        (r'\bMnica\b', 'Mónica'),
        (r'\bcientfica\b', 'científica'),
        (r'\bdcadas\b', 'décadas'),
        (r'\bmbito\b', 'ámbito'),
        (r'\bpsicloga\b', 'psicóloga'),
        (r'\beducacin\b', 'educación'),
        (r'\bdiseñar\b', 'diseñar'),  # Ya está bien, pero por si acaso
        (r'\bsegn\b', 'según'),
        (r'\bcmo\b', 'cómo'),
        (r'\bqu\b', 'qué'),
        (r'\bdnde\b', 'dónde'),
        (r'\bcuando\b', 'cuándo'),  # Solo si está en contexto de pregunta
        (r'\barchitectura\b', 'arquitectura'),  # Por si viene en inglés
    ]
    
    for pattern, replacement in accent_fixes:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Reparar palabras comunes sin acento (solo si no tienen acento y deberían tenerlo)
    # Esto es más conservador - solo repara casos muy comunes
    common_fixes = {
        'psicologa': 'psicóloga',
        'psicologo': 'psicólogo',
        'arquitecta': 'arquitecta',  # Ya está bien
        'arquitecto': 'arquitecto',  # Ya está bien
        'educacion': 'educación',
        'especializada': 'especializada',  # Ya está bien
        'especializado': 'especializado',  # Ya está bien
    }
    
    # Solo aplicar si la palabra está sola (no como parte de otra palabra)
    for wrong, correct in common_fixes.items():
        text = re.sub(r'\b' + wrong + r'\b', correct, text, flags=re.IGNORECASE)
    
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
    Extrae palabras clave relevantes y coherentes del título y raw_summary.
    Se enfoca en términos inmobiliarios, ubicaciones y conceptos clave.
    
    Args:
        title: Título de la noticia
        raw_summary: Resumen original (opcional)
        
    Returns:
        Lista de palabras clave relevantes (máximo 6-8)
    """
    # Palabras comunes a excluir (ampliado)
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
    
    # Términos inmobiliarios relevantes (prioridad alta)
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
    
    # Ubicaciones importantes (prioridad media)
    locations = {
        'madrid', 'barcelona', 'valencia', 'sevilla', 'bilbao', 'zaragoza',
        'málaga', 'murcia', 'palma', 'las palmas', 'granada', 'alicante',
        'valladolid', 'córdoba', 'vigo', 'gijón', 'hospitalet', 'vitoria',
        'castilla', 'león', 'andalucía', 'cataluña', 'comunidad valenciana',
        'galicia', 'país vasco', 'asturias', 'cantabria', 'navarra',
        'españa', 'español', 'europa', 'europeo',
    }
    
    # Combinar y limpiar texto
    combined_text = title.lower()
    if raw_summary:
        cleaned = _clean_html(raw_summary).lower()
        combined_text += " " + cleaned
    
    # Extraer palabras (solo palabras de 4+ caracteres)
    words = re.findall(r'\b[a-záéíóúñü]{4,}\b', combined_text)
    
    # Contar frecuencia de palabras para priorizar las más relevantes
    word_freq = {}
    for word in words:
        if word not in stop_words:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Filtrar y priorizar
    keywords = []
    seen = set()
    
    # Prioridad 1: Términos inmobiliarios (más relevantes)
    for word in sorted(word_freq.keys(), key=lambda x: word_freq[x], reverse=True):
        if word in real_estate_terms and word not in seen:
            keywords.append(word)
            seen.add(word)
            if len(keywords) >= 5:
                break
    
    # Prioridad 2: Ubicaciones
    if len(keywords) < 8:
        for word in sorted(word_freq.keys(), key=lambda x: word_freq[x], reverse=True):
            if word in locations and word not in seen:
                keywords.append(word)
                seen.add(word)
                if len(keywords) >= 8:
                    break
    
    # Prioridad 3: Conceptos clave (sustantivos importantes)
    if len(keywords) < 8:
        for word in sorted(word_freq.keys(), key=lambda x: word_freq[x], reverse=True):
            if word not in seen and len(word) >= 5:
                # Priorizar sustantivos (terminaciones comunes en español)
                if any(word.endswith(suffix) for suffix in ['ción', 'sión', 'dad', 'tad', 'tud', 'aje', 'ismo', 'miento']):
                    keywords.append(word)
                    seen.add(word)
                    if len(keywords) >= 8:
                        break
    
    # Si aún no tenemos suficientes, añadir palabras más frecuentes
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
    Construye el contenido completo de la noticia, limpiando metadatos pero manteniendo
    toda la información relevante. No recorta el contenido, solo lo limpia.
    
    Args:
        title: Título de la noticia
        raw_summary: Resumen original (opcional)
        
    Returns:
        Contenido completo limpio de la noticia
    """
    if not raw_summary:
        return title.strip()
    
    # Limpiar el resumen (elimina HTML, metadatos, etc.)
    cleaned_summary = _clean_html(raw_summary)
    
    # Eliminar repeticiones del título al inicio del resumen
    title_lower = title.lower().strip()
    cleaned_lower = cleaned_summary.lower().strip()
    
    # Si el resumen empieza con el título completo, eliminarlo
    if cleaned_lower.startswith(title_lower):
        cleaned_summary = cleaned_summary[len(title):].strip()
        # Eliminar puntos, comas y espacios al inicio
        cleaned_summary = re.sub(r'^[.,\s]+', '', cleaned_summary)
    
    # También buscar si el título aparece como frase completa más adelante y eliminarlo
    # Esto maneja casos donde el título se repite en medio del texto
    title_words = title_lower.split()
    if len(title_words) > 3:
        # Buscar la primera parte del título (primeras 4-5 palabras)
        title_start = ' '.join(title_words[:min(5, len(title_words))])
        # Si aparece al inicio del texto limpio, eliminarlo
        if cleaned_lower.startswith(title_start):
            # Encontrar dónde termina esta repetición
            idx = cleaned_summary.lower().find(title_start)
            if idx == 0:
                # Avanzar hasta después de la repetición
                remaining = cleaned_summary[len(title_start):].strip()
                # Buscar el siguiente punto o espacio significativo
                next_space = remaining.find(' ')
                if next_space > 0:
                    cleaned_summary = remaining[next_space:].strip()
                else:
                    cleaned_summary = remaining
                cleaned_summary = re.sub(r'^[.,\s]+', '', cleaned_summary)
    
    # Eliminar repeticiones de frases comunes al inicio
    words = cleaned_summary.split()
    if len(words) > 15:
        # Buscar si las primeras 3-5 palabras se repiten más adelante
        for i in range(3, min(8, len(words))):
            first_phrase = ' '.join(words[:i]).lower()
            # Buscar si esta frase aparece más adelante (después de la posición i)
            remaining_text = ' '.join(words[i:]).lower()
            if first_phrase in remaining_text:
                # Eliminar la primera ocurrencia
                cleaned_summary = ' '.join(words[i:])
                break
    
    # Eliminar frases de sección repetidas (ej: "Mercado Inmobiliario")
    section_phrases = ['mercado inmobiliario', 'noticias inmobiliarias', 'economía inmobiliaria']
    for phrase in section_phrases:
        # Eliminar si aparece al inicio
        if cleaned_summary.lower().startswith(phrase):
            cleaned_summary = cleaned_summary[len(phrase):].strip()
            cleaned_summary = re.sub(r'^[.,\s]+', '', cleaned_summary)
    
    # Eliminar repeticiones completas del texto (si el texto se repite palabra por palabra)
    words = cleaned_summary.split()
    if len(words) > 20:
        # Buscar si las primeras 10 palabras aparecen duplicadas más adelante
        first_10_words = ' '.join(words[:10]).lower()
        # Buscar esta frase en el resto del texto
        remaining_text = ' '.join(words[10:]).lower()
        if first_10_words in remaining_text:
            # Encontrar dónde termina la primera ocurrencia
            idx = remaining_text.find(first_10_words)
            if idx > 0:
                # Mantener solo hasta donde empieza la repetición
                cleaned_summary = ' '.join(words[:10 + idx // 2])  # Aproximado
            else:
                # Si está al inicio, eliminar la primera ocurrencia
                cleaned_summary = ' '.join(words[10:])
    
    # Combinar título y contenido
    combined = f"{title.strip()}. {cleaned_summary}"
    
    # Formatear en párrafos legibles: dividir por puntos seguidos de espacio
    # Dividir en oraciones (por puntos, signos de exclamación o interrogación)
    sentences = re.split(r'([.!?])\s+', combined)
    
    # Reconstruir oraciones con sus signos de puntuación
    reconstructed_sentences = []
    for i in range(0, len(sentences) - 1, 2):
        if i + 1 < len(sentences):
            sentence = sentences[i] + sentences[i + 1]
            sentence = sentence.strip()
            if sentence:
                reconstructed_sentences.append(sentence)
    
    # Si no se pudieron dividir bien, usar el método simple
    if not reconstructed_sentences:
        sentences = re.split(r'\.\s+', combined)
        reconstructed_sentences = [s.strip() + '.' for s in sentences if s.strip()]
    
    # Agrupar oraciones en párrafos de 2-3 oraciones cada uno para mejor legibilidad
    paragraphs = []
    current_paragraph = []
    
    for sentence in reconstructed_sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # Asegurar que termina con puntuación
        if not sentence.endswith(('.', '!', '?', '…')):
            sentence += '.'
        
        current_paragraph.append(sentence)
        
        # Crear párrafo cada 2-3 oraciones, o si la oración es muy larga (>120 chars)
        if len(current_paragraph) >= 3 or (len(sentence) > 120 and len(current_paragraph) >= 2):
            paragraphs.append(' '.join(current_paragraph))
            current_paragraph = []
    
    # Añadir el último párrafo si tiene contenido
    if current_paragraph:
        paragraphs.append(' '.join(current_paragraph))
    
    # Si no se pudieron crear párrafos (texto muy corto), devolver tal cual pero formateado
    if not paragraphs:
        # Limitar solo si es extremadamente largo
        if len(combined) > 5000:
            truncated = combined[:5000]
            last_period = truncated.rfind('. ')
            if last_period > 4500:
                combined = combined[:last_period + 1] + "…"
            else:
                combined = truncated + "…"
        return combined
    
    # Unir párrafos con doble salto de línea para mejor legibilidad
    formatted_text = '\n\n'.join(paragraphs)
    
    # Limitar solo si es extremadamente largo (más de 5000 caracteres)
    if len(formatted_text) > 5000:
        # Mantener párrafos completos hasta el límite
        truncated_paragraphs = []
        total_length = 0
        for para in paragraphs:
            if total_length + len(para) + 2 > 5000:  # +2 por el salto de línea
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
    
    # 1. CONTENIDO COMPLETO (formateado en párrafos)
    full_content = _build_extended_summary(title, raw_summary)
    sections.append("📊 CONTENIDO")
    sections.append("")
    sections.append(full_content)
    sections.append("")
    sections.append("")  # Línea en blanco adicional para separación
    
    # 2. ANÁLISIS ALTHARA
    strategic_line = _build_strategic_line(category)
    sections.append("💡 ANÁLISIS ALTHARA")
    sections.append("")
    sections.append(strategic_line)
    sections.append("")
    sections.append("")  # Línea en blanco adicional
    
    # 3. DATOS CLAVE
    key_data = _extract_key_data(raw_summary)
    if key_data:
        sections.append("📈 DATOS CLAVE")
        sections.append("")
        for data in key_data:
            sections.append(f"• {data}")
        sections.append("")
        sections.append("")  # Línea en blanco adicional
    
    # 4. PALABRAS CLAVE
    keywords = _extract_keywords(title, raw_summary)
    if keywords:
        sections.append("🔑 PALABRAS CLAVE")
        sections.append("")
        keywords_str = " • ".join(keywords)
        sections.append(keywords_str)
    
    return "\n".join(sections)
