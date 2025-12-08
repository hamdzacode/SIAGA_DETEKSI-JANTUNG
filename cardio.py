import pandas as pd
import numpy as np
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE
from sklearn.metrics import classification_report, accuracy_score

def generate_synthetic_data(n_samples=10000):
    """
    Generate synthetic data mimicking the Cardiovascular Disease dataset with more complex interactions.
    """
    np.random.seed(42)
    
    # Age: 30 to 65
    age_years = np.random.randint(30, 66, n_samples)
    
    # Gender: 1 (Women), 2 (Men)
    gender = np.random.choice([1, 2], n_samples)
    
    # BMI: 18.5 to 40.0 (slightly wider range)
    bmi = np.random.uniform(18.5, 40.0, n_samples)
    
    # MAP: 70 to 160
    map_val = np.random.uniform(70, 160, n_samples)
    
    # Cholesterol: 1 (Normal), 2 (Above Normal), 3 (Well Above Normal)
    cholesterol = np.random.choice([1, 2, 3], n_samples, p=[0.7, 0.2, 0.1])
    
    # Gluc: 1 (Normal), 2 (Above Normal), 3 (Well Above Normal)
    gluc = np.random.choice([1, 2, 3], n_samples, p=[0.8, 0.15, 0.05])
    
    # Lifestyle
    smoke = np.random.choice([0, 1], n_samples, p=[0.8, 0.2])
    alco = np.random.choice([0, 1], n_samples, p=[0.9, 0.1])
    active = np.random.choice([0, 1], n_samples, p=[0.2, 0.8])
    
    # Target generation with interactions
    # Risk increases non-linearly with age and map
    # Interaction: Smoking + High Cholesterol is worse
    # Interaction: High BMI + Inactive is worse
    
    base_score = -5.0 # Bias
    
    score = base_score + \
            (age_years / 60) ** 2 * 2.0 + \
            (bmi / 30) * 1.5 + \
            (map_val / 100) ** 1.5 * 2.5 + \
            (cholesterol - 1) * 1.2 + \
            (gluc - 1) * 0.8 + \
            smoke * 0.8 + \
            alco * 0.4 - \
            active * 1.2
            
    # Interaction terms
    score += (smoke * (cholesterol > 1)) * 1.0
    score += ((bmi > 30) * (1 - active)) * 1.0
    score += ((age_years > 50) * (map_val > 120)) * 1.0
    
    # Sigmoid to probability
    prob = 1 / (1 + np.exp(-score))
    cardio = (np.random.random(n_samples) < prob).astype(int)
    
    df = pd.DataFrame({
        'age_years': age_years,
        'gender': gender,
        'bmi': bmi,
        'map': map_val,
        'cholesterol': cholesterol,
        'gluc': gluc,
        'smoke': smoke,
        'alco': alco,
        'active': active,
        'cardio': cardio
    })
    
    return df

def train_model():
    print("Generating synthetic data (10,000 samples)...")
    df = generate_synthetic_data(n_samples=10000)
    
    X = df.drop('cardio', axis=1)
    y = df['cardio']
    
    print(f"Data shape: {X.shape}")
    print(f"Target distribution:\n{y.value_counts()}")
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    pipeline = ImbPipeline([
        ('smote', SMOTE(random_state=42)),
        ('classifier', XGBClassifier(
            use_label_encoder=False,
            eval_metric='logloss',
            random_state=42
        ))
    ])
    
    # Hyperparameter Grid
    param_grid = {
        'classifier__n_estimators': [100, 200],
        'classifier__max_depth': [3, 5, 7],
        'classifier__learning_rate': [0.01, 0.1, 0.2],
        'classifier__subsample': [0.8, 1.0]
    }
    
    print("Starting Grid Search for Hyperparameter Tuning...")
    grid_search = GridSearchCV(
        estimator=pipeline,
        param_grid=param_grid,
        scoring='accuracy',
        cv=3,
        verbose=1,
        n_jobs=-1
    )
    
    grid_search.fit(X_train, y_train)
    
    print(f"Best Parameters: {grid_search.best_params_}")
    print(f"Best CV Score: {grid_search.best_score_:.4f}")
    
    best_model = grid_search.best_estimator_
    
    print("Evaluating best model on test set...")
    y_pred = best_model.predict(X_test)
    print(classification_report(y_test, y_pred))
    print(f"Test Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    
    # Save model
    output_path = 'ml/best_xgb_pipeline.joblib'
    print(f"Saving model to {output_path}...")
    joblib.dump(best_model, output_path)
    
    # Save metadata
    import json
    from datetime import datetime
    metadata = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "trained_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "model_version": "xgb_v1.0.0",
        "best_params": grid_search.best_params_
    }
    with open('ml/model_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=4)
        
    print("Done.")

if __name__ == "__main__":
    train_model()
