import telebot
import os
import logging
import random
import time

from random import sample
from flask import Flask, request
from enum import Enum

class States(Enum):
    NO_GAME = "0"
    FIND_PLAYERS = "1"
    SET_MISSION_СOMPOSITION = "2"
    VOTE_MISSION_СOMPOSITION = "3"
    VOTE_MISSION_RESULT = "4"

SERVER = 'https://avalon-backer.herokuapp.com/'
SERVER_PORT = 65432
WEBHOOK_HOST = 'https://avalon-bot-trpo.herokuapp.com/'
WEBHOOK_PORT = 33500  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr
bot = telebot.TeleBot('1285966353:AAEIQ7RYIqx9rcV0Fm6om5RZeRSKy70Xpgc')
players = []
virtuous_team = []
evil_team = []
boss = []
list_full = []
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

def set_evil_team(chat_id):
    for i in players[chat_id]:
        if i not in virtuous_team[chat_id]:
            evil_team[chat_id].append(i)

def get_mission_len(chat_id):
    if len(players[chat_id]) == 5:
        print()
        if len(mission_result[chat_id]) == 0:
            return 2
        if len(mission_result[chat_id]) == 1:
            return 3
        if len(mission_result[chat_id]) == 2:
            return 2
        if len(mission_result[chat_id]) == 3:
            return 3
        if len(mission_result[chat_id]) == 4:
            return 3
    if len(players[chat_id]) == 6:
        if len(mission_result[chat_id]) == 0:
            return 2
        if len(mission_result[chat_id]) == 1:
            return 3
        if len(mission_result[chat_id]) == 2:
            return 4
        if len(mission_result[chat_id]) == 3:
            return 3
        if len(mission_result[chat_id]) == 4:
            return 4
    if len(players[chat_id]) == 7:
        if len(mission_result[chat_id]) == 0:
            return 2
        if len(mission_result[chat_id]) == 1:
            return 3
        if len(mission_result[chat_id]) == 2:
            return 3
        if len(mission_result[chat_id]) == 3:
            return 4
        if len(mission_result[chat_id]) == 4:
            return 4
    if len(players[chat_id]) == 8:
        if len(mission_result[chat_id]) == 0:
            return 3
        if len(mission_result[chat_id]) == 1:
            return 4
        if len(mission_result[chat_id]) == 2:
            return 4
        if len(mission_result[chat_id]) == 3:
            return 5
        if len(mission_result[chat_id]) == 4:
            return 5
    if len(players[chat_id]) == 9:
        if len(mission_result[chat_id]) == 0:
            return 3
        if len(mission_result[chat_id]) == 1:
            return 4
        if len(mission_result[chat_id]) == 2:
            return 4
        if len(mission_result[chat_id]) == 3:
            return 5
        if len(mission_result[chat_id]) == 4:
            return 5
    if len(players[chat_id]) == 10:
        if len(mission_result[chat_id]) == 0:
            return 3
        if len(mission_result[chat_id]) == 1:
            return 4
        if len(mission_result[chat_id]) == 2:
            return 3
        if len(mission_result[chat_id]) == 3:
            return 5
        if len(mission_result[chat_id]) == 4:
            return 5

