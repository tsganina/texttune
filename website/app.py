from flask import Flask, render_template, request, send_file
from gtts import gTTS
from langdetect import detect
import io
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
from collections import Counter

app = Flask(__name__)


def recognize_chunk(chunk_data):
    """
    Распознаёт текст в одном аудиофрагменте.
    :param chunk_data: Данные WAV-фрагмента
    :return: Распознанный текст и язык
    """
    recognizer = sr.Recognizer()
    with sr.AudioFile(chunk_data) as source:
        audio_data = recognizer.record(source)

    try:
        # Пробуем сначала на русском
        text = recognizer.recognize_google(audio_data, language='ru-RU')
        detected_language = detect(text)
        if detected_language == 'es':
            # Если язык оказался испанским, пробуем распознать на испанском
            text = recognizer.recognize_google(audio_data, language='es-ES')
        elif detected_language == 'en':
            # Если язык оказался английским, пробуем распознать на английском
            text = recognizer.recognize_google(audio_data, language='en-US')
        return text, detected_language
    except sr.UnknownValueError:
        try:
            # Если на русском не получилось, пробуем на испанском
            text = recognizer.recognize_google(audio_data, language='es-ES')
            return text, 'es'
        except sr.UnknownValueError:
            try:
                # Если не получилось на испанском, пробуем на английском
                text = recognizer.recognize_google(audio_data, language='en-US')
                return text, 'en'
            except sr.UnknownValueError:
                return "Не удалось распознать речь", None
            except sr.RequestError as e:
                return f"Ошибка запроса: {e}", None
    except sr.RequestError as e:
        return f"Ошибка запроса: {e}", None


def recognize_long_audio(file_data):
    """
    Обрабатывает длинное аудио, разбивает его на части и распознаёт каждую.
    :param file_data: Данные аудиофайла
    :return: Полный текст и доминирующий язык
    """
    try:
        audio = AudioSegment.from_file(io.BytesIO(file_data))
        chunks = split_on_silence(
            audio,
            min_silence_len=500,
            silence_thresh=audio.dBFS - 14,
            keep_silence=250
        )

        full_text = []
        languages = []

        for chunk in chunks:
            chunk_buffer = io.BytesIO()
            chunk.export(chunk_buffer, format="wav")
            chunk_buffer.seek(0)

            text, language = recognize_chunk(chunk_buffer)
            if text:
                full_text.append(text)
            if language:
                languages.append(language)

        # Определяем доминирующий язык
        dominant_language = Counter(languages).most_common(1)[0][0] if languages else "не определён"
        return " ".join(full_text), dominant_language
    except Exception as e:
        return f"Ошибка обработки аудио: {str(e)}", None

def text_to_audio(text):
    """
    Конвертирует текст в аудио.
    :param text: Строка текста
    :return: io.BytesIO объект с аудио и язык текста
    """
    try:
        detected_language = detect(text)
        tts = gTTS(text=text, lang=detected_language, slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer, detected_language
    except Exception as e:
        return None, f"Ошибка: {str(e)}"

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

@app.route('/audio_to_text', methods=['GET', 'POST'])
def audio_to_text_page():
    recognized_text = None
    dominant_language = None
    if request.method == 'POST':
        file = request.files['audio_file']
        if file:
            try:
                audio_file = file.read()
                recognized_text, dominant_language = recognize_long_audio(audio_file)
                if not recognized_text.strip():
                    recognized_text = "Текст не распознан."
            except Exception as e:
                recognized_text = f"Ошибка распознавания: {str(e)}"

    return render_template('audio_to_text.html', recognized_text=recognized_text, dominant_language=dominant_language)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
