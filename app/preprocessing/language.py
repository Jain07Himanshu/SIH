import re

class LanguageDetector:
    DEVANAGARI_REGEX = re.compile(r"[\u0900-\u097F]")
    LATIN_REGEX = re.compile(r"[a-zA-Z]")

    @staticmethod
    def detect(text: str) -> dict[str, str | float]:
        if not text or not text.strip():
            return {"language": "en", "confidence": 1.0, "script": "latin"}

        devanagari_count = len(LanguageDetector.DEVANAGARI_REGEX.findall(text))
        latin_count = len(LanguageDetector.LATIN_REGEX.findall(text))
        total_letters = devanagari_count + latin_count

        if total_letters == 0:
            return {"language": "en", "confidence": 1.0, "script": "latin"}

        if devanagari_count / total_letters > 0.3:
            confidence = round(devanagari_count / total_letters, 2)
            return {"language": "hi", "confidence": confidence, "script": "devanagari"}
        else:
            confidence = round(latin_count / total_letters, 2)
            return {"language": "en", "confidence": confidence, "script": "latin"}
