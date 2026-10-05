from app.schemas.complaint import ComplaintRecord, NormalizedComplaint, TextRepresentation
from app.preprocessing.cleaner import TextCleaner
from app.preprocessing.tokenizer import TextTokenizer
from app.preprocessing.language import LanguageDetector
from app.extraction.synonyms import SynonymManager

class ComplaintNormalizer:
    def __init__(self,
                 cleaner: TextCleaner | None = None,
                 tokenizer: TextTokenizer | None = None,
                 language_detector: LanguageDetector | None = None,
                 synonym_manager: SynonymManager | None = None):
        self.cleaner = cleaner or TextCleaner()
        self.tokenizer = tokenizer or TextTokenizer()
        self.language_detector = language_detector or LanguageDetector()
        self.synonym_manager = synonym_manager or SynonymManager()

    def normalize_record(self, record: ComplaintRecord) -> NormalizedComplaint:
        orig = record.text or ""
        clean_text = self.cleaner.clean(orig)

        # Tokenize without stopwords
        tokens = self.tokenizer.tokenize(clean_text, lowercase=True, remove_stopwords=True)

        # Canonicalize with civic synonyms
        canon_tokens = [self.synonym_manager.canonicalize(t) for t in tokens]

        # Representations
        semantic_text = clean_text
        keyword_text = " ".join(canon_tokens)

        text_rep = TextRepresentation(
            original=orig,
            clean=clean_text,
            semantic=semantic_text,
            keyword=keyword_text
        )

        lang_info = self.language_detector.detect(orig)

        return NormalizedComplaint(
            complaint_id=record.complaint_id,
            raw_record=record,
            text=text_rep,
            tokens=tokens,
            language=str(lang_info.get("language", "en")),
            language_confidence=float(lang_info.get("confidence", 1.0)),
            keywords=[]
        )
