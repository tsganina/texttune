import speech_recognition as sr
from pydub import AudioSegment
import langid
import re

def convert_and_transcribe(ogg_file_path):
    # Конвертация .ogg в .wav
    audio = AudioSegment.from_ogg(ogg_file_path)
    wav_file_path = ogg_file_path.replace(".ogg", ".wav")
    audio.export(wav_file_path, format="wav")

    # Создаем распознаватель
    recognizer = sr.Recognizer()

    # Открываем .wav файл
    with sr.AudioFile(wav_file_path) as source:
        print("Считываем аудио...")
        audio_data = recognizer.record(source)

    # Пробуем распознать текст
    try:
        print("Распознаем текст...")
        text = recognizer.recognize_google(audio_data, language="ru-RU")  # Принудительно русский

        print(f"Распознанный текст: {text}")

        # Проверяем, действительно ли это русский язык
        if validate_russian(text):
            detected_language = "ru"
            print(f"Определённый язык: {detected_language}")
            return text, detected_language

        # Если текст не похож на русский, пытаемся определить язык
        detected_language, confidence = langid.classify(text)
        print(f"Определённый язык через langid: {detected_language} (уверенность: {confidence})")
        return text, detected_language
    except sr.UnknownValueError:
        return "Не удалось распознать речь", None
    except sr.RequestError as e:
        return f"Ошибка сервиса распознавания речи: {e}", None

def validate_russian(text):
    """Проверка, является ли текст русским на основе алфавита."""
    russian_chars = re.compile(r"[а-яА-ЯёЁ]+")
    return bool(russian_chars.search(text))



# ogg_file = "AwACAgIAAxkBAAIGBmdLTyOoDTpmsjiE_pgWMfjUzwseAAIXYQACws5YSqQol2DkrnmLNgQ.ogg"
# transcribed_text, language = convert_and_transcribe(ogg_file)
# print("Распознанный текст:", transcribed_text)
# print("Язык:", language)



# 5854399164:AAHFDliuCyzQasUCCg1A7y_5rdY8zO7__wc