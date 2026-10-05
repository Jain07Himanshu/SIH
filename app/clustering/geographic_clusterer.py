import numpy as np
from sklearn.cluster import DBSCAN
from app.schemas.complaint import ComplaintRecord

class GeographicClusterer:
    @staticmethod
    def cluster_hotspots(complaints: list[ComplaintRecord], eps_km: float = 0.8, min_samples: int = 3) -> list[list[ComplaintRecord]]:
        coords = []
        valid_complaints = []
        for c in complaints:
            if c.latitude is not None and c.longitude is not None:
                coords.append([np.radians(c.latitude), np.radians(c.longitude)])
                valid_complaints.append(c)

        if len(coords) < min_samples:
            return []

        coords_arr = np.array(coords)
        # Earth radius = 6371.0088 km
        kms_per_radian = 6371.0088
        epsilon_radians = eps_km / kms_per_radian

        db = DBSCAN(eps=epsilon_radians, min_samples=min_samples, metric='haversine')
        labels = db.fit_predict(coords_arr)

        clusters: list[list[ComplaintRecord]] = []
        for lbl in set(labels):
            if lbl == -1:
                continue
            indices = [i for i, l in enumerate(labels) if l == lbl]
            clusters.append([valid_complaints[i] for i in indices])

        return clusters
