from appium.webdriver.common.appiumby import AppiumBy

class OperatorSessionPageLocators:
    """Локаторы экрана активной сессии в роли оператора"""

    # Кнопка "Птичка" - меню действий оператора (МДО - OAM operator actions menu)
    OAM_BIRD_BUTTON = (AppiumBy.ID, "ru.tensor.sbis.sabyadmin.debug:id/saby_admin_sbis_bird_button")
    OAM_DEVICE_SCREENS_ITEM = (AppiumBy.ID, "ru.tensor.sbis.sabyadmin.debug:id/sabyadmin_button_computer")
    OAM_FIRST_SCREEN = (AppiumBy.ID, "ru.tensor.sbis.sabyadmin.debug:id/sabyadmin_display_first")
    OAM_SECOND_SCREEN = (AppiumBy.ID, "ru.tensor.sbis.sabyadmin.debug:id/sabyadmin_second_number")
    OAM_DEVICE_SCREENS_BACK_BUTTON = (AppiumBy.ID, "ru.tensor.sbis.sabyadmin.debug:id/sabyadmin_displays_back")
    OAM_OUTSIDE_BACKDROP = (AppiumBy.ID, "ru.tensor.sabyadmin:id/touch_outside")  # Фон оверлея МДО
