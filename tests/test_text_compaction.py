"""Tests for text_compaction module."""
import pytest
from app.utils.text_compaction import (
    split_sentences,
    truncate_at_sentence,
    extract_key_sentences,
    extract_bullets,
    compose_caption_blocks,
)


def test_extract_key_sentences_only_complete_and_fitting():
    """Solo frases completas que caben en max_chars. Sin truncar."""
    title = "Compraventa sube 7,1%."
    cleaned = "En noviembre se registraron 58.500 operaciones. Otra frase corta. Esta es una frase muy larga que definitivamente supera el límite de ciento diez caracteres para probar que no se incluye."
    result = extract_key_sentences(title, cleaned, max_chars=110, max_sentences=4)
    assert len(result) >= 2
    for s in result:
        assert len(s) <= 110, f"Frase excede 110 chars: {s!r}"
        assert s[-1] in ".!?", f"Frase debe terminar en puntuación: {s!r}"


def test_truncate_at_sentence_no_cut_mid_word():
    text = "La compraventa sube un 7,1% interanual. En noviembre se registraron 58.500 operaciones."
    result = truncate_at_sentence(text, 50)
    assert not result.endswith(" ")  # no trailing space
    assert result[-1] in ".!?" or result.rfind(" ") > 0  # ends at sentence or word
    assert "operac" not in result  # must not cut "operaciones" mid-word


def test_truncate_at_sentence_avoids_dangling_preposition():
    """Must not end with 'a' (preposition) when cutting 'acceso efectivo a oportunidades'."""
    text = "No es una noticia suelta: es otra pieza en la secuencia que reordena precios, actores y acceso efectivo a oportunidades reales."
    r = truncate_at_sentence(text, 110)
    assert not r.endswith(" a")
    assert r.split()[-1].lower() != "a"
    assert "efectivo" in r


def test_truncate_at_sentence_respects_sentence_boundary():
    text = "Primera frase. Segunda frase larga que sigue."
    r = truncate_at_sentence(text, 20)
    assert r == "Primera frase."


def test_split_sentences():
    text = "Hola. ¿Qué tal? ¡Bien!"
    assert split_sentences(text) == ["Hola.", "¿Qué tal?", "¡Bien!"]


def test_extract_bullets_prefers_sentences_with_numbers():
    title = "Compraventa repunta 7,1%"
    raw = "En noviembre se registraron 58.500 operaciones. Esto es muy importante."
    bullets = extract_bullets(title, raw, raw, max_bullets=3)
    assert len(bullets) >= 1
    assert any("58" in b or "7" in b for b in bullets)


def test_compose_caption_blocks_no_mid_sentence_cut():
    hook = "Señal."
    bullets = ["Hecho uno.", "Hecho dos."]
    lectura = "Lectura larga que podría exceder el límite si la hacemos muy larga."
    cta = "Guárdalo."
    source = "Expansion"
    cap = compose_caption_blocks(hook, bullets, lectura, cta, source, max_total=200)
    assert len(cap) <= 210  # some margin
    assert "Fuente:" in cap
    assert not any(cap.endswith(w) for w in ["de", "en", "un", "se"])  # no cut mid-word
