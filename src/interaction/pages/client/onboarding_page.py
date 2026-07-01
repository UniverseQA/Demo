from src.interaction.pages.base_page import BasePage
from src.interaction.locators.first_launch_locators import StartPageLocators

class StartPage(BasePage):
    """Класс взаимодействия со стартовой страницей онбординга Saby Admin."""

    def click_start(self) -> None:
        """Нажимает на оранжевую кнопку 'Начать'."""
        self.click(StartPageLocators.START_BUTTON)

    def click_skip(self) -> None:
        """Нажимает на кнопку 'Пропустить'."""
        self.click(StartPageLocators.SKIP_BUTTON)

    def verify_visual_layout(self, template_name: str = "start_page_baseline") -> None:
        """Проверяет внешний вид стартовой страницы по эталонному скриншоту."""
        # Этот метод мы сейчас внедрим в BasePage для скриншотных тестов
        self.assert_screen_matches_template(template_name)

from src.interaction.pages.base_page import BasePage
from src.interaction.locators.first_launch_locators import NotificationPageLocators, AndroidSystemPermissionLocators

class NotificationPage(BasePage):
    """Класс взаимодействия с экраном запроса уведомлений."""

    def click_allow_onboarding(self) -> None:
        """Нажимает кнопку 'Разрешить' на экране онбординга приложения."""
        self.click(NotificationPageLocators.ALLOW_ONBOARDING_BUTTON)

    def accept_system_notification_dialog(self) -> None:
        """Ожидает системный диалог Android и нажимает на нем нативную кнопку 'Разрешить'."""
        self.click(AndroidSystemPermissionLocators.SYSTEM_ALLOW_BUTTON)

    def skip_notification(self) -> None:
        """Нажимает кнопку 'Пропустить' в верхнем углу."""
        self.click(NotificationPageLocators.SKIP_BUTTON)

    def verify_visual_layout(self, template_name: str = "notification_page_baseline") -> None:
        """Проверяет внешний вид страницы онбординга уведомлений по скриншоту."""
        self.assert_screen_matches_template(template_name)