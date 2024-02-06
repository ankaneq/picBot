import aiogram
import easyocr
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.exceptions import MessageTextIsEmpty


TOKEN_API = '6210740611:AAFzDF02G1NEQbwqFJMq6gvp4Qrf8KswVD8'

bot = Bot(TOKEN_API)
dp = Dispatcher(bot)


def text_recognition(file_path):
    text1 = ''
    reader = easyocr.Reader(["ru", "en"])
    result1 = reader.readtext(file_path, detail=0, paragraph=True)
    for line in result1:
        text1 += f"{line}\n\n"
    return text1


async def on_startup(_):
    print('я включился')


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer('Привет, отправь мне фото')


@dp.message_handler(commands=['поменять язык'])
async def change_language(message: types.Message):
    if message.text not in ['ru', 'en']:
        await message.answer(text='Язык не распознан')


@dp.message_handler(content_types=['document'])
async def handle_docs_photo(message):
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    await bot.download_file(file_path, "photo.jpg")
    try:
        await message.answer(text_recognition(r'F:\pycharm\ended_Pic_to_text_bot\photo.jpg'))
    except MessageTextIsEmpty:
        await message.answer('Я не вижу текста')


@dp.message_handler(content_types=['photo'])
async def handle_photo(message):
    file = await bot.get_file(message.photo[len(message.photo) - 1].file_id)
    file_path = file.file_path
    await bot.download_file(file_path, "photo.jpg")
    try:
        await message.answer(text_recognition(r'F:\pycharm\ended_Pic_to_text_bot\photo.jpg'))
    except MessageTextIsEmpty:
        await message.answer('Я не вижу текста')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
