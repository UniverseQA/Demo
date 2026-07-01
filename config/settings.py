import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Settings:
    # Appium & Android
    app_package: str = "com.support.remote.client"
    app_activity: str = ".MainActivity"
    appium_server_url: str = "http://127.0.0.1:4723"

    # Paths (переопределяются через переменные окружения или argparse)
    app_path: Optional[str] = os.getenv("APP_PATH")
    operator_path: str = os.getenv("OPERATOR_PATH", "./operator_cli")


# Создаем инстанс, который будет импортироваться в тесты
config = Settings()