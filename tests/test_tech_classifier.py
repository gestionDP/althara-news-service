"""Tests for tech classifier."""
import pytest
from app.tech.classifier import infer_category, extract_tags, compute_relevance_score
from app.constants_tech import TechNewsCategory


def test_infer_category_ai_ml():
    assert infer_category("OpenAI lanza GPT-5") == TechNewsCategory.AI_ML
    assert infer_category("Machine learning aplicado a salud") == TechNewsCategory.AI_ML


def test_infer_category_release():
    assert infer_category("Google lanza nueva versión beta de Chrome") == TechNewsCategory.RELEASE_UPDATE


def test_infer_category_research():
    assert infer_category("Estudio de MIT sobre robots") == TechNewsCategory.RESEARCH


def test_infer_category_startups():
    assert infer_category("Startup española levanta serie A") == TechNewsCategory.STARTUPS


def test_extract_tags():
    tags = extract_tags("OpenAI y Microsoft colaboran en IA")
    assert "ai" in tags or "ia" in tags or len(tags) > 0


def test_compute_relevance_score():
    s = compute_relevance_score("IA avanza", "machine learning", "AI_ML", "TechCrunch")
    assert 50 <= s <= 100


def test_compute_relevance_score_baseline():
    s = compute_relevance_score("Noticia genérica", "texto", "OTHER_TECH", "Source")
    assert 0 <= s <= 100
