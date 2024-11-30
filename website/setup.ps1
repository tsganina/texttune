# setup.ps1

Write-Host "Устанавливаем зависимости..."
pip install --user -r requirements.txt

Write-Host "Проверяем наличие FFmpeg..."
if (-not (Get-Command "ffmpeg" -ErrorAction SilentlyContinue)) {
    Write-Host "FFmpeg не найден. Устанавливаем FFmpeg..."
    # Для установки FFmpeg на Windows можно использовать Chocolatey (если установлен):
    choco install ffmpeg -y
} else {
    Write-Host "FFmpeg уже установлен."
}

Write-Host "Запуск приложения..."
python app.py

