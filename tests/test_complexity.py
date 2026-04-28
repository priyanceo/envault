"""Tests for envault.complexity module."""

import pytest
from envault.complexity import score_secret, enforce_complexity, ComplexityResult


def test_short_value_is_weak():
    result = score_secret("abc")
    assert result.level == "weak"
    assert result.passed is False
    assert result.score <= 1


def test_strong_value_scores_high():
    result = score_secret("MyStr0ng!P@ssword99")
    assert result.score == 4
    assert result.level == "strong"
    assert result.passed is True
    assert result.suggestions == []


def test_digits_only_suggests_letters_and_specials():
    result = score_secret("12345678")
    tips = " ".join(result.suggestions)
    assert "uppercase" in tips.lower() or "lowercase" in tips.lower()
    assert "special" in tips.lower()


def test_no_digit_suggestion():
    result = score_secret("abcdefghABCDEFGH")
    tips = " ".join(result.suggestions)
    assert "digit" in tips.lower()


def test_no_special_char_suggestion():
    result = score_secret("Abcdefgh1")
    tips = " ".join(result.suggestions)
    assert "special" in tips.lower()


def test_score_capped_at_four():
    result = score_secret("A" * 20 + "a1!")
    assert result.score <= 4


def test_enforce_complexity_passes_good_value():
    # Should not raise
    enforce_complexity("G00dP@ssword!", min_score=2)


def test_enforce_complexity_raises_on_weak_value():
    with pytest.raises(ValueError, match="too weak"):
        enforce_complexity("abc", min_score=2)


def test_enforce_complexity_custom_min_score():
    # Score 1 value: long enough but only one category met
    with pytest.raises(ValueError):
        enforce_complexity("abcdefgh", min_score=3)


def test_fair_level():
    # 8+ chars + mixed case = score 2 = fair
    result = score_secret("Abcdefgh")
    assert result.level == "fair"
    assert result.score == 2


def test_good_level():
    result = score_secret("Abcdefg1")
    assert result.level == "good"
    assert result.score == 3


def test_custom_min_length():
    result = score_secret("Ab1!", min_length=4)
    assert result.passed is True
