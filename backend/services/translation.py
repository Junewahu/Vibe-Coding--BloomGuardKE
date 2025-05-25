from typing import Dict, Any, Optional
import json
import os
from pathlib import Path
from googletrans import Translator
from ..core.config import settings

class TranslationService:
    def __init__(self):
        self.translator = Translator()
        self.translations_dir = Path("translations")
        self.translations_dir.mkdir(exist_ok=True)
        self._load_translations()

    def _load_translations(self):
        """Load all translation files."""
        self.translations = {}
        for file in self.translations_dir.glob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                self.translations[file.stem] = json.load(f)

    async def translate_text(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        """Translate text between languages."""
        if source_lang == target_lang:
            return text

        try:
            # First check if we have a cached translation
            cached = self._get_cached_translation(text, source_lang, target_lang)
            if cached:
                return cached

            # If not, use Google Translate
            result = self.translator.translate(
                text,
                src=source_lang,
                dest=target_lang
            )
            
            # Cache the translation
            self._cache_translation(text, result.text, source_lang, target_lang)
            
            return result.text
        except Exception as e:
            print(f"Translation error: {str(e)}")
            return text

    def _get_cached_translation(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> Optional[str]:
        """Get cached translation if available."""
        cache_file = self.translations_dir / f"{source_lang}_{target_lang}.json"
        if not cache_file.exists():
            return None

        with open(cache_file, "r", encoding="utf-8") as f:
            cache = json.load(f)
            return cache.get(text)

    def _cache_translation(
        self,
        source_text: str,
        translated_text: str,
        source_lang: str,
        target_lang: str
    ):
        """Cache a translation."""
        cache_file = self.translations_dir / f"{source_lang}_{target_lang}.json"
        
        # Load existing cache
        cache = {}
        if cache_file.exists():
            with open(cache_file, "r", encoding="utf-8") as f:
                cache = json.load(f)

        # Add new translation
        cache[source_text] = translated_text

        # Save cache
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)

    async def translate_template(
        self,
        template_name: str,
        context: Dict[str, Any],
        target_lang: str
    ) -> Dict[str, Any]:
        """Translate a template's context."""
        if target_lang == "en":
            return context

        translated_context = {}
        for key, value in context.items():
            if isinstance(value, str):
                translated_context[key] = await self.translate_text(
                    value,
                    "en",
                    target_lang
                )
            elif isinstance(value, dict):
                translated_context[key] = await self.translate_template(
                    f"{template_name}.{key}",
                    value,
                    target_lang
                )
            else:
                translated_context[key] = value

        return translated_context

    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages."""
        return {
            "en": "English",
            "sw": "Swahili",
            "fr": "French",
            "ar": "Arabic",
            "so": "Somali"
        }

# Create singleton instance
translation_service = TranslationService() 