from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import os
from telegram.request import HTTPXRequest
from downloader import search_track, simple_download
from typing import Dict, NamedTuple, NewType

TrackID : str
class TrackInfo(NamedTuple):
    track_name: str
    track_url :str
TRACKS_BD : Dict[TrackID, TrackInfo] = dict()
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
PROXY_ID = os.getenv('TG_PROXY_USER')
WORK_DIR = os.path.dirname(os.path.abspath(__file__))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '🔍 Привет! Я бот для поиска музыки.\n'
        'Напиши название трека или исполнителя, и я найду ссылки на скачивание.'
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Показываем статус "печатает"
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')

    # Ищем треки
    tracks = search_track(update.message.text)

    if not tracks:
        await update.message.reply_text("❌ Ничего не найдено. Попробуй изменить запрос.")
        return

    # Ограничиваем до 5 результатов
    tracks = tracks[:5]

    # Создаем клавиатуру с кнопками
    keyboard = []
    for i, track in enumerate(tracks, 1):
        # Извлекаем название трека из ссылки для лучшего отображения
        track_name = track.split('/')[-1].replace('-', ' ').title()
        id = str(i)
        # Создаем кнопку для каждого трека
        button = InlineKeyboardButton(
            text=f"{i}. {track_name[:30]}...",  # Обрезаем длинные названия
            callback_data = id
        )
        keyboard.append([button])  # Каждая кнопка на новой строке
        TRACKS_BD[id] = TrackInfo(track_name, track_url=track)

    # Добавляем кнопку для поиска нового трека
    #keyboard.append([InlineKeyboardButton(text="🔄 Новый поиск", callback_data="new_search")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"✅ Найдено треков: {len(tracks)}\nВыбери трек для скачивания:",
        reply_markup=reply_markup
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    url = TRACKS_BD[query.data].track_url
    track_dir = simple_download(url)
    print(track_dir)
    print(f'{WORK_DIR}\\{track_dir}')
    # Формируем полный путь к файлу
    file_path = os.path.join(WORK_DIR, track_dir)
    print(f"[DEBUG] Полный путь к файлу: {file_path}")

    # Проверяем, существует ли файл и не пустой ли он
    if not os.path.isfile(file_path):
        await query.edit_message_text(f"❌ Файл не найден по пути: {file_path}")
        return

    file_size = os.path.getsize(file_path)
    print(f"[DEBUG] Размер файла: {file_size} байт ({file_size / 1024 / 1024:.2f} МБ)")
    if file_size == 0:
        await query.edit_message_text("❌ Скачанный файл пустой.")
        os.remove(file_path)  # удаляем мусор
        return

    # Пробуем отправить файл как документ
    try:
        # Сообщаем о начале отправки
        await query.edit_message_text("📤 Отправляю файл...")

        with open(file_path, 'rb') as doc:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=doc,
                filename=os.path.basename(file_path),  # явно указываем имя файла
                read_timeout=120,  # увеличиваем таймауты
                write_timeout=120,
                connect_timeout=60,
                pool_timeout=120
            )

        print("✅ Документ успешно отправлен")

        # Если дошли до сюда — отправка успешна
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="✅ Файл отправлен!"
        )

        # Удаляем временный файл после отправки
        os.remove(file_path)
        print(f"[DEBUG] Временный файл удалён: {file_path}")

    except Exception as e:
        # Ловимподробную ошибку
        error_msg = f"❌ Ошибка при отправке: {type(e).__name__}: {e}"
        print(error_msg)

        # Отправляем сообщение об ошибке пользователю
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=error_msg
        )

        # Не удаляем файл, чтобы можно было проверить его вручную
        print(f"[DEBUG] Файл сохранён для анализа: {file_path}")


request = HTTPXRequest(
    proxy=PROXY_ID,  # или socks5h:// для DNS через прокси
    connection_pool_size=10
)


def main():
    print(f"Токен загружен: {TOKEN[:10]}...")

    # Создаем приложение
    app = Application.builder().token(TOKEN).request(request).build()

    # Добавляем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))

    # Запускаем бота
    print("✅ Бот запущен...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()