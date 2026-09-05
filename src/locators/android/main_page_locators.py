from appium.webdriver.common.appiumby import AppiumBy


class MainPageLocators:
    """Локаторы главной страницы приложения Saby Admin (экран с кодом)"""

    # Кнопка настроек в верхнем правом углу (иконка человечка без авторизации)
    SETTINGS_GEAR = (AppiumBy.ID, "ru.tensor.sbis.sabyadmin.debug:id/sabyadmin_unauthorized_user")

    # Текстовое поле с кодом для подключения
    CONNECTION_CODE = (AppiumBy.ID, "ru.tensor.sbis.sabyadmin.debug:id/sabyadmin_code_text")

    # Блок оператора - поле ввода кода и кнопка "Подключиться"
    CONNECTION_CODE_INPUT = (AppiumBy.ID, "ru.tensor.sbis.sabyadmin.debug:id/sabyadmin_magic_code_edit_text")
    CONNECT_BUTTON = (AppiumBy.ID, "ru.tensor.sbis.sabyadmin.debug:id/sabyadmin_connect_button")

    # --- Панель завершения сессии ---
    DISCONNECTED_PANEL = (AppiumBy.ID, "ru.tensor.sbis.sabyadmin.debug:id/modalwindows_movable_panel_container_id")
    DISCONNECTED_PANEL_TITLE = (AppiumBy.ID, "ru.tensor.sbis.sabyadmin.debug:id/sabyadmin_recent_operators_title")
    DISCONNECTED_PANEL_NAME = (AppiumBy.ID, "ru.tensor.sbis.sabyadmin.debug:id/sabyadmin_recent_operator_name")
    DISCONNECTED_PANEL_COMPANY = (AppiumBy.ID, "ru.tensor.sbis.sabyadmin.debug:id/sabyadmin_recent_operator_title_company")

    # Блок клиента - запрос на подключение
    ALLOW_CONNECTION_BUTTON = (AppiumBy.ID, "ru.tensor.sbis.sabyadmin.debug:id/sabyadmin_sbis_allow_button")