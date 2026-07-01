import pytest
from src.steps.session_steps import SessionSteps


def test_remote_support_connection_e2e(android_client, linux_operator):
    """
    Сквозной тест теперь читается как описание бизнес-процесса.
    """
    # Инициализируем бизнес-шаги, прокидывая интерфейсы
    session = SessionSteps(android_client, linux_operator)

    # Выполняем сценарий
    session.establish_remote_connection()

    # Проверяем результат
    session.verify_connection_active()