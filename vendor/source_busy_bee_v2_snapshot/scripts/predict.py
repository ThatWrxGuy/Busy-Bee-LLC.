from pathlib import Path

from busy_bee.config import load_settings
from busy_bee.schemas.inference import CustomerFeatures
from busy_bee.services.predictor import PredictorService


def main() -> None:
    settings = load_settings()
    model_path = str(Path(settings.artifacts.model_dir) / settings.artifacts.model_file)
    service = PredictorService(model_path)
    sample = CustomerFeatures(
        age=41,
        monthly_spend=175.0,
        tenure_months=10,
        contract_type="monthly",
        support_calls=2,
    )
    print(service.predict_one(sample))


if __name__ == "__main__":
    main()
