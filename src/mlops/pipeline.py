from src.mlops.feature_store import MedicalFeatureStore
from src.mlops.training import MedicalModelTrainer
from src.mlops.validation import ModelValidator
from src.mlops.monitoring import DriftDetector
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

class MLOpsPipeline:
    def __init__(self):
        self.neo4j_uri = os.getenv("NEO4J_URI")
        self.neo4j_user = os.getenv("NEO4J_USERNAME")
        self.neo4j_pass = os.getenv("NEO4J_PASSWORD")
        
        self.feature_store = MedicalFeatureStore(self.neo4j_uri, self.neo4j_user, self.neo4j_pass)
        self.trainer = MedicalModelTrainer()
        self.validator = ModelValidator()
        self.monitor = DriftDetector()

    def run_ingestion(self):
        df = self.feature_store.fetch_features_from_graph()
        path, version = self.feature_store.save_to_feature_store(df)
        return path, version, df

    def run_training(self):
        run_id, accuracy = self.trainer.train_automl()
        return run_id, accuracy

    def run_validation(self, run_id, accuracy):
        success, message = self.validator.validate_and_promote(run_id, accuracy)
        return success, message

    def check_drift(self):
        # Load latest data
        df = self.trainer.get_latest_features()
        # Simulate new data
        drifted_df = self.monitor.simulate_drift(df)
        
        drift_detected, report = self.monitor.detect_drift(df, drifted_df)
        return drift_detected, report
