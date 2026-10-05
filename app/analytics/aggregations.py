from collections import defaultdict
from app.schemas.complaint import ComplaintRecord
from app.schemas.issue import IssueRecord
from app.schemas.analytics import (
    OverviewAnalytics,
    CategoryAnalyticsItem,
    DepartmentAnalyticsItem
)
from app.classification.taxonomy import TaxonomyManager

class AnalyticsAggregator:
    def __init__(self, taxonomy_manager: TaxonomyManager | None = None):
        self.taxonomy = taxonomy_manager or TaxonomyManager()

    def compute_overview(self, complaints: list[ComplaintRecord], issues: list[IssueRecord]) -> OverviewAnalytics:
        total_c = len(complaints)
        total_i = len(issues)
        dup_c = sum(i.duplicate_count for i in issues)
        dup_rate = round((dup_c / total_c) * 100, 2) if total_c > 0 else 0.0
        avg_cluster = round(total_c / max(1, total_i), 2) if total_i > 0 else 0.0
        high_prio = sum(1 for i in issues if i.priority_summary.dominant_priority == "HIGH")
        needs_rev = sum(1 for i in issues if i.needs_review)

        return OverviewAnalytics(
            total_complaints=total_c,
            unique_issues=total_i,
            duplicate_complaints=dup_c,
            duplicate_rate=dup_rate,
            average_cluster_size=avg_cluster,
            high_priority_issues=high_prio,
            needs_review_count=needs_rev
        )

    def compute_category_analytics(self, issues: list[IssueRecord]) -> list[CategoryAnalyticsItem]:
        cat_map: dict[str, list[IssueRecord]] = defaultdict(list)
        for i in issues:
            cat_id = i.category.category_id if i.category else "OTHER_GENERAL"
            cat_map[cat_id].append(i)

        results: list[CategoryAnalyticsItem] = []
        for cat_id, cat_issues in cat_map.items():
            total_c = sum(i.complaint_count for i in cat_issues)
            total_i = len(cat_issues)
            dup_c = sum(i.duplicate_count for i in cat_issues)
            dup_rate = round((dup_c / total_c) * 100, 2) if total_c > 0 else 0.0

            cat_rec = self.taxonomy.get_category(cat_id)
            cat_name = cat_rec.name if cat_rec else (cat_issues[0].category.category_name if cat_issues[0].category else cat_id)
            dept_id = cat_rec.department_id if cat_rec else None

            # Dominant priority
            prios = [i.priority_summary.dominant_priority for i in cat_issues]
            dominant_p = max(set(prios), key=prios.count) if prios else "MEDIUM"

            results.append(CategoryAnalyticsItem(
                category_id=cat_id,
                category_name=cat_name,
                complaints=total_c,
                issues=total_i,
                duplicate_rate=dup_rate,
                department_id=dept_id,
                dominant_priority=dominant_p
            ))

        results.sort(key=lambda x: x.complaints, reverse=True)
        return results

    def compute_department_analytics(self, issues: list[IssueRecord]) -> list[DepartmentAnalyticsItem]:
        dept_map: dict[str, list[IssueRecord]] = defaultdict(list)
        for i in issues:
            dept_id = i.department.id if i.department else (i.category.department_id if i.category and i.category.department_id else "GENERAL_DEPT")
            dept_map[dept_id].append(i)

        results: list[DepartmentAnalyticsItem] = []
        for dept_id, dept_issues in dept_map.items():
            total_c = sum(i.complaint_count for i in dept_issues)
            total_i = len(dept_issues)
            high_i = sum(1 for i in dept_issues if i.priority_summary.dominant_priority == "HIGH")
            dup_c = sum(i.duplicate_count for i in dept_issues)
            dup_rate = round((dup_c / total_c) * 100, 2) if total_c > 0 else 0.0
            avg_size = round(total_c / max(1, total_i), 2)

            dept_rec = self.taxonomy.get_department(dept_id)
            dept_name = dept_rec.name if dept_rec else (dept_issues[0].department.name if dept_issues[0].department else dept_id)

            results.append(DepartmentAnalyticsItem(
                department_id=dept_id,
                department_name=dept_name,
                complaints=total_c,
                unique_issues=total_i,
                high_priority_issues=high_i,
                duplicate_rate=dup_rate,
                average_issue_size=avg_size
            ))

        results.sort(key=lambda x: x.complaints, reverse=True)
        return results
