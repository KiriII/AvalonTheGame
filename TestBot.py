import random
from enum import Enum
import telebot
import random
import time
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
votes = []
mission_result = []
current_states = []
chats = []

def get_state(chat_id):
    if chat_id in chats:
        return current_states[chats.index(chat_id)][0]
    else:
        return False

def set_state(state, chat_id):
    if chat_id in chats:
        current_states[chats.index(chat_id)][0] = state

def generate_markup(a, chat_id):
    if chat_id in chats:
        markup = telebot.types.InlineKeyboardMarkup()
        if a == 1:
            i = 1
            for item in players[chats.index(chat_id)]:
                if item != boss[chats.index(chat_id)][0]:
                    markup.add(telebot.types.InlineKeyboardButton(str(item), callback_data="btn " + str(chat_id) + " " + str(item)))
                i += 1
        elif a == 2:
            button1 = ""
            button2 = ""
            if get_state(chat_id) == States.VOTE_MISSION_СOMPOSITION:
                button1 = "Согласен"
                button2 = "Не согласен"
            elif get_state(chat_id) == States.VOTE_MISSION_RESULT:
                button1 = "Успех!"
                button2 = "Провал..."
            markup.add(telebot.types.InlineKeyboardButton(button1, callback_data="vote0 " + str(chat_id)))
            markup.add(telebot.types.InlineKeyboardButton(button2, callback_data="vote1 " + str(chat_id)))
        return markup

def timer_message(message, text, markup):
    k = 0
    while k < 3:
        if k == 0:
            message1 = bot.send_message(message.chat.id, text, reply_markup=markup)
        else:
            bot.delete_message(message.chat.id, message1.message_id)
            message1 = bot.send_message(message.chat.id, text, reply_markup=markup)
        time.sleep(10)
        k = k + 1

def get_list(elem_list, start_text):
    text = start_text
    i = 1
    if len(elem_list) != 0:
        for j in elem_list:
            text += str(i) + ". @" + str(j) + "\n"
            i += 1
    return text

def boss_vote(message, first_vote):
    if message.chat.id in chats:
        chat_id = chats.index(message.chat.id)
        if first_vote:
            bot.send_message(message.chat.id, get_list(players[chat_id], "В игре учавствуют: \n"))
        set_state(States.SET_MISSION_СOMPOSITION, message.chat.id)
        boss[chat_id].append(players[chat_id][0])
        timer_message(message, "Босс @" + str(boss[chat_id][0]) + " выбирай состав миссии",
                      generate_markup(1, message.chat.id))
        # ПРОВЕРКА НА КОЛИЧЕСТВО ЧЕЛОВЕК В КОМАНДЕ
        if len(mission_composition[chat_id]) < len(players[chat_id]) / 2:
            k = len(mission_composition[chat_id])
            while k < len(players[chat_id]) / 2:
                random_player = random.choice(players[chat_id])
                if (len(mission_composition[chat_id]) == 0 or random_player not in mission_composition[chat_id]) \
                        and random_player != boss[chat_id][0]:
                    mission_composition[chat_id].append(random_player)
                    k += 1
        if len(mission_composition[chat_id]) == 0:
            bot.send_message(message.chat.id, "В составе команды никого нет!")
        else:
            set_state(States.VOTE_MISSION_СOMPOSITION, message.chat.id)
            timer_message(message, "Команда:\n" + get_list(mission_composition[chat_id], "") +
                          "Согласны с составом команды?", generate_markup(2, message.chat.id))


def init_chat(chat_id):
    if chat_id not in chats:
        print("Chat init " + str(chat_id))
        chats.append(chat_id)
        players.append([])
        boss.append([])
        mission_composition.append([])
        voted0.append([])
        voted1.append([])
        votes.append([0, 0])
        mission_result.append([])
        current_states.append([States.NO_GAME])

@bot.message_handler(commands=['players'])
def get_text_messages(message):
    init_chat(message.chat.id)
    if message.chat.id in chats:
        chat_id = message.chat.id
        if get_state(chat_id) != States.NO_GAME:
                bot.send_message(message.chat.id, get_list(players[chats.index(message.chat.id)], ""))
        elif get_state(chat_id) == States.NO_GAME:
            bot.send_message(message.chat.id, "Игра не начата")

@bot.message_handler(commands=['state'])
def get_text_messages(message):
    init_chat(message.chat.id)
    if message.chat.id in chats:
        print(str(get_state(message.chat.id)))
        bot.send_message(message.chat.id, "state " + str(get_state(message.chat.id).name))

