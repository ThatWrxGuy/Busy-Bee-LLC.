from busy_bee.config import load_settings
from busy_bee.logging_config import configure_logging
from busy_bee.services.trainer import TrainerService


def main() -> None:
    settings = load_settings()
    configure_logging(settings.app.log_level)
    result = TrainerService(settings).run()
    print(result)


if __name__ == "__main__":
    main()
