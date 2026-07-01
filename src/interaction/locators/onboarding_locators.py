from selenium.webdriver.common.by import By

class StartPageLocators:
    """Локаторы для самой первой страницы онбординга (Start page)."""

    # Кнопка "Пропустить" вверху справа
    SKIP_BUTTON = (By.ID, "ru.tensor.sbis.sabyadmin.debug:id/onboarding_tour_close")

    # Кнопка "Начать" внизу справа
    START_BUTTON = (By.ID, "ru.tensor.sbis.sabyadmin.debug:id/onboarding_tour_button")

    # Текст дисклеймера правил и политики (для проверки видимости)
    TERMS_TEXT_VIEW = (By.ID, "ru.tensor.sbis.sabyadmin.debug:id/onboarding_tour_terms")

    # Ссылки внутри открывшегося браузера (для верификации перехода)
    BROWSER_RULES_ELEMENT = (By.XPATH, "//*[contains(@text, 'правила сервиса') or contains(@text, 'Terms')]")
    BROWSER_PRIVACY_ELEMENT = (
    By.XPATH, "//*[contains(@text, 'политика конфиденциальности') or contains(@text, 'Privacy')]")


class NotificationPageLocators:
    """Локаторы для экрана онбординга уведомлений (внутри приложения)."""

    # Оранжевая кнопка "Разрешить >" внизу справа
    ALLOW_ONBOARDING_BUTTON = (By.ID, "ru.tensor.sbis.sabyadmin.debug:id/onboarding_tour_button")

    # Кнопка "Пропустить" вверху справа
    SKIP_BUTTON = (By.ID, "ru.tensor.sbis.sabyadmin.debug:id/onboarding_tour_close")


class AndroidSystemPermissionLocators:
    """Локаторы для нативного всплывающего окна разрешений Android OS."""

    # Кнопка "Разрешить" в системном алерте
    SYSTEM_ALLOW_BUTTON = (By.ID, "com.android.permissioncontroller:id/permission_allow_button")

    # Кнопка "Запретить" в системном алерте
    SYSTEM_DENY_BUTTON = (By.ID, "com.android.permissioncontroller:id/permission_deny_button")

    # Текст самого сообщения («Разрешить приложению Saby Admin...»)
    SYSTEM_MESSAGE_TEXT = (By.ID, "com.android.permissioncontroller:id/permission_message")