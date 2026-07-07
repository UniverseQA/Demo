from src.interaction.pages.base_page import BasePage
from src.interaction.locators.android.main_page_locators import MainPageLocators
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pytest


class MainPage(BasePage):
    """Главная страница приложения Saby Admin (экран с кодом подключения)"""

    def open_settings(self) -> None:
        """Нажимает на кнопку-шестерёнку для перехода в настройки приложения"""
        self.click(MainPageLocators.SETTINGS_GEAR)

    def get_connection_code(self) -> str:
        """Считывает текущий код подключения с экрана"""
        return self.get_text(MainPageLocators.CONNECTION_CODE)

    def verify_visual_layout(self, template_name: str) -> None:
        """Проверяет внешний вид главной страницы, дожидаясь её прогрузки и скрывая код подключения"""

        # Сразу объявляем имя шаблона для глобального перехватчика падений
        pytest.last_template_name = template_name

        # Ждем прогрузки кода подключения до 30 секунд
        WebDriverWait(self.driver, 30).until(
            EC.visibility_of_element_located(MainPageLocators.CONNECTION_CODE)
        )

        # Вызываем стандартное попиксельное сравнение (маскируем только динамический код)
        self.assert_screen_matches_template(template_name, ignored_locators=[MainPageLocators.CONNECTION_CODE])
