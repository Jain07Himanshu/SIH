import numpy as np
from sklearn.cluster import AgglomerativeClustering, DBSCAN
from collections import Counter
from app.core.config import get_config
from app.schemas.complaint import ComplaintRecord, NormalizedComplaint
from app.schemas.cluster import ClusterRecord, ClusterSummary
from app.similarity.scorer import CompositeSimilarityScorer

class ComplaintClusterer:
    def __init__(self, scorer: CompositeSimilarityScorer | None = None):
        self.config = get_config()
        self.scorer = scorer or CompositeSimilarityScorer()

    def build_distance_matrix(self, normalized_complaints: list[NormalizedComplaint], embeddings: np.ndarray) -> np.ndarray:
        n = len(normalized_complaints)
        sim_matrix = np.eye(n, dtype=np.float32)

        for i in range(n):
            for j in range(i + 1, n):
                res = self.scorer.score_pair(
                    normalized_complaints[i].raw_record,
                    normalized_complaints[j].raw_record,
                    emb_a=embeddings[i],
                    emb_b=embeddings[j],
                    kw_a=normalized_complaints[i].keywords,
                    kw_b=normalized_complaints[j].keywords
                )
                sim_matrix[i, j] = res.similarity_score
                sim_matrix[j, i] = res.similarity_score

        dist_matrix = np.clip(1.0 - sim_matrix, 0.0, 1.0)
        np.fill_diagonal(dist_matrix, 0.0)
        return dist_matrix

    def cluster(self, normalized_complaints: list[NormalizedComplaint], embeddings: np.ndarray) -> ClusterSummary:
        n = len(normalized_complaints)
        if n == 0:
            return ClusterSummary(total_clusters=0, clustered_complaints=0, noise_complaints=0, clusters=[])
        if n == 1:
            record = ClusterRecord(
                cluster_id=0,
                complaint_ids=[normalized_complaints[0].complaint_id],
                size=1,
                representative_complaint_id=normalized_complaints[0].complaint_id,
                representative_keywords=[k.term for k in normalized_complaints[0].keywords[:5]],
                category_id=normalized_complaints[0].raw_record.category,
                is_noise=False,
                centroid_similarity=1.0
            )
            return ClusterSummary(total_clusters=1, clustered_complaints=1, noise_complaints=0, clusters=[record])

        dist_matrix = self.build_distance_matrix(normalized_complaints, embeddings)

        cfg = self.config.clustering
        threshold = max(0.55, cfg.cluster_selection_epsilon)

        if cfg.algorithm == "hdbscan":
            try:
                import hdbscan
                clusterer = hdbscan.HDBSCAN(
                    min_cluster_size=max(2, cfg.min_cluster_size),
                    min_samples=cfg.min_samples,
                    metric="precomputed",
                    cluster_selection_epsilon=threshold
                )
                labels = clusterer.fit_predict(dist_matrix.astype(np.float64))
            except Exception:
                agg = AgglomerativeClustering(
                    n_clusters=None,
                    distance_threshold=threshold,
                    metric="precomputed",
                    linkage="average"
                )
                labels = agg.fit_predict(dist_matrix)
        elif cfg.algorithm == "dbscan":
            db = DBSCAN(eps=threshold, min_samples=cfg.min_samples, metric="precomputed")
            labels = db.fit_predict(dist_matrix)
        else:
            agg = AgglomerativeClustering(
                n_clusters=None,
                distance_threshold=threshold,
                metric="precomputed",
                linkage="average"
            )
            labels = agg.fit_predict(dist_matrix)

        unique_labels = set(labels)
        clusters: list[ClusterRecord] = []
        noise_count = 0

        for label in sorted(unique_labels):
            indices = [i for i, lbl in enumerate(labels) if lbl == label]
            c_ids = [normalized_complaints[i].complaint_id for i in indices]
            is_noise = (label == -1)

            if is_noise:
                noise_count += len(indices)
                for idx in indices:
                    nc = normalized_complaints[idx]
                    clusters.append(ClusterRecord(
                        cluster_id=None,
                        complaint_ids=[nc.complaint_id],
                        size=1,
                        representative_complaint_id=nc.complaint_id,
                        representative_keywords=[k.term for k in nc.keywords[:4]],
                        category_id=nc.raw_record.category,
                        is_noise=True,
                        centroid_similarity=1.0
                    ))
            else:
                cluster_embeddings = embeddings[indices]
                centroid = np.mean(cluster_embeddings, axis=0)
                centroid_norm = np.linalg.norm(centroid)
                if centroid_norm > 1e-9:
                    centroid = centroid / centroid_norm

                sims_to_centroid = np.dot(cluster_embeddings, centroid)
                rep_idx = indices[int(np.argmax(sims_to_centroid))]
                rep_id = normalized_complaints[rep_idx].complaint_id

                all_kws = []
                for i in indices:
                    all_kws.extend([k.term for k in normalized_complaints[i].keywords])
                top_kws = [term for term, _ in Counter(all_kws).most_common(6)]

                clusters.append(ClusterRecord(
                    cluster_id=int(label),
                    complaint_ids=c_ids,
                    size=len(c_ids),
                    representative_complaint_id=rep_id,
                    representative_keywords=top_kws,
                    category_id=normalized_complaints[rep_idx].raw_record.category,
                    is_noise=False,
                    centroid_similarity=float(np.mean(sims_to_centroid))
                ))

        clustered_count = sum(c.size for c in clusters if not c.is_noise)
        return ClusterSummary(
            total_clusters=len([c for c in clusters if not c.is_noise]),
            clustered_complaints=clustered_count,
            noise_complaints=noise_count,
            clusters=clusters
        )
