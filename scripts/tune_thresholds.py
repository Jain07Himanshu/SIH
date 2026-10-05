import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from app.schemas.complaint import ComplaintRecord
from app.services.pipeline import GrievanceIntelligencePipeline

def run_tuning():
    print("=" * 65)
    print("SIMILARITY THRESHOLD TUNING & GRID SEARCH")
    print("=" * 65)

    pairs = [
        # True Duplicates (Label 1)
        ("Huge pothole near railway station flyover causing bike accidents", "Dangerous deep pothole outside railway station flyover, two wheelers skidding", 1),
        ("Garbage heap rotting near sector 12 park, foul smell", "Overflowing waste and trash pile at sector 12 community park", 1),
        ("Water pipeline burst in block C, road flooded since morning", "Severe drinking water pipe leakage in Block C, waterlogging road", 1),
        ("Street lights not working in ward 7 lane 3, pitch dark", "Dark street, all streetlights broken in ward 7 3rd lane", 1),
        
        # Possible Similar / Related (Label 1)
        ("Potholes all over MG road main market", "Road surface completely damaged in MG road market area", 1),
        ("Drain overflowing with sewage near hospital gate", "Hospital main entrance flooded with choked sewer water", 1),
        
        # True Negatives / Distinct Issues (Label 0)
        ("Huge pothole near metro pillar 45", "Garbage pile rotting near sector 12 park", 0),
        ("Water pipe burst in block C", "Power cut in block C since 2 hours", 0),
        ("Street light broken on 5th avenue", "Loud noise from construction site late night", 0),
        ("Illegal parking blocking school bus entrance", "Stray dog menace near colony playground", 0)
    ]

    pipeline = GrievanceIntelligencePipeline()
    scores = []
    labels = []

    print("Pair Similarity Scores:")
    for idx, (text_a, text_b, label) in enumerate(pairs, 1):
        rec_a = ComplaintRecord(complaint_id="A", text=text_a)
        rec_b = ComplaintRecord(complaint_id="B", text=text_b)
        
        norm_a = pipeline.normalizer.normalize_record(rec_a)
        norm_b = pipeline.normalizer.normalize_record(rec_b)
        
        kws_a = pipeline.keyword_extractor.extract_keywords(norm_a.text.clean)
        kws_b = pipeline.keyword_extractor.extract_keywords(norm_b.text.clean)
        
        emb_a = pipeline.encoder.encode_one(norm_a.text.semantic)
        emb_b = pipeline.encoder.encode_one(norm_b.text.semantic)
        
        res = pipeline.scorer.score_pair(rec_a, rec_b, emb_a=emb_a, emb_b=emb_b, kw_a=kws_a, kw_b=kws_b)
        scores.append(res.similarity_score)
        labels.append(label)
        tag = "DUP" if label == 1 else "NEG"
        t_a = text_a[:32]
        t_b = text_b[:32]
        print(f"  [{idx:02d}] [{tag}] Score: {res.similarity_score:0.4f} | {t_a}... vs {t_b}...")

    best_thresh = 0.50
    best_f1 = 0.0
    best_precision = 0.0
    best_recall = 0.0

    print("\nGrid Search over candidate thresholds [0.30 - 0.80]:\n")

    for th in np.arange(0.30, 0.82, 0.04):
        th = round(float(th), 2)
        preds = [1 if s >= th else 0 for s in scores]
        tp = sum(1 for p, l in zip(preds, labels) if p == 1 and l == 1)
        fp = sum(1 for p, l in zip(preds, labels) if p == 1 and l == 0)
        fn = sum(1 for p, l in zip(preds, labels) if p == 0 and l == 1)
        
        precision = tp / max(1, (tp + fp))
        recall = tp / max(1, (tp + fn))
        f1 = 2 * (precision * recall) / max(1e-9, (precision + recall))

        print(f"  Threshold: {th:0.2f} | Precision: {precision:0.2f} | Recall: {recall:0.2f} | F1: {f1:0.2f}")

        if f1 > best_f1:
            best_f1 = f1
            best_thresh = th
            best_precision = precision
            best_recall = recall

    print("\n" + "=" * 65)
    print("OPTIMAL CALIBRATED THRESHOLDS:")
    print(f"  duplicate threshold:      {max(0.70, best_thresh + 0.15):0.2f}")
    print(f"  possible_match threshold: {best_thresh:0.2f} (Max F1: {best_f1:0.2f})")
    print(f"  needs_review_margin:      0.04")
    print("=" * 65)

if __name__ == "__main__":
    run_tuning()
