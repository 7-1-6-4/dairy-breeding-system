import os
import numpy as np
import tensorflow as tf
import joblib
import json

class PredictorService:
    """Service to load and use the trained ML model"""
    
    def __init__(self):
        model_path = os.path.join('model', 'dnn_model.keras')
        scaler_path = os.path.join('model', 'scaler.pkl')
        features_path = os.path.join('model', 'feature_columns.json')
        
        # Load model
        self.model = tf.keras.models.load_model(model_path)
        print(f"✅ Model loaded from {model_path}")
        
        # Load scaler
        self.scaler = joblib.load(scaler_path)
        print(f"✅ Scaler loaded from {scaler_path}")
        
        # Load feature columns
        with open(features_path, 'r') as f:
            self.feature_columns = json.load(f)
        print(f"✅ Feature columns loaded: {self.feature_columns}")
    
    def predict_suitability(self, features):
        """
        Predict suitability score for given features
        
        Args:
            features: dict with keys matching feature_columns
        Returns:
            predicted score (0-100)
        """
        # Create feature vector in correct order
        feature_vector = []
        for col in self.feature_columns:
            if col in features:
                feature_vector.append(features[col])
            else:
                # Use defaults for missing values
                if col in ['heat_tolerance_score', 'disease_resistance_score', 'feed_efficiency_score']:
                    feature_vector.append(5)  # Medium default
                else:
                    raise ValueError(f"Missing required feature: {col}")
        
        # Convert to numpy and scale
        X = np.array([feature_vector])
        X_scaled = self.scaler.transform(X)
        
        # Predict
        prediction = self.model.predict(X_scaled, verbose=0)
        
        # Convert from 0-1 to 0-100
        return float(prediction[0][0] * 100)