def bot_vote(chat_id):
    if chat_id in chats:
        if get_state(chat_id) == States.SET_MISSION_СOMPOSITION:
            if "bot" in boss[chats.index(chat_id)][0]:
                not_boss = []
                for item in players[chats.index(chat_id)]:
                    if item != boss[chats.index(chat_id)][0]:
                        not_boss.append(item)
                mission_composition[chats.index(chat_id)] = sample(not_boss, get_mission_len(chats.index(chat_id)))
                check_full(chat_id)
                time.sleep(2)
        elif get_state(chat_id) == States.VOTE_MISSION_СOMPOSITION:
            for i in players[chats.index(chat_id)]:
                if "bot" in i and i not in voted0[chats.index(chat_id)] and i not in voted1[chats.index(chat_id)]:
                    print(i + " voted ")
                    if random.choice([True, False]):
                        votes[chats.index(chat_id)][0] = votes[chats.index(chat_id)][0] + 1
                        voted0[chats.index(chat_id)].append(i)
                    else:
                        votes[chats.index(chat_id)][1] = votes[chats.index(chat_id)][1] + 1
                        voted1[chats.index(chat_id)].append(i)
                    time.sleep(2)
                    check_full(chat_id)
        elif get_state(chat_id) == States.VOTE_MISSION_RESULT:
            for i in mission_composition[chats.index(chat_id)]:
                if "bot" in i and i not in voted0[chats.index(chat_id)] and i not in voted1[chats.index(chat_id)]:
                    if random.choice([True, False]):
                        votes[chats.index(chat_id)][0] = votes[chats.index(chat_id)][0] + 1
                        voted0[chats.index(chat_id)].append(i)
                    else:
                        votes[chats.index(chat_id)][1] = votes[chats.index(chat_id)][1] + 1
                        voted1[chats.index(chat_id)].append(i)
                    check_full(chat_id)
                    time.sleep(2)

def know_team_button(chat_id):
    if chat_id in chats:
        print(str(chat_id) + str(chats))
        markup = telebot.types.InlineKeyboardMarkup()
        text = "Узнать команду"
        markup.add(telebot.types.InlineKeyboardButton(text, callback_data="know " + str(chat_id)))
        return markup

def generate_markup(a, chat_id):
    if chat_id in chats:
        markup = telebot.types.InlineKeyboardMarkup()
        if a == 1:
            i = 1
            for item in players[chats.index(chat_id)]:
                markup.add(telebot.types.InlineKeyboardButton(str(item), callback_data="btn " + str(chat_id) + " " + str(item)))
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

