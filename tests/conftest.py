import base64
import pytest
import allure
from allure_commons.types import AttachmentType
from appium import webdriver
from appium.options.android import UiAutomator2Options
from config.settings import config
from src.core.transport.local_transport import LocalTransport
from src.interaction.cli.linux_operator_cli import LinuxOperatorCLI


def pytest_addoption(parser):
    """Регистрация аргументов командной строки для Jenkins/локального запуска."""
    parser.addoption("--app-path", action="store", default=None)
    parser.addoption("--operator-path", action="store", default=None)


@pytest.fixture(scope="session", autouse=True)
def load_config(request):
    """Считывание настроек перед стартом тестов."""
    if request.config.getoption("--app-path"):
        config.app_path = request.config.getoption("--app-path")
    if request.config.getoption("--operator-path"):
        config.operator_path = request.config.getoption("--operator-path")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Хук
    pytest
    для
    перехвата
    результатов
    теста.
    1.
    Сохраняет
    статус
    теста
    в
    объект
    'item', чтобы
    фикстура
    видела
    результат.
    2.
    Делает
    мгновенный
    скриншот
    при
    падении.
    """
    outcome = yield
    rep = outcome.get_result()

    # Записываем результат фазы (setup, call, teardown) в элемент теста
    setattr(item, f"rep_{rep.when}", rep)

    # Если тест упал непосредственно во время выполнения (call)
    if rep.when == "call" and rep.failed:
        if "android_client" in item.fixturenames:
            android_driver = item.funcargs["android_client"]
            try:
                allure.attach(
                    android_driver.get_screenshot_as_png(),
                    name="fail_screenshot_android",
                    attachment_type=AttachmentType.PNG
                )
            except Exception as e:
                print(f"Не удалось сделать скриншот экрана: {e}")


@pytest.fixture(scope="function")
def android_client(request):
    """
    Инициализация
    сессии
    Appium
    с
    автоматической
    видеозаписью
    экрана.
    Запись
    идет
    всегда, но
    прикрепляется
    к
    отчету
    только
    в
    случае
    падения
    теста.
    """
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"

    if config.app_path:
        options.app = config.app_path
    else:
        options.app_package = config.app_package
        options.app_activity = config.app_activity

    options.no_reset = True

    driver = webdriver.Remote(config.appium_server_url, options=options)

    # Включаем запись экрана Android перед стартом теста
    try:
        driver.start_recording_screen(video_type="mp4", video_quality="low", time_limit="180")
    except Exception as e:
        print(f"Не удалось запустить видеозапись Appium: {e}")

    yield driver

    # --- ТЕЙРДАУН СЕССИИ (Выполняется после теста) ---
    try:
        # Останавливаем запись и получаем Base64 строку видео
        raw_video = driver.stop_recording_screen()

        # Проверяем, завершился ли тест ошибкой (благодаря хуку выше)
        node = request.node
        if hasattr(node, "rep_call") and node.rep_call.failed:
            # Декодируем видео из Base64 в бинарный MP4 и крепим к Allure
            allure.attach(
                base64.b64decode(raw_video),
                name="fail_video_android",
                attachment_type=AttachmentType.MP4
            )
    except Exception as e:
        print(f"Ошибка при обработке видеозаписи: {e}")

    driver.quit()


@pytest.fixture(scope="function")
def linux_operator():
    """Запуск и гарантированная очистка процессов CLI-оператора."""
    transport = LocalTransport()
    operator = LinuxOperatorCLI(transport)
    operator.start_operator(binary_path=config.operator_path)

    yield operator
    operator.shutdown()