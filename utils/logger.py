import logging
import sys
from pathlib import Path


def get_logger(name: str) -> logging.Logger:
    """
    Создает
    и
    настраивает
    структурированный
    логгер
    для
    фреймворка.
    Пишет
    логи
    одновременно
    в
    stdout
    и
    в
    файл
    фреймворка
    automation.log.
    """
    logger = logging.getLogger(name)

    # Предотвращаем дублирование логов при повторном вызове
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        # Шаблон лога: Время | Уровень | Имя модуля -> Сообщение
        formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Настройка вывода в консоль
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(formatter)
        logger.addHandler(stdout_handler)

        # Настройка записи в файл в корне проекта
        log_file = Path(__file__).parent.parent / "automation.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger