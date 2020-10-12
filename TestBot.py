import random
from enum import Enum
import telebot

class States(Enum):
    NO_GAME = "0"
    FIND_PLAYERS = "1"
    SET_MISSION_СOMPOSITION = "2"
    SET_MISSION_RESULT = "3"

bot = telebot.TeleBot('1285966353:AAEIQ7RYIqx9rcV0Fm6om5RZeRSKy70Xpgc')
players = []
boss = 0
current_states = States.NO_GAME

def generate_markup():
    """
    Создаем кастомную клавиатуру для выбора ответа
    :param right_answer: Правильный ответ
    :param wrong_answers: Набор неправильных ответов
    :return: Объект кастомной клавиатуры
    """
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    # Создаем лист (массив) и записываем в него все элементыpip list
    list_items = ["1", "2", "3"]
    # Заполняем разметку перемешанными элементами
    for item in list_items:
        markup.add(item)
    return markup


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "/help":
        keyboard = telebot.types.InlineKeyboardMarkup()
        url_button = telebot.types.InlineKeyboardButton(text="Отзыв о настольной версии игры",
                                                        url="https://www.nastolki-na-polke.ru/obzory/resistance-avalon/")
        keyboard.add(url_button)
        bot.send_message(message.chat.id, "Можешь пока глянуть вот это", reply_markup=keyboard)
    elif message.text == "/hello":
        bot.send_message(message.chat.id, "Привет. Тут пока идёт стройка. Возвращайся позже!")
    elif message.text == "/create":

        #markup = generate_markup()
        bot.send_message(message.chat.id, 'Начат сбор игроков')
        current_states.self = States.FIND_PLAYERS
        players.append(message.from_user.username)
    elif message.text == "/join":
        if current_states.self == States.FIND_PLAYERS & message.from_user.username not in players:
            players.append(message.from_user.username)
            bot.send_message(message.chat.id, 'Игрок ' + message.from_user.username + ' добавлен к игре')
    elif message.text == "/showPlayers":
        if current_states.self == States.FIND_PLAYERS:
            text = ""
            i = 1
            for j in players :
                text += i + ". " + j + "\n"
                i += 1
            bot.send_message(message.chat.id, text)
    elif message.text == "/startGame":
        if current_states.self == States.FIND_PLAYERS and message.from_user.username == players[0]:
            text = ""
            i = 1
            for j in players:
                text += i + ". " + j + "\n"
                i += 1
            bot.send_message(message.chat.id, text)
            current_states.self = States.NO_GAME
    elif message.text == "/state":
        bot.send_message(message.chat.id, current_states.self)

if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
