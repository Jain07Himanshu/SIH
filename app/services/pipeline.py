import time
import uuid
import numpy as np
from app.schemas.complaint import (
    ComplaintRecord,
    NormalizedComplaint,
    BatchProcessingReport
)
from app.schemas.similarity import SimilarityMatchResult
from app.schemas.issue import IssueRecord
from app.schemas.cluster import ClusterSummary
from app.preprocessing.normalizer import ComplaintNormalizer
from app.extraction.keywords import KeywordExtractor
from app.extraction.synonyms import SynonymManager
from app.classification.taxonomy import TaxonomyManager
from app.classification.classifier import CategoryClassifier
from app.embeddings.encoder import EmbeddingEncoder
from app.embeddings.vector_store import InMemoryVectorStore
from app.similarity.scorer import CompositeSimilarityScorer
from app.clustering.complaint_clusterer import ComplaintClusterer
from app.issue.issue_builder import IssueBuilder
from app.issue.issue_updater import IssueUpdater

class GrievanceIntelligencePipeline:
    def __init__(self,
                 taxonomy_manager: TaxonomyManager | None = None,
                 synonym_manager: SynonymManager | None = None,
                 embedding_encoder: EmbeddingEncoder | None = None,
                 vector_store: InMemoryVectorStore | None = None):
        
        self.taxonomy = taxonomy_manager or TaxonomyManager()
        self.synonyms = synonym_manager or SynonymManager()
        self.encoder = embedding_encoder or EmbeddingEncoder()
        self.normalizer = ComplaintNormalizer()
        self.keyword_extractor = KeywordExtractor(synonym_manager=self.synonyms)
        self.classifier = CategoryClassifier(taxonomy_manager=self.taxonomy, synonym_manager=self.synonyms)
        self.vector_store = vector_store or InMemoryVectorStore()
        self.scorer = CompositeSimilarityScorer()
        self.clusterer = ComplaintClusterer(scorer=self.scorer)
        self.issue_builder = IssueBuilder(taxonomy_manager=self.taxonomy)
        self.issue_updater = IssueUpdater(issue_builder=self.issue_builder)

        # In-memory issue state
        self.issues: dict[str, IssueRecord] = {}
        self.complaint_to_issue: dict[str, str] = {}
        self.normalized_cache: dict[str, NormalizedComplaint] = {}
        self.issue_counter = 1

    def process_single(self, raw_record: ComplaintRecord) -> tuple[NormalizedComplaint, SimilarityMatchResult | None, IssueRecord]:
        # 1. Normalize
        norm_complaint = self.normalizer.normalize_record(raw_record)

        # 2. Extract keywords
        norm_complaint.keywords = self.keyword_extractor.extract_keywords(norm_complaint.text.clean)
        self.normalized_cache[raw_record.complaint_id] = norm_complaint

        # 3. Embedding
        embedding = self.encoder.encode_one(norm_complaint.text.semantic)

        # 4. Classify category if not specified
        cat_pred = None
        if not raw_record.category or raw_record.category.upper() == "UNKNOWN":
            cat_pred = self.classifier.classify(norm_complaint.text.clean, embedding, self.encoder)
            raw_record.category = cat_pred.category_id
            raw_record.department = cat_pred.department_id

        # 5. Search for similar candidates
        top_candidates = self.vector_store.search(embedding, top_k=10)
        best_match: SimilarityMatchResult | None = None

        if top_candidates:
            for cand_id, _, cand_meta in top_candidates:
                cand_norm = self.normalized_cache.get(cand_id)
                if not cand_norm:
                    continue
                cand_emb, _ = self.vector_store.get(cand_id)
                match_res = self.scorer.score_pair(
                    raw_record,
                    cand_norm.raw_record,
                    emb_a=embedding,
                    emb_b=cand_emb,
                    kw_a=norm_complaint.keywords,
                    kw_b=cand_norm.keywords
                )
                if best_match is None or match_res.similarity_score > best_match.similarity_score:
                    best_match = match_res

        # 6. Index into vector store
        self.vector_store.add(
            raw_record.complaint_id,
            embedding,
            {"category": raw_record.category, "department": raw_record.department}
        )

        # 7. Issue assignment / creation
        target_issue: IssueRecord | None = None
        if best_match and best_match.match_type in ("DUPLICATE", "POSSIBLY_SIMILAR"):
            matched_issue_id = self.complaint_to_issue.get(best_match.matched_complaint_id)
            if matched_issue_id and matched_issue_id in self.issues:
                existing_issue = self.issues[matched_issue_id]
                target_issue = self.issue_updater.attach_complaint(
                    existing_issue,
                    norm_complaint,
                    best_match.similarity_score
                )
                self.complaint_to_issue[raw_record.complaint_id] = target_issue.issue_id

        if target_issue is None:
            new_id = f"ISS-{self.issue_counter:03d}"
            self.issue_counter += 1
            if cat_pred is None:
                cat_pred = self.classifier.classify(norm_complaint.text.clean, embedding, self.encoder)
            target_issue = self.issue_builder.build_issue(
                issue_id=new_id,
                normalized_complaints=[norm_complaint],
                category_pred=cat_pred,
                similarity_score=1.0
            )
            self.issues[new_id] = target_issue
            self.complaint_to_issue[raw_record.complaint_id] = new_id

        return norm_complaint, best_match, target_issue

    def process_batch(self, raw_records: list[ComplaintRecord]) -> tuple[list[IssueRecord], ClusterSummary, BatchProcessingReport]:
        start_t = time.perf_counter()
        job_id = f"JOB-{uuid.uuid4().hex[:8].upper()}"

        normalized_list: list[NormalizedComplaint] = []
        for r in raw_records:
            nc = self.normalizer.normalize_record(r)
            nc.keywords = self.keyword_extractor.extract_keywords(nc.text.clean)
            self.normalized_cache[r.complaint_id] = nc
            normalized_list.append(nc)

        texts = [nc.text.semantic for nc in normalized_list]
        embeddings = self.encoder.encode(texts)

        # Classify categories
        for i, nc in enumerate(normalized_list):
            if not nc.raw_record.category or nc.raw_record.category.upper() == "UNKNOWN":
                pred = self.classifier.classify(nc.text.clean, embeddings[i], self.encoder)
                nc.raw_record.category = pred.category_id
                nc.raw_record.department = pred.department_id

        # Index all into vector store
        vector_items = [(nc.complaint_id, embeddings[i], {"category": nc.raw_record.category}) for i, nc in enumerate(normalized_list)]
        self.vector_store.add_batch(vector_items)

        # Cluster complaints into underlying issues
        cluster_summary = self.clusterer.cluster(normalized_list, embeddings)

        resulting_issues: list[IssueRecord] = []
        id_to_norm = {nc.complaint_id: nc for nc in normalized_list}

        for cl in cluster_summary.clusters:
            cl_members = [id_to_norm[cid] for cid in cl.complaint_ids if cid in id_to_norm]
            if not cl_members:
                continue

            issue_id = f"ISS-{self.issue_counter:03d}"
            self.issue_counter += 1

            cat_pred = self.classifier.classify(cl_members[0].text.clean, embeddings[0], self.encoder)
            issue_rec = self.issue_builder.build_issue(
                issue_id=issue_id,
                normalized_complaints=cl_members,
                category_pred=cat_pred,
                similarity_score=cl.centroid_similarity
            )
            issue_rec.needs_review = cl.is_noise
            self.issues[issue_id] = issue_rec
            for cid in cl.complaint_ids:
                self.complaint_to_issue[cid] = issue_id
            resulting_issues.append(issue_rec)

        duration = round(time.perf_counter() - start_t, 3)
        report = BatchProcessingReport(
            job_id=job_id,
            total=len(raw_records),
            successful=len(raw_records),
            failed=0,
            duration_seconds=duration,
            errors=[]
        )

        return resulting_issues, cluster_summary, report
