import time
from src.core.transport.base_transport import ITransport

class LinuxOperatorCLI:
    def __init__(self, transport: ITransport) -> None:
        self.transport = transport
        self.buffer = ""

    def start_operator(self, binary_path: str = "operator_cli") -> None:
        self.transport.start([binary_path])

    def wait_for_output(self, text: str, timeout: float = 10.0) -> bool:
        """Реализация WebDriverWait для консоли: non-blocking опрос буфера"""
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
