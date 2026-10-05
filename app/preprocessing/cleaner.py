import re
import unicodedata

class TextCleaner:
    BOILERPLATE_PATTERNS = [
        r"^\s*(?:dear\s+(?:sir|madam|officer|authority|team)|to\s+whom\s+it\s+may\s+concern)[,\.:\s-]*",
        r"(?:please\s+look\s+into\s+this|please\s+resolve|kindly\s+take\s+action|urgent\s+action\s+required|thanks|thanking\s+you|regards|sincerely|yours\s+faithfully).*$",
        r"\b(?:please\s+help|kindly\s+help|asap|do\s+the\s+needful)\b"
    ]

    PHONE_REGEX = re.compile(r"(?:\+?\d{1,3}[-. ]?)?\(?\d{2,5}\)?[-. ]?\d{5,10}|\b\d{10}\b")
    EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    AADHAAR_REGEX = re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b")
    VEHICLE_REGEX = re.compile(r"\b[A-Z]{2}[-\s]?[0-9]{1,2}[-\s]?[A-Z]{1,3}[-\s]?[0-9]{4}\b")
    REPEATED_PUNCT_REGEX = re.compile(r"([!?.]){2,}")
    REPEATED_CHAR_REGEX = re.compile(r"(.)\1{2,}")
    WHITESPACE_REGEX = re.compile(r"\s+")

    def __init__(self, mask_pii: bool = True, strip_boilerplate: bool = True):
        self.mask_pii = mask_pii
        self.strip_boilerplate = strip_boilerplate
        self.compiled_boilerplate = [re.compile(p, re.IGNORECASE) for p in self.BOILERPLATE_PATTERNS]

    def normalize_unicode(self, text: str) -> str:
        if not text:
            return ""
        return unicodedata.normalize("NFKC", text)

    def mask_sensitive_info(self, text: str) -> str:
        if not text:
            return ""
        text = self.AADHAAR_REGEX.sub("[AADHAAR]", text)
        text = self.EMAIL_REGEX.sub("[EMAIL]", text)
        text = self.PHONE_REGEX.sub("[PHONE]", text)
        text = self.VEHICLE_REGEX.sub("[VEHICLE]", text)
        return text

    def remove_boilerplate(self, text: str) -> str:
        if not text:
            return ""
        cleaned = text
        for pat in self.compiled_boilerplate:
            cleaned = pat.sub(" ", cleaned)
        return cleaned

    def clean(self, text: str) -> str:
        if not text or not isinstance(text, str):
            return ""

        cleaned = self.normalize_unicode(text)

        if self.mask_pii:
            cleaned = self.mask_sensitive_info(cleaned)

        # Reduce repeated punctuation: !!! -> !
        cleaned = self.REPEATED_PUNCT_REGEX.sub(r"\1", cleaned)

        # Reduce repeated chars: pleaaase -> please
        cleaned = self.REPEATED_CHAR_REGEX.sub(r"\1\1", cleaned)

        if self.strip_boilerplate:
            cleaned = self.remove_boilerplate(cleaned)

        cleaned = self.WHITESPACE_REGEX.sub(" ", cleaned).strip()

        return cleaned
