import mlflow
from mlflow.tracking import MlflowClient

def log_to_mlflow(model, accuracy):

    mlflow.set_experiment("sp500_prediction")
    mlflow.set_tracking_uri("http://localhost:5000")
    best_extra_tree = "best_extra_tree_model"

    default_logged_model = 'runs:/c413fe91b94f4a8db7492ffa6657a0f6/model'

    with mlflow.start_run():
        mlflow.sklearn.log_model(model, "model")
        mlflow.log_metric("accuracy", accuracy)
        run_id = mlflow.active_run().info.run_uuid
        actual_model_path = f"runs:/{run_id}/model"
        client = MlflowClient()
        try:
            registered_model = client.get_registered_model(best_extra_tree)
        except:
            registered_model = None

        if not registered_model:
            client.create_registered_model(best_extra_tree)
            client.create_model_version(name=best_extra_tree,
                                        source=actual_model_path,
                                        run_id=run_id)
        else:
            latest_version = client.get_latest_versions(best_extra_tree, stages=["Production"])[0]
            latest_metrics = client.get_run(latest_version.run_id).data.metrics
            if "accuracy" in latest_metrics:
                latest_accuracy = latest_metrics["accuracy"]
                if accuracy > latest_accuracy:
                    version_info = client.create_model_version(name=best_extra_tree,
                                                               source=actual_model_path,
                                                               run_id=run_id)

                    client.transition_model_version_stage(
                        name=version_info.name,
                        version=version_info.version,
                        stage="Production"
                    )

                    print("New model registered as best model!")
                    return actual_model_path
                else:
                    print("The new model isn't better")
                    return default_logged_model


def model_prediction(db_operations):

    df, prediction_df = db_operations.get_data_from_influx()
    logged_model = prediction_df["model"].iloc[0]
    loaded_model = mlflow.pyfunc.load_model(logged_model)
    prediction = loaded_model.predict(df)
    prediction_df["Target"] = prediction
    db_operations.save_prediction_to_influx(prediction_df)

    return prediction_df