@bot.message_handler(commands=['team'])
def get_text_messages(message):
    init_chat(message.chat.id)
    if message.chat.id in chats:
        chat_id = chats.index(message.chat.id)
        if get_state(chat_id) == States.SET_MISSION_СOMPOSITION:
            if len(mission_composition[chat_id][1]) != 0:
                text = get_list(mission_composition[chat_id], "")
            else:
                text = "Пустая команда для миссии"
            bot.send_message(message.chat.id, text)
        elif get_state(chat_id) == States.NO_GAME:
            bot.send_message(message.chat.id, "Игра не начата")

@bot.message_handler(commands=['help'])
def get_text_messages(message):
    init_chat(message.chat.id)
    if message.text == "/help":
        bot.send_message(message.chat.id, text="Команды:\n"
                                                             "/create для начала сбора игроков\n"
                                                             "/join для вступления в группу игроков\n"
                                                             "/startGame для начала игры\n"
                                                             "/players для показа игрков в игре - debug\n"
                                                             "/state для показа текущего состояния - debug\n"
                                                             "/team для показа текущей команды - debug\n"
                                                             "/stopVote для окончания любого голосования и перехода к следующему этапу - ??")

@bot.message_handler(commands=['create'])
def get_text_messages(message):
    chat_id = message.chat.id
    init_chat(chat_id)
    if message.chat.id == 446193106:
        bot.send_message(chat_id, 'Используй эту команду в групповом чате')
    elif get_state(chat_id) == States.NO_GAME:
        bot.send_message(chat_id, 'Начат сбор игроков')
        set_state(States.FIND_PLAYERS, message.chat.id)
        print(str(players[chats.index(chat_id)]))
        players[chats.index(chat_id)].append(message.from_user.username)


@bot.message_handler(commands=['join'])
def get_text_messages(message):
    init_chat(message.chat.id)
    if message.chat.id in chats:
        chat_id = chats.index(message.chat.id)
        print(str(players[chat_id]))
        if chat_id != 446193106 and get_state(message.chat.id) == States.FIND_PLAYERS:
            if message.from_user.username not in players[chat_id]:
                players[chat_id].append(message.from_user.username)
                bot.send_message(message.chat.id, 'Игрок ' + str(message.from_user.username) + ' добавлен к игре')

@bot.message_handler(commands=['startGame'])
def get_text_messages(message):
    init_chat(message.chat.id)
    if message.chat.id in chats:
        chat_id = chats.index(message.chat.id)
        if chat_id != 446193106 and get_state(message.chat.id) == States.FIND_PLAYERS:
            if message.from_user.username == players[chat_id][0]:
                boss_vote(message, True)


@bot.message_handler(commands=['stopVote'])
def get_text_messages(message):
    if message.chat.id in chats:
        chat_id = chats.index(message.chat.id)
        if get_state(message.chat.id) == States.VOTE_MISSION_СOMPOSITION:
            set_state(States.VOTE_MISSION_RESULT, message.chat.id)
            if votes[chat_id][0] > votes[chat_id][1]:
                votes[chat_id][0] = 0
                votes[chat_id][1] = 0
                timer_message(message, "Команда:\n" + get_list(mission_composition[chat_id], "") +
                              "Отправляется в приключение, где их ждёт...", generate_markup(2, message.chat.id))
            else:
                votes[chat_id][0] = 0
                votes[chat_id][1] = 0
                mission_composition[chat_id].clear()
                voted0[chat_id].clear()
                voted1[chat_id].clear()
                j = 0
                for i in players[chat_id]:
                    if i in boss[chat_id]:
                        if j == len(players[chat_id]) - 1:
                            boss[chat_id][0] = players[chat_id][0]
                        else:
                            boss[chat_id][0] = players[chat_id][j+1]
                        votes[chat_id][0] = 0
                        votes[chat_id][1] = 0
                        bot.send_message(message.chat.id, "Босс меняется на следующего...")
                        boss_vote(message, False)
                        return
                    j += 1
        elif get_state(message.chat.id) == States.VOTE_MISSION_RESULT:
            if votes[chat_id][0] > votes[chat_id][1]:
                votes[chat_id][0] = 0
                votes[chat_id][1] = 0
                bot.send_message(message.chat.id, "Миссия прошла успешно")
                mission_result[chat_id].append("s")
            else:
                votes[chat_id][0] = 0
                votes[chat_id][1] = 0
                bot.send_message(message.chat.id, "Миссия провалена")
                mission_result[chat_id].append("f")
            text = ""
            j = 1
            for i in mission_result[chat_id]:
                if "s" in i:
                    text += "Миссия " + str(j) + " успешно пройденна!\n"
                if "f" in i:
                    text += "Миссия " + str(j) + " провалена...\n"
                j += 1
            bot.send_message(message.chat.id, "Так так так...\n" + text)
            set_state(States.SET_MISSION_СOMPOSITION, message.chat.id)
            mission_composition[chat_id].clear()
            voted0[chat_id].clear()
            voted1[chat_id].clear()
            j = 0
            for i in players[chat_id]:
                if i in boss[chat_id]:
                    if j == len(players[chat_id]) - 1:
                        boss[chat_id][0] = players[chat_id][0]
                    else:
                        boss[chat_id][0] = players[chat_id][j + 1]
                    votes[chat_id][0] = 0
                    votes[chat_id][1] = 0
                    bot.send_message(message.chat.id, "Босс меняется на следующего...")
                    boss_vote(message, False)
                j += 1

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    init_chat(message.chat.id)
    if message.chat.id in chats:
        chat_id = chats.index(message.chat.id)
        if message.text == "/endGame":
            if get_state(message.chat.id) != States.NO_GAME and message.from_user.username in players[chat_id]:
                players[chat_id].clear()
                boss[chat_id].clear()
                mission_composition[chat_id].clear()
                voted0[chat_id].clear()
                voted1[chat_id].clear()
                votes[chat_id] = [0, 0]
                mission_result[chat_id].clear()
                current_states[chat_id] = [States.NO_GAME]



