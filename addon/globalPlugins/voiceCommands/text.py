# -*- coding: UTF-8 -*-
"""Language-aware text helpers shared by the add-on."""
import re

import languageHandler


def _turkic_casing():
    """Turkish and Azeri lowercase "I" to a dotless "ı" (and "İ" to "i"); other languages do not."""
    try:
        return languageHandler.getLanguage().replace("-", "_").split("_")[0].lower() in ("tr", "az")
    except Exception:
        return False


def lower(text):
    if _turkic_casing():
        text = text.replace("İ", "i").replace("I", "ı")
    return text.lower()


def normalize(text):
    """Lowercase, drop punctuation and collapse whitespace, so spoken text and descriptions compare equal."""
    text = re.sub(r"[^\w\s]", " ", lower(text))
    return re.sub(r"\s+", " ", text).strip()
