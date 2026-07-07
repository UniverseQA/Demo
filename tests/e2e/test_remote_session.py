import pytest
from src.interaction.pages.android.onboarding_page import OnboardingPage
from src.interaction.pages.android.main_page import MainPage
from src.interaction.pages.android.app_settings_page import AppSettingsPage
from src.interaction.pages.android.auth_page import AuthPage


def test_saby_admin_fresh_install_onboarding(android_client):
    """Смоук-тест: Чистая установка, авторизация на тесте и выдача автоподключения"""
    onboarding = OnboardingPage(android_client)

    # 1. Проходим онбординг с выдачей всех разрешений
    onboarding.pass_onboarding()

    # 2. Меняем стенд на TEST
    main_page = MainPage(android_client)
    main_page.open_settings()

    settings_page = AppSettingsPage(android_client)
    settings_page.click_sign_in()

    auth_page = AuthPage(android_client)
    auth_page.change_stand_to_test()

    # 3. Возвращаемся и логинимся (здесь позже добавим ввод proletariat1)
    auth_page.login_with_credentials("proletariat1", "qwerty1!")

    # 4. Выдаём разрешение на автоподключение
    onboarding.pass_post_auth_auto_connect()

    # 5. Сверяем финальный вид главной страницы авторизованного пользователя
    main_page.verify_visual_layout("main_page_authorized")
