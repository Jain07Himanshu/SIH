from app.services.pipeline import GrievanceIntelligencePipeline
from app.schemas.complaint import ComplaintRecord

def test_empty_and_short_texts(pipeline):
    r1 = ComplaintRecord(complaint_id="E1", text="")
    r2 = ComplaintRecord(complaint_id="E2", text="Help")
    r3 = ComplaintRecord(complaint_id="E3", text="1234567890 !@#$%^&*()")

    norm1, _, iss1 = pipeline.process_single(r1)
    norm2, _, iss2 = pipeline.process_single(r2)
    norm3, _, iss3 = pipeline.process_single(r3)

    assert iss1 is not None
    assert iss2 is not None
    assert iss3 is not None

def test_identical_complaint_batch(pipeline):
    identical = [
        ComplaintRecord(complaint_id=f"ID-{i}", text="Water pipe leaking in Sector 10", latitude=28.6, longitude=77.2)
        for i in range(5)
    ]
    issues, summary, report = pipeline.process_batch(identical)
    assert len(issues) == 1
    assert issues[0].complaint_count == 5
    assert issues[0].duplicate_count == 4
