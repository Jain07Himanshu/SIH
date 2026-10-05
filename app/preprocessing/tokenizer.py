import re

class TextTokenizer:
    CIVIC_STOPWORDS = {
        "the", "a", "an", "this", "that", "these", "those", "is", "are", "was",
        "were", "be", "been", "being", "have", "has", "had", "do", "does", "did",
        "in", "on", "at", "to", "for", "with", "about", "against", "between",
        "into", "through", "during", "before", "after", "above", "below", "from",
        "up", "down", "in", "out", "off", "over", "under", "again", "further",
        "then", "once", "here", "there", "when", "where", "why", "how", "all",
        "any", "both", "each", "few", "more", "most", "other", "some", "such",
        "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very",
        "can", "will", "just", "should", "now", "sir", "madam", "please", "help"
    }

    WORD_REGEX = re.compile(r"\b[\w'-]+\b")

    @staticmethod
    def tokenize(text: str, lowercase: bool = True, remove_stopwords: bool = False) -> list[str]:
        if not text:
            return []
        if lowercase:
            text = text.lower()
        tokens = TextTokenizer.WORD_REGEX.findall(text)
        if remove_stopwords:
            tokens = [t for t in tokens if t not in TextTokenizer.CIVIC_STOPWORDS and len(t) > 1]
        return tokens

    @staticmethod
    def extract_ngrams(tokens: list[str], min_n: int = 1, max_n: int = 3) -> list[str]:
        if not tokens:
            return []
        ngrams: list[str] = []
        for n in range(min_n, min(max_n + 1, len(tokens) + 1)):
            for i in range(len(tokens) - n + 1):
                ngrams.append(" ".join(tokens[i:i + n]))
        return ngrams
