from collections import Counter
from app.schemas.complaint import ComplaintRecord
from app.preprocessing.tokenizer import TextTokenizer

class CategoryDiscoverer:
    def __init__(self):
        self.tokenizer = TextTokenizer()

    def discover_category_for_cluster(self, complaints: list[ComplaintRecord]) -> tuple[str, str]:
        if not complaints:
            return ("DISCOVERED_GENERAL", "General Civic Issue")

        all_ngrams: list[str] = []
        for c in complaints:
            toks = self.tokenizer.tokenize(c.text, lowercase=True, remove_stopwords=True)
            ngrams = self.tokenizer.extract_ngrams(toks, min_n=1, max_n=2)
            all_ngrams.extend(ngrams)

        freq = Counter(all_ngrams)
        common = freq.most_common(2)
        if not common:
            return ("DISCOVERED_CIVIC", "Civic Maintenance Issue")

        top_terms = [t[0].title() for t in common]
        cat_name = " / ".join(top_terms) + " Issue"
        cat_id = "DISC_" + "_".join([t[0].upper().replace(" ", "_") for t in common])
        return (cat_id, cat_name)
