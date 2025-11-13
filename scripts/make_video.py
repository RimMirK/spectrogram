import argparse
import subprocess
import os
from PIL import Image, ImageDraw
from tqdm import tqdm

# Пример:
# python cut_frames.py --image spectrogram-rgb.png --audio sound.mp3 --res 1280x720 --step 4 --fps 25 --output out.mp4

def parse_res(value: str):
    try:
        w, h = map(int, value.lower().split("x"))
        return w, h
    except Exception:
        raise argparse.ArgumentTypeError("Разрешение указывай как WIDTHxHEIGHT, например 1280x720")

def main():
    parser = argparse.ArgumentParser(description="Режет RGB изображение на кадры и делает видео с 10 сек чёрного экрана в конце.")
    parser.add_argument("--image", required=True, help="Путь к RGB изображению")
    parser.add_argument("--audio", required=True, help="Путь к аудиофайлу")
    parser.add_argument("--res", type=parse_res, default=(1280, 720), help="Разрешение кадра, например 1280x720")
    parser.add_argument("--step", type=int, default=4, help="Шаг смещения окна")
    parser.add_argument("--fps", type=int, default=25, help="Частота кадров")
    parser.add_argument("--output", default="out.mp4", help="Имя выходного видеофайла")
    parser.add_argument("--bitrate", default="5000k", help="Битрейт видео")
    args = parser.parse_args()

    img = Image.open(args.image)
    width, height = img.size
    res_w, res_h = args.res
    os.makedirs("frames", exist_ok=True)

    total_frames = (width // args.step)
    print("Создаю кадры...")

    for center in tqdm(range(0, width, args.step), total=total_frames, ncols=70):
        left = max(center - res_w // 2, 0)
        right = left + res_w
        if right > width - 1:
            right = width - 1
            left = right - res_w

        o = img.crop((left, 0, right, res_h))
        draw = ImageDraw.Draw(o)
        for dx in (-1, 0, 1):
            x = center - left + dx
            draw.line((x, 0, x, res_h), fill=(0, 0, 180))

        name = f"frames/{center // args.step:06d}.png"
        o.save(name)

    # Добавляем 10 секунд чёрных кадров
    print("Добавляю 10 секунд чёрного экрана...")
    black = Image.new("RGB", (res_w, res_h), (0, 0, 0))
    extra_frames = args.fps * 10
    last_index = (width // args.step)

    for i in tqdm(range(extra_frames), desc="Чёрные кадры", ncols=70):
        black.save(f"frames/{last_index + i:06d}.png")

    # создаём временное аудио с 10 сек тишины в конце
    print("Создаю расширенное аудио...")
    extended_audio = "extended_audio.mp3"
    subprocess.run([
        "ffmpeg", "-y",
        "-i", args.audio,
        "-f", "lavfi", "-t", "10", "-i", "anullsrc=r=44100:cl=stereo",
        "-filter_complex", "[0:a][1:a]concat=n=2:v=0:a=1[outa]",
        "-map", "[outa]",
        extended_audio
    ], check=True)

    print("Кадры и аудио готовы, начинаю сборку видео...")

    subprocess.run([
        "ffmpeg", "-y",
        "-framerate", str(args.fps),
        "-i", "frames/%06d.png",
        "-i", extended_audio,
        "-b:v", args.bitrate,
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        args.output
    ], check=True)

    print(f"Видео готово: {args.output}")

if __name__ == "__main__":
    main()
