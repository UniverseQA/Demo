import sys
from pathlib import Path

# Находим корень проекта для импортов config и src
PROJECT_ROOT = str(Path(__file__).parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import base64
import pytest
import allure
from allure_commons.types import AttachmentType
from appium import webdriver
from appium.options.android import UiAutomator2Options
from config.settings import config


def pytest_addoption(parser):
    """Регистрация аргументов командной строки для Jenkins/локального запуска."""
    parser.addoption("--app-path", action="store", default=None)
    parser.addoption("--operator-path", action="store", default=None)


@pytest.fixture(scope="session", autouse=True)
def load_config(request):
    """Считывание настроек перед стартом тестов"""
    if request.config.getoption("--app-path"):
        config.app_path = request.config.getoption("--app-path")
    if request.config.getoption("--operator-path"):
        config.operator_path = request.config.getoption("--operator-path")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Отлавливает падения теста, разделяя визуальные ассерты и функциональные крэши"""
    execute = yield
    report = execute.get_result()

    # Проверяем, что тест упал именно во время выполнения (phase == 'call')
    if report.when == "call" and report.failed:
        import time
        from PIL import Image, ImageChops, ImageDraw

        # Пытаемся динамически достать драйвер из фикстур упавшего теста
        android_client = item.funcargs.get("android_client")
        if not android_client:
            return

        # Если тест упал до вызова проверок верстки, помечаем как функциональную аварию
        template_name = getattr(pytest, "last_template_name", None)
        is_functional_crash = False

        if not template_name:
            template_name = "functional_failure"
            is_functional_crash = True

        project_root = Path(__file__).parent.parent
        templates_dir = project_root / "screenshots" / "templates"
        actual_dir = project_root / "screenshots" / "actual"

        templates_dir.mkdir(parents=True, exist_ok=True)
        actual_dir.mkdir(parents=True, exist_ok=True)

        template_path = templates_dir / f"{template_name}.png"
        actual_path = actual_dir / f"{template_name}.png"
        diff_path = actual_dir / f"{template_name}_diff.png"

        # Защита от перезаписи, если base_page уже сделал снимок секунду назад
        if not is_functional_crash and actual_path.exists():
            time_since_modification = time.time() - actual_path.stat().st_mtime
            if time_since_modification < 5:
                return

        try:
            # Делаем снимок экрана аварии
            android_client.get_screenshot_as_file(str(actual_path))
            img_actual = Image.open(actual_path).convert("RGB")

            # Маскируем строку состояния Android 16
            draw_actual = ImageDraw.Draw(img_actual)
            draw_actual.rectangle([0, 0, img_actual.width, 150], fill="#18181c")
            img_actual.save(actual_path)

            # Если это обычный краш кода - клонируем скриншот в шаблоны и дифф, чтобы не делать ложных сравнений
            if is_functional_crash:
                img_actual.save(template_path)
                img_actual.save(diff_path)
                return

            # Если это визуальное падение - честно считаем неоновый дифф
            if template_path.exists():
                img_template = Image.open(template_path).convert("RGB")
                if img_template.size == img_actual.size:
                    diff = ImageChops.difference(img_template, img_actual)
                    gray_diff = diff.convert("L")
                    mask = gray_diff.point(lambda x: 255 if x > 15 else 0)
                    neon_fill = Image.new("RGB", img_actual.size, color=(255, 0, 85))
                    highlighted_diff = Image.composite(neon_fill, img_actual, mask)
                    highlighted_diff.save(diff_path)
        except Exception as e:
            print(f"Не удалось сгенерировать скриншот при падении: {e}")


@pytest.fixture(scope="function")
def android_client(request):
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.full_reset = True
    options.no_reset = False
    
    # Предотвращаем заморозку сторонних служб спецвозможностей (Android 16+)
    options.set_capability("disableSuppressAccessibilityService", True)
    options.set_capability("skipServerInstallation", False)

    if config.app_path:
        options.app = config.app_path
    else:
        options.app_package = config.app_package
        options.app_activity = config.app_activity

    driver = webdriver.Remote(config.appium_server_url, options=options)

    try:
        driver.update_settings({"waitForIdleTimeout": 0, "disableIdler": True})
    except Exception as e:
        print(f"Не удалось применить скоростные настройки: {e}")

    # --- ИСПРАВЛЕНИЕ ЗАПУСКА ЗАПИСИ ---
    try:
        # Убрали несуществующие параметры. Оставляем только чистый лимит времени (3 минуты)
        driver.start_recording_screen(time_limit=180)
    except Exception as e:
        print(f"Не удалось запустить видеозапись Appium: {e}")

    yield driver

    # --- ТЕЙРДАУН СЕССИИ (Запускается после теста) ---
    try:
        raw_video = driver.stop_recording_screen()
        video_bytes = base64.b64decode(raw_video)

        # 1. Сохраняем физический файл на диск в корень проекта (last_run.mp4)
        static_video_path = Path(PROJECT_ROOT) / "last_run.mp4"
        static_video_path.write_bytes(video_bytes)

        # 2. ИСПРАВЛЕНИЕ ДЛЯ МОНОЛИТНОГО ОТЧЕТА:
        # Прикрепляем к Allure именно созданный файл по его пути — это гарантирует появление плеера
        allure.attach.file(
            source=str(static_video_path),
            name="video_execution_run",
            attachment_type=AttachmentType.MP4
        )
    except Exception as e:
        print(f"Ошибка при обработке или вложении видеозаписи: {e}")

    try:
        driver.quit()
    except Exception as e:
        print(f"Не удалось корректно завершить сессию драйвера: {e}")


def pytest_sessionfinish(session, exitstatus):
    """
        Хук PyTest: вызывается после тестов и верстает трехпанельный отчет с интерактивным JS-ползунком скриншотов;
        - генерирует стандартный Allure. И верстает мгновенный экспресс-дашборд с видео;
        - собирает продвинутый визуальный дашборд с неоновым подсвечиванием диффов
    """

    import os
    import datetime
    import subprocess

    raw_dir = getattr(session.config.option, 'allure_report_dir', None)
    if not raw_dir:
        return

    results_dir = os.path.abspath(raw_dir)
    report_dir = os.path.join(PROJECT_ROOT, "allure-report")

    # Собираем Allure в фоне
    user_home = str(Path.home())
    npm_allure_path = os.path.join(user_home, ".npm-global", "bin", "allure")
    allure_cmd = npm_allure_path if os.path.exists(npm_allure_path) else "allure"
    subprocess.run(
        [allure_cmd, "generate", results_dir, "-o", report_dir, "--clean", "--single-file"],
        check=False
    )

    template_name = getattr(pytest, 'last_template_name', None)
    dashboard_tip = "💡 По центру: ползунок сравнения Шаблона и Актуального экрана<br><br>💡 Справа: неоновый дифф (все изменения подсвечены ярко-розовым цветом)"

    if not template_name:
        template_name = "functional_failure"
        dashboard_tip = "💥 ТЕСТ УПАЛ ДО ПРОВЕРКИ ВЕРСТКИ!<br><br>На панелях ниже отображен чистый скриншот экрана эмулятора в момент системной или функциональной аварии кода"

    if exitstatus == 0:
        status_text, status_color = "PASSED ✅", "#2ec4b6"
    else:
        status_text, status_color = "FAILED ❌", "#e71d36"

    now_time = datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')

    # Верстаем трехпанельный HTML-дашборд с адаптивным JS-слайдером по центру
    html_dashboard = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Saby Admin - Visual Dashboard</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background-color: #141416; color: #ececed; margin: 0; padding: 20px; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; background: #1c1c21; padding: 15px 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }}
        .layout {{ display: grid; grid-template-columns: 320px 1fr 1fr; gap: 20px; height: 80vh; }}
        .panel {{ background-color: #1c1c21; border-radius: 12px; padding: 20px; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 4px 15px rgba(0,0,0,0.2); overflow: hidden; }}
        .info-panel {{ align-items: flex-start; justify-content: space-between; }}
        .media-box {{ width: 100%; height: 45%; display: flex; align-items: center; justify-content: center; background: #0b0b0d; border-radius: 8px; overflow: hidden; }}
        
        h1, h2 {{ margin: 0; color: #ffffff; }}
        h2 {{ font-size: 16px; margin-bottom: 10px; align-self: flex-start; color: #a0a0ab; }}
        .status-badge {{ background-color: {status_color}; color: #ffffff; padding: 8px 16px; border-radius: 6px; font-weight: bold; font-size: 16px; }}
        .meta {{ color: #a0a0ab; font-size: 14px; margin: 5px 0; }}
        .allure-btn {{ display: inline-block; background: #7928ca; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-size: 14px; margin-top: auto; width: 85%; text-align: center; font-weight: bold; }}
        .allure-btn:hover {{ background: #943ff3; }}
        
        /* Стили для интерактивного ползунка сравнения скриншотов */
        .image-container {{ position: relative; width: 100%; height: 100%; max-height: 70vh; aspect-ratio: 1080/2400; background: #000; border-radius: 6px; overflow: hidden; }}
        .img {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: contain; pointer-events: none; }}
        .image-after {{ clip-path: polygon(0 0, 50% 0, 50% 100%, 0 100%); z-index: 2; }}
        .image-before {{ z-index: 1; }}
        .slider-input {{ position: absolute; -webkit-appearance: none; appearance: none; width: 100%; height: 100%; background: transparent; outline: none; margin: 0; cursor: ew-resize; z-index: 10; }}
        .slider-input::-webkit-slider-thumb {{ -webkit-appearance: none; appearance: none; width: 4px; height: 100vh; background: #2ec4b6; }}
        
        /* Плашки бейджей */
        .badge {{ position: absolute; top: 10px; padding: 6px 12px; background: rgba(0,0,0,0.75); color: #fff; font-size: 12px; border-radius: 4px; z-index: 5; font-weight: bold; }}
        .actual-badge {{ left: 10px; border-left: 3px solid #ff0055; }}
        .template-badge {{ right: 10px; border-right: 3px solid #2ec4b6; }}
        
        .diff-img {{ max-width: 100%; max-height: 100%; object-fit: contain; border-radius: 6px; }}
        video {{ width: 100%; height: 100%; object-fit: contain; }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>Saby Admin Test Dashboard</h1>
            <div class="meta">Запуск от: {now_time}</div>
        </div>
        <div class="status-badge">{status_text}</div>
    </div>

    <div class="layout">
        <div class="panel info-panel">
            <div style="width: 100%;">
                <h2>Сценарий автоматизации</h2>
                <div class="meta" style="color: #fff; font-weight: bold;">test_remote_session.py</div>
                <div class="meta" style="margin-top: 15px; font-size: 12px; color: #82929f;">
                    {dashboard_tip}
                </div>
            </div>
            
            <div class="media-box" style="margin-top: 20px; height: 40%;">
                <video controls autoplay muted loop>
                    <source src="last_run.mp4" type="video/mp4">
                </video>
            </div>
            
            <a href="allure-report/index.html" target="_blank" class="allure-btn">Открыть Allure Report</a>
        </div>
        
        <div class="panel">
            <h2>Интерактивный слайдер (Template vs Actual)</h2>
            <div class="image-container">
                <div class="badge actual-badge">Текущий (Actual)</div>
                <div class="badge template-badge">Эталон (Template)</div>
                <img class="img image-before" src="screenshots/templates/{template_name}.png" />
                <img class="img image-after" src="screenshots/actual/{template_name}.png" />
                <input type="range" min="0" max="100" value="50" class="slider-input" oninput="moveSlider(this.value)" />
            </div>
        </div>
        
        <div class="panel">
            <h2>Карта различий (Neon Highlights)</h2>
            <div class="media-box" style="height: 100%; background: transparent;">
                <img class="diff-img" src="screenshots/actual/{template_name}_diff.png" />
            </div>
        </div>
    </div>

    <script>
        function moveSlider(value) {{
            document.querySelector('.image-after').style.clipPath = `polygon(0 0, ${{value}}% 0, ${{value}}% 100%, 0 100%)`;
        }}
    </script>
</body>
</html>"""

    preview_path = Path(PROJECT_ROOT) / "preview.html"
    preview_path.write_text(html_dashboard, encoding="utf-8")
    print(f"\n[DASHBOARD] Продвинутый визуальный отчет готов: {preview_path}")
