#!/bin/bash

echo "Устанавливаем зависимости..."
pip3 install --user -r requirements.txt

echo "Проверяем наличие FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "FFmpeg не найден. Устанавливаем FFmpeg..."
    sudo apt update && sudo apt install -y ffmpeg
else
    echo "FFmpeg уже установлен."
fi

echo "Запуск приложения..."
python3 app.py

