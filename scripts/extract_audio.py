import sys
import os
import subprocess

# Пример:
# python extract_audio.py video.mp4

def main():
    if len(sys.argv) < 2:
        print("использование: python extract_audio.py <путь_к_видео>")
        sys.exit(1)

    video_path = os.path.abspath(sys.argv[1])
    if not os.path.isfile(video_path):
        print("файл не найден:", video_path)
        sys.exit(1)

    base_dir = os.path.dirname(video_path)
    output_path = os.path.join(base_dir, "audio.mp3")

    cmd = [
        "ffmpeg",
        "-y",               # перезаписывать без подтверждения
        "-i", video_path,   # входное видео
        "-q:a", "0",        # максимальное качество mp3
        "-map", "a",        # только аудио-дорожка
        output_path,
    ]

    subprocess.run(cmd, check=True)
    print(f"Аудио сохранено: {output_path}")

if __name__ == "__main__":
    main()
