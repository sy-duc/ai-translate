"""
Constants used across the application.
Defines domains, styles, engines, languages and app metadata.
"""

APP_NAME = "AI Translate"
APP_VERSION = "0.1.0"
APP_AUTHOR = "AI Translate Team"

# --- Supported UI languages (for interface display) ---
UI_LANGUAGES = [
    ("vi", "Tiếng Việt"),
    ("en", "English"),
    ("ja", "日本語"),
]

# --- Target languages for translation ---
TARGET_LANGUAGES = [
    ("vi", "Tiếng Việt"),
    ("en", "English"),
    ("ja", "日本語"),
]

# --- Document domains (checkbox, multi-select) ---
# (key, i18n_key, default_checked)
DOMAINS = [
    ("other", "domain_other", True),
    ("it_software", "domain_it", False),
    ("legal", "domain_legal", False),
    ("medical", "domain_medical", False),
    ("finance", "domain_finance", False),
    ("engineering", "domain_engineering", False),
    ("marketing", "domain_marketing", False),
    ("academic", "domain_academic", False),
]

# --- Translation styles (radio, single-select) ---
# (key, i18n_key)
STYLES = [
    ("default", "style_default"),
    ("formal", "style_formal"),
    ("concise", "style_concise"),
    ("creative", "style_creative"),
    ("technical", "style_technical"),
]

# --- Translation engines (radio, single-select) ---
# (key, i18n_key, requires_api_key)
ENGINES = [
    ("offline", "engine_offline", False),
    ("openai", "engine_openai", True),
    ("claude", "engine_claude", True),
    ("google", "engine_google", True),
    ("deepl", "engine_deepl", True),
    ("gemini", "engine_gemini", True),
]

# --- Supported file extensions for file dialog ---
SUPPORTED_EXTENSIONS = [
    ".xlsx", ".xls", ".docx", ".pptx", ".txt", ".csv",
]
