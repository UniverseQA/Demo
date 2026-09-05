from src.pages.base_page import BasePage
from src.locators.android.main_page_locators import MainPageLocators
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from typing import Optional
import pytest


class MainPage(BasePage):
    """Главная страница приложения Saby Admin (экран с кодом подключения)"""

    def open_settings(self) -> None:
        """Нажимает на кнопку-шестерёнку для перехода в настройки приложения"""
        self.click(MainPageLocators.SETTINGS_GEAR)

    def get_connection_code(self) -> str:
        """Считывает текущий код подключения с экрана"""
        return self.get_text(MainPageLocators.CONNECTION_CODE)

    def accept_connection_request(self, timeout: int = 20) -> None:
        """Ожидает появление диалога входящего подключения и нажимает 'Разрешить'"""
        self._show_indicator("Ожидание входящего запроса на подключение от оператора...", is_success=False)

        # 1. Ждем появление текста запроса
        self.assert_text_contains(
            locator=MainPageLocators.ALLOW_CONNECTION_BUTTON,
            expected_text="Разрешить",
            element_name="Кнопка 'Разрешить'",
            timeout=timeout,
            hold_seconds=1.5
        )

        # 2. Кликаем на кнопку «Разрешить» с подсветкой клика
        self.click(MainPageLocators.ALLOW_CONNECTION_BUTTON, step_description="click(Разрешить)")
        self._show_indicator("Подключение оператора подтверждено!", is_success=True)

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

    def enter_connection_code(self, code: str) -> None:
        """Вводит 6-ти значный код подключения"""
        element = self.find_element(MainPageLocators.CONNECTION_CODE_INPUT)
        element.clear()
        element.send_keys(code)

    def click_connect_button(self) -> None:
        """Нажимает на кнопку 'Подключиться'"""
        self.click(MainPageLocators.CONNECT_BUTTON)

    def is_disconnected_panel_displayed(self, timeout: int = 15) -> bool:
        """Проверяет появление панели 'Вы были подключены к...'"""
        print("[Appium] Ожидаем появление панели завершения сессии...")
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(MainPageLocators.DISCONNECTED_PANEL_TITLE),
            )
            return element.is_displayed()
        except Exception as e:
            print(f"\n[ERROR] Плашка завершения не появилась: {e}")
            return False

    def verify_disconnected_panel_details(
        self,
        expected_title: Optional[str] = None,
        expected_client_name: Optional[str] = None,
        expected_company: Optional[str] = None,
        timeout: int = 15
    ) -> None:
        """Построчно проверяет заголовок, ФИО и компанию на панели завершения сессии"""

        # 1. Проверка Заголовка панели
        if expected_title:
            self._show_indicator(f"Проверка заголовка (ожидается: '{expected_title}')...", is_success=False)
            self.assert_text_contains(
                locator=MainPageLocators.DISCONNECTED_PANEL_TITLE,
                expected_text=expected_title,
                element_name="Заголовок панели",
                timeout=timeout
            )
            self._show_indicator("Заголовок совпал!", is_success=True)

        # 2. Проверка ФИО Клиента / Оператора
        if expected_client_name:
            self._show_indicator(f"Проверка ФИО (ожидается: '{expected_client_name}')...", is_success=False)
            self.assert_text_contains(
                locator=MainPageLocators.DISCONNECTED_PANEL_NAME,
                expected_text=expected_client_name,
                element_name="ФИО клиента",
                timeout=timeout
            )
            self._show_indicator("ФИО клиента совпало!", is_success=True)

        # 3. Проверка Названия компании
        if expected_company:
            self._show_indicator(f"Проверка компании (ожидается: '{expected_company}')...", is_success=False)
            self.assert_text_contains(
                locator=MainPageLocators.DISCONNECTED_PANEL_COMPANY,
                expected_text=expected_company,
                element_name="Название компании",
                timeout=timeout,
                hold_seconds=2.0  # Удерживаем финальный кадр 2 секунды
            )
            self._show_indicator("Название компании совпало!", is_success=True)