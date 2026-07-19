from pathlib import Path

from PIL import Image, ImageChops, ImageDraw
import time
import pytest

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.webdriver import WebDriver


class BasePage:
    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 15)

    def find_element(self, locator: tuple[str, str]):
        return self.wait.until(EC.presence_of_element_located(locator))

    def click(self, locator: tuple[str, str]) -> None:
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def get_text(self, locator: tuple[str, str]) -> str:
        return self.find_element(locator).text

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
