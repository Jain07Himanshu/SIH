# Algorithm & Mathematical Formulation

## 1. Multi-Signal Similarity Fusion
Let complaint $A$ and complaint $B$ be compared across 6 signals:
1. **Semantic Similarity** ($S_{sem} \in [0, 1]$):
   $$S_{sem} = \frac{\mathbf{v}_A \cdot \mathbf{v}_B}{\|\mathbf{v}_A\| \|\mathbf{v}_B\|}$$
2. **Lexical Similarity** ($S_{lex} \in [0, 1]$):
   $$S_{lex} = 0.6 \cdot \text{Jaccard}(T_A, T_B) + 0.4 \cdot \text{NgramOverlap}(N_A, N_B)$$
3. **Keyword Overlap** ($S_{kw} \in [0, 1]$):
   $$S_{kw} = \frac{|K_A \cap K_B|}{|K_A \cup K_B|}$$
4. **Category Compatibility** ($S_{cat} \in [0, 1]$):
   $$S_{cat} = \begin{cases} 1.0 & \text{if exact category match} \\ 0.65 & \text{if same parent domain} \\ 0.0 & \text{otherwise} \end{cases}$$
5. **Geographic Proximity** ($S_{geo} \in [0, 1]$):
   Using Haversine distance $d(A, B)$ in meters:
   $$S_{geo} = \exp\left(-\left(\frac{d}{\sigma_{geo}}\right)^2\right) \quad \text{for } d \le d_{max}$$
6. **Temporal Proximity** ($S_{temp} \in [0, 1]$):
   Using time difference $\Delta t$ in days:
   $$S_{temp} = 2^{-\frac{\Delta t}{t_{half}}}$$

### Dynamic Renormalization:
If geographic or temporal coordinates are absent, their weights are removed from the denominator:
$$S_{final} = \frac{\sum_{i \in \text{Active}} w_i \cdot S_i}{\sum_{i \in \text{Active}} w_i}$$

---

## 2. Decision Thresholds
- $S_{final} \ge \tau_{dup} \implies \mathbf{DUPLICATE}$
- $\tau_{poss} \le S_{final} < \tau_{dup} \implies \mathbf{POSSIBLY\_SIMILAR}$
- $S_{final} < \tau_{poss} \implies \mathbf{NEW\_ISSUE}$
- Needs Review Flag: $|S_{final} - \tau| \le \delta_{margin}$
