import subprocess
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
        self._process.stdin.write(f"{data}\n")
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
