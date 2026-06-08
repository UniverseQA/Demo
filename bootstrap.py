"""
Bootstrap-скрипт: создает Enterprise-структуру фреймворка автоматизации
и сразу наполняет ключевые файлы готовым кодом.
Запуск: python bootstrap.py
"""
import os
from pathlib import Path

ROOT = Path(__file__).parent

# 1. Создаем структуру директорий
DIRS = [
    "config",
    "config/environments",
    "src/core",
    "src/core/transport",
    "src/interaction/pages/client",
    "src/interaction/pages/operator",
    "src/interaction/locators",
    "src/interaction/cli",
    "src/steps",
    "src/domain",
    "tests/fixtures",
    "tests/e2e",
    "tests/data",
    "utils",
]

for d in DIRS:
    dir_path = ROOT / d
    dir_path.mkdir(parents=True, exist_ok=True)
    if d.startswith("src") or d.startswith("tests"):
        (dir_path / "__init__.py").touch(exist_ok=True)

# 2. Словарь с готовым кодом для ключевых файлов (все внутренние кавычки экранированы)
FILES_DATA = {
    # --- КОРНЕВЫЕ НАСТРОЙКИ ---
    "pytest.ini": """[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
""",

    # --- ИНТЕРФЕЙС ТРАНСПОРТА ---
    "src/core/transport/base_transport.py": """from abc import ABC, abstractmethod

class ITransport(ABC):
    @abstractmethod
    def start(self, command: list[str]) -> None:
        \"\"\"Запускает процесс.\"\"\"
        pass

    @abstractmethod
    def write_line(self, data: str) -> None:
        \"\"\"Отправляет строку в stdin.\"\"\"
        pass

    @abstractmethod
    def read_available(self) -> str:
        \"\"\"НЕблокирующее чтение stdout.\"\"\"
        pass

    @abstractmethod
    def is_alive(self) -> bool:
        \"\"\"Жив ли процесс.\"\"\"
        pass

    @abstractmethod
    def terminate(self) -> None:
        \"\"\"Гарантированное завершение.\"\"\"
        pass
""",

    # --- РЕАЛИЗАЦИЯ ЛОКАЛЬНОГО ТРАНСПОРТА ---
    "src/core/transport/local_transport.py": """import subprocess
from queue import Empty, Queue
from threading import Thread
from src.core.transport.base_transport import ITransport

class LocalTransport(ITransport):
    def __init__(self) -> None:
        self._process = None
        self._queue = Queue()
        self._reader_thread = None

    def start(self, command: list[str]) -> None:
        self._process = subprocess.Popen(
            command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True, bufsize=1, encoding="utf-8"
        )
        self._reader_thread = Thread(target=self._enqueue_output, daemon=True)
        self._reader_thread.start()

    def _enqueue_output(self) -> None:
        for line in iter(self._process.stdout.readline, ""):
            self._queue.put(line)
        self._process.stdout.close()

    def write_line(self, data: str) -> None:
        if not self._process or not self._process.stdin:
            raise RuntimeError("Process not started")
        self._process.stdin.write(f"{data}\\n")
        self._process.stdin.flush()

    def read_available(self) -> str:
        chunks = []
        while True:
            try:
                chunks.append(self._queue.get_nowait())
            except Empty:
                break
        return "".join(chunks)

    def is_alive(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def terminate(self) -> None:
        if not self._process: return
        self._process.terminate()
        try:
            self._process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self._process.kill()
            self._process.wait(timeout=2)
        self._process = None
""",

    # --- УМНАЯ ОБЕРТКА НАД CLI ОПЕРАТОРА ---
    "src/interaction/cli/linux_operator_cli.py": """import time
from src.core.transport.base_transport import ITransport

class LinuxOperatorCLI:
    def __init__(self, transport: ITransport) -> None:
        self.transport = transport
        self.buffer = ""

    def start_operator(self, binary_path: str = "operator_cli") -> None:
        self.transport.start([binary_path])

    def wait_for_output(self, text: str, timeout: float = 10.0) -> bool:
        \"\"\"Реализация WebDriverWait для консоли: non-blocking опрос буфера\"\"\"
        end_time = time.time() + timeout
        while time.time() < end_time:
            new_data = self.transport.read_available()
            if new_data:
                self.buffer += new_data
                if text in self.buffer:
                    return True
            time.sleep(0.1)
        raise TimeoutError(f"Строка '{text}' не появилась в консоли оператора за {timeout}с. Буфер: {self.buffer}")

    def connect_to_client(self, code: str) -> None:
        self.wait_for_output("Enter connection code:")
        self.transport.write_line(code)
        self.wait_for_output("Session established")

    def shutdown(self) -> None:
        self.transport.terminate()
""",

    # --- БАЗОВАЯ СТРАНИЦА APPIUM (EXPLICIT WAITS) ---
    "src/interaction/pages/base_page.py": """from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.webdriver import WebDriver

class BasePage:
    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 15)

    def find_element(self, locator: tuple[str, str]):
        return self.wait.until(EC.presence_of_element_with_locator(locator))

    def click(self, locator: tuple[str, str]) -> None:
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def get_text(self, locator: tuple[str, str]) -> str:
        return self.find_element(locator).text
""",

    # --- ПОДВИЖНЫЙ И КАНОНИЧНЫЙ CONFTEST.PY ---
    "tests/conftest.py": """import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from src.core.transport.local_transport import LocalTransport
from src.interaction.cli.linux_operator_cli import LinuxOperatorCLI

@pytest.fixture(scope="function")
def android_client():
    \"\"\"Инициализация Appium сессии клиента по канонам 3.x версии\"\"\"
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
    \"\"\"Фикстура управления Linux CLI Оператором с гарантированным teardown\"\"\"
    transport = LocalTransport()
    operator = LinuxOperatorCLI(transport)
    operator.start_operator(binary_path="./operator_cli")
    
    yield operator
    operator.shutdown()
""",

    # --- ИТОГОВЫЙ СИНХРОННЫЙ E2E ТЕСТ ---
    "tests/e2e/test_remote_session.py": """import pytest
from selenium.webdriver.common.by import By

GENERATED_CODE_LABEL = (By.ID, "com.support.remote.client:id/code_field")
SESSION_STATUS_LABEL = (By.ID, "com.support.remote.client:id/status_field")

def test_remote_support_connection_e2e(android_client, linux_operator):
    \"\"\"
    Сквозной тест синхронизации двух независимых акторов.
    Клиент на Android генерирует код -> Оператор в Linux CLI подключается по нему.
    \"\"\"
    from src.interaction.pages.base_page import BasePage
    client_page = BasePage(android_client)
    
    connection_code = client_page.get_text(GENERATED_CODE_LABEL)
    assert connection_code != "", "Код подключения не сгенерировался!"
    
    linux_operator.connect_to_client(code=connection_code)
    
    current_status = client_page.get_text(SESSION_STATUS_LABEL)
    assert current_status == "Connected", f"Ожидался статус Connected, но получили: {current_status}"
"""
}

# 3. Физически записываем код в файлы
for path_str, code in FILES_DATA.items():
    file_path = ROOT / path_str
    if not file_path.exists():
        file_path.write_text(code, encoding="utf-8")
        print(f"[CREATED] {path_str}")
    else:
        print(f"[SKIPPED] {path_str} (уже существует)")

print("\n[SUCCESS] Базовая Enterprise-архитектура создана! Можно делать коммит.")