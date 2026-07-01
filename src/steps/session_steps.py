from src.interaction.pages.client.client_home_page import ClientHomePage
from src.interaction.pages.client.client_session_page import ClientSessionPage
from src.interaction.cli.linux_operator_cli import LinuxOperatorCLI


class SessionSteps:
    """
    Класс для описания бизнес-процессов удаленной поддержки.
    Объединяет действия клиента и оператора в единые сценарии.
    """

    def __init__(self, driver, operator_cli: LinuxOperatorCLI):
        self.client_home = ClientHomePage(driver)
        self.client_session = ClientSessionPage(driver)
        self.operator = operator_cli

    def establish_remote_connection(self) -> None:
        """Сквозной процесс: получение кода -> ввод -> проверка статуса."""
        # 1. Получаем код от клиента
        connection_code = self.client_home.get_connection_code()

        # 2. Передаем код оператору
        self.operator.connect_to_client(connection_code)

        # 3. Валидация перехода на экран сессии (неявная, через проверку статуса в тестах)

    def verify_connection_active(self) -> None:
        """Проверяет, что статус на клиенте изменился на 'Connected'."""
        status = self.client_session.get_session_status()
        assert status == "Connected", f"Ожидался статус Connected, получили: {status}"