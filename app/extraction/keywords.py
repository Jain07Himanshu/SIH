from collections import Counter
from app.schemas.complaint import KeywordItem
from app.preprocessing.tokenizer import TextTokenizer
from app.extraction.synonyms import SynonymManager
from app.extraction.phrases import PhraseExtractor
from app.extraction.entities import EntityExtractor

class KeywordExtractor:
    def __init__(self, synonym_manager: SynonymManager | None = None):
        self.tokenizer = TextTokenizer()
        self.synonyms = synonym_manager or SynonymManager()
        self.phrase_extractor = PhraseExtractor()
        self.entity_extractor = EntityExtractor()

    def extract_keywords(self, text: str, top_k: int = 8) -> list[KeywordItem]:
        if not text or not text.strip():
            return []
        clean_text = text.lower()
        items: list[KeywordItem] = []
        seen: set[str] = set()

        for loc in self.phrase_extractor.extract_location_phrases(clean_text):
            if loc not in seen and len(loc) >= 3:
                items.append(KeywordItem(term=loc, score=0.85, type="location"))
                seen.add(loc)

        for imp in self.phrase_extractor.extract_impact_phrases(clean_text):
            if imp not in seen:
                items.append(KeywordItem(term=imp, score=0.75, type="impact"))
                seen.add(imp)

        for temp in self.entity_extractor.extract_temporal_expressions(clean_text):
            if temp not in seen:
                items.append(KeywordItem(term=temp, score=0.70, type="temporal"))
                seen.add(temp)

        tokens = self.tokenizer.tokenize(clean_text, lowercase=True, remove_stopwords=True)
        ngrams = self.tokenizer.extract_ngrams(tokens, min_n=1, max_n=3)
        freq = Counter(ngrams)
        scored: list[tuple[str, float]] = []
        for term, count in freq.items():
            words = term.split()
            canon = self.synonyms.canonicalize(term)
            boost = 1.0 + 0.2 * len(words)
            score = round(min(0.98, (count * 0.4 + boost * 0.4)), 2)
            scored.append((canon, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        for term, score in scored:
            if term not in seen and len(term) >= 3:
                items.append(KeywordItem(term=term, score=score, type="issue"))
                seen.add(term)
                if len(items) >= top_k:
                    break
        return items[:top_k]
