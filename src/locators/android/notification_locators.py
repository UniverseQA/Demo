from appium.webdriver.common.appiumby import AppiumBy


class NotificationLocators:
    """Локаторы пуш-уведеомлений"""

    # Локаторы пуш-уведомления соединения
    CONNECTION_STATUS_PUSH = (AppiumBy.ID, "android:id/header_text_divider")
    CONNECTION_USER_ICON_PUSH = (AppiumBy.ID, "android:id/right_icon")
    CONNECTION_USER_NAME_PUSH = (AppiumBy.ID, "android:id/text")
    CONNECTION_USER_COMPANY_PUSH = (AppiumBy.ID, "android:id/title")
    CONNECTION_PUSH_EXPAND_BUTTON = (AppiumBy.ID, "android:id/expand_button")  # Кнопка разворачивания пуша

    # Локаторы пуш-уведомления передачи файлов
    SABY_ADMIN_GROUP_EXPAND_BUTTON = (AppiumBy.ID, "android:id/expand_button_number")
    FILE_TRANSFER_COMPLETED_PUSH = (AppiumBy.ID, "com.android.systemui:id/notification_title")
