from app.extraction.synonyms import SynonymManager
from app.extraction.phrases import PhraseExtractor
from app.extraction.entities import EntityExtractor
from app.extraction.keywords import KeywordExtractor

def test_synonym_canonicalization():
    sm = SynonymManager()
    assert sm.canonicalize("crater") == "pothole"
    assert sm.canonicalize("kachra") == "garbage"
    assert sm.canonicalize("nal") == "tap"

def test_phrase_extractor():
    text = "Huge pothole near railway station causing accidents and severe road block"
    locations = PhraseExtractor.extract_location_phrases(text)
    assert any("railway station" in loc for loc in locations)
    impacts = PhraseExtractor.extract_impact_phrases(text)
    assert any("causing accident" in imp or "severe" in imp for imp in impacts)

def test_entity_extractor():
    text = "Water is not coming since yesterday for 3 days and streetlights are also broken"
    temporals = EntityExtractor.extract_temporal_expressions(text)
    assert any("since yesterday" in t or "3 days" in t for t in temporals)
    aspects = EntityExtractor.extract_multi_issue_aspects(text)
    assert len(aspects) >= 2

def test_keyword_extractor_ranking():
    ke = KeywordExtractor()
    kws = ke.extract_keywords("Huge pothole near railway station causing accidents since yesterday", top_k=5)
    terms = [k.term for k in kws]
    assert any("pothole" in t for t in terms)
    assert any(k.type == "location" for k in kws)
    assert any(k.type == "temporal" for k in kws)
