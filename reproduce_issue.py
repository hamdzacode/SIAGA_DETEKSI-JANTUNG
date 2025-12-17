
import sys
import traceback

print("Python version:", sys.version)

try:
    import pandas
    print("pandas version:", pandas.__version__)
except ImportError:
    print("pandas not installed")

try:
    import sklearn
    print("sklearn version:", sklearn.__version__)
except ImportError:
    print("sklearn not installed")

try:
    import joblib
    print("joblib version:", joblib.__version__)
except ImportError:
    print("joblib not installed")

try:
    import shap
    print("shap version:", shap.__version__)
except ImportError:
    print("shap not installed")

print("\ntrying to import _is_pandas_df from sklearn.utils.validation...")
try:
    from sklearn.utils.validation import _is_pandas_df
    print("Success importing _is_pandas_df")
except ImportError as e:
    print("Failed importing _is_pandas_df:", e)

print("\nLoading model...")
try:
    from ml.cardio_model import CardioRiskModel, MODEL_PATH
    print(f"Model path: {MODEL_PATH}")
    if not MODEL_PATH.exists():
        print("Model file does not exist!")
    else:
        model = CardioRiskModel()
        print("Model loaded successfully!")
except Exception:
    traceback.print_exc()
