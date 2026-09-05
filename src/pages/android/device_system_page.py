from src.pages.base_page import BasePage
from src.locators.android.device_system_locators import DeviceSystemLocators


class DeviceSystemPage(BasePage):
    """Единая страница для взаимодействия с экранами ОС вне приложения"""

    def open_files_app(self) -> None:
        """Открывает системное приложение 'Файлы'"""
        if self.recorder:
            self.recorder.set_banner("Открытие приложения 'Файлы'")
        self.click(DeviceSystemLocators.FILES_APP_ICON, step_description="click(Файлы)")

    def long_press_first_file(self, duration: float = 2.0) -> None:
        """Зажимает первый файл для выделения"""
        if self.recorder:
            self.recorder.set_banner("Выделение файла долгим нажатием")
        self.long_press(
            DeviceSystemLocators.FILE_FOR_SHARING,
            duration=duration,
            step_description="long_press(File)"
        )

    def click_share(self) -> None:
        """Нажимает 'Поделиться' в верхней панели"""
        if self.recorder:
            self.recorder.set_banner("Нажатие кнопки 'Поделиться'")
        self.click(DeviceSystemLocators.SHARE_BUTTON, step_description="click(Поделиться)")

    def select_saby_admin_in_share_menu(self) -> None:
        """Выбирает Saby Admin в шторке отправки"""
        if self.recorder:
            self.recorder.set_banner("Отправка файла в сессию Saby Admin")
        self.click(
            DeviceSystemLocators.SABY_ADMIN_SHARE_TARGET,
            step_description="click(Saby Admin)"
        )

    def open_app_drawer(self) -> None:
        """Свайпает с домашнего экрана вверх, открывая меню всех приложений"""
        self.swipe_up(start_y_ratio=0.85, end_y_ratio=0.25)
