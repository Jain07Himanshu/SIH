import re

class PhraseExtractor:
    LOCATION_PREP_REGEX = re.compile(
        r"\b(?:near|outside|opposite|behind|adjacent\s+to|in\s+front\s+of|at|around|beside|along)\s+([a-zA-Z0-9\s]{3,30}?)(?=[,\.\?!]|\b(?:is|has|was|are|and|causing|with|due|since)\b|$)",
        re.IGNORECASE
    )
    CIVIC_PLACE_REGEX = re.compile(
        r"\b(?:ward\s+\d+|sector\s+\d+|block\s+[a-zA-Z0-9]+|railway\s+station|metro\s+station|bus\s+stop|bus\s+stand|hospital|school|college|market|crossroad|flyover|bridge|junction|circle|garden|park|society|colony|nagar|road|street|gali|lane)\b[a-zA-Z0-9\s]{0,20}",
        re.IGNORECASE
    )
    IMPACT_PATTERNS = [
        r"\b(?:causing\s+accidents?|hazard|dangerous|unsafe|threat)\b",
        r"\b(?:overflowing|waterlogging|flooding|stagnant\s+water)\b",
        r"\b(?:blocked|choked|clogged|traffic\s+jam|congestion)\b",
        r"\b(?:foul\s+smell|bad\s+odor|stink|unhygienic)\b",
        r"\b(?:no\s+water|water\s+crisis|shortage|blackout|power\s+cut)\b",
        r"\b(?:severe|urgent|critical|broken|damaged)\b"
    ]

    @staticmethod
    def extract_location_phrases(text: str) -> list[str]:
        if not text:
            return []
        locations: list[str] = []
        for match in PhraseExtractor.LOCATION_PREP_REGEX.finditer(text):
            loc = match.group(1).strip()
            if len(loc) >= 3 and loc.lower() not in {"the", "a", "an", "this", "our"}:
                locations.append(loc.lower())
        for match in PhraseExtractor.CIVIC_PLACE_REGEX.finditer(text):
            loc = match.group(0).strip()
            if loc and loc.lower() not in locations:
                locations.append(loc.lower())
        return list(dict.fromkeys(locations))

    @staticmethod
    def extract_impact_phrases(text: str) -> list[str]:
        if not text:
            return []
        impacts: list[str] = []
        for pat in PhraseExtractor.IMPACT_PATTERNS:
            matches = re.findall(pat, text, flags=re.IGNORECASE)
            for m in matches:
                impacts.append(m.lower().strip())
        return list(dict.fromkeys(impacts))
