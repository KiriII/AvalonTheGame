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
voted0 = []
voted1 = []
votes = [0,0]
mission_result = []
current_states = [States.NO_GAME]

def get_state():
    return current_states[0]

def set_state(state):
    current_states[0] = state

def generate_markup(a):
    markup = telebot.types.InlineKeyboardMarkup()
    if a == 1:
        i = 1
        for item in players:
            if item != boss[0] and item not in mission_composition:
                callback = "btn" + str(i)
                markup.add(telebot.types.InlineKeyboardButton(str(item), callback_data="btn" + str(item)))
            i += 1
    elif a == 2:
        if get_state() == States.VOTE_MISSION_СOMPOSITION:
            button1 = "Согласен("
            button2 = "Не согласен("
        elif get_state() == States.VOTE_MISSION_RESULT:
            button1 = "Успех!("
            button2 = "Провал...("
        markup.add(telebot.types.InlineKeyboardButton(button1 + str(votes[0]) + ")", callback_data="vote0"))
        markup.add(telebot.types.InlineKeyboardButton(button2 + str(votes[1]) + ")", callback_data="vote1"))
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
                                                             "/state для показа текущего состояния\n"
                                                             "/teamup для перехода от сбора команды к голосованию за согласие с этим составом миссии\n"
                                                             "/stopVote для окончания любого голосования и перехода к следующему этапу")

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
            bot.send_message(message.chat.id, "Босс @" + str(boss[0]) + " выбирай состав миссии", reply_markup=generate_markup(1))

@bot.message_handler(commands=['teamup'])
def get_text_messages(message):
    if get_state() == States.SET_MISSION_СOMPOSITION:
        if message.from_user.username == boss[0]:
            if len(mission_composition):
                bot.send_message(message.chat.id, "В составе команды никого нет!")
            else:
                set_state(States.VOTE_MISSION_СOMPOSITION)
                text = ""
                i = 1
                for j in mission_composition:
                    text += str(i) + ". @" + str(j) + "\n"
                    i += 1
                bot.send_message(message.chat.id, "Команда:\n" + text + "Согласны с составом команды?", reply_markup=generate_markup(2))

@bot.message_handler(commands=['stopVote'])
def get_text_messages(message):
    if get_state() == States.VOTE_MISSION_СOMPOSITION:
        if votes[0] > votes[1]:
            set_state(States.VOTE_MISSION_RESULT)
            votes[0] = 0
            votes[1] = 0
            text = ""
            i = 1
            for j in mission_composition:
                text += str(i) + ". @" + str(j) + "\n"
                i += 1
            bot.send_message(message.chat.id, "Команда:\n" + text + "Отправляется в приключение, где их ждёт...",
                             reply_markup=generate_markup(2))
        else:
            set_state(States.SET_MISSION_СOMPOSITION)
            mission_composition.clear()
            voted0.clear()
            voted1.clear()
            j = 0
            for i in players:
                if i in boss:
                    if j == len(players) - 1:
                        boss[0] = players[0]
                    else:
                        boss[0] = players[j+1]
                    votes[0] = 0
                    votes[1] = 0
                    bot.send_message(message.chat.id, "Босс меняется на следующего...")
                    bot.send_message(message.chat.id, "Босс @" + str(boss[0]) + " выбирай состав миссии",
                                     reply_markup=generate_markup(1))
                    return
                j += 1
    elif get_state() == States.VOTE_MISSION_RESULT:
        if votes[0] > votes[1]:
            votes[0] = 0
            votes[1] = 0
            bot.send_message(message.chat.id, "Миссия прошла успешно")
            mission_result.append("s")
        else:
            votes[0] = 0
            votes[1] = 0
            bot.send_message(message.chat.id, "Миссия провалена")
            mission_result.append("f")
        text = ""
        j = 1
        for i in mission_result:
            if "s" in i:
                text += "Миссия " + str(j) + " успешно пройденна!\n"
            if "f" in i:
                text += "Миссия " + str(j) + " провалена...\n"
            j += 1
        bot.send_message(message.chat.id, "Так так так...\n" + text)
        set_state(States.SET_MISSION_СOMPOSITION)
        mission_composition.clear()
        voted0.clear()
        voted1.clear()
        j = 0
        for i in players:
            if i in boss:
                if j == len(players) - 1:
                    boss[0] = players[0]
                else:
                    boss[0] = players[j + 1]
                votes[0] = 0
                votes[1] = 0
                bot.send_message(message.chat.id, "Босс меняется на следующего...")
                bot.send_message(message.chat.id, "Босс @" + str(boss[0]) + " выбирай состав миссии",
                                 reply_markup=generate_markup(1))
                return
            j += 1

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "/endGame":
        if get_state() != States.NO_GAME and message.from_user.username in players:
            players.clear()
            boss.clear()
            mission_composition.clear()
            set_state(States.NO_GAME)
            bot.send_message(message.chat.id, "Игра оконченна")


@bot.callback_query_handler(func=lambda message:'btn' in message.data)
def get_callback_btn(callback_query: telebot.types.CallbackQuery):
    if get_state() == States.SET_MISSION_СOMPOSITION:
        if callback_query.from_user.username == boss[0]:
            username = callback_query.data[3:]
            i = 1
            text = "Команда сейчас:\n"
            for j in mission_composition:
                text += str(i) + ". @" + str(j) + "\n"
                i += 1
            if len(mission_composition) == 0:
                text = "В команде никого нет!"
            if username not in mission_composition:
                bot.answer_callback_query(callback_query.id, str(username) + " добавлен к команде миссии\n" + text)
                mission_composition.append(username)
            elif username in mission_composition:
                mc = mission_composition
                mission_composition.clear()
                for i in mc:
                    if i not in username:
                        mission_composition.append(i)
                bot.answer_callback_query(callback_query.id, str(username) + " убран из состава миссии\n" + text)

@bot.callback_query_handler(func=lambda message:'vote' in message.data)
def get_callback_btn(callback_query: telebot.types.CallbackQuery):
    if get_state() == States.VOTE_MISSION_СOMPOSITION and callback_query.from_user.username in players or get_state() == States.VOTE_MISSION_RESULT and callback_query.from_user.username in mission_composition:
        vote = callback_query.data[4]
        if vote == '0':
            if callback_query.from_user.username in voted1 or callback_query.from_user.username not in voted0 and callback_query.from_user.username not in voted1:
                votes[0] = votes[0] + 1
                voted0.append(callback_query.from_user.username)
                if callback_query.from_user.username in voted1:
                    votes[1] = votes[1] - 1
                    voted1.remove(callback_query.from_user.username)
        elif vote == '1':
            if callback_query.from_user.username in voted0 or callback_query.from_user.username not in voted0 and callback_query.from_user.username not in voted1:
                votes[1] = votes[1] + 1
                voted1.append(callback_query.from_user.username)
                if callback_query.from_user.username in voted0:
                    votes[0] = votes[0] - 1
                    voted0.remove(callback_query.from_user.username)
        bot.edit_message_reply_markup(callback_query.message.chat.id, callback_query.message.message_id, reply_markup=generate_markup(2))

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
