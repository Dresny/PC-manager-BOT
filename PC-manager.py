import telebot
import os
import subprocess
import webbrowser
from PIL import Image
from io import BytesIO
import pyautogui
import platform

# Заполните все поля!!!
BOT_TOKEN = ""  # Замени на токен своего бота
ALLOWED_USER_IDS = []  # Список разрешенных User ID (через запятую!)
PASSWORD = "@dresny"  # Замени на свой пароль
AUTHORIZED_USERS = {}  # Словарь для хранения авторизованных пользователей (не трогать!!!)

SCREENSHOT_PATH = "screenshot.png"  # Путь для сохранения скриншотов
FILE_TRANSFER_FOLDER = r""  # Папка для передачи файлов (из бота на ПК) - замени!
FILE_SEND_FOLDER = r"" # Папка откуда бот будет отправлять файлы


# --- Инициализация бота ---
bot = telebot.TeleBot(BOT_TOKEN)

# --- Функции для работы с ПК --- (Остаются без изменений)
def take_screenshot():
    """Делает скриншот экрана и сохраняет его."""
    try:
        # image = pyscreenshot.grab() #быстрее, но нет курсора
        image = pyautogui.screenshot()  # медленнее, но есть курсор
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
    """Выводит сообщение на экран (Windows) в отдельном потоке."""
    try:
        import tkinter as tk
        import threading

        def show_message():
            """Функция для отображения сообщения в tkinter."""
            root = tk.Tk()
            root.title("Сообщение")
            label = tk.Label(root, text=message, padx=20, pady=10)
            label.pack()

            def close_window():
                root.destroy()

            root.after(9000, close_window)  # Закрыть окно через 9 секунд

            root.mainloop()

        # Запускаем tkinter в отдельном потоке
        thread = threading.Thread(target=show_message)
        thread.start()

        return True
    except Exception as e:
        print(f"Ошибка при выводе сообщения: {e}")
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

        # Загружаем изображение
        img = ImageTk.PhotoImage(Image.open(temp_image_path))
        panel = tk.Label(root, image=img)
        panel.pack(side="bottom", fill="both", expand="yes")

        # Закрываем окно через 5 секунд
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

# --- Клавиатуры ---
MAIN_MENU_KEYBOARD = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
MAIN_MENU_KEYBOARD.add(
    "⚙️ Выключение ПК",
    "📢 Вывод сообщения",
    "🗂️ Категории",
    "🔙 Назад"
)

CATEGORIES_KEYBOARD = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
CATEGORIES_KEYBOARD.add(
    "📤 Получение данных",
    "📥 Ввод данных",
    "🔙 Назад"
)

GET_DATA_KEYBOARD = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
GET_DATA_KEYBOARD.add(
    "📸 Скриншот экрана",
    "📤 Отправить файл с ПК",
    "🔙 Назад"
)

INPUT_DATA_KEYBOARD = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
INPUT_DATA_KEYBOARD.add(
    "🔗 Открыть ссылку",
    "💾 Отправить файл на ПК",
    "🖼️ Вывести изображение",
    "🔙 Назад"
)

# --- Состояния ---
STATE_MAIN_MENU = "main_menu"
STATE_CATEGORIES = "categories"
STATE_GET_DATA = "get_data"
STATE_INPUT_DATA = "input_data"

USER_STATES = {}  # Словарь для хранения состояний пользователей

# --- Обработчики команд ---
@bot.message_handler(commands=['start'])
def start(message):
    """Обработчик команды /start."""
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
        AUTHORIZED_USERS[user_id] = True  # Авторизуем пользователя
        USER_STATES[user_id] = STATE_MAIN_MENU
        show_main_menu(message)
    else:
        bot.send_message(user_id, "❌ Неверный пароль. Попробуйте еще раз /start")

def show_main_menu(message):
    """Показывает главное меню."""
    user_id = message.from_user.id
    if user_id in AUTHORIZED_USERS and AUTHORIZED_USERS[user_id]:
        msg = bot.send_message(user_id, "🤖 Выберите команду:", reply_markup=MAIN_MENU_KEYBOARD)
        delete_message(user_id, message.message_id)  # Удаляем предыдущее сообщение
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
            bot.send_message(user_id, "✅ ПК выключен")
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
    """Обрабатывает выбор действия (отправить или отправить и запустить)."""
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
        delete_message(user_id, message.message_id)  # Удаляем сообщение с предупреждением@bot.message_handler(func=lambda message: message.text == "🖼️ Вывести изображение", content_types=['photo'])
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

@bot.message_handler(func=lambda message: message.text == "📤 Отправить файл с ПК")
def handle_send_file(message):
    """Обрабатывает запрос на отправку файла с ПК."""
    user_id = message.from_user.id

    if user_id in AUTHORIZED_USERS and AUTHORIZED_USERS[user_id]:
        # Создаем Inline Keyboard с названиями файлов
        markup = telebot.types.InlineKeyboardMarkup()
        files = [f for f in os.listdir(FILE_SEND_FOLDER) if os.path.isfile(os.path.join(FILE_SEND_FOLDER, f))]
        for file in files:
            markup.add(telebot.types.InlineKeyboardButton(text=file, callback_data=f"send_file:{file}"))  # Добавляем callback_data

        bot.send_message(user_id, "🗂️ Выберите файл для отправки:", reply_markup=markup)
        delete_message(user_id, message.message_id)
    else:
        bot.send_message(user_id, "🚫 Пожалуйста, сначала введите пароль /start")

@bot.callback_query_handler(func=lambda call: call.data.startswith("send_file:"))
def callback_send_file(call):
    """Обрабатывает выбор файла из Inline Keyboard."""
    user_id = call.from_user.id
    file_name = call.data.split(":")[1]  # Извлекаем имя файла из callback_data
    file_path = os.path.join(FILE_SEND_FOLDER, file_name)

    try:
        with open(file_path, 'rb') as file:
            bot.send_document(user_id, file)
        bot.send_message(user_id, "✅ Файл отправлен.")
    except Exception as e:
        bot.send_message(user_id, f"❌ Не удалось отправить файл: {e}")

    delete_message(user_id, call.message.message_id) #Удаляем сообщение с клавиатурой

@bot.message_handler(func=lambda message: message.text == "🗂️ Категории")
def handle_categories(message):
    """Обрабатывает запрос на показ категорий."""
    user_id = message.from_user.id
    if user_id in AUTHORIZED_USERS and AUTHORIZED_USERS[user_id]:
        show_categories_menu(message)
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
        elif current_state == STATE_GET_DATA or current_state == STATE_INPUT_DATA:
            show_categories_menu(message)
        else:
            show_main_menu(message)
    else:
        bot.send_message(user_id, "🚫 Пожалуйста, сначала введите пароль /start")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    """Обрабатывает все остальные сообщения."""
    user_id = message.from_user.id
    if user_id in AUTHORIZED_USERS and AUTHORIZED_USERS[user_id]:
        bot.reply_to(message, "⚠️ Неизвестная команда.  Выберите команду из меню.")
        delete_message(user_id, message.message_id)
    else:
        bot.send_message(user_id, "🚫 Пожалуйста, сначала введите пароль /start")

# --- Запуск бота ---
if __name__ == '__main__':
    print("Работаем...")
    bot.infinity_polling()