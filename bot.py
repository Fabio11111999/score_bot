import time

import telebot
from telebot import types

BOT_TOKEN = "6480255635:AAHhat4oFJVwn03f9XJb7sFMADJb177vgTA"


class Game:
    def __init__(self):
        self.white_team, self.black_team = [], []
        self.start_time = None
        self.scorers, self.passer, self.time_stamps = [], [], []
        self.started = False

    def start(self) -> None:
        self.start_time = time.time()
        self.started = True


current_game = Game()
bot = telebot.TeleBot(BOT_TOKEN)
black_square = "⬛️"
white_square = "⬜️"


@bot.message_handler(commands=["reset"])
def reset(message: telebot.types.Message) -> None:
    global current_game
    current_game = Game()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("/setup_match"))
    bot.send_message(message.chat.id, "Select Option:", reply_markup=markup)


@bot.message_handler(commands=["setup_match"])
def setup_match(message: telebot.types.Message) -> None:
    text = "*Starting match setup*\nWrite the names of the players of the *White Team* separated with a whitespace"
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, register_team, "white")


def register_team(message: telebot.types.Message, color: str) -> None:
    text = f"*Team {color}*: " + message.text
    bot.send_message(message.chat.id, text, parse_mode="Markdown")
    if len(message.text.split(" ")) != 5:
        bot.send_message(
            message.chat.id, "*Wrong number of players!*", parse_mode="Markdown"
        )
        return
    if color == "white":
        current_game.white_team = message.text.split(" ")
        text = "Write the names of the players of the *Black Team* separated with a whitespace"
        sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
        bot.register_next_step_handler(sent_msg, register_team, "black")
    else:
        current_game.black_team = message.text.split(" ")
        items = [types.KeyboardButton("/teams"), types.KeyboardButton("/start_match")]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(*items)
        bot.send_message(message.chat.id, "Select Option", reply_markup=markup)


@bot.message_handler(commands=["teams"])
def ask_teams(message: telebot.types.Message) -> None:
    text = "*White Team*: "
    for player in current_game.white_team:
        text += player + " "
    text += "\n*Black Team*: "
    for player in current_game.black_team:
        text += player + " "
    bot.send_message(message.chat.id, text, parse_mode="Markdown")


@bot.message_handler(commands=["start_match"])
def start_match(message: telebot.types.Message) -> None:
    current_game.start()
    bot.send_message(message.chat.id, "Started match!", parse_mode="Markdown")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    white_buttons = [
        types.KeyboardButton(f"{white_square}{white_player}")
        for white_player in (current_game.white_team + ["own_black"])
    ]
    black_buttons = [
        types.KeyboardButton(f"{black_square}{black_player}")
        for black_player in (current_game.black_team + ["own_white"])
    ]
    items = white_buttons + black_buttons
    items.append(types.KeyboardButton("/rollback"))
    items.append(types.KeyboardButton("/end_match"))
    items.append(types.KeyboardButton("/time"))
    items.append(types.KeyboardButton("/result"))
    items.append(types.KeyboardButton("/scoreboard"))
    markup.add(*items)
    bot.send_message(message.chat.id, "Select Option:", reply_markup=markup)


def get_time_message() -> str:
    elapsed_seconds = int(time.time() - current_game.start_time)
    hours = elapsed_seconds // 3600
    minutes = (elapsed_seconds % 3600) // 60
    seconds = elapsed_seconds % 60
    return (
        "*Current Time:* `"
        + str(hours)
        + "h"
        + str(minutes)
        + "m"
        + str(seconds)
        + "s`"
    )


@bot.message_handler(commands=["time"])
def get_time(message: telebot.types.Message) -> None:
    bot.send_message(message.chat.id, get_time_message(), parse_mode="Markdown")


@bot.message_handler(commands=["result"])
def result(message: telebot.types.Message) -> None:
    text = get_time_message()
    score_white = 0
    for scorer, timestamp in zip(current_game.scorers, current_game.time_stamps):
        if scorer in current_game.white_team or scorer == "own_black":
            score_white += 1
    text += (
        "\n*Current Score:\nWhite*: "
        + str(score_white)
        + "\n*Black*: "
        + str(len(current_game.scorers) - score_white)
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")


@bot.message_handler(commands=["scoreboard"])
def scoreboard(message: telebot.types.Message) -> None:
    result(message)
    text = ""
    score_white, score_black = 0, 0
    for scorer, timestamp in zip(current_game.scorers, current_game.time_stamps):
        square = black_square
        if scorer in current_game.white_team or scorer == "own_black":
            square = white_square
            score_white += 1
        else:
            score_black += 1
        text += (
            square + f" *{scorer}* " + f" {timestamp}' ({score_white}-{score_black})\n"
        )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")


@bot.message_handler(commands=["end_match"])
def end_match(message: telebot.types.Message) -> None:
    bot.send_message(message.chat.id, get_time_message(), parse_mode="Markdown")
    scoreboard(message)
    reset(message)


@bot.message_handler(
    func=lambda message: message.text
    in [
        f"{white_square}{white_player}"
        for white_player in (current_game.white_team + ["own_black"])
    ]
    + [
        f"{black_square}{black_player}"
        for black_player in (current_game.black_team + ["own_white"])
    ]
)
def button(message: telebot.types.Message) -> None:
    current_game.scorers.append(message.text[1:][1:])
    current_game.time_stamps.append((time.time() - current_game.start_time) // 60)
    result(message)


@bot.message_handler(commands=["rollback"])
def rollback(message: telebot.types.Message) -> None:
    if len(current_game.scorers) == 0:
        bot.send_message(message.chat.id, "*No scores yet!*", parse_mode="Markdown")
        return
    current_game.scorers.pop()
    result(message)


if __name__ == "__main__":
    bot.infinity_polling()
