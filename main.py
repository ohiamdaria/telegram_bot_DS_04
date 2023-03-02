import telebot
import sqlite3
from googleapiclient.discovery import build
import os.path

bot = telebot.TeleBot("meow")
api_key = 'meow'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "users.db")


@bot.message_handler(commands=['start'])
def start(message):
    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS login_id( id INTEGER,
                                                            channel TEXT);""")

    connect.commit()

    # # check id in fields
    person_id = message.chat.id
    cursor.execute(f"SELECT id FROM login_id WHERE id = {person_id}")
    is_exists = cursor.fetchone()
    if is_exists is None:
        user_id = [message.chat.id]
        # cursor.execute("INSERT INTO login_id VALUES(?);", user_id, 'no one') # insert into if exists
        connect.commit()
    else:
        bot.send_message(message.chat.id, 'The user is exist!')
    connect.close()
    pass


@bot.message_handler(commands=['delete'])
def delete(message):
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()

    user_id = message.chat.id
    cursor.execute(f"DELETE FROM login_id WHERE id = {user_id}")
    connect.commit()

#
# @bot.message_handler(content_types=['text'])
# def get_text(message):
#     if message.text.lower() == 'hi':
#         bot.send_message(message.chat.id, 'hi')


@bot.message_handler(commands=['statistics_channel'])
def get_channel_statistic(message):
    bot.send_message(message.chat.id, "Write your channel name: ")
    bot.register_next_step_handler(message, get_channel_name)


def get_channel_name(message):
    youtube = build('youtube', 'v3', developerKey=api_key)
    mes = message.text
    channel_id = mes.split('/')[4]
    request = youtube.channels().list(
        id=channel_id,
        part='snippet,statistics'
    )
    response = request.execute()
    title = response['items'][0]['snippet']['title']
    description = response['items'][0]['snippet']['description']
    view_count = response['items'][0]['statistics']['viewCount']
    subscriber_count = response['items'][0]['statistics']['subscriberCount']
    user_id = message.chat.id
    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()
    cursor.execute("INSERT INTO login_id VALUES(?, ?);", (user_id, title))
    connect.commit()
    bot.send_message(message.chat.id, f'Statistic for channel:{title}\n'
                                      f'Description:\n{description}\n'
                                      f'ViewCount:{view_count}\n'
                                  f'subscriberCount:{subscriber_count}\n')
    pass
#     bot.send_message(message.chat.id, "Do u want to save statistic?")
#     bot.register_next_step_handler(message, response, save_statistic)
#
#
# def save_statistic(message, response):
#     if message == 'yes':
#         connect = sqlite3.connect(db_path)
#         cursor = connect.cursor()
#         # add values in fields
#         user_id = message.chat.id
#         channel = response['items'][0]['snippet']['title']
#         cursor.execute("INSERT INTO login_id VALUES(?, ?);", (user_id, channel))
#     pass


@bot.message_handler(commands=['statistics_video'])
def get_video_statistic(message):
    bot.send_message(message.chat.id, "Write your video name: ")
    bot.register_next_step_handler(message, get_video_name)

# https://www.youtube.com/watch?v=dICHLVry8Bw
def get_video_name(message):
    mes = message.text
    video_id = mes.split('/')[4]
    youtube = build('youtube', 'v3', developerKey=api_key)
    request = youtube.videos().list(
        id=video_id,
        part='snippet,statistics'
    )
    response = request.execute()
    title = response['items'][0]['snippet']['title']
    description = response['items'][0]['snippet']['description']
    viewCount = response['items'][0]['statistics']['viewCount']
    subscriberCount = response['items'][0]['statistics']['subscriberCount']
    bot.send_message(message.chat.id, f'Statistic for channel:{title}\n'
                                      f'Description:\n{description}\n')
    pass


bot.polling(none_stop=True, interval=0)
