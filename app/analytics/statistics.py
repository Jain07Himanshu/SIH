import numpy as np
from app.schemas.cluster import ClusterSummary

class ClusterStatistics:
    @staticmethod
    def compute_metrics(cluster_summary: ClusterSummary) -> dict[str, float]:
        if not cluster_summary.clusters:
            return {"mean_cluster_size": 0.0, "max_cluster_size": 0.0, "noise_ratio": 0.0}

        sizes = [c.size for c in cluster_summary.clusters if not c.is_noise]
        total_complaints = cluster_summary.clustered_complaints + cluster_summary.noise_complaints

        noise_ratio = (cluster_summary.noise_complaints / max(1, total_complaints))

        return {
            "total_clusters": float(cluster_summary.total_clusters),
            "mean_cluster_size": float(round(np.mean(sizes), 2)) if sizes else 0.0,
            "median_cluster_size": float(round(np.median(sizes), 2)) if sizes else 0.0,
            "max_cluster_size": float(max(sizes)) if sizes else 0.0,
            "noise_ratio": float(round(noise_ratio, 4))
        }
