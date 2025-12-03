# GraphRAG Medical Mining - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Clone Repository
```bash
git clone https://github.com/[your-username]/GraphRAG-Medical-Mining.git
cd GraphRAG-Medical-Mining
```

### Step 2: Get FREE API Keys

**Groq API (LLM - 100% FREE):**
1. Go to: https://console.groq.com
2. Sign up (no credit card needed)
3. Click "Create API Key"
4. Copy key (starts with `gsk_`)

**Neo4j Aura (Graph DB - FREE):**
1. Go to: https://neo4j.com/cloud/aura-free/
2. Sign up (no credit card)
3. Create free database
4. Copy connection URI, username, password

### Step 3: Configure
```bash
cp .env.example .env
# Edit .env with your API keys:
nano .env
```

### Step 4: Install & Run
```bash
# Install dependencies
pip install -r requirements.txt

# Download sample data
python scripts/download_sample_data.py

# Build knowledge graph
python src/graph_construction/build_graph.py

# Run Streamlit app
streamlit run deployment/streamlit/app.py
```

### Step 5: Deploy (Optional)
```bash
# Push to GitHub
git add .
git commit -m "Initial commit"
git push origin main

# Deploy to Streamlit Cloud
# 1. Go to streamlit.io/cloud
# 2. Connect GitHub repo
# 3. Add secrets (NEO4J_*, GROQ_API_KEY)
# 4. Click Deploy!
```

## 📊 Run Colab Notebook

Open in Colab:
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/[your-username]/GraphRAG-Medical-Mining/blob/main/notebooks/Complete_Pipeline.ipynb)

Add Colab secrets:
- GROQ_API_KEY
- NEO4J_URI
- NEO4J_PASSWORD

Run all cells!

## 🎥 Watch Demo Video

[Link to video](presentation/GraphRAG_Medical_Demo.mp4)

## 📧 Support

Issues? Email: [team-email]@sjsu.edu

---

**Total Setup Time: 5 minutes**  
**Total Cost: $0/month**  
**Queries per day: 14,400 (Groq free tier)**
