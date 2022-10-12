from bdb import effective
from functools import wraps
from typing import Dict, Callable

import telegram
from telegram import Update
from telegram.ext import CallbackContext


def send_typing_action(func: Callable):
    """Sends typing action while processing func command."""
    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=telegram.ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func




def extract_user_data_from_update(update: Update, context: CallbackContext) -> Dict:
    """ python-telegram-bot's Update instance --> User info """
    # print(f"\n\nuser_data=={context.user_data}\n\n")
    if update.effective_user is not None:
        user = update.effective_user.to_dict()
        return dict(
        user_id=user["id"],
        is_blocked_bot=False,
        **{
            k: user[k]
            for k in ["username", "first_name", "last_name", "language_code"]
            if k in user and user[k] is not None
        },
    )
    elif update.effective_user is None:
        return dict(
        user_id=context.user_data["id"],
        is_blocked_bot=False,
        **{
            k: user[k]
            for k in ["username", "first_name", "last_name", "language_code"]
            if k in user and user[k] is not None
        },
    )
        

    