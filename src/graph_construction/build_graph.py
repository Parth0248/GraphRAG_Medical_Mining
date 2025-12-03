"""Build Neo4j knowledge graph from medical data"""
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
        """Create indexes for faster queries"""
        with self.driver.session() as session:
            # Node indexes
            session.run("CREATE INDEX entity_name IF NOT EXISTS FOR (e:Entity) ON (e.name)")
            session.run("CREATE INDEX disease_name IF NOT EXISTS FOR (d:Disease) ON (d.name)")
            session.run("CREATE INDEX drug_name IF NOT EXISTS FOR (d:Drug) ON (d.name)")
            print("✓ Indexes created")
    
    def add_document(self, doc_id, title, text):
        """Add document and extract entities"""
        # Extract entities
        entities = self.extractor.extract_entities(text)
        
        with self.driver.session() as session:
            # Create document node
            session.run(
                """
                MERGE (d:Document {id: $doc_id})
                SET d.title = $title, d.text = $text
                """,
                doc_id=doc_id, title=title, text=text
            )
            
            # Create entity nodes and relationships
            for ent in entities:
                entity_type = ent['label']
                entity_name = ent['text']
                
                session.run(
                    f"""
                    MERGE (e:Entity {{name: $name}})
                    SET e.type = $type, e:{entity_type}
                    MERGE (d:Document {{id: $doc_id}})
                    MERGE (e)-[r:MENTIONED_IN]->(d)
                    ON CREATE SET r.count = 1, r.score = $score
                    ON MATCH SET r.count = r.count + 1
                    """,
                    name=entity_name, type=entity_type, 
                    doc_id=doc_id, score=ent['score']
                )
    
    def build_cooccurrence_edges(self, window_size=10):
        """Build co-occurrence relationships"""
        print("Building co-occurrence edges...")
        # This is simplified - full implementation would use sentence windows
        with self.driver.session() as session:
            session.run(
                """
                MATCH (e1:Entity)-[:MENTIONED_IN]->(d:Document)<-[:MENTIONED_IN]-(e2:Entity)
                WHERE id(e1) < id(e2)
                MERGE (e1)-[r:CO_OCCURS_WITH]-(e2)
                ON CREATE SET r.count = 1
                ON MATCH SET r.count = r.count + 1
                """
            )
        print("✓ Co-occurrence edges created")

def main():
    """Build graph from PubMed data"""
    # Load data
    data_file = "data/raw/pubmed_abstracts_expanded.json"
    
    if not Path(data_file).exists():
        print(f"⚠️  Expanded dataset not found, using original...")
        data_file = "data/raw/pubmed_abstracts.json"
    
    print(f"📂 Loading data from: {data_file}")
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
    
    for i, abstract in enumerate(abstracts):  # Process all abstracts
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
