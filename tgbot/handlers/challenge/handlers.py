
from uuid import uuid4
from telegram import ParseMode, Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle,InputTextMessageContent
from telegram.ext import CallbackContext
from group_challenge.models import Challenge, UserChallenge

from tgbot.handlers.exam import static_text
from tgbot.models import User
from exam.models import Exam, UserExam
from exam.models import Question
from tgbot.handlers.exam import keyboards
from tgbot.handlers.exam import helpers
from tgbot.handlers import onboarding
from tgbot.handlers.onboarding.keyboards import make_keyboard_for_start_command
from tgbot import consts



def inlinequery(update: Update, context: CallbackContext) -> None:
    query = update.inline_query.query

    if query == "":
        return
    elif query =="1":
        text = f"Sizni {query}-bosqich savollari bo'yicha bellashuvga taklif qilamiz!"
    elif query =="2":
        text = f"Sizni {query}-bosqich savollari bo'yicha bellashuvga taklif qilamiz!"
    elif query =="3":
        text = f"Sizni {query}-bosqich savollari bo'yicha bellashuvga taklif qilamiz!"   
    elif query =="4":
        text = f"Sizni {query}-bosqich savollari bo'yicha bellashuvga taklif qilamiz!"  
    elif query =="5":
        text = f"Sizni {query}-bosqich savollari bo'yicha bellashuvga taklif qilamiz!"
        
    results = []


    user_id = update.inline_query.from_user.id
    
    user, created = User.get_user_and_created(update, context)
    
    user_challenge = UserChallenge.objects.filter(user__user_id=user_id).filter(challenge=Challenge.objects.get(stage = query)).filter(is_active = True)
    

    if created:
        warning_text = "Siz ushbu botda yo'q ekansiz, botda sizning ismingiz \"IsmiGul\" bo'lib saqlandi. Ismingizni o'zgartirish uchun https://t.me/clc_challenge_bot botga o'tib /start deb yozing"
    else:
        warning_text = ""
        
        

    results.append(
        InlineQueryResultArticle(
            id=str(uuid4()),
            title=f"{user_challenge.challenge.title}",
            input_message_content=InputTextMessageContent(
                message_text=warning_text+text),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=consts.ACCEPT, callback_data=f"challenge-received-{consts.ACCEPT}-{user_challenge.user.user_id}-{user_challenge.id}")],
                                               [InlineKeyboardButton(
                                                   text=consts.DECLINE, callback_data=f"challenge-received-{consts.DECLINE}-{user_challenge.user.user_id}-{user_challenge.id}")]
                                               ])

        )
    )

    update.inline_query.answer(results)

    return consts.SELECTING_ACTION



def challenges_list(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Quyidagi bosqichlardan birini tanlang", reply_markup=ReplyKeyboardMarkup([
        [consts.FIRST],[consts.SECOND],[consts.THIRD],[consts.FOURTH],[consts.FIFTH],
        ], resize_keyboard=True))
    
     
    return consts.SHARING_CHALLENGE

def stage_exams(update: Update, context: CallbackContext):
    stage = update.message.text[0]
    update.message.reply_text(f"Siz {stage}-bosqich testlari bilan do'stingiz bilan bellashmoqchisiz.\n\n{consts.SHARE} tugmasini bosib Challenge ni  do'stlaringiz bilan ulashing",
                              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=consts.SHARE, switch_inline_query=f"{stage}")]]))























def exam_start(update: Update, context: CallbackContext) -> None:
    """
    TODO:
    - Pagination
    """
    exams = Exam.objects.all()
    inline_keyboard = keyboards.exam_keyboard(exams)

    if update.callback_query:
        update.callback_query.message.edit_text(
            text=static_text.exam_start, reply_markup=inline_keyboard,
            parse_mode=ParseMode.HTML
        )
    else:
        update.message.reply_text(
            text=static_text.exam_start, reply_markup=inline_keyboard)


def leader(update: Update, context: CallbackContext) -> None:
    user_exams = UserExam.objects.all().order_by("-score")
    text = ""
    for index,user_exam in enumerate (user_exams):
        text +=f"{index+1}. {user_exam.user} -  {user_exam.exam.title} - {user_exam.score} \n"
    update.message.reply_text(
            text=text)


def exam_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = update.callback_query.data.split("-")
    exam_id = data[2]
    

    query.answer()
    exam = Exam.objects.get(id=exam_id)
    text = f"{exam.title}\n\n<i>{exam.content}</i>\n\n<b>Imtixonni boshlaymizmi?</b>"
    context.bot.edit_message_text(
        text=text,
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboards.exam_start_confirmation(exam)
    )


def exam_confirmation(update: Update, context: CallbackContext) -> None:
    user = User.objects.get(user_id = update.callback_query.from_user.id)

    query = update.callback_query
    data = update.callback_query.data.split("-")
    exam_id = data[2]
    action_type = data[3]

    query.answer()
    if action_type == "start":
        exam = Exam.objects.get(id=exam_id)
        user_exam = exam.create_user_exam(user)
        user_exam.create_answers()
        question = user_exam.last_unanswered_question()

        query.delete_message()
        query.message.reply_text(
            static_text.exam_start_after_click, reply_markup=ReplyKeyboardRemove())

        helpers.send_exam_poll(context, question, user.user_id)

    elif action_type == "back":
        exam_start(update, context)


def poll_handler(update: Update, context: CallbackContext) -> None:
    # GETTING USER
    user_id = helpers.get_chat_id(update, context)
    user = User.objects.get(user_id=user_id)

    # CHECKING ANSWER
    is_correct = False
    for index, option in enumerate(update.poll.options):
        if option.voter_count >= 1:
            if index == update.poll.correct_option_id:
                is_correct = True
            break

    # SAVE ANSWER
    user_exam = UserExam.objects.filter(user=user, is_finished=False).last()
    answer_question = user_exam.last_unanswered()
    answer_question.is_correct = is_correct
    answer_question.answered = True
    answer_question.save()

    user_exam.update_score()
    user_exam = UserExam.objects.filter(user=user, is_finished=False).last()

    question = user_exam.last_unanswered_question()
    if question:
        helpers.send_exam_poll(context, question, user.user_id)
    else:
        context.bot.send_message(
            user_id, f"Imtixon tugadi.\n\nSizning natijangiz: {user_exam.score}", reply_markup=make_keyboard_for_start_command())