def check_full(chat_id):
    if chat_id in chats:
        chat_ind = chats.index(chat_id)
        print(str(voted1[chats.index(chat_id)]) + str(voted0[chats.index(chat_id)]) + str(players))
        if get_state(chat_id) == States.SET_MISSION_СOMPOSITION and len(mission_composition[chat_ind]) == get_mission_len(chats.index(chat_id)):
            if len(mission_composition[chat_ind]) == 0:
                bot.send_message(chat_id, "В составе команды никого нет!")
            else:
                set_state(States.VOTE_MISSION_СOMPOSITION, chat_id)
                bot.send_message(chat_id, "Команда:\n" + get_list(mission_composition[chat_ind], "") +
                                 "Согласны с составом команды?", reply_markup=generate_markup(2, chat_id))
                bot_vote(chat_id)
        elif get_state(chat_id) == States.VOTE_MISSION_СOMPOSITION and len(voted1[chats.index(chat_id)]) + len(voted0[chats.index(chat_id)]) == len(players[chats.index(chat_id)]):
            print("VOTE MISSION COMPOSITION " + str(voted0[chat_ind]) + str(voted1[chat_ind]) + str(len(voted1[chats.index(chat_id)]) + len(voted0[chats.index(chat_id)])) + str(len(players[chats.index(chat_id)])))
            if votes[chat_ind][0] > votes[chat_ind][1]:
                set_state(States.VOTE_MISSION_RESULT, chat_id)
                votes[chat_ind][0] = 0
                votes[chat_ind][1] = 0
                voted0[chat_ind].clear()
                voted1[chat_ind].clear()
                bot.send_message(chat_id, "Команда:\n" + get_list(mission_composition[chat_ind], "") +
                                 "Отправляется в приключение, где их ждёт...",
                                 reply_markup=generate_markup(2, chat_id))
                bot_vote(chat_id)
            else:
                votes[chat_ind][0] = 0
                votes[chat_ind][1] = 0
                mission_composition[chat_ind].clear()
                voted0[chat_ind].clear()
                voted1[chat_ind].clear()
                j = 0
                for i in players[chat_ind]:
                    if i in boss[chat_ind]:
                        if j == len(players[chat_ind]) - 1:
                            boss[chat_ind][0] = players[chat_ind][0]
                        else:
                            boss[chat_ind][0] = players[chat_ind][j + 1]
                        votes[chat_ind][0] = 0
                        votes[chat_ind][1] = 0
                        bot.send_message(chat_id, "Босс меняется на следующего...")
                        boss_vote(chats[chats.index(chat_id)], False)
                        return
                    j += 1
        elif get_state(chat_id) == States.VOTE_MISSION_RESULT and len(voted1[chats.index(chat_id)]) + len(voted0[chats.index(chat_id)]) == len(mission_composition[chats.index(chat_id)]):
            print("VOTE MISSION RESULT " + str(voted0[chat_ind]) + str(voted1[chat_ind]) + str(len(voted1[chats.index(chat_id)]) + len(voted0[chats.index(chat_id)])) + str(len(players[chats.index(chat_id)])))
            if votes[chat_ind][0] > votes[chat_ind][1]:
                votes[chat_ind][0] = 0
                votes[chat_ind][1] = 0
                bot.send_message(chat_id, "Миссия прошла успешно")
                mission_result[chat_ind].append("s")
            else:
                votes[chat_ind][0] = 0
                votes[chat_ind][1] = 0
                bot.send_message(chat_id, "Миссия провалена")
                mission_result[chat_ind].append("f")
            text = ""
            j = 1
            s = 0
            f = 0
            for i in mission_result[chat_ind]:
                if "s" in i:
                    s = s + 1
                    text += "Миссия " + str(j) + " успешно пройденна!\n"
                if "f" in i:
                    f = f + 1
                    text += "Миссия " + str(j) + " провалена...\n"
                j += 1
            bot.send_message(chat_id, "Так так так...\n" + text)
            if len(mission_result[chat_ind]) > 3:
                if s == 3:
                    bot.send_message(chat_id, "#Победа сил света\n")
                elif f == 3:
                    bot.send_message(chat_id, "#Победа сил тьмы\n")
            if s == 3 or f == 3:
                players[chat_ind].clear()
                boss[chat_ind].clear()
                mission_composition[chat_ind].clear()
                voted0[chat_ind].clear()
                voted1[chat_ind].clear()
                votes[chat_ind] = [0, 0]
                mission_result[chat_ind].clear()
                current_states[chat_ind] = [States.NO_GAME]
                virtuous_team[chat_ind].clear()
                evil_team[chat_ind].clear()
            else:
                set_state(States.SET_MISSION_СOMPOSITION, chat_id)
                mission_composition[chat_ind].clear()
                voted0[chat_ind].clear()
                voted1[chat_ind].clear()
                votes[chat_ind][0] = 0
                votes[chat_ind][1] = 0
                j = 0
                for i in players[chat_ind]:
                    if i in boss[chat_ind]:
                        if j == len(players[chat_ind]) - 1:
                            boss[chat_ind][0] = players[chat_ind][0]
                            break
                        else:
                            boss[chat_ind][0] = players[chat_ind][j + 1]
                            break
                    j += 1
                bot.send_message(chat_id, "Босс меняется на следующего...")
                set_state(States.VOTE_MISSION_СOMPOSITION, chat_id)
                boss_vote(chats[chats.index(chat_id)], False)



#def timer_message(message, text, markup):
#    k = 0
#    while k < 3:
#        if k == 0:
#            message1 = bot.send_message(message.chat.id, text, reply_markup=markup)
#        else:
#            bot.delete_message(message.chat.id, message1.message_id)
#            message1 = bot.send_message(message.chat.id, text, reply_markup=markup)
#        time.sleep(10)
#        k = k + 1

def get_list(elem_list, start_text):
    text = start_text
    i = 1
    if len(elem_list) != 0:
        for j in elem_list:
            text += str(i) + ". @" + str(j) + "\n"
            i += 1
    return text

