import subprocess
from pathlib import Path
import imageio_ffmpeg

def convert_folder(input_dir: str, output_dir: str = None) -> None:
    source_path = Path(input_dir)
    target_path = Path(output_dir) if output_dir else source_path / "converted_mp4"
    target_path.mkdir(parents=True, exist_ok=True)

    # Автоматически получает абсолютный путь к ffmpeg.exe
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    webm_files = list(source_path.glob("*.webm"))
    if not webm_files:
        print("WebM файлы не найдены.")
        return

    print(f"Найдено файлов для конвертации: {len(webm_files)}")

    for idx, file in enumerate(webm_files, start=1):
        output_file = target_path / f"{file.stem}.mp4"
        print(f"[{idx}/{len(webm_files)}] Конвертация: {file.name} -> {output_file.name}")

        cmd = [
            ffmpeg_exe,
            "-i", str(file),
            "-c:v", "libx264",
            "-crf", "23",
            "-preset", "medium",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-y",
            str(output_file)
        ]

        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        if result.returncode != 0:
            print(f"Ошибка при обработке {file.name}:\n{result.stderr.decode('utf-8')}")

    print("Пакетная конвертация завершена.")

convert_folder(r"C:\Users\User\PycharmProjects\Demo\docs\media")