from datetime import datetime
from collections import Counter
from app.schemas.complaint import NormalizedComplaint
from app.schemas.issue import IssueRecord
from app.issue.issue_builder import IssueBuilder

class IssueUpdater:
    def __init__(self, issue_builder: IssueBuilder | None = None):
        self.builder = issue_builder or IssueBuilder()

    def attach_complaint(self, issue: IssueRecord, new_complaint: NormalizedComplaint, sim_score: float) -> IssueRecord:
        if new_complaint.complaint_id in issue.complaint_ids:
            return issue

        issue.complaint_ids.append(new_complaint.complaint_id)
        issue.complaint_count = len(issue.complaint_ids)
        issue.duplicate_count = max(0, issue.complaint_count - 1)
        issue.similarity_score = round(min(issue.similarity_score, sim_score), 4)

        # Update keywords
        new_kws = [k.term for k in new_complaint.keywords]
        combined = issue.keywords + new_kws
        issue.keywords = [term for term, _ in Counter(combined).most_common(8)]

        # Update priority counts
        p = (new_complaint.raw_record.priority or "").upper()
        if p == "HIGH":
            issue.priority_summary.high_count += 1
        elif p == "LOW":
            issue.priority_summary.low_count += 1
        elif p == "MEDIUM":
            issue.priority_summary.medium_count += 1
        else:
            issue.priority_summary.unspecified_count += 1

        issue.updated_at = datetime.utcnow()
        return issue
