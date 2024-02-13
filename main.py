import asyncio
import easyocr
from gtts import gTTS
from translate import Translator

from aiogram import Bot, types, Dispatcher, F
from aiogram.types.input_file import FSInputFile
from aiogram.filters import CommandStart, Filter


# Replace with your bot token
TOKEN = '6210740611:AAFzDF02G1NEQbwqFJMq6gvp4Qrf8KswVD8'

# Initialize the bot and dispatcher
dp = Dispatcher()
bot = Bot(TOKEN)

# Set the initial language to English
language = 'en'


def text_recognition(file_path):
    text1 = ''
    reader = easyocr.Reader(["ru", "en"])
    result1 = reader.readtext(file_path, detail=0, paragraph=True)
    for line in result1:
        text1 += f"{line}\n\n"
    return text1


class ChangeLanguage(Filter):
    def __init__(self, my_text: str) -> None:
        self.my_text = my_text

    async def __call__(self, message: types.Message) -> bool:
        return message.text == self.my_text


@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    text = ('Hi! Send me a photo with text to hear it in English or Russian. Use the "/changelang" command to switch '
            'the language.')
    await message.answer(text)


@dp.message(F.photo)
async def photo_handler(message: types.Message):
    # Download the photo
    await message.answer('обработка фото...')
    file = await bot.get_file(message.photo[len(message.photo) - 1].file_id)
    file_path = file.file_path
    await bot.download_file(file_path, "photo.jpg")

    # Recognize text from the photo
    result = text_recognition(r'F:\pycharm\ended_Pic_to_text_bot\photo.jpg')

    if result:
        # Translation to chosen language
        text = Translator(to_lang=language).translate(result)

        # Convert the recognized and translated text to speech
        tts = gTTS(text=text, lang=language)
        tts.save("OutputMP3file.mp3")
        audio = FSInputFile(path="OutputMP3file.mp3")

        await bot.send_audio(message.chat.id, audio=audio)


@dp.message(ChangeLanguage('/changelang'))
async def switch_language(message: types.Message):
    global language
    if language == 'en':
        language = 'ru'
        await message.answer("The language has been changed to Russian.")
    elif language == 'ru':
        language = 'en'
        await message.answer("The language has been changed to English.")


async def main():
    await dp.start_polling(bot)


async def on_startup(_):
    print('i am on')

if __name__ == '__main__':
    asyncio.run(main())
