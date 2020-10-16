import random
from enum import Enum
import telebot
import random
import os
import logging
from flask import Flask, request


class States(Enum):
    NO_GAME = "0"
    FIND_PLAYERS = "1"
    SET_MISSION_СOMPOSITION = "2"
    VOTE_MISSION_СOMPOSITION = "3"
    VOTE_MISSION_RESULT = "4"

WEBHOOK_HOST = 'https://avalon-bot-trpo.herokuapp.com/'
WEBHOOK_PORT = 33500  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr
bot = telebot.TeleBot('1285966353:AAEIQ7RYIqx9rcV0Fm6om5RZeRSKy70Xpgc')
players = []
boss = []
mission_composition = []
current_states = [States.NO_GAME]

def get_state():
    return current_states[0]

def set_state(state):
    current_states[0] = state

def generate_markup():
    """
    Создаем кастомную клавиатуру для выбора ответа
    :param right_answer: Правильный ответ
    :param wrong_answers: Набор неправильных ответов
    :return: Объект кастомной клавиатуры
    """
    markup = telebot.types.InlineKeyboardMarkup()
    #markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    # Создаем лист (массив) и записываем в него все элементыpip list
    # Заполняем разметку перемешанными элементами
    i = 1
    for item in players:
        if item != boss[0] and item not in mission_composition:
            callback = "btn" + str(i)
            markup.add(telebot.types.InlineKeyboardButton(str(item), callback_data="btn" + str(item)))
        i += 1
    return markup

@bot.message_handler(commands=['players'])
def get_text_messages(message):
    if get_state() != States.NO_GAME:
        text = ""
        i = 1
        if len(players) != 0:
            for j in players:
                text += str(i) + ". @" + str(j) + "\n"
                i += 1
            bot.send_message(message.chat.id, text)
    elif get_state() == States.NO_GAME:
        bot.send_message(message.chat.id, "Игра не начата")

@bot.message_handler(commands=['state'])
def get_text_messages(message):
    bot.send_message(message.chat.id, "state " + str(get_state().name))

@bot.message_handler(commands=['team'])
def get_text_messages(message):
    if get_state() == States.SET_MISSION_СOMPOSITION:
        text = ""
        i = 1
        if len(mission_composition) != 0:
            for j in mission_composition:
                text += str(i) + ". @" + str(j) + "\n"
                i += 1
        else:
            text = "Пустая команда для миссии"
        bot.send_message(message.chat.id, text)
    elif get_state() == States.NO_GAME:
        bot.send_message(message.chat.id, "Игра не начата")

@bot.message_handler(commands=['help'])
def get_text_messages(message):
    if message.text == "/help":
        bot.send_message(message.chat.id, text="Команды:\n"
                                                             "/create для начала сбора игроков\n"
                                                             "/join для вступления в группу игроков\n"
                                                             "/startGame для начала игры\n"
                                                             "/players для показа игрков в игре\n"
                                                             "/team для показа текущей команды для миссии\n"
                                                             "/state для показа текущего состояния")

@bot.message_handler(commands=['create'])
def get_text_messages(message):
    if message.chat.id == 446193106:
        bot.send_message(message.chat.id, 'Используй эту команду в групповом чате')
    elif get_state() == States.NO_GAME:
        bot.send_message(message.chat.id, 'Начат сбор игроков')
        set_state(States.FIND_PLAYERS)
        players.append(message.from_user.username)

@bot.message_handler(commands=['join'])
def get_text_messages(message):
    if message.chat.id != 446193106 and get_state() == States.FIND_PLAYERS:
        if message.from_user.username not in players:
            players.append(message.from_user.username)
            bot.send_message(message.chat.id, 'Игрок ' + str(message.from_user.username) + ' добавлен к игре')

@bot.message_handler(commands=['startGame'])
def get_text_messages(message):
    if message.chat.id != 446193106 and get_state() == States.FIND_PLAYERS:
        if message.from_user.username == players[0]:
            text = ""
            i = 1
            for j in players:
                text += str(i) + ". @" + str(j) + "\n"
                i += 1
            bot.send_message(message.chat.id, text)
            set_state(States.SET_MISSION_СOMPOSITION)
            boss.append(random.choice(players))
            bot.send_message(message.chat.id, "Босс @" + str(boss[0]) + " выбирай состав миссии", reply_markup=generate_markup())

@bot.callback_query_handler(func=lambda message:message.data)
def get_callback_btn(callback_query: telebot.types.CallbackQuery):
    if get_state() == States.SET_MISSION_СOMPOSITION :
        if callback_query.from_user.username == boss[0] :
            username = callback_query.data[3:]
            bot.answer_callback_query(callback_query.id, str(username) + " добавлен к команде миссии")
            mission_composition.append(username)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "/endGame":
        if get_state() != States.NO_GAME and message.from_user.username in players:
            players.clear()
            boss.clear()
            mission_composition.clear()
            set_state(States.NO_GAME)
            bot.send_message(message.chat.id, "Игра оконченна")


if __name__ == '__main__':
    if "HEROKU" in list(os.environ.keys()):
        logger = telebot.logger
        telebot.logger.setLevel(logging.INFO)

        server = Flask(__name__)


        @server.route("/bot", methods=['POST'])
        def getMessage():
            bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
            print("getMessage")
            return "!", 200


        @server.route("/")
        def webhook():
            bot.remove_webhook()
            bot.set_webhook(
                url=WEBHOOK_HOST)  # этот url нужно заменить на url вашего Хероку приложения
            return "?", 200


        server.run(host=WEBHOOK_LISTEN, port=os.environ.get('PORT', 80))
    else:
        # если переменной окружения HEROKU нету, значит это запуск с машины разработчика.
        # Удаляем вебхук на всякий случай, и запускаем с обычным поллингом.
        bot.remove_webhook()
        bot.polling(none_stop=True)
#bot.polling(none_stop=True, interval=0)
