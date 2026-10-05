from app.preprocessing.tokenizer import TextTokenizer
from app.extraction.synonyms import SynonymManager

class LexicalSimilarityCalculator:
    def __init__(self, synonym_manager: SynonymManager | None = None):
        self.tokenizer = TextTokenizer()
        self.synonyms = synonym_manager or SynonymManager()

    def calculate(self, text_a: str, text_b: str) -> float:
        if not text_a or not text_b:
            return 0.0
        tokens_a = [self.synonyms.canonicalize(t) for t in self.tokenizer.tokenize(text_a.lower(), remove_stopwords=True)]
        tokens_b = [self.synonyms.canonicalize(t) for t in self.tokenizer.tokenize(text_b.lower(), remove_stopwords=True)]

        set_a = set(tokens_a)
        set_b = set(tokens_b)

        if not set_a or not set_b:
            return 0.0

        intersection = set_a.intersection(set_b)
        union = set_a.union(set_b)
        jaccard = len(intersection) / len(union)

        # Character n-gram overlap
        ngrams_a = set(self.tokenizer.extract_ngrams(tokens_a, min_n=1, max_n=2))
        ngrams_b = set(self.tokenizer.extract_ngrams(tokens_b, min_n=1, max_n=2))
        ngram_sim = len(ngrams_a.intersection(ngrams_b)) / max(1, len(ngrams_a.union(ngrams_b)))

        return float(round(0.6 * jaccard + 0.4 * ngram_sim, 4))
