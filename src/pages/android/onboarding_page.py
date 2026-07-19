from src.pages.base_page import BasePage
from src.locators.android.onboarding_locators import (
    CommonOnboardingLocators,
    ScreenShareSystemLocators,
    NotificationSystemLocators,
    AccessibilitySystemLocators,
    OverlaySystemLocators,
    FileSystemSystemLocators
)


class OnboardingPage(BasePage):
    """Класс для взаимодействия со всеми видами онбординга в приложении"""

    # --- БАЗОВЫЕ КЛИКИ ---

    def click_tour_button(self) -> None:
        """Нажимает на нижнюю кнопку продолжения тура онбординга (Начать / Разрешить / Начать работу)"""
        self.click(CommonOnboardingLocators.MAIN_TOUR_BUTTON)

    def click_skip_tour(self) -> None:
        """Нажимает на кнопку 'Пропустить' в верхнем углу тура"""
        self.click(CommonOnboardingLocators.SKIP_TOUR_BUTTON)

    def accept_screen_share(self) -> None:
        """Нажимает 'Показать экран' в системном запросе Android"""
        self.click(ScreenShareSystemLocators.ALLOW_BUTTON)

    # --- УМНЫЙ ВОЗВРАТ ИЗ НАСТРОЕК ОС ---

    def return_to_app(self) -> None:
        """Умный возврат в приложение из системных настроек ОС Android с ожиданием пакета"""
        import time
        from selenium.webdriver.support.ui import WebDriverWait

        app_package = "ru.tensor.sbis.sabyadmin.debug"

        # Циклически нажимаем Назад, пока верхним пакетом не станет наше приложение
        for attempt in range(5):
            if self.driver.current_package == app_package:
                break
            self.driver.press_keycode(4)
            time.sleep(0.8)

        # Ждем полной стабилизации интерфейса Saby Admin после возвращения фокуса
        try:
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.current_package == app_package
            )
        except Exception:
            raise RuntimeError("Не удалось дождаться появления Saby Admin на экране")

    # --- ВЫСОКОУРОВНЕВЫЕ СЦЕНАРИИ (СТРАТЕГИИ) ---

    def pass_onboarding(self) -> None:
        """Полное прохождение онбординга с выдачей всех разрешений"""

        # 1. Экран приветствия
        self.click_tour_button()

        # 2. Экран уведомлений
        self.click_tour_button()
        self.click(NotificationSystemLocators.SYSTEM_ALLOW_BUTTON)

        # 3. Спец. возможности
        self.click_tour_button()
        self.click(AccessibilitySystemLocators.APP_POPUP_ALLOW_BUTTON)
        self.click(AccessibilitySystemLocators.SABY_ADMIN_SERVICE_ITEM)
        self.click(AccessibilitySystemLocators.SERVICE_MAIN_SWITCH)
        self.click(AccessibilitySystemLocators.DIALOG_ALLOW_BUTTON)
        self.return_to_app()

        # 4. Отображение поверх других приложений
        self.click_tour_button()
        self.click(OverlaySystemLocators.SABY_ADMIN_MENU_ITEM)
        self.click(OverlaySystemLocators.OVERLAY_SWITCH_CONTAINER)
        self.return_to_app()

        # 5. Доступ к файловой системе
        self.click_tour_button()
        self.click(FileSystemSystemLocators.FILE_SWITCH_CONTAINER)
        self.return_to_app()

        # 6. Клик на "Начать работу"
        self.click_tour_button()

    def pass_post_auth_auto_connect(self) -> None:
        """Выдача разрешения на автоподключение после авторизации"""
        # Клик по кнопке "Разрешить" на экране автоподключения
        self.click_tour_button()

        # Системное окно Android: клик по кнопке "Показать экран"
        self.accept_screen_share()

    def skip_onboarding_completely(self) -> None:
        """Быстрый пропуск онбординга через кнопку верхнего тулбара"""
        self.click_skip_tour()
