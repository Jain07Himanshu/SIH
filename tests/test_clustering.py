from app.services.pipeline import GrievanceIntelligencePipeline
from app.schemas.complaint import ComplaintRecord

def test_clustering_groups_duplicates(pipeline, sample_complaints):
    issues, cluster_summary, report = pipeline.process_batch(sample_complaints)
    assert len(issues) >= 3
    assert cluster_summary.total_clusters >= 1
    assert report.successful == 6

    # Verify pothole complaints (C01, C02, C03) group together
    pothole_issue = next((i for i in issues if "C01" in i.complaint_ids), None)
    assert pothole_issue is not None
    assert "C02" in pothole_issue.complaint_ids
    assert pothole_issue.complaint_count >= 2
    assert pothole_issue.duplicate_count >= 1
