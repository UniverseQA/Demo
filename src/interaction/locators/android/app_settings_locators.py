from selenium.webdriver.common.by import By


class AppSettingsLocators:
    """Локаторы экрана настроек приложения"""

    # Синяя кнопка "Войти" в самом верхнем блоке
    SIGN_IN_BUTTON = (By.ID, "ru.tensor.sbis.sabyadmin.debug:id/sabyadmin_sign_in_button")

    # Кнопка "Назад" в левом верхнем углу тулбара
    TOOLBAR_BACK_BUTTON = (By.ID, "ru.tensor.sbis.sabyadmin.debug:id/top_navigation_btn_back")