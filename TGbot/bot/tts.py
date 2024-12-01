from gtts import gTTS
from langdetect import detect
import io

def text_to_audio(text):
    try:
        # Определяем язык текста
        detected_language = detect(text)
        # Создаем аудио с использованием gTTS
        tts = gTTS(text=text, lang=detected_language, slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)

        with open("output_audio.mp3", "wb") as f:
            f.write(audio_buffer.read())
        print(f"Аудио успешно создано на языке: {detected_language}")

        return audio_buffer, detected_language
    except Exception as e:
        return None, f"Ошибка: {str(e)}"

# text = "Привет! Коты инопланетяне скоро захватят землю, не слушайте говорящие компоты!"
# text = "Hello dear friends! Today we will code an assistant."
# audio_data, language = text_to_audio(text)

# if audio_data:
#     # Сохраняем аудио в файл
#     with open("output_audio.mp3", "wb") as f:
#         f.write(audio_data.read())
#     print(f"Аудио успешно создано на языке: {language}")
# else:
#     print(f"Не удалось создать аудио: {language}")