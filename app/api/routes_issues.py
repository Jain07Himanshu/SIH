from fastapi import APIRouter, HTTPException, Depends
from app.schemas.issue import IssueRecord, IssueMergeRequest, IssueSplitRequest, IssueOperationResponse
from app.issue.issue_resolver import IssueResolver
from app.services.pipeline import GrievanceIntelligencePipeline
from app.api.routes_analysis import get_pipeline

router = APIRouter(prefix="/api/v1/issues", tags=["Canonical Issues"])

@router.get("", response_model=list[IssueRecord])
def list_issues(category_id: str | None = None,
                department_id: str | None = None,
                dominant_priority: str | None = None,
                pipeline: GrievanceIntelligencePipeline = Depends(get_pipeline)):
    issues = list(pipeline.issues.values())
    if category_id:
        issues = [i for i in issues if i.category and i.category.category_id == category_id]
    if department_id:
        issues = [i for i in issues if i.department and i.department.id == department_id]
    if dominant_priority:
        issues = [i for i in issues if i.priority_summary.dominant_priority.upper() == dominant_priority.upper()]
    return issues

@router.get("/{issue_id}", response_model=IssueRecord)
def get_issue(issue_id: str, pipeline: GrievanceIntelligencePipeline = Depends(get_pipeline)):
    if issue_id not in pipeline.issues:
        raise HTTPException(status_code=404, detail=f"Issue '{issue_id}' not found.")
    return pipeline.issues[issue_id]

@router.post("/merge", response_model=IssueOperationResponse)
def merge_issues(req: IssueMergeRequest, pipeline: GrievanceIntelligencePipeline = Depends(get_pipeline)):
    if req.target_issue_id not in pipeline.issues:
        raise HTTPException(status_code=404, detail=f"Target issue '{req.target_issue_id}' not found.")
    if req.source_issue_id not in pipeline.issues:
        raise HTTPException(status_code=404, detail=f"Source issue '{req.source_issue_id}' not found.")

    target = pipeline.issues[req.target_issue_id]
    source = pipeline.issues[req.source_issue_id]

    res = IssueResolver.merge_issues(target, source, reason=req.reason)

    # Remap complaints
    for cid in source.complaint_ids:
        pipeline.complaint_to_issue[cid] = target.issue_id

    del pipeline.issues[source.issue_id]
    return res

@router.post("/split", response_model=IssueOperationResponse)
def split_issue(req: IssueSplitRequest, pipeline: GrievanceIntelligencePipeline = Depends(get_pipeline)):
    if req.parent_issue_id not in pipeline.issues:
        raise HTTPException(status_code=404, detail=f"Parent issue '{req.parent_issue_id}' not found.")

    parent = pipeline.issues[req.parent_issue_id]
    new_issue_id = f"ISS-{pipeline.issue_counter:03d}"
    pipeline.issue_counter += 1

    res = IssueResolver.split_issue(parent, req.complaint_ids, new_issue_id, new_issue_title=req.new_issue_title, reason=req.reason)
    if not res.success:
        raise HTTPException(status_code=400, detail=res.message)

    new_issue = res.resulting_issues[1]
    pipeline.issues[new_issue.issue_id] = new_issue
    for cid in req.complaint_ids:
        pipeline.complaint_to_issue[cid] = new_issue.issue_id

    return res
