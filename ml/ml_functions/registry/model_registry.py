import mlflow
from mlflow.tracking import MlflowClient
from ml.features.preprocessing import get_data


def log_sklearn_model_to_mlflow(model, accuracy, feature_names=None):

    mlflow.set_experiment("sp500_prediction")
    mlflow.set_tracking_uri("http://localhost:5000")
    best_model= f"best_{model.__class__.__name__}_model"

    default_logged_model = 'ExtraTreesClassifier'
    default_logged_accuracy = 0.8477341389728097
    default_model_path = "runs:/5a62984791c945a1bae69cd36a1a23fb/model"

    ## Save Feature names
    # pd.DataFrame({'feature_names': feature_names}).to_csv("features.csv", index=False)
    # mlflow.log_artifact("features.csv")

    with mlflow.start_run():
        mlflow.sklearn.log_model(model, "model")
        mlflow.log_metric("accuracy", accuracy)
        run_id = mlflow.active_run().info.run_uuid
        actual_model_path = f"runs:/{run_id}/model"
        client = MlflowClient()
        try:
            registered_model = client.get_registered_model(best_model)
        except Exception as e:
            if "RESOURCE_DOES_NOT_EXIST" in str(e):
                registered_model = None
            else:
                raise

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
                    return actual_model_path
                else:
                    print("The new model isn't better")
                    return default_model_path