def boss_vote(chat_id, first_vote):
    #print(str(chats))
    print(str(boss))
    if chat_id in chats:
        #chat_id = chats.index(chat_id)
        mission_composition[chats.index(chat_id)].clear()
        if first_vote:
            bot.send_message(chat_id, get_list(players[chats.index(chat_id)], "В игре учавствуют: \n"), reply_markup= know_team_button(chat_id))
            boss[chats.index(chat_id)].append(players[chats.index(chat_id)][0])
        else:
            j = 0
            for i in players[chats.index(chat_id)]:
                print(i)
                if i == boss[chats.index(chat_id)]:
                    if j == len(players[chats.index(chat_id)]):
                        boss[chats.index(chat_id)][0] = players[chats.index(chat_id)][0]
                        break
                    else:
                        boss[chats.index(chat_id)][0] = i
                        break
                j = j + 1
        set_state(States.SET_MISSION_СOMPOSITION, chat_id)
        bot.send_message(chat_id, "Босс @" + str(boss[chats.index(chat_id)][0]) + " выбирай состав миссии. В этой миссии должно быть " + str(get_mission_len(chats.index(chat_id))),
                         reply_markup=generate_markup(1, chat_id))
        bot_vote(chat_id)
        #print(str(get_state(chat_id)) + " " + str(boss[chats.index(chat_id)]))


def init_chat(chat_id):
    if chat_id not in chats:
        #print("Chat init " + str(chat_id))
        chats.append(chat_id)
        players.append([])
        virtuous_team.append([])
        evil_team.append([])
        boss.append([])
        mission_composition.append([])
        voted0.append([])
        voted1.append([])
        votes.append([0, 0])
        mission_result.append([])
        current_states.append([States.NO_GAME])
        list_full.append([0])

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
    bot.send_message(message.chat.id, text="Команды:\n"
                                                             "/create для начала сбора игроков\n"
                                                             "/join для вступления в группу игроков\n"
                                                             "/startGame для начала игры\n"
                                                             "/leave для выхода из группы игроков\n"
                                                             "/players для показа игрков в игре - debug\n"
                                                             "/state для показа текущего состояния - debug\n"
                                                             "/team для показа текущей команды - debug\n"
                                                             "/addBot - debug")

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

@bot.message_handler(commands=['leave'])
def get_text_messages(message):
    init_chat(message.chat.id)
    if message.chat.id in chats:
        chat_id = chats.index(message.chat.id)
        print(str(players[chat_id]))
        if chat_id != 446193106 and get_state(message.chat.id) == States.FIND_PLAYERS:
            if message.from_user.username in players[chat_id]:
                if message.from_user.username == players[chat_id][0]:
                    bot.send_message(message.chat.id, 'Лидер не может покинуть игру. Попробуй /endGame')
                else:
                    new_players = []
                    for i in players[chat_id]:
                        if i != message.from_user.username:
                            new_players.append(i)
                    players[chat_id] = new_players
                    bot.send_message(message.chat.id, 'Игрок ' + str(message.from_user.username) + ' убран из игры')

@bot.message_handler(commands=['addBot'])
def get_text_messages(message):
    bot = "bot" + str(len(players[chats.index(message.chat.id)]))
    players[chats.index(message.chat.id)].append(bot)


@bot.message_handler(commands=['startGame'])
def get_text_messages(message):
    init_chat(message.chat.id)
    if message.chat.id in chats:
        chat_id = chats.index(message.chat.id)
        if chat_id != 446193106 and get_state(message.chat.id) == States.FIND_PLAYERS:
            if message.from_user.username == players[chat_id][0]:
                #channel = grpc.insecure_channel('localhost:50051')
                #stub = avalonGame.GameServiceStub(channel)
                #Players = []
                #for i in players[chat_id]:
                #    Players.append(avalonGame_pb2.Player(user_name= i))
                #good_team = avalonGame_pb2.VirtuousTeam(members= Players)
                #response = stub.CreateSession(avalonGame_pb2.GameConfig(good_team= good_team))
                #print("Session crated: ")
                if len(players[chat_id]) < 5 or len(players[chat_id]) > 10:
                    bot.send_message(message.chat.id, "В игре должно быть от 5 до 10 игроков. Сейчас " + str(len(players[chat_id])))
                else:
                    if len(players[chat_id]) == 5:
                        virtuous_team[chat_id] = sample(players[chat_id], 3)
                        set_evil_team(chat_id)
                    if len(players[chat_id]) == 6:
                        virtuous_team[chat_id] = sample(players[chat_id], 4)
                        set_evil_team(chat_id)
                    if len(players[chat_id]) == 7:
                        virtuous_team[chat_id] = sample(players[chat_id], 4)
                        set_evil_team(chat_id)
                    if len(players[chat_id]) == 8:
                        virtuous_team[chat_id] = sample(players[chat_id], 5)
                        set_evil_team(chat_id)
                    if len(players[chat_id]) == 9:
                        virtuous_team[chat_id] = sample(players[chat_id], 6)
                        set_evil_team(chat_id)
                    if len(players[chat_id]) == 10:
                        virtuous_team[chat_id] = sample(players[chat_id], 6)
                        set_evil_team(chat_id)
                    print(str(get_list(virtuous_team[chat_id], "Virtuous team:") + str(get_list(evil_team[chat_id], "evil_team: "))))
                    boss_vote(message.chat.id, True)


