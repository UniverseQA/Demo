import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from src.core.transport.local_transport import LocalTransport
from src.interaction.cli.linux_operator_cli import LinuxOperatorCLI

@pytest.fixture(scope="function")
def android_client():
    """Инициализация Appium сессии клиента по канонам 3.x версии"""
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = "Android_Emulator"
    options.app_package = "com.support.remote.client"
    options.app_activity = ".MainActivity"
    options.no_reset = True
    
    driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
    yield driver
    driver.quit()

@pytest.fixture(scope="function")
def linux_operator():
    """Фикстура управления Linux CLI Оператором с гарантированным teardown"""
    transport = LocalTransport()
    operator = LinuxOperatorCLI(transport)
    operator.start_operator(binary_path="./operator_cli")
    
    yield operator
    operator.shutdown()
