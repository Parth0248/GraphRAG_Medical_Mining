import pandas as pd
import numpy as np
from scipy.stats import ks_2samp
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DriftDetector:
    def __init__(self):
        pass

    def detect_drift(self, reference_df, current_df, threshold=0.05):
        """
        Detects drift between two datasets using KS Test for numerical features.
        """
        drift_report = {}
        drift_detected = False
        
        # Identify numerical columns (excluding target/id)
        numeric_cols = reference_df.select_dtypes(include=[np.number]).columns.tolist()
        cols_to_check = [c for c in numeric_cols if c not in ['target_category', 'disease']]
        
        for col in cols_to_check:
            if col not in current_df.columns:
                continue
                
            stat, p_value = ks_2samp(reference_df[col], current_df[col])
            
            is_drift = p_value < threshold
            drift_report[col] = {
                "p_value": p_value,
                "drift_detected": is_drift
            }
            if is_drift:
                drift_detected = True
                
        return drift_detected, drift_report

    def simulate_drift(self, df):
        """
        Creates a drifted version of the dataset for testing purposes.
        """
        drifted_df = df.copy()
        # Shift the distribution of a random feature
        cols = [c for c in df.columns if 'symptom_' in c]
        if cols:
            target_col = cols[0]
            # Flip values or add noise
            # Since our features are 0/1, let's just flip a bunch of 0s to 1s
            mask = drifted_df[target_col] == 0
            # Flip 50% of them
            flip_indices = drifted_df[mask].sample(frac=0.5).index
            drifted_df.loc[flip_indices, target_col] = 1
            
        return drifted_df
