from abc import ABC, abstractmethod


class ITransport(ABC):
    @abstractmethod
    def start(self, command: list[str]) -> None:
        """Запускает процесс."""
        pass

    @abstractmethod
    def write_line(self, data: str) -> None:
        """Отправляет строку в stdin."""
        pass

    @abstractmethod
    def read_available(self) -> str:
        """НЕблокирующее чтение stdout."""
        pass

    @abstractmethod
    def is_alive(self) -> bool:
        """Жив ли процесс."""
        pass

    @abstractmethod
    def terminate(self) -> None:
        """Гарантированное завершение."""
        pass
