import pytest
from src.pages.android.onboarding_page import OnboardingPage
from src.pages.android.main_page import MainPage
from src.pages.android.app_settings_page import AppSettingsPage
from src.pages.android.auth_page import AuthPage
from utils.saby_admin_console import SabyAdminConsole
from src.pages.android.device_system_page import DeviceSystemPage
from src.pages.android.notification_page import NotificationPage


def test_saby_admin_fresh_install_onboarding(android_client, video_recorder):
    """Смоук-тест: Чистая установка, авторизация на тесте и выдача автоподключения"""
    onboarding = OnboardingPage(android_client, recorder=video_recorder)

    # 1. Проходим онбординг с выдачей всех разрешений
    onboarding.pass_onboarding()
    # onboarding.skip_onboarding_completely()

    # 2. Меняем стенд на TEST
    main_page = MainPage(android_client, recorder=video_recorder)
    main_page.open_settings()

    settings_page = AppSettingsPage(android_client, recorder=video_recorder)
    settings_page.click_sign_in()

    auth_page = AuthPage(android_client, recorder=video_recorder)
    auth_page.change_stand_to_test()
    # auth_page.change_stand_to_fix()

    # 3. Логинимся
    auth_page.login_with_credentials("proletariat1", "qwerty1!")
    # auth_page.login_with_credentials("russia7", "qwerty1")

    # 4. Выдаём разрешение на автоподключение
    onboarding.pass_post_auth_auto_connect()

    # 5. Сверяем финальный вид главной страницы авторизованного пользователя
    client_code = main_page.get_connection_code()
    # main_page.verify_visual_layout("main_page_authorized")

    # 6. Запускаем консоль на стенде TEST
    console = SabyAdminConsole()
    console.start_as_operator(
        connect_code=client_code,
        server_type=2,
        login_pass="russia:qwerty1"
    )

    try:
        # 7. Подтверждаем запрос на подключение
        main_page.accept_connection_request()

        # 8. Переход в меню всех приложений со свайпом снизу вверх
        device_system_page = DeviceSystemPage(android_client, recorder=video_recorder)
        device_system_page.open_app_drawer()

        # 9. Выбор приложения «Файлы», лонг-пресс по первому файлу и шэринг в Saby Admin
        device_system_page.open_files_app()
        device_system_page.long_press_first_file(duration=2.0)
        device_system_page.click_share()
        device_system_page.select_saby_admin_in_share_menu()

        # 10. Консоль принимает файл
        if video_recorder:
            video_recorder.set_banner("Оператор принимает файл (type_id 21 -> 13 -> 19 -> 20)")

        console.handle_incoming_file_transfer(destination_path="/tmp")

        # 11. Проверяем Push-уведомление об успешной передаче на клиенте
        notification_page = NotificationPage(android_client, recorder=video_recorder)
        notification_page.verify_file_transfer_completed_push()

        # 11. Завершаем сессию консолью и проверяем плашку
        console.disconnect_session()
        main_page.verify_disconnected_panel_details(
            expected_title="К вам был подключен"
        )

    finally:
        console.stop()
