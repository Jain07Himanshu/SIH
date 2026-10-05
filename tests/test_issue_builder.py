from app.issue.issue_builder import IssueBuilder
from app.issue.issue_resolver import IssueResolver
from app.preprocessing.normalizer import ComplaintNormalizer
from app.schemas.complaint import ComplaintRecord

def test_issue_title_and_gis():
    builder = IssueBuilder()
    norm = ComplaintNormalizer()

    r1 = ComplaintRecord(complaint_id="C1", text="Deep pothole near railway station", latitude=28.6139, longitude=77.2090, priority="HIGH")
    r2 = ComplaintRecord(complaint_id="C2", text="Dangerous crater near railway station", latitude=28.6141, longitude=77.2092, priority="HIGH")

    nc1 = norm.normalize_record(r1)
    nc2 = norm.normalize_record(r2)

    issue = builder.build_issue("ISS-001", [nc1, nc2])
    assert "pothole" in issue.title.lower() or "railway station" in issue.title.lower()
    assert issue.location is not None
    assert issue.location.latitude == round((28.6139 + 28.6141) / 2, 6)
    assert issue.priority_summary.dominant_priority == "HIGH"
    assert issue.duplicate_count == 1

def test_issue_merge_and_split():
    builder = IssueBuilder()
    norm = ComplaintNormalizer()

    r1 = ComplaintRecord(complaint_id="C1", text="Pothole on main road")
    r2 = ComplaintRecord(complaint_id="C2", text="Another pothole on road")
    r3 = ComplaintRecord(complaint_id="C3", text="Streetlight broken")

    i1 = builder.build_issue("ISS-1", [norm.normalize_record(r1), norm.normalize_record(r2)])
    i2 = builder.build_issue("ISS-2", [norm.normalize_record(r3)])

    # Merge
    res_merge = IssueResolver.merge_issues(i1, i2, reason="Consolidation")
    assert res_merge.success is True
    assert "C3" in i1.complaint_ids
    assert i1.complaint_count == 3

    # Split
    res_split = IssueResolver.split_issue(i1, ["C3"], "ISS-3", new_issue_title="Split Streetlight")
    assert res_split.success is True
    assert i1.complaint_count == 2
    assert "C3" not in i1.complaint_ids
    assert res_split.resulting_issues[1].issue_id == "ISS-3"
