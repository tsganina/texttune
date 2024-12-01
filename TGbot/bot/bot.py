from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio, logging
from tts import text_to_audio
from dotenv import load_dotenv
import os, sr, test

load_dotenv()

logging.basicConfig(level=logging.INFO)

bot = Bot(token="7674632667:AAFLtHGSPZ7iTWqEBS9BhXr0Jqj_-b9jKDY")
dp = Dispatcher(bot=bot)

# router = Router()

start_kb = InlineKeyboardBuilder(markup=[
    [InlineKeyboardButton(text='Речь в текст', callback_data='SR')],
    [InlineKeyboardButton(text='Текст в речь', callback_data='TTS')]
])
# builder = InlineKeyboardBuilder(markup=start_kb)

class FSMTTS(StatesGroup):
    type_text = State()

@dp.message(Command('start'))
async def start(message: types.Message):
    await message.answer('Привет!\n\nЯ бот, который умеет переводить речь в текст и наоборот.', reply_markup=start_kb.as_markup())


@dp.callback_query(lambda c: c.data=='TTS')
async def text_to_speech_button(callback: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback.from_user.id, 'Напиши текст')
    await state.set_state(FSMTTS.type_text)


@dp.message(FSMTTS.type_text)
async def gettin_text(message: types.Message, state: FSMContext):
    text = message.text
    audio, lang = text_to_audio(text)
    voiceFile = FSInputFile('output_audio.mp3')
    await bot.send_voice(message.from_user.id, voice=voiceFile, caption="Вот ваше аудио", reply_markup=start_kb.as_markup())
    os.remove('output_audio.mp3')
    await state.clear()
    

class FSMSR(StatesGroup):
    wait_audio = State()

@dp.callback_query(lambda c: c.data=="SR")
async def startSR(callback: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback.from_user.id, "Пришли мне аудио")
    await state.set_state(FSMSR.wait_audio)


@dp.message(FSMSR.wait_audio)
async def wait_audio(message: types.Message, state: FSMContext):
    user_audio = message.voice

    # Получаем информацию о файле с помощью Bot
    bot = message.bot
    file = await bot.get_file(user_audio.file_id)

    # Скачиваем файл
    file_path = f"{user_audio.file_id}.ogg"  # Указываем имя файла
    await bot.download_file(file.file_path, destination=file_path)

    print(f"Файл сохранен как {file_path}")
    transcribed_text, language = sr.convert_and_transcribe(file_path)
    await message.answer(transcribed_text, reply_markup=start_kb.as_markup())
    os.remove(file_path)



async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())