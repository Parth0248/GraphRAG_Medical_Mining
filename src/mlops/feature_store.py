import pandas as pd
from neo4j import GraphDatabase
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MedicalFeatureStore:
    def __init__(self, neo4j_uri, neo4j_user, neo4j_password):
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        self.feature_store_path = "data/feature_store"
        os.makedirs(self.feature_store_path, exist_ok=True)

    def close(self):
        self.driver.close()

    def fetch_features_from_graph(self):
        """
        Extracts Disease-Symptom relationships from Neo4j to build a dataset.
        Target: Disease Name (or Category if available)
        Features: Multi-hot encoded symptoms
        """
        logger.info("Fetching data from Neo4j...")
        query = """
        MATCH (d:Entity)-[:MENTIONED_IN]->(doc:Document)
        WHERE d.type = 'DISEASE'
        OPTIONAL MATCH (d)-[:CO_OCCURS_WITH]-(s:Entity)
        WHERE s.type = 'SYMPTOM'
        RETURN d.name as disease, collect(s.name) as symptoms
        """
        # Note: In our current graph schema, we might rely on CO_OCCURS_WITH for symptoms
        # or just use the text embeddings. For this MLOps demo, we'll simulate a 
        # "Disease Classification" task based on co-occurring entities (symptoms/treatments).
        
        with self.driver.session() as session:
            result = session.run(query)
            data = [record.data() for record in result]
            
        if not data:
            logger.warning("No data found in Neo4j! creating dummy data for demonstration.")
            # Fallback for demo if graph is empty or schema differs
            return self._create_dummy_data()

        df = pd.DataFrame(data)
        
        # Feature Engineering: Multi-hot encode symptoms
        # 1. Explode symptoms
        # 2. Get top N most common symptoms to use as features
        
        # Flatten all symptoms to find unique ones
        all_symptoms = set()
        for symptoms in df['symptoms']:
            all_symptoms.update(symptoms)
            
        # Create feature columns
        # For simplicity in this demo, let's just take top 20 most common "symptoms" (co-occurring entities)
        # In a real scenario, we'd have a curated list.
        
        # Let's pivot: One row per disease, columns for each symptom (1 if present, 0 if not)
        # This is essentially a Bag of Words on symptoms
        
        # Simplified approach:
        # Create a list of all unique symptoms found
        unique_symptoms = sorted(list(all_symptoms))[:50] # Limit to top 50 to avoid explosion
        
        features = []
        for _, row in df.iterrows():
            row_features = {'disease': row['disease']}
            current_symptoms = set(row['symptoms'])
            for symptom in unique_symptoms:
                row_features[f"symptom_{symptom}"] = 1 if symptom in current_symptoms else 0
            features.append(row_features)
            
        feature_df = pd.DataFrame(features)
        
        # Add a synthetic "Target" category for classification if not present
        # e.g., "Chronic", "Acute", "Infectious" based on simple hashing or keywords
        feature_df['target_category'] = feature_df['disease'].apply(self._assign_category)
        
        logger.info(f"Feature extraction complete. Shape: {feature_df.shape}")
        return feature_df

    def _assign_category(self, disease_name):
        # Simple rule-based labeling for demo purposes
        name = disease_name.lower()
        if any(x in name for x in ['cancer', 'tumor', 'carcinoma']):
            return 'Oncology'
        elif any(x in name for x in ['heart', 'cardio', 'artery']):
            return 'Cardiology'
        elif any(x in name for x in ['diabetes', 'insulin', 'sugar']):
            return 'Endocrinology'
        elif any(x in name for x in ['virus', 'bacterial', 'infection']):
            return 'Infectious'
        else:
            return 'General'

    def _create_dummy_data(self):
        # Create synthetic data if graph is empty
        data = []
        categories = ['Oncology', 'Cardiology', 'Endocrinology', 'Infectious']
        for i in range(100):
            cat = categories[i % 4]
            data.append({
                'disease': f'Disease_{i}',
                'symptom_fever': 1 if cat == 'Infectious' else 0,
                'symptom_pain': 1,
                'symptom_fatigue': 1 if cat in ['Oncology', 'Infectious'] else 0,
                'target_category': cat
            })
        return pd.DataFrame(data)

    def save_to_feature_store(self, df, version=None):
        if version is None:
            version = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        filename = f"features_{version}.parquet"
        path = os.path.join(self.feature_store_path, filename)
        df.to_parquet(path, index=False)
        logger.info(f"Saved features to {path}")
        return path, version

if __name__ == "__main__":
    # Test
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    fs = MedicalFeatureStore(
        os.getenv("NEO4J_URI"),
        os.getenv("NEO4J_USERNAME"),
        os.getenv("NEO4J_PASSWORD")
    )
    df = fs.fetch_features_from_graph()
    fs.save_to_feature_store(df)
    fs.close()
