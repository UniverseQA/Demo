from pathlib import Path

from PIL import Image, ImageChops, ImageDraw
import time
import pytest

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput


class BasePage:
    def __init__(self, driver: WebDriver, recorder=None, timeout: int = 15) -> None:
        self.driver = driver
        self.recorder = recorder
        self.wait = WebDriverWait(self.driver, timeout)

    def click(self, locator, step_description: str = "click") -> None:
        """Выполняет клик с запеканием рамки и подписи 'click' в видео"""
        element = self.find_element(locator)
        rect = element.rect

        if self.recorder:
            self.recorder.capture_frame(
                self.driver,
                element_rect=rect,
                action_name="click"
            )

        element.click()

    def type_in(self, locator, text: str) -> None:
        """Вводит текст и запекает плашку 'type_in(значение)'"""
        element = self.find_element(locator)
        rect = element.rect

        if self.recorder:
            self.recorder.capture_frame(
                self.driver,
                element_rect=rect,
                action_name="type_in",
                status_text=text
            )

        element.clear()
        element.send_keys(text)

    def long_press(
            self,
            locator: tuple,
            duration: float = 2.0,
            step_description: str = "long_press",
            timeout: int = 15
    ) -> None:
        """Выполняет долгое зажатие (Long Press) на элементе через Appium W3C Actions"""
        element = WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )

        if self.recorder:
            self.recorder.capture_frame(
                self.driver,
                element_rect=element.rect,
                action_name="long_press",
                status_text=f"{duration}s",
                hold_seconds=1.5
            )

        # Выполняем тач-зажатие через W3C Actions
        actions = ActionChains(self.driver)
        actions.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
        actions.w3c_actions.pointer_action.move_to(element)
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.pause(duration)
        actions.w3c_actions.pointer_action.release()
        actions.perform()

    def swipe_up(
            self,
            start_y_ratio: float = 0.8,
            end_y_ratio: float = 0.2,
            duration_ms: int = 400
    ) -> None:
        """Выполняет свайп снизу вверх (например, для открытия App Drawer)"""
        size = self.driver.get_window_size()
        width = size["width"]
        height = size["height"]

        start_x = width // 2
        start_y = int(height * start_y_ratio)
        end_y = int(height * end_y_ratio)

        if self.recorder:
            self.recorder.set_banner("Свайп вверх: открытие списка всех приложений")
            self.recorder.capture_frame(
                self.driver,
                action_name="swipe_up",
                status_text="App Drawer",
                hold_seconds=1.2
            )

        actions = ActionChains(self.driver)
        actions.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
        actions.w3c_actions.pointer_action.move_to_location(start_x, start_y)
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.pause(0.05)
        actions.w3c_actions.pointer_action.move_to_location(start_x, end_y)
        actions.w3c_actions.pointer_action.pause(duration_ms / 1000.0)
        actions.w3c_actions.pointer_action.release()
        actions.perform()

    def open_notifications_shade(self) -> None:
        """Открывает шторку уведомлений Android"""
        if self.recorder:
            self.recorder.set_banner("Открытие шторки уведомлений Android")
        self.driver.open_notifications()
        time.sleep(1.0)
    def assert_text_contains(
            self,
            locator: tuple,
            expected_text: str,
            element_name: str = "Element",
            timeout: int = 15,
            hold_seconds: float = 1.5
    ) -> None:
        """
        Универсальная проверка: ожидает элемент, сверяет текст,
        подсвечивает рамкой на видео и рисует шапочный баннер
        """
        # 1. Ждем появление элемента в UI
        element = WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )
        actual_text = element.text

        # 2. Запекаем кадр с рамкой и баннером в видеорекордер (если он подключен)
        if self.recorder:
            short_expected = expected_text[:20] + "..." if len(expected_text) > 20 else expected_text
            self.recorder.set_banner(f'("{element_name}").should_contain("{short_expected}")')
            self.recorder.capture_frame(
                self.driver,
                element_rect=element.rect,
                action_name="Displayed",
                status_text="OK",
                hold_seconds=hold_seconds
            )

        # 3. Функциональный ассерт
        assert expected_text in actual_text, (
            f"Текст в '{element_name}' не совпал. В UI: '{actual_text}', Ожидалось: '{expected_text}'"
        )

    def find_element(self, locator: tuple[str, str]):
        return self.wait.until(EC.presence_of_element_located(locator))

    def get_text(self, locator: tuple[str, str]) -> str:
        return self.find_element(locator).text

    def _show_indicator(self, message: str, is_success: bool = False) -> None:
        """Выводит цветную индикацию шага в консоль и отправляет Toast на устройство"""
        # ANSI-коды цветов для консоли
        RED = "\033[91m"
        GREEN = "\033[92m"
        RESET = "\033[0m"

        color = GREEN if is_success else RED
        tag = "[SUCCESS]" if is_success else "[CHECKING]"

        # Печать в терминал
        print(f"{color}{tag} {message}{RESET}")

        # Отображение Toast-всплывашки прямо на экране телефона через Appium Settings
        try:
            self.driver.execute_script(
                "mobile: shell",
                {
                    "command": "am",
                    "args": ["broadcast", "-a", "com.appium.settings.toast", "-e", "message", f"{tag} {message}"]
                }
            )
        except Exception:
            pass  # Пропускаем, если у драйвера нет прав на shell-команды

    @staticmethod
    def _mask_top_panel(draw, width: int, height: int = 150) -> None:
        """Маскирует верхнюю панель часов и таймера Android 16"""
        draw.rectangle([0, 0, width, height], fill="#18181c")

    def assert_screen_matches_template(self, template_name: str, ignored_locators: list | None = None) -> None:
        """Сверяет экран с шаблоном с учетом плотности пикселей и умными повторами оверлеев"""
        # Сохраняем имя текущего шаблона в pytest, чтобы передать его в финальный HTML-отчет
        pytest.last_template_name = template_name

        project_root = Path(__file__).parent.parent.parent.parent
        templates_dir = project_root / "screenshots" / "templates"
        actual_dir = project_root / "screenshots" / "actual"

        templates_dir.mkdir(parents=True, exist_ok=True)
        actual_dir.mkdir(parents=True, exist_ok=True)

        template_path = templates_dir / f"{template_name}.png"
        actual_path = actual_dir / f"{template_name}.png"
        diff_path = actual_dir / f"{template_name}_diff.png"

        # Если базового шаблона вообще нет, делаем быстрый снимок и выходим
        if not template_path.exists():
            self.driver.get_screenshot_as_file(str(actual_path))
            img_initial = Image.open(actual_path).convert("RGB")
            draw_initial = ImageDraw.Draw(img_initial)
            self._mask_top_panel(draw_initial, img_initial.width)
            img_initial.save(actual_path)
            img_initial.save(template_path)
            img_initial.save(diff_path)
            print(f"\n[VISUAL] Создан новый базовый эталон: {template_path}")
            return

        img_template = Image.open(template_path).convert("RGB")

        # Цикл умных повторов (3 попытки с паузой), чтобы переждать всплывающие окна и дампы памяти
        max_attempts = 3
        for attempt in range(max_attempts):
            self.driver.get_screenshot_as_file(str(actual_path))
            img_actual = Image.open(actual_path).convert("RGB")
            draw_actual = ImageDraw.Draw(img_actual)

            # Маскируем верхнюю панель часов и таймера Android 16
            self._mask_top_panel(draw_actual, img_actual.width)

            if ignored_locators:
                # Вычисляем точный коэффициент масштабирования логических dp в физические пиксели
                window_size = self.driver.get_window_size()
                scale_x = img_actual.width / window_size['width']
                scale_y = img_actual.height / window_size['height']

                for locator in ignored_locators:
                    try:
                        element = self.driver.find_element(*locator)
                        location = element.location
                        size = element.size

                        # Пересчитываем геометрию элемента под реальное разрешение картинки
                        x = int(location['x'] * scale_x)
                        y = int(location['y'] * scale_y)
                        w = int(size['width'] * scale_x)
                        h = int(size['height'] * scale_y)

                        draw_actual.rectangle([x, y, x + w, y + h], fill="#18181c")
                    except Exception:
                        pass

            # Сохраняем маскированный скриншот ПЕРЕД сравнением
            img_actual.save(actual_path)

            if img_template.size != img_actual.size:
                raise AssertionError(
                    f"Размеры экранов не совпадают! Эталон: {img_template.size}, Текущий: {img_actual.size}")

            # Считаем разницу пикселей
            diff = ImageChops.difference(img_template, img_actual)
            gray_diff = diff.convert("L")
            hist = gray_diff.histogram()
            changed_pixels = sum(hist[15:])

            # Генерируем карту различий для отчета
            mask = gray_diff.point(lambda x: 255 if x > 15 else 0)
            neon_fill = Image.new("RGB", img_actual.size, color=(255, 0, 85))
            highlighted_diff = Image.composite(neon_fill, img_actual, mask)
            highlighted_diff.save(diff_path)

            # Если уложились в лимит изменений — тест успешно пройден
            if changed_pixels <= 150:
                return

            # Если это не последняя попытка — даем оверлеям время исчезнуть
            if attempt < max_attempts - 1:
                print(f"\n[VISUAL] Обнаружено расхождение ({changed_pixels} px). Повторная попытка {attempt + 1}...")
                time.sleep(4.0)

        # Если после всех попыток экран все еще не совпадает — роняем тест
        raise AssertionError(
            f"Визуальный вид экрана не соответствует эталону {template_name}! Изменилось пикселей: {changed_pixels} (порог: 150)")

    # Управление ориентацией устройства
    def set_orientation(self, orientation: str) -> None:
        """Меняет ориентацию экрана ('LANDSCAPE' или 'PORTRAIT')"""
        print(f"[Appium] Меняем ориентацию устройства на {orientation}")
        self.driver.orientation = orientation.upper()

    def get_orientation(self) -> str:
        """Возвращает текущую ориентацию устройства"""
        return self.driver.orientation.upper()

    def is_element_present(self, locator: tuple, timeout: int = 2) -> bool:
        """Быстрая проверка наличия элемента на экране"""

        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))
            return True
        except Exception:
            return False
