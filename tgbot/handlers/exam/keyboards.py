from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup

from tgbot.handlers.onboarding.manage_data import SECRET_LEVEL_BUTTON


def exam_keyboard(exams) -> InlineKeyboardMarkup:
    buttons = []
    for exam in exams:
        buttons.append([InlineKeyboardButton(
            exam.title, callback_data=f'exam-start-{exam.id}'), ])

    return InlineKeyboardMarkup(buttons)


def test_start_confirmation(exam) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(
            "🔙 Orqaga", callback_data=f'test-confirmation-{exam.id}-back'), InlineKeyboardButton(
            "Boshlash", callback_data=f'test-confirmation-{exam.id}-start')]
    ]
    return InlineKeyboardMarkup(buttons)
