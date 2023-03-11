import telebot
from telebot import types
import imaplib
import email
import base64
from kekes import key_1
import time
import re
import sqlite3

bot = telebot.TeleBot(key_1)
global come_amount
come_amount = 0

global mail_log
global pass_email

def connect_imap():
    mail_pass = pass_email
    username = mail_log
    imap_server = "imap.mail.ru"
    imap = imaplib.IMAP4_SSL(imap_server)
    imap.login(username, mail_pass)
    imap.select('inbox')
    return imap

def get_conn():
    return sqlite3.connect('emails.db', check_same_thread=False)

@bot.message_handler(commands=['use'])
def get_password(message):
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

def get_vadim_sum(msg):
        bot.send_message(msg.chat.id, f"Сумма заявки:  {msg.text}")
        global vadim_sum
        vadim_sum = int(msg.text)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("💰")
    btn2 = types.KeyboardButton("🏁")
    btn3 = types.KeyboardButton("⛔")
    btn4 = types.KeyboardButton("📧")
    markup.add(btn1, btn2, btn3,btn4)
    bot.send_message(message.chat.id,
                     text="Салам, {0.first_name}! Выбери команду".format(
                         message.from_user), reply_markup=markup)


@bot.message_handler(content_types=['text'])
def func(message):
    global flag
    flag = False
    if (message.text == "💰"):
        mesg = bot.send_message(message.chat.id, 'Введи сумму заявки без пробелов и символов')
        bot.register_next_step_handler(mesg, get_vadim_sum)


    elif (message.text == "🏁"):
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

    elif (message.text == "⛔"):
        bot.send_message(message.chat.id, text="Стопаю шарманку !")
        flag = False
        return flag

    if (message.text == "📧"):
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



bot.polling(none_stop=True)
