# CRISP‑DM for GraphRAG for Medical Data Mining

## 1. Business / Problem Understanding

Objective
- Build an evidence-backed QA system for medical queries that combines a knowledge graph and dense vector retrieval with LLM generation (GraphRAG).
- Provide concise, citation-aware answers and paths in the knowledge graph to support research and demonstrational clinical workflows.

Stakeholders
- Project team (data scientists, engineers)
- Clinical collaborators and domain experts
- Professors / sponsors
- Demo users (researchers, students); production clinical use requires further validation.

Success criteria
- Retrieval: Recall@10 ≈ 87.3% on MedQA (target consistent with repository results).
- Ranking: MRR ≈ 0.82.
- Generation: citation accuracy and factuality targets consistent with repository evaluations (citation accuracy ≈ 89–91%, hallucination rate ≈ 8.7%).
- Latency: average end‑to‑end latency ≈ 2.34s (demo target).
- Reproducibility: ability to run core pipeline via provided scripts, Dockerfile, and deployment docs.

Constraints and risks
- Sensitive data (PHI) requires ethical and legal review (IRB, HIPAA, GDPR).
- Domain bias (cardiology/oncology over-represented).
- LLM hallucinations and citation errors need mitigation.
- Compute limits for large models.

---

## 2. Data Understanding

Primary data sources (as described in the repo)
- PubMed / PMC abstracts subset (15,000 abstracts in repo description).
- Disease–symptom CSV (Kaggle-derived or internal; ~4,920 pairs).
- Drug–disease associations (DrugBank open subset; ~2,500 triplets).
- MedQA question set (1,273 questions; train/val/test splits used for evaluation).

Key artifacts in repository
- data/raw/ (raw documents)
- data/processed/entities.csv and relationships.csv
- embeddings (e.g., embeddings.npy) and FAISS index artifacts
- evaluation splits: medqa_train/val/test JSON files
- TESTING_SUMMARY.md and PROJECT_SUMMARY.md outlining dataset statistics and QA splits

Exploratory analyses to confirm
- Document counts, lengths, and distribution
- Entity counts and types (diseases, symptoms, drugs, anatomy, gene, biomarker)
- Relationship counts and PMI distribution
- Ontology mapping coverage (SNOMED‑CT, RxNorm, HPO)
- Missing & duplicate detection metrics

Tools used / recommended
- pandas, numpy for tabular analysis
- scispaCy / BioBERT for NER
- Neo4j queries for graph statistics
- matplotlib / seaborn for visualization

Checkpoint outputs
- Data inventory report (counts, distributions)
- Mapping coverage report (e.g., ~94.3% mapping as cited)
- A small manual validation sample (e.g., 500 entity normalization checks)

---

## 3. Data Preparation

Goals
- Clean and normalize documents.
- Extract and canonicalize entities and relations.
- Build a reproducible knowledge graph and vector embeddings.

Key steps performed / to perform (aligned with repo)
1. Text cleaning
   - Strip XML/HTML, normalize Unicode, handle abbreviations, remove very short abstracts (<50 words).
2. NER & normalization
   - Use BioBERT-based NER and scispaCy for entity extraction.
   - Map entities to ontologies: Diseases→SNOMED‑CT, Drugs→RxNorm, Symptoms→HPO.
   - Use fuzzy matching to merge variants and record canonical IDs.
3. Relation extraction
   - Sentence-level co‑occurrence and dependency-based pattern matching.
   - Compute PMI and threshold edges (PMI > 3.0 or occurrence in ≥ 3 documents).
4. Graph construction
   - Create heterogeneous Neo4j schema (node types: Disease, Symptom, Drug, Procedure, Anatomy, Gene, Biomarker).
   - Add node/edge properties: frequency, ontology_id, PMI weight, provenance.
   - Create indexes on node properties (name, type, ontology_id).
5. Embedding generation
   - Use BioBERT (768‑dim) to embed documents/entities.
   - Batch processing (32–64), truncate/pad to model max length.
   - Persist embeddings (npy) and build FAISS index (IndexFlatIP for small scale, IVF‑PQ for large).
6. Linking & provenance
   - Maintain mapping from graph nodes to source documents (title, DOI, offsets).
   - Store processing logs and provenance metadata.
7. Anonymization
   - Ensure no PHI remains in processed artifacts; apply regex-based redaction and document audits.

Artifacts and scripts (repository alignment)
- generate_project.py (exists in repo) and other scripts under src/ or scripts/ for extraction and processing
- embeddings.npy, faiss index files, Neo4j import/export scripts
- data_prep_report.json or equivalent logs (recommend adding if missing)

Validation checkpoints
- Manual review samples for entity normalization and relations
- PMI distribution checks and edge threshold sensitivity
- Verify FAISS nearest neighbors for curated seed queries

---

## 4. Modeling

