# **GraphRAG for Medical Data Mining**

## **1\. Project Overview**

This project proposes the development of an AI-powered medical data mining platform that leverages GraphRAG (Graph-based Retrieval-Augmented Generation) and large language models to analyze, organize, and retrieve relevant healthcare insights from unstructured medical datasets. The system will integrate data mining, graph databases, and AI-assisted document retrieval to enhance medical research and diagnostic decision support. Following the CRISP-DM methodology, the project will include stages of data collection, preprocessing, modeling, evaluation, and deployment.

## **2\. Objectives**

• Collect and preprocess medical datasets (disease reports, patient records, medical articles).

• Apply data mining and NLP techniques to extract structured information from unstructured medical text.

• Implement GraphRAG using vector databases and graph networks to enhance knowledge retrieval.

• Evaluate model accuracy and retrieval relevance through medical benchmark datasets.

• Develop a Streamlit/Gradio-based demo for real-time query and visualization.

## **3\. Methodology**

Step 1: Data Collection and Preprocessing

• Source open medical datasets (e.g., Google datasets or Kaggle healthcare data). Perform data cleaning, tokenization, entity recognition (diseases, drugs, symptoms), and anonymization.

Step 2: Graph Construction and Vectorization

• Use vector embeddings (MiniLM, BioBERT) to represent text. Store entities in a graph database (Neo4j). Construct relationships such as disease–symptom–treatment links.

Step 3: RAG Pipeline Integration

• Integrate a retrieval-augmented generation system combining a vector store (FAISS/Pinecone) with LLM inference. Implement GraphRAG to retrieve semantically related nodes and context documents.

Step 4: Model Evaluation

• Evaluate retrieval precision (Recall@k, MRR), entity extraction F1, and knowledge graph accuracy. Use confusion matrices and visual dashboards (Plotly, TensorBoard).

Step 5: Application Deployment

• Deploy backend via FastAPI, host data on AWS (RDS \+ S3), and integrate frontend with Streamlit or Gradio.

## **4\. Technologies to Be Used**

Programming Language: Python  
Libraries: PyTorch, Hugging Face Transformers, Neo4j, FAISS, LangChain, NetworkX  
Backend: FastAPI  
Frontend: Streamlit / Gradio  
Database: PostgreSQL \+ Neo4j (Graph DB)  
Visualization: Plotly, TensorBoard  
Cloud: AWS (EC2, S3, RDS, API Gateway)

## **5\. Expected Outcomes**

• A functional AI-driven data mining system for medical research and analysis.

• A GraphRAG-powered retrieval system capable of semantic search and medical knowledge discovery.

• Visualization dashboard showing key metrics and graph insights.

• Deployed demo application accessible via GitHub and Colab.

## **6\. Significance of the Project**

This project integrates data mining, natural language processing, and graph-based AI to address challenges in medical knowledge retrieval and analysis. It demonstrates how data-driven approaches can improve healthcare decision-making, enhance information accessibility, and support evidence-based clinical research.

## **7\. Team Responsibilities and Timeline**

The project team consists of four members, each responsible for key components aligned with their strengths:

| Team Member | Responsibilities |
| :---- | :---- |
| Kalhar Mayurbhai Patel | Lead ML Engineer – Data preprocessing, model training, and evaluation of GraphRAG pipeline. |
| Michael Kennedy | Infrastructure & Deployment Engineer – AWS setup, FastAPI backend, CI/CD automation, and system scalability. |
| Yu Hsuan Lee | System Analyst & Backend Developer – System analysis, API pipeline integration, and database management (Neo4j \+ PostgreSQL). |
| Parth Maradia | AI Engineer – LangGraph/RAG integration, LLM fine-tuning, and embedding optimization. |

The project follows a 10-week timeline leading to the final submission on December 2, 2025\.

| Week | Tasks / Milestones |
| :---- | :---- |
| Week 1–2 | Finalize topic, collect datasets (MIMIC-III, PubMed, Kaggle healthcare). Define data schema and perform initial data cleaning. |
| Week 3–4 | Entity extraction (diseases, symptoms, drugs). Construct a knowledge graph and vector database (Neo4j \+ FAISS). |
| Week 5–6 | Develop RAG pipeline and integrate GraphRAG module. Begin preliminary evaluation (Recall@k, F1). |
| Week 7–8 | Build backend APIs (FastAPI) and frontend demo (Streamlit/Gradio). Deploy to the AWS test environment. |
| Week 9 | Conduct ablation studies, model fine-tuning, and performance visualization dashboard setup. |
| Week 10 | Prepare project report, presentation slides, and record final demo video for GitHub submission. |

