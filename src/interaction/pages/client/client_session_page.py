from src.interaction.pages.base_page import BasePage
from src.interaction.locators.client_locators import ClientSessionLocators


class ClientSessionPage(BasePage):
    """
    Класс взаимодействия с экраном активной сессии удаленной поддержки на Android.

    Отвечает за мониторинг состояния соединения и корректное завершение работы сессии.
    """

    def get_session_status(self) -> str:
        """
        Получает
        текущий
        текстовый
        статус
        сессии
        из
        UI
        приложения.

        Используется
        для
        верификации
        успешного
        сопряжения
        в
        ассертах
        тестов.
        :return: Текстовый
        статус(например, 'Connected', 'Disconnected').
        """
        status = self.get_text(ClientSessionLocators.SESSION_STATUS_LABEL)
        return status.strip()

    def disconnect_from_session(self) -> None:
        """
        Инициирует
        разрыв
        текущей
        сессии
        удаленной
        поддержки
        со
        стороны
        клиента.

        Нажимает
        кнопку
        отключения
        и
        переводит
        приложение
        обратно
        на
        домашний
        экран.
        """
        self.click(ClientSessionLocators.DISCONNECT_BUTTON)