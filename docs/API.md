# API Documentation

The backend logic is modularized in `src/`. While the primary interface is Streamlit, the core components can be used programmatically.

## Core Modules

### 1. Entity Extraction (`src.preprocessing.entity_extractor`)

```python
from src.preprocessing.entity_extractor import MedicalEntityExtractor

extractor = MedicalEntityExtractor()
entities = extractor.extract_entities("Patient presents with Type 2 Diabetes and hypertension.")
# Returns: [{'text': 'Type 2 Diabetes', 'label': 'DISEASE'}, {'text': 'hypertension', 'label': 'DISEASE'}]
```

### 2. Graph Retrieval (`src.retrieval.hybrid_retriever`)

```python
from src.retrieval.hybrid_retriever import HybridRetriever

retriever = HybridRetriever(neo4j_uri, neo4j_user, neo4j_password)
context = retriever.retrieve("What treats Diabetes?", top_k=5)
# Returns: List of relevant documents/graph paths
```

### 3. LLM Generation (`src.generation.llm_generator`)

```python
from src.generation.llm_generator import LLMGenerator

generator = LLMGenerator(api_key="gsk_...")
answer = generator.generate_answer(query="What treats Diabetes?", context=context)
# Returns: "Metformin is a primary treatment..."
```

### 4. MLOps Pipeline (`src.mlops.pipeline`)

```python
from src.mlops.pipeline import MLOpsPipeline

pipeline = MLOpsPipeline()
pipeline.run_ingestion()  # Fetches data from Neo4j
pipeline.run_training()   # Trains LightGBM model
pipeline.check_drift()    # Checks for data drift
```

## External APIs Used

*   **Neo4j Aura**: Uses Bolt protocol (port 7687).
*   **Groq API**: Uses `chat.completions.create` (Llama-3 model).