@bot.message_handler(commands=['vote'])
def get_text_messages(message):
    chat_id = message.chat.id
    init_chat(chat_id)
    if message.chat.id in chats:
        if get_state(chat_id) == States.SET_MISSION_СOMPOSITION:
            bot.send_message(chat_id, "Босс @" + str(boss[chats.index(chat_id)][0]) + " выбирай состав миссии. В этой миссии должно быть " + str(get_mission_len(chats.index(chat_id))),
                             reply_markup=generate_markup(1, message.chat.id))
            bot_vote(chat_id)
        elif get_state(chat_id) == States.VOTE_MISSION_СOMPOSITION:
            bot.send_message(chat_id, "Команда:\n" + get_list(mission_composition[chats.index(chat_id)], "") +
                          "Согласны с составом команды?", reply_markup=generate_markup(2, message.chat.id))
            bot_vote(chat_id)
        elif get_state(chat_id) == States.VOTE_MISSION_RESULT:
            bot.send_message(chat_id, "Команда:\n" + get_list(mission_composition[chats.index(chat_id)], "") +
                          "Отправляется в приключение, где их ждёт...", reply_markup=generate_markup(2, message.chat.id))
            bot_vote(chat_id)


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
                virtuous_team[chat_id].clear()
                evil_team[chat_id].clear()



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
            check_full(chat_id)

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
            if callback_query.from_user.username in virtuous_team[chats.index(chat_id)]:
                bot.answer_callback_query(callback_query.id, "Ты можешь голосовать только за успех")
            elif callback_query.from_user.username in voted0[chats.index(chat_id)] or callback_query.from_user.username not in\
                    voted0[chats.index(chat_id)] and callback_query.from_user.username not in voted1[chats.index(chat_id)]:
                votes[chats.index(chat_id)][1] = votes[chats.index(chat_id)][1] + 1
                voted1[chats.index(chat_id)].append(callback_query.from_user.username)
                if callback_query.from_user.username in voted0[chats.index(chat_id)]:
                    votes[chats.index(chat_id)][0] = votes[chats.index(chat_id)][0] - 1
                    voted0[chats.index(chat_id)].remove(callback_query.from_user.username)
        check_full(chat_id)
        print("Golosa za: " + str(votes[chats.index(chat_id)][0]) + " protiv: " + str(votes[chats.index(chat_id)][1]) + " state: " +
              str(get_state(chat_id)))

@bot.callback_query_handler(func=lambda message:'know' in message.data)
def get_callback_btn(callback_query: telebot.types.CallbackQuery):
    chat_id = int(callback_query.data.split()[1])
    if callback_query.from_user.username in virtuous_team[chats.index(chat_id)]:
        bot.answer_callback_query(callback_query.id, "Вы в команде добра")
    else:
        text = ""
        for i in evil_team[chats.index(chat_id)]:
            if callback_query.from_user.username not in i:
                text = text + i + "\n"
        bot.answer_callback_query(callback_query.id, "Вы в команде зла " + text)


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
        #logging.basicConfig()
        bot.remove_webhook()
        bot.polling(none_stop=True)
#bot.polling(none_stop=True, interval=0)
