class LinuxCliPatterns:
    """Текстовые маркеры и подсказки из stdout Linux CLI приложения"""

    # Строка-приглашение к вводу кода подключения
    PROMPT_ENTER_CODE = "Enter connection code:"

    # Строка, сигнализирующая об успешном сопряжении
    STATUS_SESSION_ESTABLISHED = "Session established"

    # Строка ошибки при неверном коде
    ERROR_INVALID_CODE = "Error: Invalid connection code"

    # Строка закрытия сессии
    STATUS_SESSION_CLOSED = "Session closed by peer"
