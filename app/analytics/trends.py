from datetime import datetime
from collections import defaultdict
from app.schemas.complaint import ComplaintRecord
from app.schemas.issue import IssueRecord
from app.schemas.analytics import TrendAnalytics, TrendDataPoint

class TrendAnalyzer:
    @staticmethod
    def analyze_trends(complaints: list[ComplaintRecord], issues: list[IssueRecord], interval: str = "daily") -> TrendAnalytics:
        complaint_counts: dict[str, int] = defaultdict(int)
        for c in complaints:
            ts = c.timestamp or datetime.utcnow()
            if interval == "monthly":
                period = ts.strftime("%Y-%m")
            elif interval == "weekly":
                period = ts.strftime("%Y-W%W")
            else:
                period = ts.strftime("%Y-%m-%d")
            complaint_counts[period] += 1

        issue_counts: dict[str, int] = defaultdict(int)
        duplicate_counts: dict[str, int] = defaultdict(int)
        for i in issues:
            ts = i.created_at or datetime.utcnow()
            if interval == "monthly":
                period = ts.strftime("%Y-%m")
            elif interval == "weekly":
                period = ts.strftime("%Y-W%W")
            else:
                period = ts.strftime("%Y-%m-%d")
            issue_counts[period] += 1
            duplicate_counts[period] += i.duplicate_count

        all_periods = sorted(set(list(complaint_counts.keys()) + list(issue_counts.keys())))
        data_points: list[TrendDataPoint] = []
        for p in all_periods:
            data_points.append(TrendDataPoint(
                period=p,
                complaint_count=complaint_counts.get(p, 0),
                issue_count=issue_counts.get(p, 0),
                duplicate_count=duplicate_counts.get(p, 0)
            ))

        return TrendAnalytics(interval=interval, trends=data_points)
