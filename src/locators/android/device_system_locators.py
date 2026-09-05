from appium.webdriver.common.appiumby import AppiumBy


class DeviceSystemLocators:
    """Локаторы системных приложений и шторки Android"""

    # Иконка приложения "Файлы"
    FILES_APP_ICON = (AppiumBy.XPATH, "//android.widget.TextView[@content-desc='Файлы']")
    # Файл для передачи
    FILE_FOR_SHARING = (AppiumBy.ID, "com.google.android.documentsui:id/icon_thumb")

    # Кнопка "Поделиться" в верхней панели проводника
    SHARE_BUTTON = (AppiumBy.XPATH, "//android.widget.Button[@content-desc='Поделиться']")

    # Иконка Saby Admin в меню "Поделиться"
    SABY_ADMIN_SHARE_TARGET = (
        AppiumBy.XPATH,
        '//android.widget.TextView[@resource-id="android:id/text1" and @text="Saby Admin.debug"]')

