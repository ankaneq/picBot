import asyncio
import easyocr


from gtts import gTTS
from translate import Translator

from aiogram import Bot, types, Dispatcher, F
from aiogram.types.input_file import FSInputFile
from aiogram.filters import CommandStart, Filter
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import CallbackQuery


# Bot token
TOKEN = '6210740611:AAFzDF02G1NEQbwqFJMq6gvp4Qrf8KswVD8'

# Initialize the bot and dispatcher
dp = Dispatcher()
bot = Bot(TOKEN)

# Flags
language = 'en'
switch_audio_text_output_flag = 0


async def main():
    await dp.start_polling(bot)


def text_recognition(file_path):
    text1 = ''
    reader = easyocr.Reader(["ru", "en"])
    # Recognizing text from the photo
    result1 = reader.readtext(file_path, detail=0, paragraph=True)
    for line in result1:
        text1 += f"{line}\n\n"
    return text1


def keyboard():
    builder = ReplyKeyboardBuilder()

    for i in ['/commands', '/start', '/clear', '/change_language', '/switch_audio_text_output', '/keyboard']:
        builder.button(text=i)
    builder.adjust(2)
    return builder.as_markup()


def inline_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="keyboard",
        callback_data=MyCallback(foo="keyboard", bar="42")
        # Value can be not packed to string inplace, because builder knows what to do with callback instance
    )
    return builder.as_markup()


class Command(Filter):
    def __init__(self, my_text: str) -> None:
        self.my_text = my_text

    async def __call__(self, message: types.Message) -> bool:
        return message.text == self.my_text


class MyCallback(CallbackData, prefix="my"):
    foo: str
    bar: int


@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    if language == 'en':
        text = 'Hi! Send me a photo with text to hear it in English or Russian.'
    else:
        text = 'Привет! Отправь мне фото с текстом чтобы услышать его на Русском или Английском.'
    await message.answer(text, reply_markup=inline_keyboard())


@dp.message(Command("/keyboard"))
async def command_keyboard_handler(message: types.Message):
    await message.answer(' ', reply_markup=keyboard())


@dp.message(Command("/commands"))
async def all_commands(message: types.Message):
    await message.answer('/commands, /start, /clear, /change_language, /switch_audio_text_output, /keyboard')


@dp.message(Command("/switch_audio_text_output"))
async def switch_audio_text_output(message: types.Message):
    global switch_audio_text_output_flag
    if switch_audio_text_output_flag:
        switch_audio_text_output_flag = 0
        if language == 'en':
            await message.answer('Now bot sending text')
        else:
            await message.answer('Теперь бот отправляет текст')
    else:
        if language == 'en':
            await message.answer('Now bot sending audio')
        else:
            await message.answer('Теперь бот отправляет голосовое сообщение')
        switch_audio_text_output_flag = 1


@dp.message(Command("/clear"))
async def cmd_clear(message: types.Message):
    try:
        # delete all messages (message_id = 0)
        for i in range(message.message_id, 0, -1):
            await bot.delete_message(message.from_user.id, i)
    except TelegramBadRequest as ex:
        pass


@dp.message(Command('/change_language'))
async def switch_language(message: types.Message):
    global language

    if language == 'en':
        language = 'ru'
        await message.answer("Язык был изменен на русский.")

    elif language == 'ru':
        language = 'en'
        await message.answer("The language has been changed to English.")


# Filter callback by type and value of field :code:`foo`
@dp.callback_query(MyCallback.filter(F.foo == "keyboard"))
async def my_callback_foo(query: CallbackQuery, callback_data: MyCallback):
    if language == 'ru':
        await query.message.answer('чтобы открыть все функции нажмите на /keyboard')
    else:
        await query.message.answer('to see all of the bot functions press /keyboard')

@dp.message(F.photo)
async def photo_handler(message: types.Message):
    if language == 'ru':
        await message.answer('обработка фото...')
    else:
        await message.answer('photo processing...')

    # Download the photo
    file = await bot.get_file(message.photo[len(message.photo) - 1].file_id)
    file_path = file.file_path
    await bot.download_file(file_path, "photo.jpg")

    # Recognize text from the photo
    result = text_recognition(r'F:\pycharm\ended_Pic_to_text_bot\photo.jpg')

    if result:
        # Translation to chosen language
        text = Translator(to_lang=language).translate(result)

        if not switch_audio_text_output_flag:
            await message.answer(text)

        else:
            # Convert the recognized and translated text to speech
            tts = gTTS(text=text, lang=language)
            tts.save("OutputMP3file.mp3")
            audio = FSInputFile(path="OutputMP3file.mp3")

            await bot.send_audio(message.chat.id, audio=audio)


if __name__ == '__main__':
    print('Bot is running')
    asyncio.run(main())
