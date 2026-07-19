from src.pages.base_page import BasePage
from src.locators.android.app_settings_locators import AppSettingsLocators

class AppSettingsPage(BasePage):
    """Экран настроек приложения"""

    def click_sign_in(self) -> None:
        """Нажимает на синюю кнопку 'Войти' в шапке настроек"""
        self.click(AppSettingsLocators.SIGN_IN_BUTTON)

    def click_back(self) -> None:
        """Нажимает кнопку 'Назад' в тулбаре для возврата на Главную страницу"""
        self.click(AppSettingsLocators.TOOLBAR_BACK_BUTTON)