import ray


@ray.remote(num_cpus=5)
def train_and_tune_extra_tree_model(sp500_data):
    from sklearn.metrics import accuracy_score
    from sklearn.ensemble import ExtraTreesClassifier
    from sklearn.model_selection import train_test_split
    from ray import tune
    from ray.tune.sklearn import TuneSearchCV

    X = sp500_data.drop(['Target'], axis=1)
    train_x, test_x, train_y, test_y = train_test_split(X, sp500_data['Target'], test_size=0.25, random_state=42)

    model = ExtraTreesClassifier(random_state=42)
    param_distributions = {
        'n_estimators': tune.randint(100, 2000),
        'max_depth': tune.randint(100, 2000),
        "criterion": tune.choice(["gini", "entropy"]),
        'min_samples_split': tune.choice([1, 2, 5]),
        'min_samples_leaf': tune.choice([1, 2, 5]),
        'max_features': tune.choice(['auto', 'sqrt', 'log2'])
    }

    tuner = TuneSearchCV(
        model,
        param_distributions,
        n_trials=10,  # Anzahl der Durchläufe
        early_stopping=False,  # Frühzeitiges Stoppen für schlecht abschneidende Trials
        max_iters=10,  # Maximale Anzahl von Iterationen pro Trial
        search_optimization="random",  # Optimierungsalgorithmus
        cv=5,  # Kreuzvalidierung
        random_state=42,
    )
    tuner.fit(train_x, train_y)
    best_model = tuner.best_estimator_
    # joblib.dump(best_model, './data/predict_model/best_extra_tree_model.pkl')
    predictions = best_model.predict(test_x)
    accuracy = accuracy_score(test_y, predictions)
    print(f"Best model parameters: {tuner.best_params_}")
    print(f"Test Accuracy: {accuracy}")

    return best_model, accuracy


def log_to_mlflow(model, accuracy):
    import mlflow
    from mlflow.tracking import MlflowClient

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
    import mlflow

    df, prediction_df = db_operations.get_data_from_influx()
    logged_model = prediction_df["model"].iloc[0]
    loaded_model = mlflow.pyfunc.load_model(logged_model)
    prediction = loaded_model.predict(df)
    prediction_df["Target"] = prediction
    db_operations.save_prediction_to_influx(prediction_df)

    return prediction_df
