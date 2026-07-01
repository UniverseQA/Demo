from src.interaction.pages.base_page import BasePage
from src.interaction.locators.client_locators import ClientHomeLocators


class ClientHomePage(BasePage):
    """
    Класс взаимодействия с главным экраном клиента Android (режим ожидания).

    Управляет элементами генерации кода и инициации сессии удаленной поддержки.
    """

    def get_connection_code(self) -> str:
        """
        Считывает
        сгенерированный
        код
        подключения
        с
        экрана
        приложения.

        :return: Строка
        с
        кодом
        подключения(например, '123-456').
        """
        # Метод find_element в BasePage использует WebDriverWait, исключая гонки софта
        code = self.get_text(ClientHomeLocators.GENERATED_CODE_LABEL)
        return code.strip()

    def refresh_connection_code(self) -> None:
        """
        Выполняет
        принудительное
        обновление
        кода
        удаленного
        подключения.

        Используется, если
        текущий
        код
        устарел
        по
        таймауту
        или
        скомпрометирован.
        """
        self.click(ClientHomeLocators.REFRESH_CODE_BUTTON)