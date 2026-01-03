import ray

from sklearn.metrics import accuracy_score
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.model_selection import train_test_split
from ray import tune
from ray.tune.sklearn import TuneSearchCV

@ray.remote(num_cpus=5)
def train_and_tune_extra_tree_model(sp500_data):


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



