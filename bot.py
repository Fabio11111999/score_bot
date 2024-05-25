import time
from collections import defaultdict

import telebot
from telebot import types

BOT_TOKEN = "6480255635:AAHhat4oFJVwn03f9XJb7sFMADJb177vgTA"
ball_emoji, assist_emoji = "⚽", "🎯"


class Game:
    def __init__(self):
        self.white_team, self.black_team = [], []
        self.start_time = None
        self.scorers, self.assists, self.time_stamps = [], [], []
        self.started = False

    def start(self) -> None:
        self.start_time = time.time()
        self.started = True


current_games: dict[int, Game] = {}

bot = telebot.TeleBot(BOT_TOKEN)
black_square = "⬛️"
white_square = "⬜️"


@bot.message_handler(commands=["reset"])
def reset(message: telebot.types.Message) -> None:
    global current_games
    current_games[message.chat.id] = Game()
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
    if len(message.text.split(" ")) == 0:
        bot.send_message(
            message.chat.id, "*Wrong number of players!*", parse_mode="Markdown"
        )
        return
    if color == "white":
        current_games[message.chat.id].white_team = message.text.split(" ")
        text = "Write the names of the players of the *Black Team* separated with a whitespace"
        sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
        bot.register_next_step_handler(sent_msg, register_team, "black")
    else:
        current_games[message.chat.id].black_team = message.text.split(" ")
        items = [types.KeyboardButton("/teams"), types.KeyboardButton("/start_match")]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(*items)
        bot.send_message(message.chat.id, "Select Option", reply_markup=markup)


@bot.message_handler(commands=["teams"])
def ask_teams(message: telebot.types.Message) -> None:
    text = "*White Team*: "
    for player in current_games[message.chat.id].white_team:
        text += player + " "
    text += "\n*Black Team*: "
    for player in current_games[message.chat.id].black_team:
        text += player + " "
    bot.send_message(message.chat.id, text, parse_mode="Markdown")


@bot.message_handler(commands=["start_match"])
def start_match(message: telebot.types.Message) -> None:
    bot.send_message(message.chat.id, "Started match!", parse_mode="Markdown")
    current_games[message.chat.id].start()
    show_goals_assists_buttons(message)


def show_goals_assists_buttons(
    message: telebot.types.Message,
    goals: bool = True,
    team: str = "white",
    scorer: str = "",
) -> None:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    white_buttons = [
        types.KeyboardButton(
            f"{white_square}{white_player}{ball_emoji if goals else assist_emoji}"
        )
        for white_player in (
            current_games[message.chat.id].white_team + ["none" if goals is False else "own_black"]
        )
        if scorer != white_player
    ]

    black_buttons = [
        types.KeyboardButton(
            f"{black_square}{black_player}{ball_emoji if goals else assist_emoji}"
        )
        for black_player in (
            current_games[message.chat.id].black_team + ["none" if goals is False else "own_white"]
        )
        if scorer != black_player
    ]
    if goals is False:
        if team == "white":
            black_buttons = []
        else:
            white_buttons = []

    items = white_buttons + black_buttons
    if goals is True:
        items.append(types.KeyboardButton("/rollback"))
        items.append(types.KeyboardButton("/end_match"))
        items.append(types.KeyboardButton("/time"))
        items.append(types.KeyboardButton("/result"))
        items.append(types.KeyboardButton("/scoreboard"))
    markup.add(*items)
    bot.send_message(
        message.chat.id,
        "Select Scorer:" if goals is True else "Select Assister:",
        reply_markup=markup,
    )


def get_time_message(chat_id: int) -> str:
    elapsed_seconds = int(time.time() - current_games[chat_id].start_time)
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
    bot.send_message(message.chat.id, get_time_message(message.chat.id), parse_mode="Markdown")


@bot.message_handler(commands=["result"])
def result(message: telebot.types.Message) -> None:
    text = get_time_message(message.chat.id)
    score_white = 0
    for scorer in current_games[message.chat.id].scorers:
        if scorer in current_games[message.chat.id].white_team or scorer == "own_black":
            score_white += 1
    text += (
        "\n*Current Score:\nWhite*: "
        + str(score_white)
        + "\n*Black*: "
        + str(len(current_games[message.chat.id].scorers) - score_white)
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")


@bot.message_handler(commands=["scoreboard"])
def scoreboard(message: telebot.types.Message) -> None:
    result(message)
    text = ""
    score_white, score_black = 0, 0
    for scorer, timestamp in zip(current_games[message.chat.id].scorers, current_games[message.chat.id].time_stamps):
        square = black_square
        if scorer in current_games[message.chat.id].white_team or scorer == "own_black":
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
    scoreboard(message)
    print_stats(message.chat.id)
    reset(message)


@bot.message_handler(
    func=lambda message: message.text
    in [
        f"{white_square}{white_player}{ball_emoji}"
        for white_player in (current_games[message.chat.id].white_team + ["own_black"])
    ]
    + [
        f"{black_square}{black_player}{ball_emoji}"
        for black_player in (current_games[message.chat.id].black_team + ["own_white"])
    ]
)
def goal(message: telebot.types.Message) -> None:
    player = message.text[1:][1:-1]
    current_games[message.chat.id].scorers.append(player)
    current_games[message.chat.id].time_stamps.append((time.time() - current_games[message.chat.id].start_time) // 60)
    result(message)
    show_goals_assists_buttons(
        message,
        goals=False,
        team="white" if player in current_games[message.chat.id].white_team else "black",
        scorer=player,
    )


@bot.message_handler(
    func=lambda message: message.text
    in [
        f"{white_square}{white_player}{assist_emoji}"
        for white_player in (current_games[message.chat.id].white_team + ["none"])
    ]
    + [
        f"{black_square}{black_player}{assist_emoji}"
        for black_player in (current_games[message.chat.id].black_team + ["none"])
    ]
)
def assist(message: telebot.types.Message) -> None:
    player = message.text[1:][1:-1]
    current_games[message.chat.id].assists.append(player)
    show_goals_assists_buttons(message, goals=True)
    result(message)


def print_stats(chat_id: int):
    scorers: dict[int, int] = defaultdict(int)
    assists: dict[int, int] = defaultdict(int)
    for s, a in zip(current_games[chat_id].scorers, current_games[chat_id].assists):
        if s == "own_black" or s == "own_white":
            continue
        scorers[s] += 1
        if a != "none":
            assists[a] += 1
    text = "*Stats:*"
    for white_player in current_games[chat_id].white_team:
        text += (
            f"\n{white_square}{white_player}: "
            f"{ball_emoji * scorers[white_player] + assist_emoji * assists[white_player]}"
        )
    for black_player in current_games[chat_id].black_team:
        text += (
            f"\n{black_square}{black_player}: "
            f"{ball_emoji * scorers[black_player] + assist_emoji * assists[black_player]}"
        )
    bot.send_message(chat_id, text, parse_mode="Markdown")


@bot.message_handler(commands=["rollback"])
def rollback(message: telebot.types.Message) -> None:
    if len(current_games[message.chat.id].scorers) == 0:
        bot.send_message(message.chat.id, "*No scores yet!*", parse_mode="Markdown")
        return
    current_games[message.chat.id].scorers.pop()
    current_games[message.chat.id].time_stamps.pop()
    current_games[message.chat.id].assists.pop()
    result(message)


if __name__ == "__main__":
    bot.infinity_polling()
