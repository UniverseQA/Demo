from selenium.webdriver.common.by import By


class ClientHomeLocators:
    """Локаторы для главного экрана мобильного клиента (режим ожидания подключения)."""

    # Поле, где отображается сгенерированный код для оператора
    GENERATED_CODE_LABEL = (By.ID, "com.support.remote.client:id/code_field")

    # Кнопка принудительного перегенерации кода (если есть в аппке)
    REFRESH_CODE_BUTTON = (By.ID, "com.support.remote.client:id/refresh_button")


class ClientSessionLocators:
    """Локаторы для экрана активной сессии удаленной поддержки."""

    # Текстовый статус сессии (например, "Connected", "Disconnected")
    SESSION_STATUS_LABEL = (By.ID, "com.support.remote.client:id/status_field")

    # Кнопка завершения сессии со стороны клиента
    DISCONNECT_BUTTON = (By.ID, "com.support.remote.client:id/disconnect_button")


