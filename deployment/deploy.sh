#!/bin/bash
# GraphRAG Medical Mining - Deployment Script (100% FREE)

echo "================================="
echo "GraphRAG Medical Mining Deployment"
echo "================================="

# Check Python
python3 --version || { echo "Python 3.8+ required"; exit 1; }

# Install dependencies
echo "\n📦 Installing dependencies..."
pip install -r requirements.txt --quiet

# Download sample data
echo "\n📥 Downloading sample data..."
python scripts/download_sample_data.py

# Setup Neo4j Aura (instructions)
echo "\n🗄️  Neo4j Aura Setup:"
echo "1. Go to: https://neo4j.com/cloud/aura-free/"
echo "2. Sign up (free, no credit card)"
echo "3. Create database"
echo "4. Copy connection details to .env"
read -p "Press Enter when Neo4j is ready..."

# Build knowledge graph
echo "\n🕸️  Building knowledge graph..."
python src/graph_construction/build_graph.py

# Setup Groq API
echo "\n🚀 Groq API Setup:"
echo "1. Go to: https://console.groq.com"
echo "2. Sign up (free, no credit card)"
echo "3. Get API key"
echo "4. Add to .env file"
read -p "Press Enter when Groq key is ready..."

# Test system
echo "\n🧪 Testing system..."
python -c "from src.generation.llm_generator import MedicalAnswerGenerator; print('✓ LLM works')"

# Deploy to Streamlit Cloud
echo "\n☁️  Streamlit Cloud Deployment:"
echo "1. Push code to GitHub"
echo "2. Go to: https://streamlit.io/cloud"
echo "3. Connect GitHub repo"
echo "4. Add secrets (NEO4J_*, GROQ_API_KEY)"
echo "5. Deploy!"

echo "\n✅ Setup complete!"
echo "Run locally: streamlit run deployment/streamlit/app.py"
