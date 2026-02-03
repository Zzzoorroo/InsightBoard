import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os

class BusinessBrain:
    def __init__(self, target_column='churn'):
        # Initialize the model and the target we want to predict
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.target_column = target_column
        self.features = []

    def load_and_analyze(self, file_path):
        """Dynamically loads CSV or Excel and generates insights."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Could not find the file at {file_path}")

        # Handle different file formats
        df = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)
        
        # Dynamic Feature Selection: everything except the target
        self.features = [col for col in df.columns if col != self.target_column]
        
        print(f"📊 Dataset Loaded: {len(df)} rows")
        print(f"Target: {self.target_column} | Features: {', '.join(self.features)}")
        
        self._generate_visuals(df)
        return df

    def _generate_visuals(self, df):
        """Generates a correlation heatmap and feature distributions."""
        plt.figure(figsize=(10, 6))
        # Select only numeric columns for correlation
        numeric_df = df.select_dtypes(include=['number'])
        if not numeric_df.empty:
            sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', fmt='.2f')
            plt.title("Business Feature Correlation")
            plt.show()
        else:
            print("⚠️ No numeric columns found for correlation heatmap")

    def train(self, df):
        """Trains the model using the dynamic feature set."""
        X = df[self.features]
        y = df[self.target_column]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.model.fit(X_train, y_train)
        
        # Generate Meaningful Insights: Feature Importance
        importances = pd.Series(self.model.feature_importances_, index=self.features)
        print("\n💡 Key Business Drivers (Feature Importance):")
        print(importances.sort_values(ascending=False))
        
    def predict_risk(self, **kwargs):
        """Accepts dynamic keyword arguments matching the feature names."""
        # Ensure input matches training features order
        input_values = [kwargs.get(feat, 0) for feat in self.features]
        input_data = [input_values]
        
        prediction = self.model.predict(input_data)[0]
        probability = self.model.predict_proba(input_data)[0][1]
        
        return {
            "risk_score": f"{round(probability * 100, 2)}%",
            "status": "High Risk" if prediction == 1 else "Low Risk"
        }

# --- DYNAMIC TEST ---
if __name__ == "__main__":
    brain = BusinessBrain(target_column='churn')
    
    # You can now point this to any CSV file
    df = brain.load_and_analyze("E_commerce.csv")
    
    # For now, let's auto-generate a dummy CSV to prove it works
    dummy_path = "dynamic_business_data.csv"
    pd.DataFrame({
        'monthly_spend': [20, 100, 25, 120, 30, 150, 40, 200] * 10,
        'tenure': [1, 24, 2, 36, 3, 48, 5, 60] * 10,
        'support_calls': [5, 1, 4, 0, 6, 1, 5, 0] * 10,
        'churn': [1, 0, 1, 0, 1, 0, 1, 0] * 10
    }).to_csv(dummy_path, index=False)

    business_df = brain.load_and_analyze(df)
    brain.train(business_df)
    
    # Flexible prediction
    result = brain.predict_risk(monthly_spend=35, tenure=3, support_calls=7)
    print(f"\nAnalysis Result: {result}")