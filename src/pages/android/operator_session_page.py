import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.pages.base_page import BasePage
from src.locators.android.operator_session_locators import OperatorSessionPageLocators


class OperatorSessionPage(BasePage):
    """Страница активной сессии оператора"""

    def is_session_active(self, timeout: int = 20) -> bool:
        """Проверяет появление птички МДО"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(OperatorSessionPageLocators.OAM_BIRD_BUTTON),
            )
            return element.is_displayed()
        except Exception as e:
            print(f"\n[ERROR] Сессия не активировалась за {timeout} секунд: {e}")
            return False

    def open_oam(self) -> None:
        """Нажимает на кнопку птички (МДО)"""
        print("[Appium] Открываем МДО (клик по птичке)")
        self.click(OperatorSessionPageLocators.OAM_BIRD_BUTTON)

    def select_device_screens(self) -> None:
        """Выбирает пункт 'Экраны устройства' в МДО"""
        print("[Appium] Выбираем пункт 'Экраны устройства'")
        self.click(OperatorSessionPageLocators.OAM_DEVICE_SCREENS_ITEM)

    def select_first_screen(self) -> None:
        """Выбирает первый экран в МДО 'Экраны устройства'"""
        print("[Appium] Выбираем первый экран")
        self.click(OperatorSessionPageLocators.OAM_FIRST_SCREEN)

    def select_second_screen(self) -> None:
        """Выбирает второй экран в МДО 'Экраны устройства'"""
        print("[Appium] Выбираем второй экран")
        self.click(OperatorSessionPageLocators.OAM_SECOND_SCREEN)

    def back_to_oam_from_device_screens(self) -> None:
        """Нажимает на стрелочку Назад из раздела 'Экраны устройства'"""
        print("[Appium] Нажимаем на стрелочку назад")
        self.click(OperatorSessionPageLocators.OAM_DEVICE_SCREENS_BACK_BUTTON)

    def close_oam(self, max_depth: int = 3) -> None:
        """Закрывает МДО с любой глубины вложенности подменю до появления кнопки птички"""
        print("[Appium] Закрываем МДО...")

        for level in range(max_depth):
            # Если птичка видна — МДО полностью закрыто
            if self.is_element_present(OperatorSessionPageLocators.OAM_BIRD_BUTTON, timeout=1):
                print("[Appium] МДО полностью закрыто, птичка видна на экране")
                return

            print(f"[Appium] Шаг {level + 1}: птичка скрыта. Нажимаем 'Назад' для выхода из подменю МДО")
            self.driver.back()

        # Финальная проверка
        assert self.is_element_present(OperatorSessionPageLocators.OAM_BIRD_BUTTON, timeout=3), (
            "Ошибка: не удалось закрыть МДО, кнопка 'птички' не появилась после выхода из подменю"
        )
