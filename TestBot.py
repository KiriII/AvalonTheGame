import random

import telebot

bot = telebot.TeleBot('1285966353:AAEIQ7RYIqx9rcV0Fm6om5RZeRSKy70Xpgc')


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
    elif message.text == "/game":
        markup = generate_markup()
        bot.send_message(message.chat.id, 'Угадай число', reply_markup=markup)
        check_answer()
    else:
        bot.send_message(message.chat.id, "спам")

@bot.message_handler(func=lambda message: True, content_types=['text'])
def check_answer(message):
    # Если функция возвращает None -> Человек не в игре
    answer = str(random.randint(1, 3))
    # Как Вы помните, answer может быть либо текст, либо None
    # Если None:
    if not answer:
        bot.send_message(message.chat.id, 'Чтобы начать игру, выберите команду /game')
    else:
        # Уберем клавиатуру с вариантами ответа.
        keyboard_hider = telebot.types.ReplyKeyboardRemove()
        # Если ответ правильный/неправильный
        if message.text == answer:
            bot.send_message(message.chat.id, 'Верно!', reply_markup=keyboard_hider)
        else:
            bot.send_message(message.chat.id, 'Увы, Вы не угадали. Попробуйте ещё раз! Ответ: ' + answer,
                             reply_markup=keyboard_hider)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
