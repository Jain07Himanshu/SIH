from app.schemas.complaint import ComplaintRecord
from app.similarity.scorer import CompositeSimilarityScorer
from app.embeddings.encoder import EmbeddingEncoder
from app.extraction.keywords import KeywordExtractor

def test_duplicate_decision_identical():
    scorer = CompositeSimilarityScorer()
    encoder = EmbeddingEncoder()
    ke = KeywordExtractor()

    text = "Large dangerous pothole near railway station pillar 10"
    rec_a = ComplaintRecord(complaint_id="A", text=text, category="ROAD_POTHOLE", latitude=28.6139, longitude=77.2090)
    rec_b = ComplaintRecord(complaint_id="B", text=text, category="ROAD_POTHOLE", latitude=28.6139, longitude=77.2090)

    emb_a = encoder.encode_one(rec_a.text)
    emb_b = encoder.encode_one(rec_b.text)
    kws_a = ke.extract_keywords(rec_a.text)
    kws_b = ke.extract_keywords(rec_b.text)

    res = scorer.score_pair(rec_a, rec_b, emb_a=emb_a, emb_b=emb_b, kw_a=kws_a, kw_b=kws_b)
    assert res.match_type == "DUPLICATE"
    assert res.similarity_score >= 0.85
    assert res.evidence.explanation.same_category is True

def test_new_issue_decision_unrelated():
    scorer = CompositeSimilarityScorer()
    encoder = EmbeddingEncoder()
    ke = KeywordExtractor()

    rec_a = ComplaintRecord(complaint_id="A", text="Large pothole on road", category="ROAD_POTHOLE")
    rec_b = ComplaintRecord(complaint_id="B", text="Stray dog barking all night", category="OTHER_GENERAL")

    emb_a = encoder.encode_one(rec_a.text)
    emb_b = encoder.encode_one(rec_b.text)
    kws_a = ke.extract_keywords(rec_a.text)
    kws_b = ke.extract_keywords(rec_b.text)

    res = scorer.score_pair(rec_a, rec_b, emb_a=emb_a, emb_b=emb_b, kw_a=kws_a, kw_b=kws_b)
    assert res.match_type == "NEW_ISSUE"
    assert res.similarity_score < 0.60
