import os
import pty
import json
import logging
import re
import subprocess
import threading
import time
from typing import Optional, List, Dict, Any

# Импортируем путь к бинарнику из локального конфига
from config.local_settings import CONSOLE_PATH

logger = logging.getLogger(__name__)


class SabyAdminConsole:
    """Управление консольным приложением SabyAdmin через subprocess"""

    def __init__(self, binary_path: str = CONSOLE_PATH):
        self.binary_path = binary_path
        self.process: Optional[subprocess.Popen] = None
        self.master_fd: Optional[int] = None  # Файловый дескриптор PTY
        self.connection_code: Optional[str] = None
        self._reader_thread: Optional[threading.Thread] = None
        self._is_connected: bool = False
        self._stop_reading = threading.Event()
        # Список для хранения всех входящих JSON-событий от консоли
        self.received_messages: List[Dict[str, Any]] = []

    def _read_stdout_loop(self) -> None:
        """Фоновое чтение и логирование STDOUT процесса"""
        while self.process and self.process.poll() is None:
            line = self.process.stdout.readline()
            if line:
                clean_line = line.strip()
                print(f"[SabyAdminConsole STDOUT] {clean_line}")

                # Ловим 6-значный код
                if not self.connection_code:
                    match = re.search(r'"code"\s*:\s*"?(\d{6})"?', line)
                    if match:
                        self.connection_code = match.group(1)

                # Ловим сигнал об успешном установлении соединения
                if "remoteprofiledata" in clean_line.lower() or "sessionstarted" in clean_line.lower():
                    self._is_connected = True

    def start_as_client(
        self,
        server_type: Optional[int] = 2,
        ensure_online: bool = True,
        authorize_connection: bool = True,
        login_pass: str = "russia:qwerty1"
    ) -> str:
        """Запускает консоль внутри реального PTY (псевдотерминала)"""
        cmd = [self.binary_path]
        if server_type is not None:
            cmd.append(f"--server_type={server_type}")
        if ensure_online:
            cmd.append("--ensure_online")
        if authorize_connection:
            cmd.append("--authorize_connection")
        if login_pass:
            cmd.append(f"--login_pass={login_pass}")

        # Создаем виртуальный терминал (master/slave)
        self.master_fd, slave_fd = pty.openpty()

        self.process = subprocess.Popen(
            cmd,
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            close_fds=True,
            text=False
        )
        os.close(slave_fd)  # Закрываем slave в родительском процессе

        # Фоновый поток считывает данные из master_fd PTY
        self._reader_thread = threading.Thread(target=self._read_pty_loop, daemon=True)
        self._reader_thread.start()

        if ensure_online:
            self.send_network_available(True)

        return self.wait_for_code()

    def _read_pty_loop(self) -> None:
        """Построчно считывает PTY-вывод, логирует его и парсит JSON в self.received_messages"""
        buffer = ""
        while not self._stop_reading.is_set():
            try:
                data = os.read(self.master_fd, 1024).decode('utf-8', errors='replace')
                if not data:
                    break

                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    clean_line = line.strip()
                    if not clean_line:
                        continue

                    print(f"[SabyAdminConsole STDOUT] {clean_line}")

                    # Пытаемся распарсить строку как JSON-сообщение
                    try:
                        if clean_line.startswith("{") and clean_line.endswith("}"):
                            msg_json = json.loads(clean_line)
                            self.received_messages.append(msg_json)
                    except json.JSONDecodeError:
                        pass
            except OSError:
                break
    def start_as_operator(
            self,
            server_type: int = 2,
            login_pass: str = "",
            connect_code: Optional[str] = None,
            proxy: Optional[str] = None,
            turn_only: bool = False
    ) -> None:
        """Запускает консоль в режиме оператора внутри реального PTY (псевдотерминала)"""
        cmd = [self.binary_path]

        if server_type is not None:
            cmd.append(f"--server_type={server_type}")
        if login_pass:
            cmd.append(f"--login_pass={login_pass}")
        if connect_code:
            clean_code = connect_code.replace(" ", "").strip()
            cmd.append(f"--connect={clean_code}")
        if turn_only:
            cmd.append("--turn_only")
        if proxy:
            cmd.append(f"--proxy={proxy}")

        print(f"\n[SabyAdminConsole] Запуск процесса оператора: {' '.join(cmd)}")

        # Создаем виртуальный терминал (master/slave)
        self.master_fd, slave_fd = pty.openpty()

        self.process = subprocess.Popen(
            cmd,
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            close_fds=True,
            text=False
        )
        os.close(slave_fd)  # Закрываем slave в родительском процессе
        print(f"[SabyAdminConsole] PID процесса оператора: {self.process.pid}")

        # Фоновый поток считывает данные из master_fd PTY через твой _read_pty_loop
        self._reader_thread = threading.Thread(target=self._read_pty_loop, daemon=True)
        self._reader_thread.start()

    def wait_for_code(self, timeout: float = 15.0) -> str:
        """
        Ожидает генерацию 6-значного кода подключения (type_id: 47)
        Структура события: {"type_id": 47, "data": {"code": "376338"}}
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            # 1. Проверяем накопившиеся JSON-сообщения
            for msg in list(self.received_messages):
                if msg.get("type_id") == 47:
                    data = msg.get("data", {})
                    # Извлекаем код с учётом регистра
                    code = data.get("code") or data.get("Code") or msg.get("code")
                    if code and str(code).isdigit() and len(str(code)) == 6:
                        print(f"[SabyAdminConsole] Получен код подключения: {code}")
                        return str(code)

            time.sleep(0.2)
        raise TimeoutError("Не удалось получить 6-значный код от SabyAdminConsole")

    def wait_for_connection(self, timeout: int = 15) -> bool:
        """Ожидает подтверждения установки соединения в логах консоли"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self._is_connected:
                return True
            time.sleep(0.5)
        return False

    def send_command(self, type_id: int, data: Optional[dict] = None) -> None:
        """Отправляет команду в формате JSON через master_fd PTY"""
        cmd_dict = {"type_id": type_id, "data": data or {}}
        cmd_str = json.dumps(cmd_dict, ensure_ascii=False) + "\n"
        print(f"[SabyAdminConsole STDIN] >> {cmd_str.strip()}")
        if self.master_fd:
            os.write(self.master_fd, cmd_str.encode('utf-8'))
    def send_network_available(self, available: bool = True) -> None:
        """Команда эмуляции доступности сети"""
        self.send_command(51, {"network_available": available})

    def accept_connection(self) -> None:
        """Отправляет согласие на входящее подключение"""
        print("[SabyAdminConsole STDIN] Отправка согласия на подключение: '1'")
        if self.process and self.process.stdin:
            self.process.stdin.write("1\n")
            self.process.stdin.flush()

    def reject_connection(self) -> None:
        """Отправляет отказ от входящего подключения"""
        print("[SabyAdminConsole STDIN] Отправка отказа от подключения: '2'")
        if self.process and self.process.stdin:
            self.process.stdin.write("2\n")
            self.process.stdin.flush()

    def disconnect_session(self, type_id: int = 5) -> None:
        """Завершает соединение консольным SA через STDIN"""
        print("[SabyAdminConsole STDIN] Завершение сессии со стороны консоли...")
        self.send_command(type_id)

    def wait_for_event(self, expected_type_id: int, timeout: float = 15.0) -> Dict[str, Any]:
        """Ожидает событие с заданным type_id в буфере received_messages"""
        print(f"[SabyAdminConsole] Ожидание события type_id: {expected_type_id}...")
        start_time = time.time()

        while time.time() - start_time < timeout:
            # Проверяем буфер прочитанных сообщений из PTY/STDOUT
            for msg in reversed(self.received_messages):
                if isinstance(msg, dict) and msg.get("type_id") == expected_type_id:
                    print(f"[SabyAdminConsole] Получено событие type_id: {expected_type_id} -> {msg}")
                    return msg
            time.sleep(0.2)

        raise TimeoutError(f"Событие type_id: {expected_type_id} не поступило за {timeout} сек. Получено всего сообщений: {len(self.received_messages)}")

    def handle_incoming_file_transfer(self, destination_path: str = "/tmp", timeout: float = 20.0) -> None:
        """
        Полный цикл приёма файла:
        1. Ждём 21 (ReadyToReceiveFiles) — клиент готов отдавать
        2. Отправляем 13 (DestinationPath) — оператор указывает каталог сохранения
        3. Ждём 19 (FileTransferSessionStarted) — сессия передачи стартовала
        4. Ждём 20 (FileTransferSessionFinished) — файл доставлен
        """
        # Создаем каталог сохранения, если он не существует
        os.makedirs(destination_path, exist_ok=True)

        # 1. Ждем сигнал готовности клиента (21)
        print("[SabyAdminConsole] Ожидание готовности клиента к передаче (type_id: 21)...")
        self.wait_for_event(expected_type_id=21, timeout=timeout)

        # 2. Оператор подтверждает прием и отправляет путь сохранения (13)
        print(f"[SabyAdminConsole] Отправка согласия на приём файлов (type_id: 13) в '{destination_path}'")
        self.send_command(
            type_id=13,
            data={"DestinationPath": destination_path}
        )

        # 3. Теперь ждем фактический старт передачи (19)
        print("[SabyAdminConsole] Ожидание старта сессии передачи (type_id: 19)...")
        self.wait_for_event(expected_type_id=19, timeout=timeout)

        # 4. Ждем успешное завершение передачи файла (20)
        print("[SabyAdminConsole] Ожидание завершения передачи (type_id: 20)...")
        self.wait_for_event(expected_type_id=20, timeout=timeout)
        print("[SabyAdminConsole] Файл успешно передан и сохранён!")


    def accept_incoming_file(self, destination_path: str = "/tmp") -> None:
        """
        Отправляет команду подтверждения приёма файла оператором.
        type_id: 13, data: {"DestinationPath": "<путь>"}
        """
        print(f"[SabyAdminConsole] Отправка команды приёма файла в директорию: {destination_path}")
        self.send_command(
            type_id=13,
            data={"DestinationPath": destination_path}
        )

    def stop(self) -> None:
        """Безопасное завершение OS-процесса (для tearDown)"""
        if self.process:
            print("[SabyAdminConsole] Остановка процесса утилиты...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            print("[SabyAdminConsole] Процесс остановлен")
