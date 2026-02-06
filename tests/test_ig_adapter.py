"""Tests for IG adapter."""
import pytest
from app.adapters.ig_adapter import (
    generate_ig_draft,
    generate_variants,
    BODY_MAX,
    SLIDES_COUNT,
    OXONO_HASHTAGS_MIN,
    OXONO_HASHTAGS_MAX,
)


def test_generate_ig_draft_tech(sample_tech_news):
    draft = generate_ig_draft(sample_tech_news, brand="oxono")
    assert draft["hook"]
    assert len(draft["carousel_slides"]) == SLIDES_COUNT
    for slide in draft["carousel_slides"]:
        assert "title" in slide and "body" in slide
        assert len(slide["body"]) <= BODY_MAX
    assert draft["source_line"]
    assert draft["disclaimer"]
    assert OXONO_HASHTAGS_MIN <= len(draft["hashtags"]) <= OXONO_HASHTAGS_MAX
    assert len(draft["caption"]) >= 100


def test_generate_ig_draft_real_estate(sample_real_estate_news):
    draft = generate_ig_draft(sample_real_estate_news, brand="althara")
    assert draft["hook"]
    assert len(draft["carousel_slides"]) == SLIDES_COUNT
    assert draft["source_line"]
    assert draft["disclaimer"]


def test_generate_variants(sample_tech_news):
    variants = generate_variants(sample_tech_news, n=3, brand="oxono")
    assert len(variants) == 3
    for v in variants:
        assert len(v["carousel_slides"]) == SLIDES_COUNT
