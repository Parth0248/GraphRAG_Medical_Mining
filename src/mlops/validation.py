import mlflow
from mlflow.tracking import MlflowClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelValidator:
    def __init__(self, model_name="Medical_Disease_Classifier"):
        self.client = MlflowClient()
        self.model_name = model_name

    def validate_and_promote(self, run_id, accuracy, threshold=0.6):
        """
        Validates the model from a specific run and promotes it if it meets criteria.
        """
        logger.info(f"Validating Run ID: {run_id} with Accuracy: {accuracy}")
        
        if accuracy < threshold:
            logger.warning(f"Model failed validation. Accuracy {accuracy} < Threshold {threshold}")
            return False, "Accuracy below threshold"
            
        # Check if model is registered
        try:
            self.client.create_registered_model(self.model_name)
        except Exception:
            pass # Already exists
            
        # Create Version
        model_uri = f"runs:/{run_id}/model"
        model_version = self.client.create_model_version(
            name=self.model_name,
            source=model_uri,
            run_id=run_id
        )
        
        # Transition to Production
        self.client.transition_model_version_stage(
            name=self.model_name,
            version=model_version.version,
            stage="Production",
            archive_existing_versions=True
        )
        
        logger.info(f"Model Version {model_version.version} promoted to Production!")
        return True, f"Promoted Version {model_version.version} to Production"

    def get_production_model(self):
        """
        Get details of the current production model.
        """
        try:
            latest = self.client.get_latest_versions(self.model_name, stages=["Production"])
            if latest:
                return latest[0]
            return None
        except Exception as e:
            logger.error(f"Error getting production model: {e}")
            return None
