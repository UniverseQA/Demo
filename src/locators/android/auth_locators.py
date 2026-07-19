from selenium.webdriver.common.by import By


class AuthPageLocators:
    """Локаторы экрана авторизации"""

    # Поле ввода логина (привязываемся к уникальному родительскому ViewGroup)
    LOGIN_FIELD = (By.XPATH, "//android.view.ViewGroup[@resource-id='ru.tensor.sbis.sabyadmin.debug:id/auth_login']//android.widget.EditText")

    # Первая промежуточная кнопка-стрелка после ввода логина
    FIRST_NEXT_BUTTON = (By.ID, "ru.tensor.sbis.sabyadmin.debug:id/auth_first_btn")

    # Поле ввода пароля (появляется после клика на FIRST_NEXT_BUTTON)
    PASSWORD_FIELD = (By.XPATH, "//android.view.ViewGroup[@resource-id='ru.tensor.sbis.sabyadmin.debug:id/auth_password']//android.widget.EditText")

    # Финальная синяя круглая кнопка входа со стрелкой
    LOGIN_BUTTON = (By.ID, "ru.tensor.sbis.sabyadmin.debug:id/auth_second_btn")

    # Выпадающий список (выбор стенда) под полями логина
    STAND_SPINNER = (By.ID, "ru.tensor.sbis.sabyadmin.debug:id/auth_stand_spinner")

    # Элемент тестового стенда внутри открывшегося спиннера
    TEST_STAND_OPTION = (By.XPATH, "//*[@text='TEST']")

    # Кнопка "Назад" в левом верхнем углу тулбара авторизации
    TOOLBAR_BACK_BUTTON = (By.ID, "ru.tensor.sbis.sabyadmin.debug:id/top_navigation_btn_back")
