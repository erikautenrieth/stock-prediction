import os
import pathlib
import mlflow

from mlflow.tracking import MlflowClient
from ml.features.preprocessing import get_data


def _set_mlflow_tracking():
    """Set MLflow tracking URI from env or default to local mlruns"""
    uri = os.getenv("MLFLOW_TRACKING_URI", "mlruns")
    if "://" not in uri:
        uri = pathlib.Path(uri).resolve().as_uri()
    mlflow.set_tracking_uri(uri)


def log_sklearn_model_to_mlflow(model, accuracy, feature_names=None):
    """ Log a sklearn model with mlflow
    :param model: sklearn model
    :param accuracy: model accuracy
    :param feature_names: list of feature names
    :return: None
    """

    _set_mlflow_tracking()
    mlflow.set_experiment("sp500_prediction")
    
    best_model = f"best_{model.__class__.__name__}_model"

    #default_logged_model = 'ExtraTreesClassifier'
    default_model_path = load_model_path()

    with mlflow.start_run():
        mlflow.sklearn.log_model(model, "model")
        mlflow.log_metric("accuracy", accuracy)
        run_info = mlflow.active_run().info
        run_id = getattr(run_info, "run_id", None) or getattr(run_info, "run_uuid", None)
        actual_model_path = f"runs:/{run_id}/model"
        client = MlflowClient()
        try:
            registered_model = client.get_registered_model(best_model)
        except Exception as e:
            if "RESOURCE_DOES_NOT_EXIST" in str(e):
                registered_model = None
            else:
                print("Fehler:", e)
                registered_model = None

        if not registered_model:
            client.create_registered_model(best_model)
            version_info = client.create_model_version(name=best_model,
                                                       source=actual_model_path,
                                                       run_id=run_id)

            client.transition_model_version_stage(
                name=best_model,
                version=version_info.version,
                stage="Production"
            )
            print("First model registered as best model!")
            save_model_path(actual_model_path)
            return

        else:
            latest_version = client.get_latest_versions(best_model, stages=["Production"])[0]
            latest_metrics = client.get_run(latest_version.run_id).data.metrics
            if "accuracy" in latest_metrics:
                latest_accuracy = latest_metrics["accuracy"]
                if accuracy > latest_accuracy:
                    version_info = client.create_model_version(name=best_model,
                                                               source=actual_model_path,
                                                               run_id=run_id)

                    client.transition_model_version_stage(
                        name=version_info.name,
                        version=version_info.version,
                        stage="Production"
                    )
                    stock_data, last_day_df = get_data(save_data=True, new_model=(model.__class__.__name__, accuracy))
                    print("New model registered as best model!")
                    save_model_path(actual_model_path)
                    return actual_model_path
                else:
                    print("The new model isn't better")
                    return default_model_path

def save_model_path(actual_model_path):
    model_file_path = f"{os.getcwd()}/ml/data/metadata/actual_model.txt"
    with open(model_file_path, 'w') as file:
        file.write(actual_model_path)
    print("Model path saved!")

def load_model_path():
    model_file_path = f"{os.getcwd()}/ml/data/metadata/actual_model.txt"
    try:
        with open(model_file_path, 'r') as file:
            model_path = file.read()
        print("Model path loaded!")
        return model_path
    except FileNotFoundError:
        print("Model path file not found.")