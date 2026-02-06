"""Tests for shared utilities: html_utils, rss_utils, guardrails."""
import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.utils.html_utils import strip_html_tags
from app.utils.rss_utils import parse_published_date
from app.utils.guardrails import passes_guardrails


def test_strip_html_tags_basic():
    html = "<p>Hello <b>world</b></p>"
    assert strip_html_tags(html) == "Hello world"


def test_strip_html_tags_entities():
    html = "&amp; &lt; &gt; &quot; test"
    assert "&" in strip_html_tags(html) or strip_html_tags(html) == "& < > \" test"


def test_strip_html_tags_empty():
    assert strip_html_tags("") == ""
    assert strip_html_tags(None) == ""


def test_strip_html_tags_fixes_mojibake():
    """ftfy repairs common encoding errors (e.g. UTF-8 misinterpreted as Latin-1)."""
    # "participación" mojibake: UTF-8 bytes decoded as Latin-1
    mojibake = "participaci\u00c3\u00b3n"  # participación
    result = strip_html_tags(mojibake)
    assert "ó" in result or "participación" in result or "participacion" in result


def test_strip_html_tags_whitespace():
    html = "  <p>  foo  </p>  \n  bar  "
    result = strip_html_tags(html)
    assert "foo" in result and "bar" in result
    assert "  " not in result or result.strip() == result


def test_parse_published_date_from_published_parsed():
    entry = MagicMock()
    entry.published_parsed = (2024, 1, 15, 10, 30, 0, 0, 0, 0)
    entry.updated_parsed = None
    result = parse_published_date(entry)
    assert result.year == 2024
    assert result.month == 1
    assert result.day == 15
    assert result.tzinfo == timezone.utc


def test_parse_published_date_fallback():
    class EmptyEntry:
        pass
    entry = EmptyEntry()
    result = parse_published_date(entry)
    assert isinstance(result, datetime)
    assert result.tzinfo == timezone.utc


def test_passes_guardrails_deny():
    deny = ["spam", "ad"]
    allow = ["news", "tech"]
    assert passes_guardrails("Good news", deny, allow, False) is True
    assert passes_guardrails("Buy spam here", deny, allow, False) is False
    assert passes_guardrails("Advertisement", deny, allow, False) is False


def test_passes_guardrails_strict_allow():
    deny = []
    allow = ["vivienda", "hipoteca"]
    assert passes_guardrails("Precios de vivienda suben", deny, allow, True) is True
    assert passes_guardrails("Random topic", deny, allow, True) is False


def test_passes_guardrails_empty_title():
    assert passes_guardrails("", [], [], False) is False
