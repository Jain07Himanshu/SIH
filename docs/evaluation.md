# Evaluation & Benchmark Methodology

## Key Evaluation Metrics
1. **Duplicate Detection**:
   - Precision: $\frac{TP}{TP + FP}$
   - Recall: $\frac{TP}{TP + FN}$
   - F1 Score: $\frac{2 \cdot P \cdot R}{P + R}$
2. **Category Classification**:
   - Top-1 Accuracy: Accuracy of primary predicted category vs ground truth.
3. **Clustering Quality**:
   - Adjusted Rand Index (ARI)
   - Cluster Purity & Noise Ratio
4. **Latency & Throughput**:
   - Single Complaint Latency ($P_{50}, P_{95} < 50\text{ms}$)
   - Batch Processing Throughput ($> 250\text{ complaints/sec}$)
