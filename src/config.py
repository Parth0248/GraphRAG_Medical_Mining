"""Configuration management"""
import os
from dotenv import load_dotenv

load_dotenv()

# Neo4j
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# Groq API
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"  # Latest Llama 3.3, FREE, 14,400 req/day

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
