import time
from selenium.webdriver.support import expected_conditions as EC
from src.pages.base_page import BasePage
from src.locators.android.auth_locators import AuthPageLocators


class AuthPage(BasePage):
    """Экран авторизации"""

    def change_stand_to_test(self) -> None:
        """Открывает спиннер стендов и переключает его на TEST"""
        self.click(AuthPageLocators.STAND_SPINNER)
        self.click(AuthPageLocators.TEST_STAND_OPTION)
        time.sleep(1.0)

    def login_with_credentials(self, login_value: str = "proletariat1", password_value: str = "qwerty1!") -> None:
        """Заполняет поля логина и пароля с учетом двухэтапного флоу авторизации"""
        # Этап 1: Вводим логин и жмем первую стрелку
        login_element = self.wait.until(EC.visibility_of_element_located(AuthPageLocators.LOGIN_FIELD))
        login_element.clear()
        login_element.send_keys(login_value)
        self.click(AuthPageLocators.FIRST_NEXT_BUTTON)

        # Этап 2: Ждем появления поля пароля, заполняем его и жмем Вход
        password_element = self.wait.until(EC.visibility_of_element_located(AuthPageLocators.PASSWORD_FIELD))
        password_element.clear()
        password_element.send_keys(password_value)
        self.click(AuthPageLocators.LOGIN_BUTTON)
        time.sleep(2.0)

    def click_back(self) -> None:
        """Нажимает кнопку 'Назад' в тулбаре для возврата на экран настроек"""
        self.click(AuthPageLocators.TOOLBAR_BACK_BUTTON)