# Base Image: Python 3.11 (Slim version for lighter container)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (if any needed for libraries like xgboost)
# RUN apt-get update && apt-get install -y --no-install-recommends ...

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose Streamlit default port
EXPOSE 8501

# Command to run the application
CMD ["streamlit", "run", "streamlit_app/app.py"]
