from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from tgbot.models import User

def send_test(update, context, question, user_exam):
    user, _ = User.get_user_and_created(update, context)

    questions_count = context.user_data["questions_count"] 
    number_of_test = context.user_data["number_of_test"]

    text = f"<b>Savol:</b> {question.content}\n"
    variants = ["A", "B", "C"]
    buttons = []
    
    for index, question_option in enumerate(question.options.order_by("?")):
            text += f"{variants[index]}) {question_option.content}"
            buttons.append([InlineKeyboardButton(f"{variants[index]}", callback_data=f"question-variant-{question.id}-{question_option.id}-{user_exam.id}")])
            
    if number_of_test==1:
        context.bot.send_message(chat_id = user.user_id,text=text, reply_markup = InlineKeyboardMarkup(buttons), parse_mode = ParseMode.HTML)
        context.user_data["number_of_test"]+=1
    else:     
        print(f"number=-------={context.user_data['number_of_test']}")   
        update.callback_query.edit_message_text(text = text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)
        context.user_data["number_of_test"]+=1
    
    



def send_exam_poll(context, question, chat_id):
    # POLL OPTIONS
    options = []
    correct_option_id = 0
    for index, option, in enumerate(question.options.all().order_by("?")):
        options.append(option.content)
        if option.is_correct:
            correct_option_id = index

    message = context.bot.send_poll(chat_id,
                                    question.content, options, type="quiz", correct_option_id=correct_option_id)
    # SAVE POLL ID WITH CHAT ID
    context.bot_data.update({message.poll.id: message.chat.id})
    


def get_chat_id(update, context):
    chat_id = -1

    if update.message is not None:
        chat_id = update.message.chat.id
    elif update.callback_query is not None:
        chat_id = update.callback_query.message.chat.id
    elif update.poll is not None:
        chat_id = context.bot_data[update.poll.id]

    return chat_id
