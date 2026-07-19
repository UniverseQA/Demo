from selenium.webdriver.common.by import By


class CommonOnboardingLocators:
    """Общие локаторы для элементов самого приложения Saby Admin, повторяющихся на экранах"""
    # Кнопка "Пропустить" вверху справа
    SKIP_TOUR_BUTTON = (By.ID, "ru.tensor.sbis.sabyadmin.debug:id/onboarding_tour_close")

    # Главная оранжевая кнопка внизу справа (Начать / Разрешить / Начать работу)
    MAIN_TOUR_BUTTON = (By.ID, "ru.tensor.sbis.sabyadmin.debug:id/onboarding_tour_button")


class StartPageLocators:
    """Локаторы стартового экрана онбординга"""
    # Текст дисклеймера правил сервиса
    TERMS_TEXT_VIEW = (By.ID, "ru.tensor.sbis.sabyadmin.debug:id/onboarding_tour_terms")

    # Ссылки внутри открывшегося браузера (для верификации перехода)
    BROWSER_RULES_ELEMENT = (By.XPATH, "//*[contains(@text, 'правила сервиса') or contains(@text, 'Terms')]")
    BROWSER_PRIVACY_ELEMENT = (By.XPATH, "//*[contains(@text, 'политика конфиденциальности') or contains(@text, 'Privacy')]")


# ==============================================================================#
# СИСТЕМНЫЕ ЛОКАТОРЫ ОС ANDROID (Уникальны для каждого шага)                    #
# ==============================================================================#

class NotificationSystemLocators:
    """2. Системное всплывающее окно разрешений уведомлений Android"""
    # Убрали .google из ID, теперь путь полностью совпадает с системным дампом
    SYSTEM_ALLOW_BUTTON = (By.ID, "com.android.permissioncontroller:id/permission_allow_button")
    SYSTEM_DENY_BUTTON = (By.ID, "com.android.permissioncontroller:id/permission_deny_button")
    SYSTEM_MESSAGE_TEXT = (By.ID, "com.android.permissioncontroller:id/permission_message")


class AccessibilitySystemLocators:
    """3. Системные настройки cпец. возможностей Android"""
    # Кастомный попап внутри приложения перед уходом в настройки системы Android
    APP_POPUP_ALLOW_BUTTON = (By.XPATH, "//*[@text='РАЗРЕШИТЬ' or @resource-id='android:id/button1']")

    # Пункт в списке спец. возможностей
    SABY_ADMIN_SERVICE_ITEM = (By.XPATH, "//*[contains(@text, 'Saby') and @resource-id='android:id/title']")

    # Главный тумблер включения службы
    SERVICE_MAIN_SWITCH = (By.ID, "com.android.settings:id/main_switch_bar")

    # Кнопка "Разрешить" в диалоге полного контроля устройства
    DIALOG_ALLOW_BUTTON = (By.ID, "android:id/accessibility_permission_enable_allow_button")


class OverlaySystemLocators:
    """4. Системный список и тумблер 'Поверх других приложений'"""
    SABY_ADMIN_MENU_ITEM = (By.XPATH, "//*[contains(@text, 'Saby Admin.debug')]")
    OVERLAY_SWITCH_CONTAINER = (By.XPATH, "//android.view.View[@checkable='true']")


class FileSystemSystemLocators:
    """5. Системный экран настроек 'Доступ ко всем файлам'"""
    FILE_SWITCH_CONTAINER = (By.XPATH, "//android.view.View[@checkable='true']")


class ScreenShareSystemLocators:
    """Системное окно Android для разрешения трансляции экрана"""

    # Кнопка "Показать экран" в диалоговом окне ОС
    ALLOW_BUTTON = (By.ID, "android:id/button1")

    # Кнопка "Отмена"
    CANCEL_BUTTON = (By.ID, "android:id/button2")
