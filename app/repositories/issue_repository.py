from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.db.models import IssueModel, IssueMemberModel
from app.schemas.issue import IssueRecord

class IssueRepository(BaseRepository):
    def save_issue(self, issue: IssueRecord) -> IssueModel:
        model = self.db.query(IssueModel).filter(IssueModel.issue_id == issue.issue_id).first()
        if not model:
            model = IssueModel(
                issue_id=issue.issue_id,
                title=issue.title,
                category_id=issue.category.category_id if issue.category else None,
                department_id=issue.department.id if issue.department else None,
                representative_complaint_id=issue.representative_complaint_id,
                complaint_count=issue.complaint_count,
                duplicate_count=issue.duplicate_count,
                similarity_score=issue.similarity_score,
                dominant_priority=issue.priority_summary.dominant_priority,
                latitude=issue.location.latitude if issue.location else None,
                longitude=issue.location.longitude if issue.location else None,
                radius_meters=issue.location.radius_meters if issue.location else 0.0,
                keywords_json=issue.keywords,
                needs_review=issue.needs_review
            )
            self.db.add(model)
        else:
            model.title = issue.title
            model.complaint_count = issue.complaint_count
            model.duplicate_count = issue.duplicate_count
            model.similarity_score = issue.similarity_score
            model.dominant_priority = issue.priority_summary.dominant_priority
            model.keywords_json = issue.keywords
            model.needs_review = issue.needs_review

        self.db.commit()

        # Update member mappings
        for cid in issue.complaint_ids:
            exists = self.db.query(IssueMemberModel).filter(
                IssueMemberModel.issue_id == issue.issue_id,
                IssueMemberModel.complaint_id == cid
            ).first()
            if not exists:
                member = IssueMemberModel(
                    issue_id=issue.issue_id,
                    complaint_id=cid,
                    similarity_score=issue.similarity_score,
                    is_representative=(cid == issue.representative_complaint_id)
                )
                self.db.add(member)
        self.db.commit()
        return model

    def get_by_id(self, issue_id: str) -> IssueModel | None:
        return self.db.query(IssueModel).filter(IssueModel.issue_id == issue_id).first()

    def get_all(self, limit: int = 100, offset: int = 0) -> list[IssueModel]:
        return self.db.query(IssueModel).offset(offset).limit(limit).all()
