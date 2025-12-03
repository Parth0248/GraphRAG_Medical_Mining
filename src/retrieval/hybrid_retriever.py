"""Hybrid Graph + Vector Retrieval"""
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
        """Generate BioBERT embedding"""
        inputs = self.tokenizer(text, return_tensors="pt", 
                               truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
            embedding = outputs.last_hidden_state[:, 0, :].numpy()
        return embedding[0]
    
    def graph_retrieve(self, query, k=10):
        """Retrieve from knowledge graph"""
        with self.driver.session() as session:
            # Simple entity-based retrieval
            result = session.run(
                """
                MATCH (e:Entity)-[:MENTIONED_IN]->(d:Document)
                WHERE e.name CONTAINS $query OR d.title CONTAINS $query
                RETURN d.id as doc_id, d.title as title, d.text as text, 
                       count(e) as relevance
                ORDER BY relevance DESC
                LIMIT $k
                """,
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
        """Retrieve using FAISS vector search"""
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
        """Combine graph and vector retrieval"""
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
