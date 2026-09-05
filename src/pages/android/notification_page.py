from typing import Optional
from src.pages.base_page import BasePage
from src.locators.android.notification_locators import NotificationLocators


class NotificationPage(BasePage):
    """Страница пуш-уведомлений"""

    def expand_saby_admin_notification_group(self, timeout: int = 15) -> None:
        "Разворачивает группу уведомлений Saby Admin"
        try:
            self.click(NotificationLocators.SABY_ADMIN_GROUP_EXPAND_BUTTON)
        except Exception:
            ...

    def verify_file_transfer_completed_push(self, timeout: int = 15) -> None:
        """Проверяет появление Push-уведомления о завершении передачи/скачивания файла"""
        self._show_indicator("Ожидание Push-уведомления о передаче файла...", is_success=False)

        # 1. Открываем шторку
        self.open_notifications_shade()

        # 2. Раскрываем группу Saby Admin
        self.expand_saby_admin_notification_group()
        # 3. Используем базовый метод assert_text_contains для подсвечивания в видео
        self.assert_text_contains(
            locator=NotificationLocators.FILE_TRANSFER_COMPLETED_PUSH,
            expected_text="Скачивание файлов с устройства завершено",
            element_name="Push передачи файлов",
            timeout=timeout,
            hold_seconds=2.0
        )
        self._show_indicator("Push о передаче файла получен!", is_success=True)

        # 4. Возвращаемся в приложение
        self.driver.back()
