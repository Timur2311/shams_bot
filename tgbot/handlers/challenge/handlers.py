
from uuid import uuid4
from telegram import ParseMode, Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle,InputTextMessageContent, ParseMode
from telegram.ext import CallbackContext, ConversationHandler
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
from utils.check_subscription import check_subscription


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


    # user_id = update.inline_query.from_user.id
    
    user, created = User.get_user_and_created(update, context)
    
    user_challenge = UserChallenge.objects.filter(user=user).filter(challenge__stage = query).filter(is_active=True).first()
    
    

    if created:
        warning_text = "Siz ushbu botda yo'q ekansiz, botda sizning ismingiz \"IsmiGul\" bo'lib saqlandi. Ismingizni o'zgartirish uchun https://t.me/clc_challenge_bot botga o'tib /start deb yozing"
    else:
        warning_text = ""
        
        
 
    results.append(
        InlineQueryResultArticle(
            id=str(uuid4()),
            title=f"{user_challenge.challenge.stage}",
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
        [consts.FIRST],[consts.SECOND],[consts.THIRD],[consts.FOURTH],[consts.FIFTH],[consts.BACK]
        ], resize_keyboard=True))
    
     
    return consts.SHARING_CHALLENGE

def stage_exams(update: Update, context: CallbackContext):
    chat_member = context.bot.get_chat_member(
        consts.CHANNEL_USERNAME, update.message.from_user.id)
    if chat_member['status'] == "left":
        u = User.objects.get(user_id=update.message.from_user.id)
        check_subscription(update,context, u)
    else:
        stage = update.message.text[0]
        challenge = Challenge.objects.get(stage=stage)
        user_id=update.message.from_user.id
        
        user_challenge = challenge.create_user_challenge(user_id, challenge)

        
        challenge_stage = update.message.reply_text(f"Siz {stage}-bosqich testlari bilan do'stingiz bilan bellashmoqchisiz.\n\n{consts.SHARE} tugmasini bosib Challenge ni  do'stlaringiz bilan ulashing yoki <b>\"{consts.RANDOM_OPPONENT}\"</b> tugmasini bosing!",
                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=consts.SHARE, switch_inline_query=f"{stage}")],[InlineKeyboardButton(text=consts.RANDOM_OPPONENT, callback_data=f"{consts.RANDOM_OPPONENT}-{user_challenge.id}")],[InlineKeyboardButton(consts.REVOKE, callback_data=f"revoke-challenge-{user_challenge.id}-{user_id}")]]), parse_mode=ParseMode.HTML)
        context.user_data['challenge_stage_message_id'] = challenge_stage.message_id
        
    return consts.SHARING_CHALLENGE

def challenge_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    data = update.callback_query.data.split("-")
    received_type = data[2]
    challenge_owner_id = data[3]
    challenge_id = data[4]
    user_challenge = UserChallenge.objects.get(id=challenge_id)

    user, _ = User.get_user_and_created(update, context)

    query_user_id = str(query.from_user.id)

    if user.name == "IsmiGul":
        context.user_data[consts.FROM_CHAT] = True
        if query_user_id != challenge_owner_id:
            query.edit_message_text(f"Siz https://t.me/clc_challenge_bot botimizda \"IsmiGul\" bo'lib qolib ketibsiz, iltimos botga o'tib ro'yxatdan o'ting. Ro'xatdan o'tib bo'lgach \"Tekshirish\" tugmasini bosing", reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Tekshirish", callback_data=f"check-{user_challenge.id}-{challenge_owner_id}-{user.user_id}-{received_type}")]]))

    elif received_type == consts.ACCEPT:
        print(
            f"\n\nquery--->{type(query.from_user.id)}\nowner--->{type(challenge_owner_id)}")
        if query_user_id != challenge_owner_id:
            user_challenge.users.add(user)
            query.edit_message_text(text=f"<a href='tg://user?id={query.from_user.id}'>{user.name}</a> qabul qilindi, challenge haqida to'liqroq ma'lumot uchun\"{user_challenge.challenge.title}\" ni ustiga bosing.",  reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(f"{user_challenge.challenge.title}", callback_data=f"detail-page-{user_challenge.id}")]]), parse_mode=ParseMode.HTML)
    elif received_type == consts.DECLINE:
        if query_user_id != challenge_owner_id:
            query.edit_message_text(
                f" <a href='tg://user?id={query.from_user.id}'>{user.name}</a> challenge ga qatnashishni qabul qilmadi.")

def back_to_challenge_stage(update: Update, context: CallbackContext):
    data = update.callback_query.data.split("-")
    user_challenge_id = data[2]
    user_id = data[3]
    message_id = context.user_data["challenge_stage_message_id"]
    
    user_challenge = UserChallenge.objects.get(id = user_challenge_id)
    user_challenge.delete()
    
    context.bot.delete_message(chat_id = update.callback_query.message.chat_id, message_id =context.user_data["challenge_stage_message_id"])
    
    
    context.bot.send_message(chat_id = user_id, text = "Quyidagi bosqichlardan birini tanlang", reply_markup=ReplyKeyboardMarkup([
        [consts.FIRST],[consts.SECOND],[consts.THIRD],[consts.FOURTH],[consts.FIFTH],[consts.BACK]
        ], resize_keyboard=True))
    
    return consts.SHARING_CHALLENGE
    
    
    
    

















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
