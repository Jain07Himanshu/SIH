import numpy as np
from sklearn.cluster import DBSCAN
from app.schemas.issue import IssueRecord

class IssueClusterer:
    @staticmethod
    def cluster_similar_issues(issues: list[IssueRecord], issue_embeddings: np.ndarray, eps: float = 0.20) -> list[list[str]]:
        if len(issues) < 2:
            return [[i.issue_id for i in issues]] if issues else []

        dist_matrix = 1.0 - np.dot(issue_embeddings, issue_embeddings.T)
        np.fill_diagonal(dist_matrix, 0.0)

        db = DBSCAN(eps=eps, min_samples=2, metric='precomputed')
        labels = db.fit_predict(dist_matrix)

        groups: list[list[str]] = []
        for lbl in set(labels):
            if lbl == -1:
                continue
            indices = [i for i, l in enumerate(labels) if l == lbl]
            groups.append([issues[i].issue_id for i in indices])

        return groups
