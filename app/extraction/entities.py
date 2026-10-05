import re

class EntityExtractor:
    TEMPORAL_REGEX = re.compile(
        r"\b(?:since\s+yesterday|since\s+last\s+(?:week|month)|for\s+(?:\d+|two|three|four|five|six|seven|ten|a\s+few)\s+(?:days|hours|weeks|months)|every\s+(?:morning|evening|night|day)|last\s+(?:night|week|month)|past\s+\d+\s+days)\b",
        re.IGNORECASE
    )

    # Primary aspect splitters: 'and also', 'as well as', 'and', 'along with', semicolons, commas preceding conjunctions
    ASPECT_SPLIT_REGEX = re.compile(
        r"(?:\s+(?:and\s+also|as\s+well\s+as|along\s+with|moreover|furthermore|additionally|plus|and)\s+|\s*;\s*|\s*,\s*(?:and|also)\s+)",
        re.IGNORECASE
    )

    @staticmethod
    def extract_temporal_expressions(text: str) -> list[str]:
        if not text:
            return []
        return [m.lower().strip() for m in EntityExtractor.TEMPORAL_REGEX.findall(text)]

    @staticmethod
    def extract_multi_issue_aspects(text: str) -> list[str]:
        if not text or not text.strip():
            return [text.strip()] if text else []

        clauses = EntityExtractor.ASPECT_SPLIT_REGEX.split(text)
        cleaned = [c.strip() for c in clauses if len(c.strip().split()) >= 2]
        return cleaned if len(cleaned) > 1 else [text.strip()]
