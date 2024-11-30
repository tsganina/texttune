from flask import Flask, render_template, request, send_file
from gtts import gTTS
from langdetect import detect
import io
import speech_recognition as sr
from pydub import AudioSegment
import os

app = Flask(__name__)

def convert_to_wav_in_memory(file_data):
    """
    Конвертирует аудиофайл в формат WAV в памяти.
    :param file_data: Данные аудиофайла в байтах
    :return: io.BytesIO объект с WAV-аудио
    """
    audio = AudioSegment.from_file(io.BytesIO(file_data))  # Загружаем аудио из памяти
    wav_buffer = io.BytesIO()  # Создаём буфер для WAV
    audio.export(wav_buffer, format='wav')  # Экспортируем как WAV
    wav_buffer.seek(0)  # Возвращаем указатель на начало файла
    return wav_buffer

def text_to_audio(text):
    try:
        # Определяем язык текста
        detected_language = detect(text)
        # Создаем аудио с использованием gTTS
        tts = gTTS(text=text, lang=detected_language, slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer, detected_language
    except Exception as e:
        return None, f"Ошибка: {str(e)}"

def recognize_audio(file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)
    
    try:
        text = recognizer.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        return "Не удалось распознать речь"
    except sr.RequestError as e:
        return f"Ошибка запроса к сервису распознавания: {e}"

@app.route('/')
def index():
    return render_template('index.html', title="Главная страница")

@app.route('/text_to_audio', methods=['GET', 'POST'])
def text_to_audio_page():
    if request.method == 'POST':
        text = request.form['text']
        if text:
            audio_data, language = text_to_audio(text)
            if audio_data:
                return send_file(audio_data, as_attachment=True, download_name="output_audio.mp3", mimetype='audio/mp3')
            else:
                return f"Не удалось создать аудио: {language}"
        return "Пожалуйста, введите текст для конвертации."
    return render_template('text_to_audio.html')

# Функция для преобразования в формат WAV
def convert_to_wav_in_memory(audio_file):
    audio = AudioSegment.from_file(io.BytesIO(audio_file))
    wav_buffer = io.BytesIO()
    audio.export(wav_buffer, format='wav')
    wav_buffer.seek(0)
    return wav_buffer

# Функция для определения языка текста
def detect_language(text):
    try:
        language = detect(text)
        if language == 'ru':
            return 'ru'
        elif language == 'es':
            return 'es'
        else:
            return 'en'
    except:
        return 'en'  # По умолчанию считаем английский

# Функция для распознавания речи с учетом языка
def recognize_audio(audio_file):
    wav_audio = convert_to_wav_in_memory(audio_file)  # Преобразуем в WAV
    recognizer = sr.Recognizer()

    with sr.AudioFile(wav_audio) as source:
        audio_data = recognizer.record(source)

    # Попробуем распознать текст на русском
    try:
        text = recognizer.recognize_google(audio_data, language='ru-RU')
        detected_language = detect_language(text)  # Определяем язык

        if detected_language == 'en':
            # Если язык оказался английским, пробуем распознать на английском
            text = recognizer.recognize_google(audio_data, language='en-US')
            language = 'английский'
        elif detected_language == 'es':
            # Если язык испанский, пробуем распознать на испанском
            text = recognizer.recognize_google(audio_data, language='es-ES')
            language = 'испанский'
        else:
            language = 'русский'

        return text, language
    except sr.UnknownValueError:
        try:
            # Если не получилось на русском, пробуем на испанском
            text = recognizer.recognize_google(audio_data, language='es-ES')
            language = 'испанский'
            return text, language
        except sr.UnknownValueError:
            try:
                # Если не получилось на испанском, пробуем на английском
                text = recognizer.recognize_google(audio_data, language='en-US')
                language = 'английский'
                return text, language
            except sr.UnknownValueError:
                return "Не удалось распознать речь", None
            except sr.RequestError as e:
                return f"Ошибка запроса к сервису распознавания: {e}", None

# Маршрут Flask для страницы с распознаванием аудио в текст
@app.route('/audio_to_text', methods=['GET', 'POST'])
def audio_to_text_page():
    recognized_text = None  # Переменная для текста
    if request.method == 'POST':
        file = request.files['audio_file']
        if file:
            try:
                # Получаем файл, распознаем речь и определяем язык
                audio_file = file.read()
                recognized_text, language = recognize_audio(audio_file)
            except Exception as e:
                recognized_text = f"Ошибка распознавания: {str(e)}"

    return render_template('audio_to_text.html', recognized_text=recognized_text)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)

