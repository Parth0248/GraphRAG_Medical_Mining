# GraphRAG Medical AI - Project Documentation

## 1. Executive Summary
GraphRAG Medical AI is an advanced intelligent information retrieval system designed to assist healthcare professionals. It combines the structured reasoning of **Knowledge Graphs** with the generative capabilities of **Large Language Models (LLMs)** and the reliability of **MLOps**. This hybrid "GraphRAG" approach ensures that answers are not just fluent but also factually grounded in verified medical data.

## 2. System Architecture

The system is built on a modular architecture comprising four key pillars:

1.  **Data Layer (Knowledge Graph)**: Neo4j database storing structured medical entities (Diseases, Drugs, Symptoms) and their relationships.
2.  **Intelligence Layer (RAG + LLM)**: Groq API (Llama-3.3-70B) for generating natural language responses augmented by graph context.
3.  **MLOps Layer**: A complete pipeline for training, validating, and monitoring predictive models using MLflow and LightGBM.
4.  **Application Layer**: A Streamlit-based web interface deployed on Google Cloud Run.

## 3. Data Flow & Components

### 3.1. Data Ingestion & Graph Construction
*   **Source**: PubMed Abstracts (Simulated/Real).
*   **Entity Extraction**: `src/preprocessing/entity_extractor.py` uses **BioBERT** (a biomedical-specific BERT model) to extract entities like *Diabetes* (Disease) or *Metformin* (Drug) from raw text.
*   **Graph Builder**: `src/graph_construction/build_graph.py` constructs the graph in Neo4j, creating nodes and relationships (e.g., `(Diabetes)-[:MENTIONED_IN]->(Abstract)`).

### 3.2. Retrieval Augmented Generation (RAG)
*   **Query Processing**: When a user asks a question, the system identifies key entities.
*   **Graph Traversal**: It queries Neo4j to find related neighbors (e.g., "What treats Diabetes?" -> finds linked Drugs).
*   **Context Injection**: This structured knowledge is formatted into a prompt for the LLM.
*   **Generation**: The LLM generates a response based *only* on the provided graph context, reducing hallucinations.

### 3.3. MLOps Pipeline
To ensure the system adapts to new data, we implemented a robust MLOps pipeline (`src/mlops/`):
1.  **Feature Store**: Extracts graph patterns into tabular data (Disease-Symptom matrices).
2.  **AutoML Training**: Trains LightGBM models to predict diseases based on symptoms.
3.  **Validation**: "Gatekeeper" checks model accuracy (>80%) before promotion.
4.  **Drift Detection**: Monitors data distribution to detect shifts (e.g., new symptom patterns) and trigger retraining.

## 4. Technology Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | Streamlit | Interactive Web UI |
| **Database** | Neo4j Aura | Graph Database (Knowledge Graph) |
| **LLM** | Groq (Llama-3) | Generative AI & Reasoning |
| **NLP** | BioBERT / Transformers | Named Entity Recognition (NER) |
| **MLOps** | MLflow | Experiment Tracking & Model Registry |
| **ML Model** | LightGBM | Gradient Boosting for Classification |
| **Deployment** | Google Cloud Run | Containerized Hosting |
| **Hosting** | Firebase Hosting | Secure URL & CDN |

## 5. Key Features & Use Cases

### 5.1. Intelligent Q&A
*   **Use Case**: A doctor asks, "What are the side effects of Lisinopril?"
*   **Mechanism**: GraphRAG retrieves "Lisinopril" nodes and their "Side Effect" connections to answer accurately.

### 5.2. Differential Diagnosis
*   **Use Case**: Input symptoms "Fever, Cough, Fatigue".
*   **Mechanism**: The system ranks diseases based on the overlap of symptoms in the Knowledge Graph (Jaccard Similarity).

### 5.3. Drug Safety Analysis
*   **Use Case**: Check interaction between "Aspirin" and "Warfarin".
*   **Mechanism**: Finds shortest paths between drugs in the graph to identify known interaction risks.

### 5.4. MLOps Dashboard
*   **Use Case**: Administrators monitor model health.
*   **Mechanism**: Displays training metrics, validation status, and data drift alerts.

## 6. Future Roadmap
*   **Real-time Learning**: Connect MLOps pipeline to live hospital records.
*   **Multimodal RAG**: Incorporate X-rays and MRI images into the graph.
*   **Federated Learning**: Train models across hospitals without sharing patient data.
