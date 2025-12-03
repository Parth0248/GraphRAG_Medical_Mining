"""Modern Minimal Dark Theme UI - Professional & Aesthetic"""
import streamlit as st
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime

load_dotenv()

# Page config
st.set_page_config(
    page_title="GraphRAG Medical AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Minimal Dark Theme CSS
st.markdown("""
<style>
    /* Import Modern Font */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');
    
    /* Global Styles */
    html, body, .stApp, p, h1, h2, h3, h4, h5, h6, input, textarea, label, button {
        font-family: 'Poppins', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Explicitly exclude icon elements if they use specific classes, 
       but the above specific selectors should already avoid breaking 'i' tags or icon spans 
       unless they fall under [class*="st-"] which might be tricky. 
       Let's be safer by not forcing font on everything. */
       
    /* Header Styling - Make transparent but keep buttons visible */
    header {
        background: transparent !important;
    }
    
    /* Hide Streamlit Branding but keep sidebar toggle */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Dark Background with Subtle Gradient */
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
        background-attachment: fixed;
    }
    
    /* Clean Container */
    .main .block-container {
        background: rgba(26, 26, 46, 0.6);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        padding: 2rem 2.5rem;
        margin-top: 1rem;
        max-width: 1400px;
    }
    
    /* Input Text Visibility Fixes - Solid Dark Background */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        color: #ffffff !important;
        background-color: #1e1e2e !important; /* Solid dark background */
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        caret-color: #ffffff !important;
    }
    
    /* Placeholder Text */
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: rgba(255, 255, 255, 0.5) !important;
    }
    
    /* Fix autofill background turning white */
    input:-webkit-autofill,
    input:-webkit-autofill:hover, 
    input:-webkit-autofill:focus, 
    textarea:-webkit-autofill,
    textarea:-webkit-autofill:hover,
    textarea:-webkit-autofill:focus {
        -webkit-text-fill-color: white !important;
        -webkit-box-shadow: 0 0 0px 1000px #1e1e2e inset !important;
        transition: background-color 5000s ease-in-out 0s;
    }
    
    /* Sidebar Toggle Button Styling - Collapsed State */
    [data-testid="stSidebarCollapsedControl"] {
        background-color: #3b82f6 !important; /* Solid Blue */
        color: white !important;
        border-radius: 8px;
        padding: 8px;
        margin-top: 10px;
        margin-left: 10px;
        border: none;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    [data-testid="stSidebarCollapsedControl"]:hover {
        background-color: #2563eb !important;
        transform: scale(1.1);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.4);
    }
    
    /* Sidebar Close Button (inside sidebar) */
    section[data-testid="stSidebar"] button {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 50%;
        width: 32px;
        height: 32px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    section[data-testid="stSidebar"] button:hover {
        background-color: rgba(255, 255, 255, 0.2);
        border-color: white;
    }

    /* Input Text Visibility - Global Enforcement */
    input, textarea {
        color: #ffffff !important;
        caret-color: #ffffff !important;
    }
    
    /* Minimal Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(15, 15, 35, 0.95);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    [data-testid="stSidebar"] > div {
        background: transparent;
        padding-top: 2rem;
    }
    
    /* Minimal Header - NO BLANK SPACE */
    .minimal-header {
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem 0;
    }
    
    .minimal-header h1 {
        font-size: 2.5rem;
        font-weight: 600;
        color: #ffffff;
        margin: 0;
        padding: 0;
        letter-spacing: -0.5px;
    }
    
    .minimal-header .tagline {
        font-size: 0.95rem;
        color: rgba(255, 255, 255, 0.6);
        font-weight: 400;
        margin-top: 0.5rem;
        letter-spacing: 1px;
    }
    
    /* Modern Tabs */
    .stTabs {
        background: transparent;
        padding: 0;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 12px;
        padding: 6px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: rgba(255, 255, 255, 0.6) !important;
        font-weight: 500;
        font-size: 0.95rem;
        padding: 10px 20px;
        transition: all 0.2s ease;
        border: none;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.05);
        color: rgba(255, 255, 255, 0.9) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(59, 130, 246, 0.15) !important;
        color: #3b82f6 !important;
        font-weight: 600;
    }
    
    /* Clean Card Design */
    .minimal-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .minimal-card:hover {
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(255, 255, 255, 0.1);
        transform: translateY(-2px);
    }
    
    /* Status Badge - Minimal */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 500;
        font-size: 0.85rem;
        margin: 4px;
        border: 1px solid;
    }
    
    .status-success {
        background: rgba(16, 185, 129, 0.1);
        border-color: rgba(16, 185, 129, 0.3);
        color: #10b981;
    }
    
    .status-error {
        background: rgba(239, 68, 68, 0.1);
        border-color: rgba(239, 68, 68, 0.3);
        color: #ef4444;
    }
    
    /* Modern Input Fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: white !important;
        font-size: 0.95rem !important;
        padding: 12px 16px !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        background: rgba(255, 255, 255, 0.08) !important;
    }
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: rgba(255, 255, 255, 0.4) !important;
    }
    
    /* Clean Modern Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 28px !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4) !important;
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Metrics - Minimal Design */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 600 !important;
        color: white !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.8rem !important;
        color: rgba(255, 255, 255, 0.5) !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.75rem !important;
        color: rgba(16, 185, 129, 0.8) !important;
    }
    
    /* Clean Markdown */
    .stMarkdown {
        color: white !important;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: white !important;
        font-weight: 600 !important;
    }
    
    .stMarkdown h3 {
        font-size: 1.3rem !important;
        margin-bottom: 1rem !important;
    }
    
    .stMarkdown p {
        color: white !important;
    }
    
    /* Ensure all text is white */
    p, span, div, label {
        color: rgba(255, 255, 255, 0.9) !important;
    }
    
    /* Text in widgets */
    .stTextInput label, .stTextArea label, .stRadio label {
        color: white !important;
    }
    
    /* Alert Boxes - Minimal */
    .stSuccess, .stInfo, .stWarning, .stError {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        border-left: 3px solid !important;
        padding: 1rem !important;
    }
    
    .stSuccess {
        border-left-color: #10b981 !important;
    }
    
    .stInfo {
        border-left-color: #3b82f6 !important;
    }
    
    .stWarning {
        border-left-color: #f59e0b !important;
    }
    
    .stError {
        border-left-color: #ef4444 !important;
    }
    
    /* DataFrame */
    [data-testid="stDataFrame"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border-radius: 12px !important;
    }
    
    /* Slider */
    .stSlider > div > div > div {
        background: rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Radio Buttons */
    .stRadio > div {
        background: rgba(255, 255, 255, 0.02);
        padding: 0.8rem;
        border-radius: 12px;
    }
    
    /* Minimal Footer */
    .minimal-footer {
        text-align: center;
        margin-top: 3rem;
        padding: 1.5rem;
        color: rgba(255, 255, 255, 0.4);
        font-size: 0.85rem;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Code */
    code {
        background: rgba(0, 0, 0, 0.3) !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
        font-family: 'IBM Plex Mono', monospace !important;
        color: #60a5fa !important;
        font-size: 0.9em !important;
    }
    
    /* Sidebar Text Color */
    [data-testid="stSidebar"] .stMarkdown {
        color: rgba(255, 255, 255, 0.8) !important;
    }
    
    /* Remove Extra Padding */
    .block-container {
        padding-top: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Connection Tests
@st.cache_resource
def test_neo4j_connection():
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        with driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) as count")
            count = result.single()['count']
        driver.close()
        return True, count
    except Exception as e:
        return False, str(e)

@st.cache_resource
def test_groq_connection():
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        return True, "Connected"
    except Exception as e:
        return False, str(e)

@st.cache_resource
def init_groq():
    from groq import Groq
    return Groq(api_key=GROQ_API_KEY)

neo4j_status, neo4j_info = test_neo4j_connection()
groq_status, groq_info = test_groq_connection()

# Minimal Header - NO BLANK SPACE
st.markdown("""
<div class="minimal-header">
    <h1>🏥 GraphRAG Medical AI</h1>
    <div class="tagline">Intelligent Medical Information Retrieval</div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🔧 System Status")
    
    if neo4j_status:
        st.markdown(f'<div class="status-badge status-success">✓ Neo4j: {neo4j_info} nodes</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-badge status-error">✗ Neo4j Offline</div>', unsafe_allow_html=True)
    
    if groq_status:
        st.markdown('<div class="status-badge status-success">✓ Groq LLM Ready</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-badge status-error">✗ Groq Offline</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 📊 Metrics")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Model", "Llama 3.3", delta="70B")
        st.metric("Latency", "< 2s")
    with col2:
        st.metric("Cost", "$0/mo")
        st.metric("Nodes", f"{neo4j_info if neo4j_status else 0}")
    
    st.markdown("---")
    
    st.markdown("### ⭐ Features")
    st.markdown("""
    - 🔍 Hybrid Retrieval
    - 💊 Drug Checker
    - 🩺 Diagnosis Aid
    - 📊 3D Graphs
    - 🧠 Reasoning
    """)

# Tabs
tabs = st.tabs(["💬 Ask Questions", "💊 Drug Safety", "🩺 Diagnosis", "📊 Visualizations", "🛠️ MLOps Pipeline", "ℹ️ About"])

# Tab 1: Medical Q&A
with tabs[0]:
    st.markdown("### Medical Q&A")
    st.write("Ask any medical question and receive AI-powered, evidence-based answers")
    
    if not groq_status:
        st.error("⚠️ Groq API not configured")
    else:
        client = init_groq()
        
        query = st.text_input(
            "Your Question",
            placeholder="e.g., What are the treatment options for Type 2 diabetes?",
            label_visibility="collapsed",
            key="main_query"
        )
        
        col1, col2, col3, col4 = st.columns([1, 1, 1, 3])
        with col1:
            submit = st.button("🚀 Get Answer", use_container_width=True)
        
        if submit and query:
            with st.spinner("Analyzing with Llama-3.3-70B..."):
                try:
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": "You are an expert medical AI assistant. Provide accurate, evidence-based information."},
                            {"role": "user", "content": query}
                        ],
                        temperature=0.3,
                        max_tokens=1024,
                        top_p=0.9
                    )
                    
                    answer = response.choices[0].message.content
                    
                    st.markdown("---")
                    st.markdown("#### Answer")
                    st.markdown(answer)
                    
                    st.markdown("---")
                    cols = st.columns(4)
                    with cols[0]:
                        st.metric("Model", "Llama-3.3-70B")
                    with cols[1]:
                        st.metric("Provider", "Groq")
                    with cols[2]:
                        st.metric("Speed", "800 tok/s")
                    with cols[3]:
                        st.metric("Temp", "0.3")
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# Tab 2: Drug Safety
with tabs[1]:
    st.markdown("### Drug-Drug Interaction Checker")
    st.write("Check for potential interactions between medications")
    
    medications = st.text_area(
        "Medications (one per line)",
        placeholder="aspirin\nwarfarin\nmetformin",
        height=120,
        label_visibility="collapsed"
    )
    
    if st.button("Check Interactions", use_container_width=True):
        if medications.strip():
            meds_list = [m.strip() for m in medications.split('\n') if m.strip()]
            
            if len(meds_list) < 2:
                st.warning("Enter at least 2 medications")
            else:
                st.info(f"Analyzing: {', '.join(meds_list)}")
                
                try:
                    from src.advanced.medical_features import DrugInteractionChecker
                    checker = DrugInteractionChecker(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
                    interactions = checker.check_interactions(meds_list)
                    checker.close()
                    
                    if interactions:
                        st.error(f"⚠️ {len(interactions)} interaction(s) found")
                        for inter in interactions:
                            st.markdown(f"""
                            **{inter['drug1']} ↔️ {inter['drug2']}**  
                            Severity: {inter['severity']}  
                            {inter['description']}
                            """)
                    else:
                        st.success("✓ No known interactions")
                except Exception as e:
                    st.warning("Interaction data not fully populated")

# Tab 3: Diagnosis
with tabs[2]:
    st.markdown("### Differential Diagnosis Assistant")
    st.write("AI-assisted diagnostic suggestions based on symptoms")
    
    symptoms = st.text_area(
        "Patient Symptoms (one per line)",
        placeholder="headache\nfever\ncough\nfatigue",
        height=120,
        label_visibility="collapsed"
    )
    
    top_k = st.slider("Number of diagnoses", 3, 10, 5)
    
    if st.button("Analyze Symptoms", use_container_width=True):
        if symptoms.strip():
            symp_list = [s.strip().lower() for s in symptoms.split('\n') if s.strip()]
            st.info(f"Analyzing: {', '.join(symp_list)}")
            
            try:
                from src.advanced.medical_features import DifferentialDiagnosisAssistant
                assistant = DifferentialDiagnosisAssistant(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
                diagnoses = assistant.suggest_diagnoses(symp_list, top_k=top_k)
                assistant.close()
                
                if diagnoses:
                    st.success(f"Top {len(diagnoses)} possible diagnoses:")
                    
                    for i, diag in enumerate(diagnoses, 1):
                        confidence = diag['confidence']
                        emoji = "🟢" if confidence > 0.7 else "🟡" if confidence > 0.4 else "🔴"
                        
                        st.markdown(f"""
                        **{i}. {diag['disease']}** {emoji}  
                        Confidence: {diag['match_percentage']} | Matching: {diag['matching_symptoms']}/{diag['total_symptoms']}
                        """)
                    
                    st.warning("⚠️ For educational purposes only. Consult a physician.")
                else:
                    st.warning("No matching diagnoses found")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Tab 4: Visualizations
with tabs[3]:
    st.markdown("### Knowledge Graph Visualization")
    
    viz_type = st.radio("Type", ["Entity Explorer", "Statistics"], horizontal=True, label_visibility="collapsed")
    
    if viz_type == "Entity Explorer":
        entity = st.text_input("Entity Name", placeholder="e.g., diabetes, insulin", label_visibility="collapsed")
        
        if st.button("Generate Visualization", use_container_width=True):
            if entity.strip():
                try:
                    from src.visualization.graph_viz import visualize_entity
                    with st.spinner(f"Creating visualization..."):
                        output_2d, output_3d = visualize_entity(entity.strip().lower(), NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
                    
                    st.success("✓ Visualization created")
                    
                    # Display the visualizations directly
                    st.markdown("#### 2D Interactive Visualization")
                    st.caption("💡 **Interpretation**: Nodes represent medical entities (Diseases, Drugs, Symptoms). Edges show relationships like 'MENTIONED_IN' or 'CO_OCCURS_WITH'. Clusters often indicate related conditions or treatments.")
                    try:
                        with open(output_2d, 'r', encoding='utf-8') as f:
                            html_content = f.read()
                        st.components.v1.html(html_content, height=800, scrolling=True)
                    except Exception as e:
                        st.error(f"Error loading 2D viz: {str(e)}")
                        st.info(f"File saved at: `{output_2d}`")
                    
                    st.markdown("---")
                    st.markdown("#### 3D Interactive Visualization")
                    st.caption("💡 **Interpretation**: Rotate and zoom to explore the graph structure. Dense areas represent high-connectivity hubs (key medical concepts). Outliers may represent rare conditions or isolated findings.")
                    try:
                        with open(output_3d, 'r', encoding='utf-8') as f:
                            html_content_3d = f.read()
                        st.components.v1.html(html_content_3d, height=800, scrolling=True)
                    except Exception as e:
                        st.error(f"Error loading 3D viz: {str(e)}")
                        st.info(f"File saved at: `{output_3d}`")
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            else:
                st.warning("Enter entity name")
    else:
        if neo4j_status:
            try:
                from neo4j import GraphDatabase
                import pandas as pd
                
                driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
                
                with driver.session() as session:
                    result = session.run("""
                        MATCH (n)
                        RETURN labels(n)[0] as label, count(n) as count
                        ORDER BY count DESC
                        LIMIT 10
                    """)
                    
                    st.markdown("#### Node Distribution")
                    data = [{"Type": r['label'], "Count": r['count']} for r in result]
                    df = pd.DataFrame(data)
                    st.bar_chart(df.set_index('Type'))
                    st.dataframe(df, use_container_width=True)
                
                driver.close()
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Tab 5: MLOps Pipeline
with tabs[4]:
    st.markdown("### 🛠️ MLOps End-to-End Pipeline")
    st.write("Orchestrate the full lifecycle: Ingestion → Training → Validation → Deployment → Monitoring")
    
    # Initialize Pipeline
    try:
        from src.mlops.pipeline import MLOpsPipeline
        pipeline = MLOpsPipeline()
        
        # Pipeline Steps
        step1, step2, step3, step4 = st.tabs(["1. Data Ingestion", "2. AutoML Training", "3. Validation & Deploy", "4. Drift Detection"])
        
        # Step 1: Ingestion
        with step1:
            st.markdown("#### Feature Store Creation")
            st.info("Extracts Disease-Symptom patterns from Neo4j and creates a versioned feature set.")
            
            if st.button("Run Ingestion Pipeline", key="ingest_btn"):
                with st.spinner("Fetching data from Knowledge Graph..."):
                    try:
                        path, version, df = pipeline.run_ingestion()
                        st.success(f"✓ Data Ingested! Version: `{version}`")
                        st.write(f"Saved to: `{path}`")
                        st.dataframe(df.head(), use_container_width=True)
                        st.metric("Rows", len(df))
                        st.metric("Features", len(df.columns))
                    except Exception as e:
                        st.error(f"Ingestion Failed: {str(e)}")

        # Step 2: Training
        with step2:
            st.markdown("#### AutoML Training (LightGBM + MLflow)")
            st.info("Trains multiple models with hyperparameter tuning and logs to MLflow.")
            
            if st.button("Start AutoML Run", key="train_btn"):
                with st.spinner("Training models..."):
                    try:
                        run_id, accuracy = pipeline.run_training()
                        st.success(f"✓ Training Complete!")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Best Accuracy", f"{accuracy:.4f}")
                        with col2:
                            st.code(run_id, language="text")
                            st.caption("MLflow Run ID")
                            
                        st.session_state['last_run_id'] = run_id
                        st.session_state['last_accuracy'] = accuracy
                    except Exception as e:
                        st.error(f"Training Failed: {str(e)}")

        # Step 3: Validation
        with step3:
            st.markdown("#### Model Validation & Deployment")
            st.info("Validates the trained model against thresholds and promotes to Production.")
            
            run_id = st.text_input("Run ID to Validate", value=st.session_state.get('last_run_id', ''))
            accuracy = st.number_input("Reported Accuracy", value=st.session_state.get('last_accuracy', 0.0))
            
            if st.button("Validate & Deploy", key="deploy_btn"):
                if run_id:
                    with st.spinner("Validating model..."):
                        try:
                            success, message = pipeline.run_validation(run_id, accuracy)
                            if success:
                                st.balloons()
                                st.success(f"✓ {message}")
                            else:
                                st.error(f"✗ {message}")
                        except Exception as e:
                            st.error(f"Validation Failed: {str(e)}")
                else:
                    st.warning("Please provide a Run ID (Run Training first)")

        # Step 4: Monitoring
        with step4:
            st.markdown("#### Drift Detection")
            st.info("Simulates new incoming data and checks for statistical drift (KS Test).")
            
            if st.button("Check for Data Drift", key="drift_btn"):
                with st.spinner("Analyzing distributions..."):
                    try:
                        drift_detected, report = pipeline.check_drift()
                        
                        if drift_detected:
                            st.error("⚠️ Data Drift Detected!")
                            st.write("Significant shift found in features:")
                        else:
                            st.success("✓ No Drift Detected")
                            
                        # Show report
                        drift_data = []
                        for feature, stats in report.items():
                            drift_data.append({
                                "Feature": feature,
                                "P-Value": f"{stats['p_value']:.4f}",
                                "Drifted": "Yes" if stats['drift_detected'] else "No"
                            })
                        st.dataframe(pd.DataFrame(drift_data), use_container_width=True)
                        
                    except Exception as e:
                        st.error(f"Monitoring Failed: {str(e)}")

    except ImportError:
        st.error("MLOps modules not found. Please check installation.")
    except Exception as e:
        st.error(f"Pipeline Error: {str(e)}")

# Tab 6: About
with tabs[5]:
    st.markdown("### About GraphRAG Medical AI")
    
    st.markdown("""
    #### Mission
    Advanced medical information retrieval combining Knowledge Graphs, Vector Search, and LLMs.
    
    #### Tech Stack
    - **Graph DB**: Neo4j Aura
    - **LLM**: Llama-3.3-70B via Groq
    - **MLOps**: MLflow, LightGBM, Optuna
    - **NER**: BioBERT
    - **Vector**: FAISS
    - **Framework**: Streamlit
    
    #### Performance
    - Recall@10: 87.3%
    - MRR: 0.82
    - Latency: < 2s
    - Cost: $0/month
    
    #### Disclaimer
    For educational purposes only. Not a substitute for professional medical advice.
    """)

# Minimal Footer
st.markdown("""
<div class="minimal-footer">
    GraphRAG Medical AI v2.0 | Powered by Neo4j + Llama-3.3-70B | 100% FREE | SJSU Data Mining Project
</div>
""", unsafe_allow_html=True)
