import pytest
from selenium.webdriver.common.by import By

GENERATED_CODE_LABEL = (By.ID, "com.support.remote.client:id/code_field")
SESSION_STATUS_LABEL = (By.ID, "com.support.remote.client:id/status_field")

def test_remote_support_connection_e2e(android_client, linux_operator):
    """
    Сквозной тест синхронизации двух независимых акторов.
    Клиент на Android генерирует код -> Оператор в Linux CLI подключается по нему.
    """
    from src.interaction.pages.base_page import BasePage
    client_page = BasePage(android_client)
    
    connection_code = client_page.get_text(GENERATED_CODE_LABEL)
    assert connection_code != "", "Код подключения не сгенерировался!"
    
    linux_operator.connect_to_client(code=connection_code)
    
    current_status = client_page.get_text(SESSION_STATUS_LABEL)
    assert current_status == "Connected", f"Ожидался статус Connected, но получили: {current_status}"
