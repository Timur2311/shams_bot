
from re import L
from django.utils import timezone
from telegram import ParseMode, Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, ConversationHandler
from tgbot import consts

from tgbot.handlers.exam import static_text
from tgbot.models import User
from exam.models import Exam, UserExam
from exam.models import Question
from tgbot.handlers.exam import keyboards
from tgbot.handlers.exam import helpers
from tgbot.handlers import onboarding
from tgbot.handlers.onboarding.keyboards import make_keyboard_for_start_command


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


def passing_test(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Quyidagi bosqichlardan birini tanlang", reply_markup=ReplyKeyboardMarkup([
        [consts.FIRST],[consts.SECOND],[consts.THIRD],[consts.FOURTH],[consts.FIFTH],
        ], resize_keyboard=True))
    
    return consts.PASS_TEST

def stage_exams(update: Update, context: CallbackContext) -> None:
    stage = update.message.text[0]
    
    exams = Exam.objects.filter(stage = stage)
    buttons = []
    for exam in exams:
        buttons.append([InlineKeyboardButton(f"{exam.tour}-tur savollari", callback_data=f"passing-test-{exam.id}-{update.message.from_user.id}")])
        
    update.message.reply_text("Quyidagi imtihonlardan birini tanlang⬇️", reply_markup=InlineKeyboardMarkup(buttons))
    
    return consts.PASS_TEST



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
    user_id =  data[3]
    

    query.answer()
    exam = Exam.objects.get(id=exam_id)
    text = f"<b>{exam.title}</b> \n\n<b>Testni boshlaymizmi?</b>"
    context.bot.edit_message_text(
        text=text,
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboards.test_start_confirmation(exam)
    )


def exam_confirmation(update: Update, context: CallbackContext) -> None:
    user, _ = User.get_user_and_created(update, context)

    query = update.callback_query
    data = update.callback_query.data.split("-")
    exam_id = data[2]
    action_type = data[3]

    query.answer()
    if action_type == "start":
        exam = Exam.objects.get(id=exam_id)
        user_exam, counter = exam.create_user_exam(user)
        context.user_data['id'] = update.callback_query.from_user.id
        if counter>0:
            user_exam.create_answers()
            question = user_exam.last_unanswered_question()
            query.delete_message()
            query.message.reply_text(
            f"Test boshlandi!\n\n Testlar soni: {counter} ta", reply_markup=ReplyKeyboardRemove())
            helpers.send_exam_poll(context, question, user.user_id)
        elif counter == 0:
            query.delete_message()
            query.message.reply_text(
            "Ushbu testdagi hamma savollarga to'g'ri javob bergansiz ", reply_markup=ReplyKeyboardRemove())

        

        

    elif action_type == "back":
        exam_start(update, context)


def poll_handler(update: Update, context: CallbackContext) -> None:
    print("\n\n\poll handlerga kirdi \n\n")
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
