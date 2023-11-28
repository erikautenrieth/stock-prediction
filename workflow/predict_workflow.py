from ml_functions.model_serve import SageMakerHandler

sagemaker_handler = SageMakerHandler(app_name="stockmodel", region="eu-central-1")
sagemaker_handler.get_data_and_predict()