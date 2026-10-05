from app.preprocessing.cleaner import TextCleaner
from app.preprocessing.tokenizer import TextTokenizer
from app.preprocessing.language import LanguageDetector
from app.preprocessing.normalizer import ComplaintNormalizer
from app.schemas.complaint import ComplaintRecord

def test_cleaner_pii_and_unicode():
    cleaner = TextCleaner()
    raw = "Dear Sir, please fix pothole at 9876543210 or user@example.com ASAP!!!!"
    cleaned = cleaner.clean(raw)
    assert "[PHONE]" in cleaned
    assert "[EMAIL]" in cleaned
    assert "!" not in cleaned or cleaned.count("!") == 1
    assert "sir" not in cleaned.lower()

def test_tokenizer_ngrams():
    tok = TextTokenizer()
    tokens = tok.tokenize("pothole on the road", remove_stopwords=True)
    assert "pothole" in tokens
    assert "road" in tokens
    assert "on" not in tokens
    assert "the" not in tokens
    ngrams = tok.extract_ngrams(tokens, min_n=1, max_n=2)
    assert "pothole road" in ngrams or "pothole" in ngrams

def test_language_detection():
    det = LanguageDetector()
    res_en = det.detect("Water leakage in sector 5 since yesterday")
    assert res_en["language"] == "en"
    assert res_en["confidence"] > 0.8

def test_normalizer_multi_representation():
    norm = ComplaintNormalizer()
    rec = ComplaintRecord(complaint_id="C1", text="Big pothole near metro pillar 10")
    normalized = norm.normalize_record(rec)
    assert normalized.text.original == "Big pothole near metro pillar 10"
    assert "pothole" in normalized.text.clean
    assert "pothole" in normalized.text.semantic
    assert "pothole" in normalized.text.keyword
