from pathlib import Path

import csv

import joblib
import mlflow
import mlflow.sklearn
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "model.pkl"


def main() -> None:
    iris = load_iris()
    X, y = iris.data, iris.target
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    mlflow.set_tracking_uri("sqlite:///" + (ROOT / "mlflow.db").as_posix())
    mlflow.set_experiment("iris")

    n_estimators = 100
    with mlflow.start_run():
        model = RandomForestClassifier(
            n_estimators=n_estimators, random_state=42
        ).fit(X_train, y_train)
        predictions = model.predict(X_test)
        accuracy = model.score(X_test, y_test)
        rows = []
        for index, (features, actual, predicted) in enumerate(
            zip(X_test, y_test, predictions), start=1
        ):
            rows.append({
                "test_number": index,
                "sepal_length_cm": float(features[0]),
                "sepal_width_cm": float(features[1]),
                "petal_length_cm": float(features[2]),
                "petal_width_cm": float(features[3]),
                "actual_species": str(iris.target_names[actual]),
                "predicted_species": str(iris.target_names[predicted]),
                "correct": bool(actual == predicted),
            })
        output = ROOT / "results"
        output.mkdir(exist_ok=True)
        csv_path = output / "test_predictions.csv"
        with csv_path.open("w", newline="", encoding="utf-8-sig") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        mlflow.log_artifact(str(csv_path), artifact_path="evaluation")
        mlflow.log_table({key: [row[key] for row in rows] for key in rows[0]}, artifact_file="evaluation/test_predictions.json")
        mlflow.log_params({"train_samples": len(X_train), "test_samples": len(X_test),
                           "random_state": 42})
        mlflow.log_metric("correct_predictions", int((predictions == y_test).sum()))

        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_metric("accuracy", accuracy)
        mlflow.sklearn.log_model(
            model, name="model", serialization_format="cloudpickle",
            input_example=X_train[:1],
        )
        joblib.dump(model, MODEL_PATH)

    print(f"accuracy={accuracy:.4f}")
    print(f"model saved to {MODEL_PATH}")


if __name__ == "__main__":
    main()
