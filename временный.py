from pathlib import Path
from PIL import Image, ImageDraw

# Укажи точный путь к файлу скриншота, который ты скачал из Appium Inspector
source_screenshot = Path('/home/vm.hudasov/Desktop/Screenshot_1783305242.png')

# Путь для сохранения эталона в проект
template_path = Path("screenshots/templates/main_page_authorized.png")
template_path.parent.mkdir(parents=True, exist_ok=True)

# Открываем картинку и замазываем динамические элементы под цвет темной темы
img = Image.open(source_screenshot).convert("RGB")
draw = ImageDraw.Draw(img)

# Закрашиваем область кода [48, 889, 290, 999] под цвет фона приложения
draw.rectangle([48, 889, 290, 999], fill="#18181c")

# Автоматически замазываем верхние 150px экрана, чтобы скрыть строку состояния Android 16
draw.rectangle([0, 0, img.width, 150], fill="#18181c")

# Сохраняем чистый эталон
img.save(template_path)
print(f"Идеальный шаблон без кода и статус-бара создан и сохранен в: {template_path}")