"""
Internationalization (i18n) manager.
Loads translation strings from JSON files in resources/i18n/.
Supports runtime language switching with preference persistence.
"""

import json
import os

# Path to i18n resource directory (relative to project root)
_I18N_DIR = os.path.join(os.path.dirname(__file__), "..", "resources", "i18n")

# Path to user config file for persisting preferences
_CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".ai-translate")
_CONFIG_FILE = os.path.join(_CONFIG_DIR, "config.json")


class I18nManager:
    """Manages UI translation strings with runtime language switching."""

    def __init__(self, default_lang: str = "vi"):
        # Try to load saved language preference
        saved_lang = self._load_saved_language()
        self._current_lang = saved_lang or default_lang

        self._strings: dict[str, str] = {}
        self._fallback: dict[str, str] = {}
        # Load Vietnamese as fallback (always available)
        self._fallback = self._load_lang("vi")
        # Load the requested language
        self._strings = self._load_lang(self._current_lang)

    def _load_lang(self, lang_code: str) -> dict[str, str]:
        """Load translation strings from a JSON file."""
        file_path = os.path.join(_I18N_DIR, f"{lang_code}.json")
        if not os.path.exists(file_path):
            return {}
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def set_language(self, lang_code: str) -> None:
        """Switch the active UI language and persist the choice."""
        self._current_lang = lang_code
        self._strings = self._load_lang(lang_code)
        self._save_language(lang_code)

    def _load_saved_language(self) -> str | None:
        """Load previously saved language preference from config file."""
        try:
            if os.path.exists(_CONFIG_FILE):
                with open(_CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
                return config.get("language")
        except (json.JSONDecodeError, OSError):
            pass
        return None

    def _save_language(self, lang_code: str) -> None:
        """Persist language preference to config file."""
        try:
            config = {}
            if os.path.exists(_CONFIG_FILE):
                with open(_CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
            config["language"] = lang_code
            os.makedirs(_CONFIG_DIR, exist_ok=True)
            with open(_CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except OSError:
            pass  # Non-critical: preference just won't persist

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
