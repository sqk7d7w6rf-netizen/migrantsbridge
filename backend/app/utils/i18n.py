"""Simple internationalization helper with JSON language file support."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Base directory for translation files
TRANSLATIONS_DIR = Path(__file__).parent.parent / "translations"

# In-memory translation cache: {language_code: {key: translation}}
_cache: dict[str, dict[str, str]] = {}

# Default translations (English) built-in as fallback
_DEFAULT_TRANSLATIONS: dict[str, str] = {
    "welcome": "Welcome to MigrantsBridge",
    "appointment.reminder": "You have an appointment on {date} at {time}",
    "appointment.confirmed": "Your appointment has been confirmed",
    "appointment.cancelled": "Your appointment has been cancelled",
    "case.opened": "Your case #{case_number} has been opened",
    "case.updated": "Your case #{case_number} has been updated",
    "case.closed": "Your case #{case_number} has been closed",
    "document.uploaded": "Document '{document_name}' has been uploaded successfully",
    "document.verified": "Document '{document_name}' has been verified",
    "document.rejected": "Document '{document_name}' requires attention",
    "invoice.created": "Invoice #{invoice_number} has been created",
    "invoice.payment_received": "Payment received for invoice #{invoice_number}",
    "intake.submitted": "Your intake form has been submitted successfully",
    "intake.approved": "Your intake submission has been approved",
    "intake.needs_info": "Additional information needed for your intake submission",
    "task.assigned": "Task '{task_title}' has been assigned to you",
    "task.due_soon": "Task '{task_title}' is due on {due_date}",
    "general.error": "An error occurred. Please try again or contact support.",
    "general.success": "Operation completed successfully",
}


def load_language(language_code: str) -> dict[str, str]:
    """Load translations for a language code from JSON file or return defaults."""
    if language_code in _cache:
        return _cache[language_code]

    if language_code == "en":
        _cache["en"] = _DEFAULT_TRANSLATIONS.copy()
        return _cache["en"]

    translations_file = TRANSLATIONS_DIR / f"{language_code}.json"
    if translations_file.exists():
        try:
            with open(translations_file, "r", encoding="utf-8") as f:
                translations = json.load(f)
            _cache[language_code] = translations
            return translations
        except (json.JSONDecodeError, OSError):
            logger.warning("Failed to load translations for %s", language_code)

    # Fallback to English
    return load_language("en")


def translate(key: str, language: str = "en", **kwargs: Any) -> str:
    """Translate a key to the given language, with optional string formatting.

    Args:
        key: The translation key (e.g., "appointment.reminder").
        language: ISO 639-1 language code (default "en").
        **kwargs: Format parameters for the translation string.

    Returns:
        The translated and formatted string.
    """
    translations = load_language(language)
    template = translations.get(key)

    if template is None:
        # Fallback to English if key not found in target language
        if language != "en":
            en_translations = load_language("en")
            template = en_translations.get(key)

    if template is None:
        logger.warning("Missing translation key: %s (language=%s)", key, language)
        return key

    try:
        return template.format(**kwargs) if kwargs else template
    except (KeyError, IndexError):
        logger.warning("Translation format error for key=%s, kwargs=%s", key, kwargs)
        return template


def clear_cache() -> None:
    """Clear the translation cache (useful for testing or reloading)."""
    _cache.clear()


def get_available_languages() -> list[str]:
    """Return list of available language codes."""
    languages = ["en"]
    if TRANSLATIONS_DIR.exists():
        for f in TRANSLATIONS_DIR.glob("*.json"):
            lang = f.stem
            if lang not in languages:
                languages.append(lang)
    return sorted(languages)
