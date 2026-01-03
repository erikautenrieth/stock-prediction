import sys
import os
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

import boto3
from mlflow.deployments import get_deploy_client
from dotenv import load_dotenv

load_dotenv()


region = os.getenv('SAGEMAKER_REGION')
model_uri = f"{base_dir}/mlruns/354565172707154508/5a62984791c945a1bae69cd36a1a23fb/artifacts/model"
aws_account_id = os.getenv('AWS_ACCOUNT_ID')
execution_role_arn = "arn:aws:iam::401605265667:role/service-role/AmazonSageMakerServiceCatalogProductsUseRole"
name = "for-sagemaker-deployment"
tag_id = '2.8.1'
image_url = f"{aws_account_id}.dkr.ecr.{region}.amazonaws.com/{name}:" + tag_id

bucket_name=""

config = {
    "execution_role_arn": execution_role_arn,
    "bucket_name": bucket_name,
    "image_url": image_url,
    "region_name": os.getenv('SAGEMAKER_REGION'),
    "archive": False,
    "instance_type": "ml.m5.large", # ml.t3.medium
    "instance_count": 1,
    "synchronous": True,
    "timeout_seconds": 3600,
    "variant_name": "prod-variant-1",
    "tags": {"training_timestamp": "2023-11-22"},
}

boto3.setup_default_session(
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=region
)

## (1) AWS Container
# mlflow sagemaker build-and-push-container --build --push -c for-sagemaker-deployment


## (2) Sagemaker Endpoint
client = get_deploy_client("sagemaker")

client.create_deployment(
    name="stockmodel",
    model_uri=model_uri,
    flavor="python_function",
    config=config,
)