@bot.callback_query_handler(func=lambda message:'btn' in message.data)
def get_callback_btn(callback_query: telebot.types.CallbackQuery):
    message_split = callback_query.data.split()
    chat_id = int(message_split[1])
    #print(str(chats) + " " + str(message_split[1]) + " " + str(int(message_split[1]) in chats) + " " + str(get_state(chat_id)) + " " + str(boss[chats.index(chat_id)][0]))
    username = message_split[2]
    if get_state(chat_id) == States.SET_MISSION_СOMPOSITION:
        if callback_query.from_user.username == boss[chats.index(chat_id)][0]:
            i = 1
            text = "Команда сейчас:\n"
            if username not in mission_composition[chats.index(chat_id)]:
                mission_composition[chats.index(chat_id)].append(username)
                for j in mission_composition[chats.index(chat_id)]:
                    text += str(i) + ". @" + str(j) + "\n"
                    i += 1
                if len(mission_composition[chats.index(chat_id)]) == 0:
                    text += "В команде никого нет!"
                bot.answer_callback_query(callback_query.id, str(username) + " добавлен к команде миссии\n" + text)
            elif username in mission_composition[chats.index(chat_id)]:
                mc = mission_composition[chats.index(chat_id)]
                mission_composition[chats.index(chat_id)].clear()
                for i in mc:
                    if i not in username:
                        mission_composition[chats.index(chat_id)].append(i)
                for j in mission_composition[chats.index(chat_id)]:
                    text += str(i) + ". @" + str(j) + "\n"
                    i += 1
                if len(mission_composition[chats.index(chat_id)]) == 0:
                    text += "В команде никого нет!"
                bot.answer_callback_query(callback_query.id, str(username) + " убран из состава миссии\n" + text)

@bot.callback_query_handler(func=lambda message:'vote' in message.data)
def get_callback_btn(callback_query: telebot.types.CallbackQuery):
    chat_id = int(callback_query.data.split()[1])
    if get_state(chat_id) == States.VOTE_MISSION_СOMPOSITION and callback_query.from_user.username in \
            players[chats.index(chat_id)] or get_state(chat_id) == States.VOTE_MISSION_RESULT and \
            callback_query.from_user.username in mission_composition[chats.index(chat_id)]:
        vote = callback_query.data[4]
        if vote == '0':
            if callback_query.from_user.username in voted1[chats.index(chat_id)] or callback_query.from_user.username not in\
                    voted0[chats.index(chat_id)] and callback_query.from_user.username not in voted1[chats.index(chat_id)]:
                votes[chats.index(chat_id)][0] = votes[chats.index(chat_id)][0] + 1
                voted0[chats.index(chat_id)].append(callback_query.from_user.username)
                if callback_query.from_user.username in voted1[chats.index(chat_id)]:
                    votes[chats.index(chat_id)][1] = votes[chats.index(chat_id)][1] - 1
                    voted1[chats.index(chat_id)].remove(callback_query.from_user.username)
        elif vote == '1':
            if callback_query.from_user.username in voted0[chats.index(chat_id)] or callback_query.from_user.username not in\
                    voted0[chats.index(chat_id)] and callback_query.from_user.username not in voted1[chats.index(chat_id)]:
                votes[chats.index(chat_id)][1] = votes[chats.index(chat_id)][1] + 1
                voted1[chats.index(chat_id)].append(callback_query.from_user.username)
                if callback_query.from_user.username in voted0[chats.index(chat_id)]:
                    votes[chats.index(chat_id)][0] = votes[chats.index(chat_id)][0] - 1
                    voted0[chats.index(chat_id)].remove(callback_query.from_user.username)
        print("Golosa za: " + str(votes[chats.index(chat_id)][0]) + " protiv: " + str(votes[chats.index(chat_id)][1]) + " state: " +
              str(get_state(chat_id)))

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
