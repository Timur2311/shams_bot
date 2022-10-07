from telegram import ReplyKeyboardMarkup
from tgbot.handlers.onboarding.static_text import TEEST, CHALLENGE, LEADER, CONTACTUS


def make_keyboard_for_start_command() -> ReplyKeyboardMarkup:
    buttons = [
        [TEEST,CHALLENGE],
        [LEADER, CONTACTUS]
    ]

    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)
