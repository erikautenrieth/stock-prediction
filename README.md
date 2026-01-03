# Stock-Prediction
Stock Prediction Pipeline with Machine Learning

Note: This is a work in progress. I will be updating this repository as I continue to work on this project.

## Prerequisites
- Python 3.8+
- Conda (for environment management)
- Git

## Local Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/stock-prediction.git
cd stock-prediction
```

### 2. Create and Activate Conda Environment
```bash
conda create -n scipy python=3.8
conda activate scipy
```

### 3. Install Dependencies
```bash
pip install -r frontend/requirements.txt
pip install -r requirements.txt  # if exists, or install manually: pandas, scikit-learn, mlflow, influxdb-client, yfinance, streamlit, etc.
```

### 4. Set Environment Variables
Create a `.env` file in the root directory with:
```
INFLUXDB_HOST=your-influxdb-host
INFLUXDB_TOKEN=your-token
INFLUXDB_ORG=your-org
INFLUXDB_BUCKET=your-bucket
INFLUXDB_PREDICTIONS_DB=predictions
MLFLOW_TRACKING_URI=mlruns
```

## Usage

### Train Model
Run the notebook `model_lifecycle.ipynb` in Jupyter to train and log the model.

### Run Prediction Workflow
```bash
python -m ml.ml_functions.mlflow_predict_workflow
```

### Start Frontend
```bash
cd frontend
streamlit run streamlit_app.py
```

## Project Structure
- `ml/`: Machine learning code (features, training, registry, serve)
- `frontend/`: Streamlit app for visualization
- `model_lifecycle.ipynb`: Main notebook for model lifecycle
