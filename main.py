import telebot
from telebot import types
import imaplib
import email
import base64
from kekes import key_1
from kekes import users
import time
import re
import sqlite3

bot = telebot.TeleBot(key_1)
global come_amount
come_amount = 0

global mail_log
global pass_email

# ---------------------- РАБОТА С БД -----------------------------

def get_conn():
    return sqlite3.connect('emails.db', check_same_thread=False)

@bot.message_handler(commands=['add'])
def add_email(message):
    if message.from_user.username in users:
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
    else:
        bot.send_message(message.chat.id, '❌ Доступ запрещен ! ❌')


@bot.message_handler(commands=['delete'])
def delete_email(message):
    if message.from_user.username in users:
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
    else:
        bot.send_message(message.chat.id, '❌ Доступ запрещен ! ❌')

@bot.message_handler(commands=['list'])
def list_emails(message):
    if message.from_user.username in users:
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
    else:
        bot.send_message(message.chat.id, '❌ Доступ запрещен ! ❌')


@bot.message_handler(commands=['use'])
def get_password(message):
    if message.from_user.username in users:
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
    else:
        bot.send_message(message.chat.id, '❌ Доступ запрещен !❌ ')




@bot.message_handler(commands=['use'])
def get_password(message):
    if message.from_user.username in users:
        # Получение почты, для которой нужно получить пароль
        email = message.text.split()[0]
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
            bot.send_message(message.chat.id, f"Почта успешно заменена на {email}")
            global mail_log
            mail_log = email
            global pass_email
            pass_email = password
        else:
            bot.send_message(message.chat.id, f"Почта {email} не найдена в базе данных. Можешь добавить её тут: @mail_base_umoney_bot")
    else:
        bot.send_message(message.chat.id, '❌ Доступ запрещен !❌ ')



# --------------------------------------------------------------------

def connect_imap():
    mail_pass = pass_email
    username = mail_log
    imap_server = "imap.mail.ru"
    imap = imaplib.IMAP4_SSL(imap_server)
    imap.login(username, mail_pass)
    imap.select('inbox')
    return imap


def get_vadim_sum(msg):
        bot.send_message(msg.chat.id, f"Сумма заявки:  {msg.text}")
        global vadim_sum
        vadim_sum = int(msg.text)

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.username in users:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("💰")
        btn2 = types.KeyboardButton("🏁")
        btn3 = types.KeyboardButton("⛔")
        btn4 = types.KeyboardButton("📧")
        markup.add(btn1, btn2, btn3,btn4)
        if message.from_user.username in users:
            bot.send_message(message.chat.id,
                             text="Салам, {0.first_name}! Выбери команду".format(
                                 message.from_user), reply_markup=markup)
        else:
            bot.send_message(message.chat.id,'Тебя нет в базе !')
    else:
        bot.send_message(message.chat.id, '❌ Доступ запрещен !❌ ')

@bot.message_handler(content_types=['text'])
def func(message):
    global flag
    flag = False
    if (message.text == "💰"):
        if message.from_user.username in users:
            mesg = bot.send_message(message.chat.id, 'Введи сумму заявки без пробелов и символов')
            bot.register_next_step_handler(mesg, get_vadim_sum)
        else:
            bot.send_message(message.chat.id, '❌ Доступ запрещен !❌ ')

    elif (message.text == "🏁"):
        if message.from_user.username in users:
            flag = True

            bot.send_message(message.chat.id, 'Запускаю шарманку !')
            while flag:
                    time.sleep(1)
                    mail = connect_imap()
                    mail.select('inbox')
                    status, messages = mail.search(None, 'UNSEEN')
                    message_ids = messages[0].split()

                    body = ''

                    for id in message_ids:
                        status, msg_data = mail.fetch(id, '(RFC822)')
                        for response_part in msg_data:
                            if isinstance(response_part, tuple):
                                msg = email.message_from_bytes(response_part[1])
                                if msg.is_multipart():
                                    for payload in msg.get_payload():
                                        if payload.get_content_type() == 'text/plain':
                                            body = payload.get_payload(decode=True).decode('utf-8')
                                else:
                                    body = msg.get_payload(decode=True).decode('utf-8')

                    if 'В кошелёк пришли деньги' in body:
                        start_index = body.find('В кошелёк пришли деньги')
                        end_index = body.find('Все детали — в истории событий')

                        if start_index >= 0 and end_index >= 0:
                            result = body[start_index:end_index]
                            result = result.replace('В кошелёк пришли деньги','')
                            result = result.replace('Способ пополнения Сбербанк, пополнение','')
                            bot.send_message(message.chat.id, text=result)

                            came = re.findall(r"(?<=Пришло\s).*(?=\s₽)", result)
                            came = came[0]
                            came = came.replace(' ', '')
                            global come_amount
                            come_amount += int(came)

                            bot.send_message(message.chat.id, f"Сумма заявки:  {come_amount}/{vadim_sum}")

                            if come_amount >= vadim_sum:
                                bot.send_message(message.chat.id, '🤑 Финиш🏁')
                                come_amount = 0
                                break

                    elif 'Мы расторгаем с вами соглашение,' in body:
                        find_wall = body.rfind('кошелёк')
                        find_work = body.rfind('работает')
                        body = body[find_wall:find_work]
                        body = body.replace('больше не', 'заблокировали! Стоп!📛')
                        body = body.replace('кошелёк', '⚡️Кошелек')
                        bot.send_message(message.chat.id, body)
        else:
            bot.send_message(message.chat.id, '❌ Доступ запрещен !❌ ')

    elif (message.text == "⛔"):
        if message.from_user.username in users:
            bot.send_message(message.chat.id, text="Стопаю шарманку !")
            flag = False
            return flag
        else:
            bot.send_message(message.chat.id, '❌ Доступ запрещен !❌ ')

    if (message.text == "📧"):
        if message.from_user.username in users:

            conn = sqlite3.connect('emails.db')

            # Создание курсора
            cursor = conn.cursor()

            # Выполнение запроса
            cursor.execute("SELECT * FROM emails")

            # Получение результатов запроса
            rows = cursor.fetchall()

            # Закрытие курсора и соединения
            cursor.close()
            conn.close()

            output = ''

            for i in range(len(rows)):
                output += rows[i][1]
            output = output.replace(".ru", ".ru ")
            output = output.replace(" ","\n")
            mesg = bot.send_message(message.chat.id, output)
            bot.register_next_step_handler(mesg, get_password)
        else:
            bot.send_message(message.chat.id, '❌ Доступ запрещен !❌ ')


bot.polling(none_stop=True)
