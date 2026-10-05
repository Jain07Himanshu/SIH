from datetime import datetime
from app.schemas.issue import IssueRecord, IssueOperationResponse

class IssueResolver:
    @staticmethod
    def merge_issues(target_issue: IssueRecord, source_issue: IssueRecord, reason: str | None = None) -> IssueOperationResponse:
        # Transfer all complaints
        for cid in source_issue.complaint_ids:
            if cid not in target_issue.complaint_ids:
                target_issue.complaint_ids.append(cid)

        target_issue.complaint_count = len(target_issue.complaint_ids)
        target_issue.duplicate_count = max(0, target_issue.complaint_count - 1)

        # Merge priorities
        target_issue.priority_summary.high_count += source_issue.priority_summary.high_count
        target_issue.priority_summary.medium_count += source_issue.priority_summary.medium_count
        target_issue.priority_summary.low_count += source_issue.priority_summary.low_count
        target_issue.priority_summary.unspecified_count += source_issue.priority_summary.unspecified_count

        # Merge keywords
        from collections import Counter
        merged_kws = target_issue.keywords + source_issue.keywords
        target_issue.keywords = [k for k, _ in Counter(merged_kws).most_common(8)]
        target_issue.updated_at = datetime.utcnow()

        return IssueOperationResponse(
            success=True,
            message=f"Merged issue {source_issue.issue_id} into {target_issue.issue_id}. Reason: {reason or 'Duplicate issue consolidation'}",
            affected_issue_ids=[target_issue.issue_id, source_issue.issue_id],
            resulting_issues=[target_issue]
        )

    @staticmethod
    def split_issue(parent_issue: IssueRecord,
                    complaint_ids_to_split: list[str],
                    new_issue_id: str,
                    new_issue_title: str | None = None,
                    reason: str | None = None) -> IssueOperationResponse:
        
        remaining_ids = [cid for cid in parent_issue.complaint_ids if cid not in complaint_ids_to_split]
        if not remaining_ids:
            return IssueOperationResponse(
                success=False,
                message="Cannot split all complaints out of parent issue.",
                affected_issue_ids=[parent_issue.issue_id],
                resulting_issues=[parent_issue]
            )

        parent_issue.complaint_ids = remaining_ids
        parent_issue.complaint_count = len(remaining_ids)
        parent_issue.duplicate_count = max(0, len(remaining_ids) - 1)
        parent_issue.updated_at = datetime.utcnow()

        new_issue = IssueRecord(
            issue_id=new_issue_id,
            title=new_issue_title or f"Split Issue from {parent_issue.issue_id}",
            category=parent_issue.category,
            department=parent_issue.department,
            keywords=parent_issue.keywords.copy(),
            representative_complaint_id=complaint_ids_to_split[0],
            complaint_ids=complaint_ids_to_split,
            complaint_count=len(complaint_ids_to_split),
            duplicate_count=max(0, len(complaint_ids_to_split) - 1),
            location=parent_issue.location,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        return IssueOperationResponse(
            success=True,
            message=f"Successfully split {len(complaint_ids_to_split)} complaints from {parent_issue.issue_id} into {new_issue_id}. Reason: {reason or 'Manual review split'}",
            affected_issue_ids=[parent_issue.issue_id, new_issue.issue_id],
            resulting_issues=[parent_issue, new_issue]
        )
