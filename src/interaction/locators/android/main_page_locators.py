from selenium.webdriver.common.by import By


class MainPageLocators:
    """Локаторы главной страницы приложения Saby Admin (экран с кодом)"""

    # Кнопка настроек в верхнем правом углу (иконка человечка без авторизации)
    SETTINGS_GEAR = (By.ID, "ru.tensor.sbis.sabyadmin.debug:id/sabyadmin_unauthorized_user")

    # Текстовое поле с кодом для подключения
    CONNECTION_CODE = (By.ID, "ru.tensor.sbis.sabyadmin.debug:id/sabyadmin_code_text")
