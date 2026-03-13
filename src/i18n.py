"""
Internationalization (i18n) manager.
Loads translation strings from JSON files in resources/i18n/.
Supports runtime language switching.
"""

import json
import os

# Path to i18n resource directory (relative to project root)
_I18N_DIR = os.path.join(os.path.dirname(__file__), "..", "resources", "i18n")


class I18nManager:
    """Manages UI translation strings with runtime language switching."""

    def __init__(self, default_lang: str = "vi"):
        self._current_lang = default_lang
        self._strings: dict[str, str] = {}
        self._fallback: dict[str, str] = {}
        # Load Vietnamese as fallback (always available)
        self._fallback = self._load_lang("vi")
        # Load the requested language
        self._strings = self._load_lang(default_lang)

    def _load_lang(self, lang_code: str) -> dict[str, str]:
        """Load translation strings from a JSON file."""
        file_path = os.path.join(_I18N_DIR, f"{lang_code}.json")
        if not os.path.exists(file_path):
            return {}
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def set_language(self, lang_code: str) -> None:
        """Switch the active UI language."""
        self._current_lang = lang_code
        self._strings = self._load_lang(lang_code)

    @property
    def current_language(self) -> str:
        """Return current language code."""
        return self._current_lang

    def t(self, key: str, **kwargs) -> str:
        """
        Get translated string by key.
        Falls back to Vietnamese if key not found in current language.
        Supports {placeholder} formatting via kwargs.
        """
        text = self._strings.get(key) or self._fallback.get(key, key)
        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, ValueError):
                pass
        return text
