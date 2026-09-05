import time

import pytest
from utils.saby_admin_console import SabyAdminConsole
from src.pages.android.onboarding_page import OnboardingPage
from src.pages.android.main_page import MainPage
from src.pages.android.app_settings_page import AppSettingsPage
from src.pages.android.auth_page import AuthPage
from src.pages.android.operator_session_page import OperatorSessionPage
from src.pages.base_page import BasePage


def test_establish_connection_as_operator(android_client, video_recorder):
    """Установка соединения в роли оператора с авто-подтверждением клиентом"""

    # 1. Проходим стартовый онбординг приложения
    onboarding = OnboardingPage(android_client, recorder=video_recorder)
    onboarding.pass_onboarding()
    # onboarding.skip_onboarding_completely()

    # 2. Меняем стенд на TEST
    main_page = MainPage(android_client, recorder=video_recorder)
    main_page.open_settings()

    settings_page = AppSettingsPage(android_client, recorder=video_recorder)
    settings_page.click_sign_in()

    auth_page = AuthPage(android_client, recorder=video_recorder)
    auth_page.change_stand_to_test()

    # 3. Логинимся
    auth_page.login_with_credentials("proletariat1", "qwerty1!")

    # 4. Выдаём разрешение на автоподключение после авторизации
    onboarding.pass_post_auth_auto_connect()

    # 5. Запускаем консоль на стенде TEST с флагом authorize_connection=True
    console = SabyAdminConsole()
    connection_code = console.start_as_client(
        server_type=2,
        ensure_online=True,
        authorize_connection=True
    )

    try:
        # 6. Вводим код подключения на мобилке и нажимаем подключиться
        main_page.enter_connection_code(connection_code)
        main_page.click_connect_button()

        # 7. Консоль сама подтвердит вход, проверяем появление экрана сессии
        operator_session_page = OperatorSessionPage(android_client, recorder=video_recorder)
        assert operator_session_page.is_session_active(), "Сессия удаленного управления не активировалась"

        # 8. Работа с МДО (птичка) -> Экраны устройства -> Первый экран -> Закрытие МДО
        operator_session_page.open_oam()
        operator_session_page.select_device_screens()
        operator_session_page.select_first_screen()
        operator_session_page.back_to_oam_from_device_screens()
        operator_session_page.close_oam()

        # 9. Изменение ориентации оператора и проверка смены
        operator_session_page.set_orientation("LANDSCAPE")
        assert operator_session_page.get_orientation() == "LANDSCAPE", "Ориентация не изменилась на LANDSCAPE"

        # 10. Возвращение вертикальной ориентации оператора
        operator_session_page.set_orientation("PORTRAIT")

        # 11. Завершение соединения на стороне консольного клиента
        console.disconnect_session()

        # 12. Детальная построчная проверка данных плашки завершения с цветной индикацией
        main_page.verify_disconnected_panel_details(
            expected_title="Вы были подключены к",
            expected_client_name="СидоровСидоровСидоровСидоровСидоровСидоровСидоровСидоровСидоровСидоровСидоровСидоровСидоровСидоровСидоровСидоровСидоровСидоровСидоровСидоровСидоровСидоровСидоровСидоровСидоровСидоровСидоровСидоровСидо ЮпитерЮпитерЮпитерЮпитерЮпитерЮпитерЮпитерЮпитерЮпитерЮпитерЮпитерЮпитерЮпитерЮпитерЮпитерЮпитерЮпитерЮпитерЮпитерЮпитерЮпитерЮпитерЮпитерЮпитерЮпитерЮпитерЮпитерЮпитерЮпитерЮпитерЮпитерЮпитерЮпитерЮп",
            expected_company="Огроменейшая организация по размеру и количеству Дженна Ортега — Уэнздей Аддамс, 16-летняя девочка-подросток, обладающая экстрасенсорными способностями. Дочь Гомеса и Мортиши. Ортега также исполняет роль мексиканской ведьмы Гуди Аддамс, одной из первых поселенцев в США и дальнего предка Уэнздей. Карина Варади — маленькая Уэнздей. Гвендолин Кристи — директор Академии «Невермор» Лариса Уимс. Бывшая подруга и соседка по комнате Мортиши Аддамс. Оливер Викхэм — молодая Лариса Уимс. Рики Линдхоум — доктор Валери Кинботт, психиатр в городе Джерико. Джейми МакШейн — Донован Галпин, шериф в городе Джерико. Отец Тайлера. Бен Уилсон — молодой Донован Галпин."
        )

    finally:
        # Гарантированный сброс ориентации и зачистка процесса консоли
        try:
            base_page = BasePage(android_client, recorder=video_recorder)
            base_page.set_orientation("PORTRAIT")
        except Exception:
            pass
        console.stop()