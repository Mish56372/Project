from telebot import TeleBot, types
from telebot.types import Message
from info import scales, survey

TOKEN = '6815959128:AAEdGQwoEYfIkVw9dozCqiKkR8L2Y0QvkLc'
bot = TeleBot(TOKEN)

users = {}

hideKeyboard = types.ReplyKeyboardRemove()

main_keyboard = types.ReplyKeyboardMarkup(
    row_width=3,
    resize_keyboard=True
)
main_keyboard.add(*['/start', '/start_survey', '/help'])


def check_user(uid: int) -> None:
    if uid not in users:
        users[uid] = {}
        users[uid]['q_num'] = 0
        for s in scales:
            users[uid][s] = 0
    print(users)


@bot.message_handler(commands=["start"])
def handle_start(message: Message):
    uid = message.from_user.id
    check_user(uid)
    bot.send_message(
        message.chat.id,
        f"<b>Привет, {message.chat.first_name}!</b>\n\n"
        f"Нажми /start_survey для начала анкетирования\n"
        f"Используй /help для помощи\n",
        parse_mode="HTML",
        reply_markup=main_keyboard
    )


@bot.message_handler(commands=["help"])
def help_comm(message: Message):
    uid = message.from_user.id
    check_user(uid)
    bot.send_message(
        message.chat.id,
        """<b>Список доступных команд:</b>
        
/start - начать использование бота
/start_survey - начать анкетирование
/result - показать результат <b>(бот сам предложит!)</b>
/max_survey - показать максимумы характеристик""",
        parse_mode="HTML",
        reply_markup=main_keyboard
    )


@bot.message_handler(commands=["max_survey"])
def max_survey(message: Message):
    uid = message.from_user.id
    check_user(uid)
    bot.send_message(
        message.chat.id,
        """<b>Максимумы характеристик:</b>
        
Трудолюбивость - <b>47</b>
Интеллектуальность - <b>44</b>
Навыки - <b>39</b>
Целеустремлённость - <b>42</b>

<b>Максимальную характеристику можно набрать только в одной категории!</b>""",
        parse_mode="HTML",
        reply_markup=main_keyboard
    )


@bot.message_handler(commands=["start_survey"])
def handle_survey(message: Message):
    uid = message.from_user.id
    check_user(uid)
    if message == '/start_survey':
        bot.send_message(
            message.chat.id,
            f"Отвечай на вопросы кнопками. В конце получишь результат\n\n",
            parse_mode="HTML",
            reply_markup=hideKeyboard
        )
        for s in scales:
            users[uid][s] = 0
        users[uid]['q_num'] = 0

    if users[uid]['q_num']:
        try:
            prev_question = survey[users[uid]['q_num'] - 1]
            print(prev_question, message.text, prev_question['a'][message.text])
            for i in range(len(scales)):
                users[uid][i] += prev_question['a'][message.text][i]
        except KeyError:
            bot.send_message(
                message.chat.id,
                f"Я не распознал ваше сообщение."
            )
    if users[uid]['q_num'] >= len(survey):
        bot.register_next_step_handler(message, handle_result)
        bot.send_message(
            message.chat.id,
            f"<b>Готово! Анкета закончилась</b>.\n"
            f"Результаты доступны по нажатию: /result",
            parse_mode="HTML",
            reply_markup=hideKeyboard
        )
        users[uid]['q_num'] = 0
        return

    bot.register_next_step_handler(message, handle_survey)
    q_num = users[uid]['q_num']
    question = survey[q_num]
    answers_keyboard = types.ReplyKeyboardMarkup(
        row_width=len(question['a']),
        resize_keyboard=True
    )
    answers_keyboard.add(*question['a'])
    bot.send_message(
        message.chat.id,
        f"<b>Вопрос № {q_num + 1}</b>:\n"
        f"<i>{survey[q_num]['q']}</i>",
        parse_mode="HTML",
        reply_markup=answers_keyboard
    )
    users[uid]['q_num'] += 1


@bot.message_handler(commands=["result"])
def handle_result(message: Message):
    uid = message.from_user.id
    check_user(uid)
    bot.send_message(
        message.chat.id,
        f"<b>Твои результаты, {message.chat.first_name}!</b>:\n\n"
        f"{[scales[i] + ' ' + str(users[uid][i]) for i in range(4)]}"
        f"\n\nЧтобы начать заново нажми /start_survey"
        f"\nЗа подробной информацией обратитесь в /help",
        parse_mode="HTML",
        reply_markup=main_keyboard
    )


print(TOKEN)
bot.polling()
