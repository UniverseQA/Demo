import os
import cv2
import numpy as np
import allure
from pathlib import Path


class ActionVideoRecorder:
    """Генератор видео с динамическим оверлеем (рамки, действия, топовый баннер)"""

    def __init__(self, fps: int = 5, output_path: str = "last_run.webm"):
        self.fps = fps
        self.output_path = str(output_path)
        self.frames = []
        self.current_banner = "Test Execution Started"

    def set_banner(self, text: str) -> None:
        """Устанавливает текст для верхнего баннера шага"""
        self.current_banner = text

    def capture_frame(
        self,
        driver,
        element_rect: dict = None,
        action_name: str = None,
        status_text: str = None,
        hold_seconds: float = 1.5  # Время удержания каждого кадра в видео (сек)
    ) -> None:
        """Делает скриншот с адаптивным оверлеем и удержанием кадра"""
        raw_png = driver.get_screenshot_as_png()
        nparr = np.frombuffer(raw_png, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        height, width, _ = img.shape

        # Динамический коэффициент масштабирования под любое разрешение (1080p, 1440p)
        scale = width / 1080.0
        font_scale = max(0.9, 1.2 * scale)
        thickness = max(2, int(4 * scale))
        border_thick = max(4, int(7 * scale))
        banner_h = int(80 * scale)

        # 1. ВЕРХНИЙ БАННЕР (Крупный желто-черный заголовок)
        cv2.rectangle(img, (0, 0), (width, banner_h), (0, 0, 0), -1)
        cv2.rectangle(img, (0, 0), (width, banner_h), (0, 215, 255), thickness)

        banner_text = f"({self.current_banner})"
        cv2.putText(
            img, banner_text, (int(20 * scale), int(banner_h * 0.65)),
            cv2.FONT_HERSHEY_SIMPLEX, font_scale * 0.8, (0, 255, 255), thickness, cv2.LINE_AA
        )

        # 2. КРУПНАЯ ПОДСВЕТКА ЭЛЕМЕНТА (Рамка + Четкая плашка)
        if element_rect:
            x, y = int(element_rect['x']), int(element_rect['y'])
            w, h = int(element_rect['width']), int(element_rect['height'])

            # Заметная толстая красная рамка
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), border_thick)

            # Текст лейбла (click, type_in, Displayed)
            label = action_name if action_name else "Action"
            if status_text:
                label = f"{label}({status_text})"

            # Рисуем плашку подписи прямо над элементом
            (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
            label_y = max(banner_h + int(30 * scale), y - int(10 * scale))

            # Красный фоновый прямоугольник под текст
            cv2.rectangle(
                img,
                (x, label_y - label_h - int(15 * scale)),
                (x + label_w + int(25 * scale), label_y + int(10 * scale)),
                (0, 0, 255),
                -1
            )
            # Четкий белый текст
            cv2.putText(
                img, label, (x + int(10 * scale), label_y - int(5 * scale)),
                cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness, cv2.LINE_AA
            )

        # 3. Нормализация скорости: дублируем кадр на заданное время (hold_seconds)
        repeat_count = max(1, int(self.fps * hold_seconds))
        for _ in range(repeat_count):
            self.frames.append(img)

    def save_and_attach_to_allure(self, attachment_name: str = "Execution Video") -> None:
        """Склеивает кадры в WebM (VP8/VP9) для идеальной совместимости с HTML5 в Linux"""
        if not self.frames:
            print("[VideoRecorder] Нет записанных кадров.")
            return

        out_path = Path(self.output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        height, width, _ = self.frames[0].shape

        # VP80 / VP90 — программные WebM-кодеки, идеальные для браузеров и Linux без v4l2m2m
        codecs_to_try = [('VP80', 'webm'), ('VP90', 'webm'), ('mp4v', 'mp4')]
        out = None

        for codec, ext in codecs_to_try:
            try:
                fourcc = cv2.VideoWriter_fourcc(*codec)
                test_path = str(out_path.with_suffix(f".{ext}"))
                out = cv2.VideoWriter(test_path, fourcc, self.fps, (width, height))
                if out.isOpened():
                    self.output_path = test_path
                    print(f"[VideoRecorder] Инициализирован программный кодек: {codec} ({ext})")
                    break
            except Exception:
                continue

        if not out or not out.isOpened():
            print("[ERROR] Не удалось инициализировать видеокодек!")
            return

        for frame in self.frames:
            out.write(frame)
        out.release()

        final_file = Path(self.output_path)
        if final_file.exists():
            allure.attach.file(
                source=str(final_file),
                name=attachment_name,
                attachment_type=allure.attachment_type.WEBM if final_file.suffix == '.webm' else allure.attachment_type.MP4
            )
            print(f"[VideoRecorder] Видео сохранено ({len(self.frames)} кадров): {final_file}")