Objectives
- Implement a hybrid retrieval pipeline combining graph traversal and dense retrieval.
- Fuse retrieval signals and produce high-quality context for LLM generation.
- Keep interfaces testable and reproducible.

Components and implemented choices (from repo)
1. Embedding model
   - BioBERT (dmis‑lab/biobert‑v1.1) producing 768‑dim vectors (document & entity embeddings).
2. Vector index & search
   - FAISS used (IndexFlatIP for exact small scale; IVF‑PQ option documented for scale).
   - Typical vector_top_k = 20.
3. Graph retrieval
   - 2‑hop traversal from query entities with intent-specific edge filtering.
4. Fusion & reranking
   - Reciprocal Rank Fusion (RRF) to combine graph and vector ranks.
   - Cross‑encoder reranker applied to top candidates (rerank top_k to get final top 5 contexts).
5. LLM generation
   - Use of a local or hosted LLM; prompt enforces use of provided context and citations.
   - Generation parameters per repo: temperature ≈ 0.3, top_p ≈ 0.9, max_tokens ≈ 512.
   - Ablation studies and prompt effects described in README.

Optional verification module
- Post‑generation fact‑checking or claim verification step (recommended to reduce hallucinations); not required but beneficial.

Hyperparameter tuning (documented approach)
- Grid search across: graph_hops (1–3), vector_top_k (10–50), rrf_k, llm_temperature, max_context_length.
- Cross‑validation on validation split (5‑fold) as documented.

Artifacts to save
- FAISS index files, embedding checkpoints, reranker model checkpoint, prompt templates, model_config JSON.

Validation
- Unit tests and integration tests (e.g., smoke tests already suggested earlier).
- End‑to‑end pipeline tests to ensure retrieval → generation behavior.

---

## 5. Evaluation

Metrics (consistent with README)
- Retrieval: Recall@5, Recall@10 (Recall@10 ≈ 87.3% reported), MRR (≈ 0.82), NDCG@10.
- Generation: ROUGE‑L (≈ 0.67 reported), BERTScore (≈ 0.84), manual medical factual accuracy (~91.3% in repo summary).
- Safety: Hallucination rate ≈ 8.7% as reported; citation accuracy ≈ 89–91%.
- System: end‑to‑end latency ≈ 2.34s, throughput ~25 queries/min.

Evaluation protocol (aligned)
- Use MedQA splits for retrieval and generation evaluation.
- Ground‑truth document annotations for retrieval evaluation.
- Manual review sample (e.g., 200 responses) for factual accuracy, citation accuracy, hallucination analysis (as in TESTING_SUMMARY.md).
- Statistical testing for significance vs baselines (paired t‑tests where used in repo).

Reporting & artifacts
- Evaluation reports, PR curves, ablation tables (present in README and TESTING_SUMMARY.md).
- Save evaluated model version, test logs, and annotated samples for audit.

Acceptance criteria
- Match repository targets: Recall@10 ≈ 87.3%, MRR ≈ 0.82, generation factuality and citation accuracy within reported ranges.

---

## 6. Deployment (aligned to repo)

Deployment goals
- Provide a reproducible demo and deployment path using repository artifacts.
- Ensure secure handling of sensitive data and operations.

Repository-supported deployment artifacts
- Dockerfile (present in repo)
- DEPLOYMENT_INSTRUCTIONS.txt (present)
- requirements.txt and setup.py
- Quickstart and instructions (QUICKSTART.md)

Recommended runtime architecture (consistent with repo)
- Neo4j for graph database (persisted)
- FAISS index served in‑memory or memory‑mapped
- LLM inference layer (hosted remote or local GPU); note the README discusses several LLM options
- API server (FastAPI) to orchestrate retrieval + generation
- Containerization via Docker for demo and reproducibility

MLOps and automation (note about verification)
- The repository currently contains deployment and reproducibility artifacts (Dockerfile, deployment instructions). The repo does NOT contain explicit Databricks pipeline configuration, notebooks, or job definitions that prove a Databricks MLOps pipeline is implemented.
- If you want to include "Databricks MLOps pipeline implemented" in documentation or slides, add pipeline artifacts (notebooks, job JSON, pipeline YAML, Databricks Model Registry entries) to the repo so the claim can be verified.
- Recommended MLOps practices: model versioning (MLflow / model registry), CI/CD via GitHub Actions, scheduled retraining jobs, and monitoring. You can implement these using Databricks, Airflow, or other MLOps platforms; the choice must be documented and artifacts added.

Security, monitoring, and compliance
- Store secrets in a secure vault (Databricks secret scope, GitHub Secrets, or HashiCorp Vault).
- TLS for external endpoints and access control for Neo4j.
- Audit logs and data retention policies for any sensitive data; do not include PHI in repo artifacts.

Deployment acceptance
- Demo endpoint returns citation-backed answers with acceptable latency for demo mode (≤ 3s).
- Docker-based demo runs reproducibly following DEPLOYMENT_INSTRUCTIONS.txt.