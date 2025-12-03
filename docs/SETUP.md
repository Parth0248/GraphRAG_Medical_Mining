# Setup and Installation Guide

## Prerequisites

*   **Python**: 3.8 or higher
*   **Git**: For version control
*   **Neo4j Aura**: Free tier account (for the Knowledge Graph)
*   **Groq API Key**: Free API key (for the LLM)
*   **Google Cloud SDK**: For deployment (optional)

## Local Development Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/[your-username]/GraphRAG-Medical-Mining.git
    cd GraphRAG-Medical-Mining
    ```

2.  **Create Virtual Environment**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\Activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Configuration**
    Create a `.env` file in the root directory:
    ```ini
    NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
    NEO4J_USERNAME=neo4j
    NEO4J_PASSWORD=your-password
    GROQ_API_KEY=gsk_...
    ```

5.  **Build the Knowledge Graph**
    This script fetches data and populates Neo4j:
    ```bash
    python src/graph_construction/build_graph.py
    ```

6.  **Run the Application**
    ```bash
    streamlit run deployment/streamlit/app_final.py
    ```

## Deployment

See `WALKTHROUGH.md` for detailed deployment steps using Google Cloud Run and Firebase.
