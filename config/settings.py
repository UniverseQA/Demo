import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Settings:
    # Appium & Android
    app_package: str = "ru.tensor.sbis.sabyadmin.debug"
    app_activity: str = ".MainActivity"
    appium_server_url: str = "http://127.0.0.1:4723"

    # Пути по умолчанию (берутся из переменных окружения)
    app_path: Optional[str] = os.getenv("APP_PATH")
    operator_path: str = os.getenv("OPERATOR_PATH", "./operator_cli")


# Инициализируем базовый конфиг
config = Settings()

# --- МЕХАНИЗМ ЛОКАЛЬНОГО ОВЕРРАЙДА ---
try:
    # Пытаемся импортировать локальные пути из /config/local_settings.py
    from config import local_settings

    if hasattr(local_settings, "APP_PATH"):
        config.app_path = local_settings.APP_PATH
    if hasattr(local_settings, "OPERATOR_PATH"):
        config.operator_path = local_settings.OPERATOR_PATH

    print(f"[CONFIG] Подгружены локальные настройки для PyCharm. APK: {config.app_path}")
except ImportError:
    # Если файла нет (например, в Jenkins) — просто идем дальше по дефолтам
    pass
