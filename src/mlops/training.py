import mlflow
import mlflow.lightgbm
import lightgbm as lgb
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report
import os
import glob
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MedicalModelTrainer:
    def __init__(self, experiment_name="Medical_Disease_Classification"):
        mlflow.set_experiment(experiment_name)
        self.feature_store_path = "data/feature_store"

    def get_latest_features(self):
        files = glob.glob(os.path.join(self.feature_store_path, "features_*.parquet"))
        if not files:
            raise FileNotFoundError("No feature files found in feature store!")
        latest_file = max(files, key=os.path.getctime)
        logger.info(f"Loading features from {latest_file}")
        return pd.read_parquet(latest_file)

    def train_automl(self, test_size=0.2):
        """
        Simulates an AutoML run by trying a few configurations.
        """
        df = self.get_latest_features()
        
        # Prepare Data
        X = df.drop(columns=['disease', 'target_category'])
        y = df['target_category']
        
        # Encode target
        y = y.astype('category').cat.codes
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
        
        # Create LightGBM dataset
        train_data = lgb.Dataset(X_train, label=y_train)
        test_data = lgb.Dataset(X_test, label=y_test, reference=train_data)
        
        # Hyperparameters to try (Mini Search Space)
        configs = [
            {'num_leaves': 31, 'learning_rate': 0.05, 'n_estimators': 100},
            {'num_leaves': 50, 'learning_rate': 0.1, 'n_estimators': 100},
            {'num_leaves': 20, 'learning_rate': 0.01, 'n_estimators': 200}
        ]
        
        best_accuracy = 0
        best_run_id = None
        
        for params in configs:
            with mlflow.start_run(run_name=f"LGBM_{params['num_leaves']}_{params['learning_rate']}"):
                # Log params
                mlflow.log_params(params)
                
                # Train
                model = lgb.train(
                    params,
                    train_data,
                    valid_sets=[test_data],
                    callbacks=[lgb.log_evaluation(10)]
                )
                
                # Predict
                y_pred_prob = model.predict(X_test)
                y_pred = [1 if x > 0.5 else 0 for x in y_pred_prob] # Binary/Multiclass logic needed
                # For multiclass, predict returns matrix. 
                # Let's handle multiclass properly
                if len(y.unique()) > 2:
                    params['objective'] = 'multiclass'
                    params['num_class'] = len(y.unique())
                    # Re-train with multiclass param
                    model = lgb.train(
                        params,
                        train_data,
                        valid_sets=[test_data],
                        callbacks=[lgb.log_evaluation(0)] # Silence
                    )
                    y_pred_prob = model.predict(X_test)
                    y_pred = [x.argmax() for x in y_pred_prob]
                else:
                    params['objective'] = 'binary'
                    # Re-train
                    model = lgb.train(
                        params,
                        train_data,
                        valid_sets=[test_data],
                        callbacks=[lgb.log_evaluation(0)]
                    )
                    y_pred_prob = model.predict(X_test)
                    y_pred = [1 if x > 0.5 else 0 for x in y_pred_prob]

                # Metrics
                acc = accuracy_score(y_test, y_pred)
                f1 = f1_score(y_test, y_pred, average='weighted')
                
                mlflow.log_metric("accuracy", acc)
                mlflow.log_metric("f1_score", f1)
                
                # Log Model
                mlflow.lightgbm.log_model(model, "model")
                
                logger.info(f"Run finished. Acc: {acc:.4f}")
                
                if acc > best_accuracy:
                    best_accuracy = acc
                    best_run_id = mlflow.active_run().info.run_id
                    
        logger.info(f"Best Run ID: {best_run_id} with Accuracy: {best_accuracy}")
        return best_run_id, best_accuracy

if __name__ == "__main__":
    trainer = MedicalModelTrainer()
    trainer.train_automl()
