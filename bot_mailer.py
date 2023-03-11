import telebot
import sqlite3
import threading
from kekes import key_2

# Токен бота, который нужно получить у BotFather в Telegram
TOKEN = '6196341596:AAExFNBwlm7SF8yeqRsLYiDRbIg0vY4HvlE'

# Создание объекта бота
bot = telebot.TeleBot(TOKEN)

# Функция для создания соединения к базе данных в каждом потоке
def get_conn():
    return sqlite3.connect('emails.db', check_same_thread=False)

# Обработчик команды /add
@bot.message_handler(commands=['add'])
def add_email(message):
    # Получение почты и пароля от пользователя
    email = message.text.split()[1]
    password = message.text.split()[2]
    # Создание соединения и курсора
    conn = get_conn()
    cursor = conn.cursor()
    # Добавление в базу данных
    cursor.execute("INSERT INTO emails (email, password) VALUES (?, ?)", (email, password))
    conn.commit()
    # Закрытие соединения
    cursor.close()
    conn.close()
    bot.send_message(message.chat.id, f"Email {email} с паролем {password} добавлен в базу данных")

# Обработчик команды /delete
@bot.message_handler(commands=['delete'])
def delete_email(message):
    # Получение почты, которую нужно удалить
    email = message.text.split()[1]
    # Создание соединения и курсора
    conn = get_conn()
    cursor = conn.cursor()
    # Удаление из базы данных
    cursor.execute("DELETE FROM emails WHERE email=?", (email,))
    conn.commit()
    # Закрытие соединения
    cursor.close()
    conn.close()
    bot.send_message(message.chat.id, f"Email {email} удален из базы данных")

# Обработчик команды /list
@bot.message_handler(commands=['list'])
def list_emails(message):
    try:
        # Создание соединения и курсора
        conn = get_conn()
        cursor = conn.cursor()
        # Получение всех почт и паролей из базы данных
        cursor.execute("SELECT email, password FROM emails")
        rows = cursor.fetchall()
        # Формирование списка в виде строки
        emails_list = ''
        for row in rows:
            emails_list += f"{row[0]} - {row[1]}\n"
        # Закрытие соединения
        cursor.close()
        conn.close()
        # Отправка списка пользователю
        bot.send_message(message.chat.id, emails_list)
    except:
        bot.send_message(message.chat.id, 'В базе нет ничего')

@bot.message_handler(commands=['use'])
def get_password(message):
    # Получение почты, для которой нужно получить пароль
    print(message.text.split())
    email = message.text.split()[1]
    print(email)
    # Создание соединения и курсора
    conn = get_conn()
    cursor = conn.cursor()
    # Получение пароля из базы данных
    cursor.execute("SELECT password FROM emails WHERE email=?", (email,))
    result = cursor.fetchone()
    # Закрытие соединения
    cursor.close()
    conn.close()
    if result:
        password = result[0]
        bot.send_message(message.chat.id, f"Пароль для почты {email}: {password}")
    else:
        bot.send_message(message.chat.id, f"Почта {email} не найдена в базе данных")
# Запуск бота
bot.polling()
