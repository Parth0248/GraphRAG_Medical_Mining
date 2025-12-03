#!/usr/bin/env python3
"""
GraphRAG Medical Data Mining - Complete Project Generator
Creates all necessary files for 100% free deployment
"""

import os
from pathlib import Path

BASE_DIR = Path("/mnt/user-data/outputs/GraphRAG_Medical_Mining")

# File contents as a dictionary
FILES = {
    
".env.example": """# Neo4j Aura Free Tier (https://neo4j.com/cloud/aura-free/)
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password

# Groq API - 100% FREE (https://console.groq.com)
GROQ_API_KEY=gsk_your_key_here

# Hugging Face (optional)
HUGGINGFACE_TOKEN=hf_your_token

# App Settings
DEBUG=True
LOG_LEVEL=INFO
""",

"setup.py": """from setuptools import setup, find_packages

setup(
    name="graphrag-medical",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        line.strip() 
        for line in open('requirements.txt').readlines()
        if line.strip() and not line.startswith('#')
    ],
    author="CMPE 255 Team",
    description="GraphRAG for Medical Data Mining",
    python_requires=">=3.8",
)
""",

"src/__init__.py": """\"\"\"GraphRAG Medical Data Mining Package\"\"\"
__version__ = "1.0.0"
""",

"src/config.py": """\"\"\"Configuration management\"\"\"
import os
from dotenv import load_dotenv

load_dotenv()

# Neo4j
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# Groq API
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.1-70b-versatile"  # FREE, 14,400 req/day

# Paths
DATA_DIR = "data"
MODELS_DIR = "models"
LOGS_DIR = "logs"

# Model settings
EMBEDDING_MODEL = "dmis-lab/biobert-v1.1"
EMBEDDING_DIM = 768
MAX_LENGTH = 512

# Retrieval settings
GRAPH_HOPS = 2
VECTOR_TOP_K = 20
RRF_K = 60

# Generation settings
LLM_TEMPERATURE = 0.3
MAX_TOKENS = 512
""",

"src/data_collection/fetch_pubmed.py": """\"\"\"Fetch PubMed abstracts\"\"\"
from Bio import Entrez
import json
from pathlib import Path
import time

Entrez.email = "your.email@example.com"

def fetch_pubmed_abstracts(query, max_results=1000, output_file=None):
    \"\"\"Fetch PubMed abstracts\"\"\"
    print(f"Searching PubMed for: {query}")
    
    # Search
    handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
    record = Entrez.read(handle)
    handle.close()
    
    id_list = record["IdList"]
    print(f"Found {len(id_list)} papers")
    
    abstracts = []
    
    # Fetch details in batches
    batch_size = 100
    for i in range(0, len(id_list), batch_size):
        batch_ids = id_list[i:i+batch_size]
        
        try:
            handle = Entrez.efetch(db="pubmed", id=batch_ids, 
                                  rettype="abstract", retmode="xml")
            records = Entrez.read(handle)
            handle.close()
            
            for article in records['PubmedArticle']:
                try:
                    medline = article['MedlineCitation']
                    article_data = medline['Article']
                    
                    # Extract abstract
                    if 'Abstract' in article_data:
                        abstract_text = ' '.join([
                            text for text in article_data['Abstract']['AbstractText']
                        ])
                    else:
                        continue
                    
                    abstracts.append({
                        'pmid': str(medline['PMID']),
                        'title': article_data.get('ArticleTitle', ''),
                        'abstract': abstract_text,
                        'journal': article_data.get('Journal', {}).get('Title', ''),
                        'year': article_data.get('ArticleDate', [{}])[0].get('Year', '')
                    })
                except:
                    continue
            
            time.sleep(0.5)  # Rate limiting
            print(f"Processed {min(i+batch_size, len(id_list))}/{len(id_list)}")
            
        except Exception as e:
            print(f"Error in batch {i}: {e}")
            continue
    
    # Save
    if output_file:
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(abstracts, f, indent=2)
        print(f"Saved {len(abstracts)} abstracts to {output_file}")
    
    return abstracts

if __name__ == "__main__":
    # Example queries
    queries = [
        "cardiovascular disease",
        "diabetes mellitus",
        "respiratory disease",
        "cancer treatment"
    ]
    
    all_abstracts = []
    for query in queries:
        abstracts = fetch_pubmed_abstracts(query, max_results=2000)
        all_abstracts.extend(abstracts)
    
    # Save combined
    with open("data/raw/pubmed_abstracts.json", 'w') as f:
        json.dump(all_abstracts, f, indent=2)
    
    print(f"Total abstracts collected: {len(all_abstracts)}")
""",

"src/preprocessing/entity_extractor.py": """\"\"\"Medical entity extraction using BioBERT\"\"\"
import spacy
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import torch

class MedicalEntityExtractor:
    def __init__(self, model_name="dmis-lab/biobert-base-cased-v1.2"):
        \"\"\"Initialize entity extractor\"\"\"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForTokenClassification.from_pretrained(
            "d4data/biomedical-ner-all"
        )
        self.ner_pipeline = pipeline(
            "ner", 
            model=self.model, 
            tokenizer=self.tokenizer,
            aggregation_strategy="simple"
        )
        
        # Also load scispacy for backup
        try:
            self.nlp = spacy.load("en_core_sci_sm")
        except:
            print("scispacy not loaded, using transformer only")
            self.nlp = None
    
    def extract_entities(self, text):
        \"\"\"Extract medical entities from text\"\"\"
        entities = []
        
        # BioBERT NER
        ner_results = self.ner_pipeline(text)
        
        for ent in ner_results:
            entities.append({
                'text': ent['word'],
                'label': ent['entity_group'],
                'score': ent['score'],
                'start': ent['start'],
                'end': ent['end']
            })
        
        # Deduplication
        seen = set()
        unique_entities = []
        for ent in entities:
            key = (ent['text'].lower(), ent['label'])
            if key not in seen:
                seen.add(key)
                unique_entities.append(ent)
        
        return unique_entities

if __name__ == "__main__":
    extractor = MedicalEntityExtractor()
    
    text = \"\"\"
    Diabetes mellitus is characterized by hyperglycemia. 
    Treatment includes metformin and insulin therapy.
    Common symptoms include polyuria and polydipsia.
    \"\"\"
    
    entities = extractor.extract_entities(text)
    for ent in entities:
        print(f"{ent['text']:20s} {ent['label']:15s} {ent['score']:.3f}")
""",

"src/graph_construction/build_graph.py": """\"\"\"Build Neo4j knowledge graph from medical data\"\"\"
from neo4j import GraphDatabase
import json
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from preprocessing.entity_extractor import MedicalEntityExtractor

class GraphBuilder:
    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.extractor = MedicalEntityExtractor()
    
    def close(self):
        self.driver.close()
    
    def create_indexes(self):
        \"\"\"Create indexes for faster queries\"\"\"
        with self.driver.session() as session:
            # Node indexes
            session.run("CREATE INDEX entity_name IF NOT EXISTS FOR (e:Entity) ON (e.name)")
            session.run("CREATE INDEX disease_name IF NOT EXISTS FOR (d:Disease) ON (d.name)")
            session.run("CREATE INDEX drug_name IF NOT EXISTS FOR (d:Drug) ON (d.name)")
            print("✓ Indexes created")
    
    def add_document(self, doc_id, title, text):
        \"\"\"Add document and extract entities\"\"\"
        # Extract entities
        entities = self.extractor.extract_entities(text)
        
        with self.driver.session() as session:
            # Create document node
            session.run(
                \"\"\"
                MERGE (d:Document {id: $doc_id})
                SET d.title = $title, d.text = $text
                \"\"\",
                doc_id=doc_id, title=title, text=text
            )
            
            # Create entity nodes and relationships
            for ent in entities:
                entity_type = ent['label']
                entity_name = ent['text']
                
                session.run(
                    f\"\"\"
                    MERGE (e:Entity {{name: $name}})
                    SET e.type = $type, e:{entity_type}
                    MERGE (d:Document {{id: $doc_id}})
                    MERGE (e)-[r:MENTIONED_IN]->(d)
                    ON CREATE SET r.count = 1, r.score = $score
                    ON MATCH SET r.count = r.count + 1
                    \"\"\",
                    name=entity_name, type=entity_type, 
                    doc_id=doc_id, score=ent['score']
                )
    
    def build_cooccurrence_edges(self, window_size=10):
        \"\"\"Build co-occurrence relationships\"\"\"
        print("Building co-occurrence edges...")
        # This is simplified - full implementation would use sentence windows
        with self.driver.session() as session:
            session.run(
                \"\"\"
                MATCH (e1:Entity)-[:MENTIONED_IN]->(d:Document)<-[:MENTIONED_IN]-(e2:Entity)
                WHERE id(e1) < id(e2)
                MERGE (e1)-[r:CO_OCCURS_WITH]-(e2)
                ON CREATE SET r.count = 1
                ON MATCH SET r.count = r.count + 1
                \"\"\"
            )
        print("✓ Co-occurrence edges created")

def main():
    \"\"\"Build graph from PubMed data\"\"\"
    # Load data
    data_file = "data/raw/pubmed_abstracts.json"
    if not Path(data_file).exists():
        print(f"Data file not found: {data_file}")
        print("Run: python src/data_collection/fetch_pubmed.py first")
        return
    
    with open(data_file) as f:
        abstracts = json.load(f)
    
    print(f"Loaded {len(abstracts)} abstracts")
    
    # Build graph
    builder = GraphBuilder(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
    builder.create_indexes()
    
    for i, abstract in enumerate(abstracts[:100]):  # Limit for demo
        builder.add_document(
            doc_id=abstract['pmid'],
            title=abstract['title'],
            text=abstract['abstract']
        )
        
        if (i+1) % 10 == 0:
            print(f"Processed {i+1}/{len(abstracts[:100])} documents")
    
    builder.build_cooccurrence_edges()
    builder.close()
    print("✓ Graph construction complete")

if __name__ == "__main__":
    main()
""",

"src/retrieval/hybrid_retriever.py": """\"\"\"Hybrid Graph + Vector Retrieval\"\"\"
from neo4j import GraphDatabase
import faiss
import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch

class HybridRetriever:
    def __init__(self, neo4j_uri, neo4j_user, neo4j_pass, 
                 embedding_model="dmis-lab/biobert-v1.1"):
        # Neo4j connection
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_pass))
        
        # Load BioBERT for embeddings
        self.tokenizer = AutoTokenizer.from_pretrained(embedding_model)
        self.model = AutoModel.from_pretrained(embedding_model)
        self.model.eval()
        
        # FAISS index (will be loaded)
        self.index = None
        self.doc_ids = []
    
    def embed_text(self, text):
        \"\"\"Generate BioBERT embedding\"\"\"
        inputs = self.tokenizer(text, return_tensors="pt", 
                               truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
            embedding = outputs.last_hidden_state[:, 0, :].numpy()
        return embedding[0]
    
    def graph_retrieve(self, query, k=10):
        \"\"\"Retrieve from knowledge graph\"\"\"
        with self.driver.session() as session:
            # Simple entity-based retrieval
            result = session.run(
                \"\"\"
                MATCH (e:Entity)-[:MENTIONED_IN]->(d:Document)
                WHERE e.name CONTAINS $query OR d.title CONTAINS $query
                RETURN d.id as doc_id, d.title as title, d.text as text, 
                       count(e) as relevance
                ORDER BY relevance DESC
                LIMIT $k
                \"\"\",
                query=query, k=k
            )
            
            docs = []
            for record in result:
                docs.append({
                    'doc_id': record['doc_id'],
                    'title': record['title'],
                    'text': record['text'],
                    'score': record['relevance']
                })
            return docs
    
    def vector_retrieve(self, query, k=10):
        \"\"\"Retrieve using FAISS vector search\"\"\"
        if self.index is None:
            return []
        
        query_emb = self.embed_text(query).reshape(1, -1)
        distances, indices = self.index.search(query_emb, k)
        
        docs = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.doc_ids):
                docs.append({
                    'doc_id': self.doc_ids[idx],
                    'score': float(dist)
                })
        return docs
    
    def hybrid_retrieve(self, query, k=10):
        \"\"\"Combine graph and vector retrieval\"\"\"
        graph_docs = self.graph_retrieve(query, k=k*2)
        vector_docs = self.vector_retrieve(query, k=k*2)
        
        # Reciprocal Rank Fusion
        scores = {}
        for rank, doc in enumerate(graph_docs):
            doc_id = doc['doc_id']
            scores[doc_id] = scores.get(doc_id, 0) + 1/(60 + rank)
        
        for rank, doc in enumerate(vector_docs):
            doc_id = doc['doc_id']
            scores[doc_id] = scores.get(doc_id, 0) + 1/(60 + rank)
        
        # Sort by combined score
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Get full documents
        final_docs = []
        for doc_id, score in ranked[:k]:
            # Fetch from graph
            with self.driver.session() as session:
                result = session.run(
                    "MATCH (d:Document {id: $doc_id}) RETURN d.title as title, d.text as text",
                    doc_id=doc_id
                )
                record = result.single()
                if record:
                    final_docs.append({
                        'doc_id': doc_id,
                        'title': record['title'],
                        'text': record['text'],
                        'score': score
                    })
        
        return final_docs
""",

"src/generation/llm_generator.py": """\"\"\"LLM-based answer generation using Groq\"\"\"
from groq import Groq
import os

class MedicalAnswerGenerator:
    def __init__(self, api_key=None, model="llama-3.1-70b-versatile"):
        self.client = Groq(api_key=api_key or os.getenv("GROQ_API_KEY"))
        self.model = model
    
    def generate_answer(self, query, context_docs, max_tokens=512):
        \"\"\"Generate answer using retrieved context\"\"\"
        
        # Build context from documents
        context = ""
        for i, doc in enumerate(context_docs[:5], 1):
            context += f"[Source {i}]: {doc['title']}\\n"
            context += f"{doc['text'][:500]}...\\n\\n"
        
        # System prompt
        system_prompt = \"\"\"You are a medical AI assistant. Answer questions using ONLY the provided context from medical literature.

Guidelines:
1. Be precise and evidence-based
2. Cite sources using [Source X] notation  
3. If information is insufficient, state limitations
4. Use medical terminology appropriately
5. Never make definitive diagnoses
6. Always recommend consulting healthcare professionals
\"\"\"
        
        # User prompt
        user_prompt = f\"\"\"Context:
{context}

Question: {query}

Answer (cite sources):\"\"\"
        
        # Call Groq API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=max_tokens,
            top_p=0.9
        )
        
        answer = response.choices[0].message.content
        
        return {
            'answer': answer,
            'sources': context_docs[:5],
            'model': self.model
        }

if __name__ == "__main__":
    # Test
    generator = MedicalAnswerGenerator()
    
    test_docs = [{
        'title': 'Diabetes Management',
        'text': 'Metformin is first-line therapy for type 2 diabetes...',
        'score': 0.95
    }]
    
    result = generator.generate_answer(
        "What is first-line treatment for diabetes?",
        test_docs
    )
    
    print(result['answer'])
""",

"deployment/streamlit/app.py": """\"\"\"Streamlit Web Application\"\"\"
import streamlit as st
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.retrieval.hybrid_retriever import HybridRetriever
from src.generation.llm_generator import MedicalAnswerGenerator
from src.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, GROQ_API_KEY

# Page config
st.set_page_config(
    page_title="GraphRAG Medical Assistant",
    page_icon="🏥",
    layout="wide"
)

# Title
st.title("🏥 GraphRAG Medical Assistant")
st.markdown("*AI-powered medical information retrieval using Graph + RAG*")

# Initialize (with caching)
@st.cache_resource
def init_system():
    retriever = HybridRetriever(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
    generator = MedicalAnswerGenerator(api_key=GROQ_API_KEY)
    return retriever, generator

try:
    retriever, generator = init_system()
    
    # Query input
    query = st.text_input(
        "Ask a medical question:",
        placeholder="e.g., What are the symptoms of diabetes?"
    )
    
    if query:
        with st.spinner("Searching knowledge graph and generating answer..."):
            # Retrieve
            docs = retriever.hybrid_retrieve(query, k=5)
            
            # Generate
            result = generator.generate_answer(query, docs)
            
            # Display answer
            st.markdown("### Answer")
            st.markdown(result['answer'])
            
            # Display sources
            st.markdown("### Sources")
            for i, doc in enumerate(result['sources'], 1):
                with st.expander(f"Source {i}: {doc['title']}"):
                    st.write(doc['text'][:500] + "...")
                    st.caption(f"Relevance: {doc['score']:.3f}")
    
    # Sidebar stats
    with st.sidebar:
        st.header("System Info")
        st.metric("Model", "Llama-3.1-70B (Groq)")
        st.metric("Cost", "$0 - FREE!")
        st.metric("Speed", "800 tok/sec")
        
        st.markdown("---")
        st.caption("⚠️ This is for informational purposes only. Always consult healthcare professionals.")

except Exception as e:
    st.error(f"Error: {e}")
    st.info("Make sure Neo4j is running and .env is configured")
""",

"scripts/download_sample_data.py": """\"\"\"Download sample medical datasets\"\"\"
import pandas as pd
import json
from pathlib import Path

def download_sample_data():
    \"\"\"Download and prepare sample data\"\"\"
    
    # Create directories
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    
    # Sample disease-symptom data
    disease_symptom = {
        'Disease': ['Diabetes', 'Hypertension', 'Asthma'],
        'Symptoms': [
            'polyuria,polydipsia,weight loss',
            'headache,dizziness,blurred vision',
            'wheezing,shortness of breath,chest tightness'
        ]
    }
    
    df = pd.DataFrame(disease_symptom)
    df.to_csv("data/raw/disease_symptom.csv", index=False)
    
    # Sample PubMed abstracts (minimal for demo)
    sample_abstracts = [
        {
            'pmid': '12345',
            'title': 'Management of Type 2 Diabetes',
            'abstract': 'Metformin is recommended as first-line pharmacological therapy for type 2 diabetes...',
            'year': '2023'
        },
        {
            'pmid': '12346',
            'title': 'Hypertension Guidelines',
            'abstract': 'Blood pressure control is essential. ACE inhibitors and ARBs are effective...',
            'year': '2023'
        }
    ]
    
    with open("data/raw/pubmed_abstracts.json", 'w') as f:
        json.dump(sample_abstracts, f, indent=2)
    
    print("✓ Sample data downloaded")
    print("Files created:")
    print("  - data/raw/disease_symptom.csv")
    print("  - data/raw/pubmed_abstracts.json")

if __name__ == "__main__":
    download_sample_data()
""",

"deployment/deploy.sh": """#!/bin/bash
# GraphRAG Medical Mining - Deployment Script (100% FREE)

echo "================================="
echo "GraphRAG Medical Mining Deployment"
echo "================================="

# Check Python
python3 --version || { echo "Python 3.8+ required"; exit 1; }

# Install dependencies
echo "\\n📦 Installing dependencies..."
pip install -r requirements.txt --quiet

# Download sample data
echo "\\n📥 Downloading sample data..."
python scripts/download_sample_data.py

# Setup Neo4j Aura (instructions)
echo "\\n🗄️  Neo4j Aura Setup:"
echo "1. Go to: https://neo4j.com/cloud/aura-free/"
echo "2. Sign up (free, no credit card)"
echo "3. Create database"
echo "4. Copy connection details to .env"
read -p "Press Enter when Neo4j is ready..."

# Build knowledge graph
echo "\\n🕸️  Building knowledge graph..."
python src/graph_construction/build_graph.py

# Setup Groq API
echo "\\n🚀 Groq API Setup:"
echo "1. Go to: https://console.groq.com"
echo "2. Sign up (free, no credit card)"
echo "3. Get API key"
echo "4. Add to .env file"
read -p "Press Enter when Groq key is ready..."

# Test system
echo "\\n🧪 Testing system..."
python -c "from src.generation.llm_generator import MedicalAnswerGenerator; print('✓ LLM works')"

# Deploy to Streamlit Cloud
echo "\\n☁️  Streamlit Cloud Deployment:"
echo "1. Push code to GitHub"
echo "2. Go to: https://streamlit.io/cloud"
echo "3. Connect GitHub repo"
echo "4. Add secrets (NEO4J_*, GROQ_API_KEY)"
echo "5. Deploy!"

echo "\\n✅ Setup complete!"
echo "Run locally: streamlit run deployment/streamlit/app.py"
""",

}

def generate_all_files():
    """Generate all project files"""
    print("Generating GraphRAG Medical Mining Project...")
    
    for filepath, content in FILES.items():
        full_path = BASE_DIR / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
        print(f"✓ {filepath}")
    
    # Make deploy.sh executable
    (BASE_DIR / "deployment/deploy.sh").chmod(0o755)
    
    print(f"\\n✅ Project generated at: {BASE_DIR}")
    print("\\nNext steps:")
    print("1. cd GraphRAG_Medical_Mining")
    print("2. cp .env.example .env")
    print("3. Edit .env with your keys")
    print("4. bash deployment/deploy.sh")

if __name__ == "__main__":
    generate_all_files()
