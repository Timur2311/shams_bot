
from email import message
from uuid import uuid4
from datetime import datetime
from telegram import ParseMode, Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent, ParseMode
from telegram.ext import CallbackContext, ConversationHandler
from group_challenge.models import Challenge, UserChallenge, UserChallengeAnswer

from tgbot.handlers.exam import static_text
from tgbot.models import User
from exam.models import Exam, UserExam, QuestionOption
from exam.models import QuestionOption
from tgbot.handlers.exam import keyboards
from tgbot.handlers.exam import helpers
from tgbot.handlers.onboarding.keyboards import make_keyboard_for_start_command
from tgbot import consts
from utils.check_subscription import check_subscription


def inlinequery(update: Update, context: CallbackContext) -> None:

    query = update.inline_query.query

    if query == "":
        return
    elif query == "1":
        text = f"Sizni {query}-bosqich savollari bo'yicha bellashuvga taklif qilamiz!"
    elif query == "2":
        text = f"Sizni {query}-bosqich savollari bo'yicha bellashuvga taklif qilamiz!"
    elif query == "3":
        text = f"Sizni {query}-bosqich savollari bo'yicha bellashuvga taklif qilamiz!"
    elif query == "4":
        text = f"Sizni {query}-bosqich savollari bo'yicha bellashuvga taklif qilamiz!"
    elif query == "5":
        text = f"Sizni {query}-bosqich savollari bo'yicha bellashuvga taklif qilamiz!"
    else:
        return

    results = []

    user, _ = User.get_user_and_created(update, context)

    user_challenge = UserChallenge.objects.filter(
        user=user, challenge__stage=query, opponent=None, is_active=True).last()

    results.append(
        InlineQueryResultArticle(
            id=str(uuid4()),
            title=f"{user_challenge.challenge.stage}",
            input_message_content=InputTextMessageContent(
                message_text=text),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=consts.ACCEPT, callback_data=f"received-challenge-{consts.ACCEPT}-{user_challenge.user.user_id}-{user_challenge.id}")],
                                               [InlineKeyboardButton(
                                                   text=consts.DECLINE, callback_data=f"received-challenge-{consts.DECLINE}-{user_challenge.user.user_id}-{user_challenge.id}")]
                                               ])
        )
    )

    update.inline_query.answer(results)


def challenges_list(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Quyidagi bosqichlardan birini tanlang", reply_markup=ReplyKeyboardMarkup([
        [consts.FIRST], [consts.SECOND], [consts.THIRD], [
            consts.FOURTH], [consts.FIFTH], [consts.BACK]
    ], resize_keyboard=True))

    return consts.SHARING_CHALLENGE


def stage_exams(update: Update, context: CallbackContext):
    u = User.objects.get(user_id=update.message.from_user.id)

    chat_member = context.bot.get_chat_member(
        consts.CHANNEL_USERNAME, update.message.from_user.id)
    if chat_member['status'] == "left":
        check_subscription(update, context, u)
    else:
        stage = update.message.text[0]
        challenge = Challenge.objects.get(stage=stage)

        user_challenge = challenge.create_user_challenge(u.user_id, challenge)

        challenge_stage = update.message.reply_text(f"Siz {stage}-bosqich testlari bilan do'stingiz bilan bellashmoqchisiz.\n\n{consts.SHARE} tugmasini bosib Challenge ni  do'stlaringiz bilan ulashing yoki <b>\"{consts.RANDOM_OPPONENT}\"</b> tugmasini bosing!",
                                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=consts.SHARE, switch_inline_query=f"{stage}")], [InlineKeyboardButton(text=consts.RANDOM_OPPONENT, callback_data=f"{consts.RANDOM_OPPONENT}-{user_challenge.id}-{u.user_id}")], [InlineKeyboardButton(consts.REVOKE, callback_data=f"revoke-challenge-{u.user_id}")]]), parse_mode=ParseMode.HTML)
        user_challenge.created_challenge_message_id = str(challenge_stage.message_id)
        user_challenge.created_challenge_chat_id = str(update.message.chat_id)
        user_challenge.save()

    return consts.SHARING_CHALLENGE


def challenge_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    data = update.callback_query.data.split("-")
    received_type = data[2]
    challenge_owner_id = data[3]
    challenge_id = data[4]
    user_challenge = UserChallenge.objects.get(id=int(challenge_id))

    user, _ = User.get_user_and_created(update, context)

    # user.user_id = str(query.from_user.id)

    if user.name == "IsmiGul":
        context.user_data[consts.FROM_CHAT] = True
        if user.user_id != challenge_owner_id:
            query.edit_message_text(f"Siz https://t.me/shamsquizbot botimizda \"IsmiGul\" bo'lib qolib ketibsiz, iltimos botga o'tib ro'yxatdan o'ting. Ro'xatdan o'tib bo'lgach \"Tekshirish\" tugmasini bosing", reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Tekshirish", callback_data=f"check-{user_challenge.id}-{challenge_owner_id}-{user.user_id}-{received_type}")]]))

    elif received_type == consts.ACCEPT:

        if user.user_id != challenge_owner_id:
            user_challenge.users.add(user)
            user_challenge.opponent = user
            user_challenge.save()
            if data[1] == "revansh":

                context.bot.send_message(chat_id=challenge_owner_id, text=f"<a href='tg://user?id={user.user_id}'>{user.name}</a> bellashuvga rozi bo'ldi.Bellashuvni boshlash uchun \"Boshlash\" tugmasini bosing ", reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Boshlash", callback_data=f"challenge-confirmation-{user_challenge.id}-start-user-{challenge_owner_id}")]]), parse_mode=ParseMode.HTML)
                query.delete_message()
                message_id = context.bot_data[f"{user_challenge.opponent.user_id}"]["ended_challenge"][0]
                context.bot.delete_message(chat_id = query.message.chat_id, message_id = message_id )
                context.bot.send_message(chat_id=user.user_id, text="Siz bellashuvga rozi bo'ldingiz. Bellashuvni boshlash uchun \"Boshlash\" tugmasini bosing ",
                                         reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Boshlash", callback_data=f"challenge-confirmation-{user_challenge.id}-start-opponent-{user.user_id}")]]), parse_mode=ParseMode.HTML)
            elif data[1] == "challenge":

                query.edit_message_text(
                    text=f"<a href='tg://user?id={query.from_user.id}'>{user.name}</a> bellashuvni qabul qildi.", parse_mode=ParseMode.HTML)
                message_id = user_challenge.created_challenge_message_id
                chat_id = user_challenge.created_challenge_chat_id
                context.bot.delete_message(
                    chat_id=chat_id, message_id=message_id)
                context.bot.send_message(chat_id=challenge_owner_id, text=f"<a href='tg://user?id={user.user_id}'>{user.name}</a> bellashuvga rozi bo'ldi.Bellashuvni boshlash uchun \"Boshlash\" tugmasini bosing ", reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Boshlash", callback_data=f"challenge-confirmation-{user_challenge.id}-start-user-{challenge_owner_id}")]]), parse_mode=ParseMode.HTML)
                context.bot.send_message(chat_id=user.user_id, text="Siz bellashuvga rozi bo'ldingiz. Bellashuvni boshlash uchun \"Boshlash\" tugmasini bosing ",
                                         reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Boshlash", callback_data=f"challenge-confirmation-{user_challenge.id}-start-opponent-{user.user_id}")]]), parse_mode=ParseMode.HTML)
    elif received_type == consts.DECLINE:
        if user.user_id != challenge_owner_id:
            query.edit_message_text(
                f" <a href='tg://user?id={query.from_user.id}'>{user.name}</a> challenge ga qatnashishni rad etdi.", parse_mode=ParseMode.HTML)


def user_check(update: Update, context: CallbackContext):
    query = update.callback_query
    data = update.callback_query.data.split("-")
    user_challenge_id = data[1]
    user_challenge = UserChallenge.objects.get(id=user_challenge_id)
    challenge_owner_id = data[2]
    user_id = data[3]
    received_type = data[4]
    user, _ = User.get_user_and_created(update, context)

    user.user_id = str(query.from_user.id)

    if user.name == "IsmiGul":
        if user.user_id != challenge_owner_id:
            query.edit_message_text(f"Siz <a href='https://t.me/clc_challenge_bot'>ShamsBot</a> botimizda hali ham \"IsmiGul\" bo'lib qolib ketibsiz, iltimos botga o'tib ro'yxatdan o'ting. Ro'xatdan o'tib bo'lgach \"Tekshirish\" tugmasini bosing", reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Tekshirish", callback_data=f"check-{user_challenge_id}-{challenge_owner_id}-{user_id}-{received_type}")]]), parse_mode=ParseMode.HTML)

    elif received_type == consts.ACCEPT:
        if user.user_id != challenge_owner_id:
            user_challenge.users.add(user)
            user_challenge.opponent = user
            user_challenge.save()
            query.edit_message_text(
                f"<a href='tg://user?id={query.from_user.id}'>{user.name}</a> bellashuvga rozilik bildirdi.", parse_mode=ParseMode.HTML)
            created_challenge_info = context.bot_data[f"{challenge_owner_id}"]["created_challenge"]
            context.bot.delete_message(
                chat_id=created_challenge_info[1], message_id=created_challenge_info[0])
            context.bot.send_message(chat_id=challenge_owner_id, text=f"<a href='tg://user?id={user.user_id}'>{user.name}</a> bellashuvga rozi bo'ldi.Bellashuvni boshlash uchun \"Boshlash\" tugmasini bosing ", reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Boshlash", callback_data=f"challenge-confirmation-{user_challenge.id}-start-user-{challenge_owner_id}")]]), parse_mode=ParseMode.HTML)
            context.bot.send_message(chat_id=user.user_id, text="Siz bellashuvga rozi bo'ldingiz. Bellashuvni boshlash uchun \"Boshlash\" tugmasini bosing ",
                                     reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Boshlash", callback_data=f"challenge-confirmation-{user_challenge.id}-start-opponent-{user.user_id}")]]))
    elif received_type == consts.DECLINE:
        if user.user_id != challenge_owner_id:
            query.edit_message_text(
                f"<a href='tg://user?id={query.from_user.id}'>{user.name}</a> bellashuvga rozilik bildirmadi.", parse_mode=ParseMode.HTML)


def challenge_confirmation(update: Update, context: CallbackContext) -> None:

    query = update.callback_query
    data = update.callback_query.data.split("-")
    user_challenge_id = data[2]
    user_type = data[4]
    user_id = data[5]
    user = User.objects.get(user_id=user_id)
    user_challenge = UserChallenge.objects.get(id=int(user_challenge_id))
    
    query.answer()

    if user_type == "user":
        now = datetime.now()
        user_challenge.user_started_at = now
        user_challenge.save()

        context.user_data["number_of_test"] = 1

        user_challenge.create_user_answers()
        question = user_challenge.last_unanswered_question(user_challenge.user)
        query.delete_message()
        del_message = query.message.reply_text(
            f"Test boshlandi!\n\n Testlar soni: 10 ta", reply_markup=ReplyKeyboardRemove())
        context.user_data["message_id"] = del_message.message_id
        context.user_data["chat_id"] = update.callback_query.message.chat_id

        helpers.send_test(update=update, context=context,
                          question=question, user_exam=user_challenge, user=user)

    elif user_type == "opponent":
        now = datetime.now()
        user_challenge.opponent_started_at = now
        user_challenge.save()
        context.user_data["number_of_test"] = 1

        user_challenge.create_opponent_answers()
        question = user_challenge.last_unanswered_question(
            user_challenge.opponent)
        query.delete_message()
        del_message = query.message.reply_text(
            f"Test boshlandi!\n\n Testlar soni: 10 ta", reply_markup=ReplyKeyboardRemove())
        context.user_data["message_id"] = del_message.message_id
        context.user_data["chat_id"] = update.callback_query.message.chat_id
        helpers.send_test(update=update, context=context,
                          question=question, user_exam=user_challenge, user=user)

    return consts.SHARING_CHALLENGE


def challenge_handler(update: Update, context: CallbackContext):
    data = update.callback_query.data.split("-")
    question_id = data[2]
    question_option_id = data[3]
    user_challenge_id = data[4]
    from_user_id = data[5]

    user = User.objects.get(user_id=from_user_id)

    question_option = QuestionOption.objects.get(id=question_option_id)

    user_challenge_answers = UserChallengeAnswer.objects.filter(
        user_challenge__id=user_challenge_id).filter(question__id=question_id).filter(user=user)
    user_challenge_answer = user_challenge_answers[0]

    user_challenge = UserChallenge.objects.get(id=user_challenge_id)

    text = f"Bellashuv turi: {user_challenge.challenge.stage}-bosqich savollari. "

    user_challenge_answer.is_correct = question_option.is_correct
    user_challenge_answer.answered = True
    user_challenge_answer.save()

    question = user_challenge.last_unanswered_question(user)
    if question:
        helpers.send_test(update=update, context=context,
                          question=question, user_exam=user_challenge, user=user)

    else:
        now = datetime.now()
        update.callback_query.delete_message()
        context.bot.delete_message(
            chat_id=context.user_data['chat_id'], message_id=context.user_data["message_id"])
        if user.user_id == user_challenge.user.user_id:  # user ekan
            user_challenge.update_score("user")
            user_challenge.user_finished_at = now
            user_challenge.is_user_finished = True
            user_challenge.is_random_opponent = False
            user_challenge.save()
            if user_challenge.is_opponent_finished:
                user_message_info = context.bot_data[f"{user_challenge.opponent.user_id}"]["exam_finished"]
                context.bot.delete_message(
                    chat_id=user_message_info[1], message_id=user_message_info[0])
                user_challenge.is_active = False
                user_challenge.save()
                user_duration = user_challenge.user_duration()
                opponent_duration = user_challenge.opponent_duration()
                user_time = helpers.get_duration(user_duration)
                opponent_time = helpers.get_duration(opponent_duration)
                if user_challenge.user_score>user_challenge.opponent_score:
                    print("birinchi if ga kirdi")

                    text += f"\n<a href='tg://user?id={user_challenge.user.user_id}'>{user_challenge.user.name}</a>:👑{user_challenge.user_score}/10  ⏳{user_time}\n<a href='tg://user?id={user_challenge.opponent.user_id}'>{user_challenge.opponent.name}</a>:😭{user_challenge.opponent_score}/10  ⏳{opponent_time}"
                elif user_challenge.user_score==user_challenge.opponent_score:
                    print("ikkinchi if ga kirdi")

                    if user_duration<opponent_duration:
                        print("uchinchi if ga kirdi")

                        text += f"\n<a href='tg://user?id={user_challenge.user.user_id}'>{user_challenge.user.name}</a>:👑{user_challenge.user_score}/10  ⏳{user_time}\n<a href='tg://user?id={user_challenge.opponent.user_id}'>{user_challenge.opponent.name}</a>:😭{user_challenge.opponent_score}/10  ⏳{opponent_time}"
                user_message = context.bot.send_message(
                    chat_id=user_challenge.user.user_id, text=text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Qayta bellashish", callback_data=f"revansh-{user_challenge.challenge.id}-{user_challenge.user.user_id}-{user_challenge.opponent.user_id}")], [InlineKeyboardButton("Bosh Sahifa", callback_data=f"home-page-{user_challenge.user.user_id}")]]), parse_mode=ParseMode.HTML)
                opponent_message = context.bot.send_message(
                    chat_id=user_challenge.opponent.user_id, text=text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Qayta bellashish", callback_data=f"revansh-{user_challenge.challenge.id}-{user_challenge.opponent.user_id}-{user_challenge.user.user_id}")], [InlineKeyboardButton("Bosh Sahifa", callback_data=f"home-page-{user_challenge.opponent.user_id}")]]), parse_mode=ParseMode.HTML)
                context.bot_data.update({f"{user_challenge.user.user_id}": {"ended_challenge": [
                                        user_message.message_id, update.callback_query.message.chat_id]}})
                context.bot_data.update({f"{user_challenge.opponent.user_id}": {"ended_challenge": [
                                        opponent_message.message_id, update.callback_query.message.chat_id]}})
                return ConversationHandler.END
            else:
                text += "\nHali raqibingiz tugatmadi. Raqibingiz tugatishi bilan sizga test natijalarini jo'natamiz."
                not_finished_text = context.bot.send_message(
                    user.user_id, text=text)
                context.bot_data.update(
                    {f"{user.user_id}": {"exam_finished": [not_finished_text.message_id, update.callback_query.message.chat_id]}})

        elif user.user_id == user_challenge.opponent.user_id:  # opponent ekan
            user_challenge.update_score("opponent")
            user_challenge.opponent_finished_at = now
            user_challenge.is_opponent_finished = True
            user_challenge.is_random_opponent = False
            user_challenge.save()

            if user_challenge.is_user_finished:
                user_message_info = context.bot_data[f"{user_challenge.user.user_id}"]["exam_finished"]
                context.bot.delete_message(
                    chat_id=user_message_info[1], message_id=user_message_info[0])
                user_challenge.is_active = False
                user_challenge.save()
                user_duration = user_challenge.user_duration()
                opponent_duration = user_challenge.opponent_duration()
                user_time = helpers.get_duration(user_duration)
                opponent_time = helpers.get_duration(opponent_duration)
                if user_challenge.user_score>user_challenge.opponent_score:
                    print("birinchi if ga kirdi")
                    text += f"\n<a href='tg://user?id={user_challenge.user.user_id}'>{user_challenge.user.name}</a>:👑{user_challenge.user_score}/10  ⏳{user_time}\n<a href='tg://user?id={user_challenge.opponent.user_id}'>{user_challenge.opponent.name}</a>:😭{user_challenge.opponent_score}/10  ⏳{opponent_time}"
                elif user_challenge.user_score==user_challenge.opponent_score:
                    print("ikkinchi if ga kirdi")
                    if user_duration<opponent_duration:
                        print("uchinchi if ga kirdi")

                        text += f"\n<a href='tg://user?id={user_challenge.user.user_id}'>{user_challenge.user.name}</a>:👑{user_challenge.user_score}/10  ⏳{user_time}\n<a href='tg://user?id={user_challenge.opponent.user_id}'>{user_challenge.opponent.name}</a>:😭{user_challenge.opponent_score}/10  ⏳{opponent_time}"
                user_message = context.bot.send_message(
                    chat_id=user_challenge.user.user_id, text=text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Qayta bellashish", callback_data=f"revansh-{user_challenge.challenge.id}-{user_challenge.user.user_id}-{user_challenge.opponent.user_id}")], [InlineKeyboardButton("Bosh Sahifa", callback_data=f"home-page-{user_challenge.user.user_id}")]]), parse_mode=ParseMode.HTML)
                opponent_message = context.bot.send_message(
                    chat_id=user_challenge.opponent.user_id, text=text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Qayta bellashish", callback_data=f"revansh-{user_challenge.challenge.id}-{user_challenge.opponent.user_id}-{user_challenge.user.user_id}")], [InlineKeyboardButton("Bosh Sahifa", callback_data=f"home-page-{user_challenge.opponent.user_id}")]]), parse_mode=ParseMode.HTML)
                context.bot_data.update({f"{user_challenge.user.user_id}": {"ended_challenge": [
                                        user_message.message_id, update.callback_query.message.chat_id]}})
                context.bot_data.update({f"{user_challenge.opponent.user_id}": {"ended_challenge": [
                                        opponent_message.message_id, update.callback_query.message.chat_id]}})
                return ConversationHandler.END

            else:
                text += "\nHali raqibingiz tugatmadi. Raqibingiz tugatishi bilan sizga test natijalarini jo'natamiz."

                not_finished_text = context.bot.send_message(
                    user.user_id, text=text)
                context.bot_data.update(
                    {f"{user_challenge.opponent.user_id}": {"exam_finished": [not_finished_text.message_id, update.callback_query.message.chat_id]}})

    return consts.SHARING_CHALLENGE


def back_to_challenge_stage(update: Update, context: CallbackContext):
    data = update.callback_query.data.split("-")
    user_challenge_id = data[2]
    user_id = data[3]
    message_id = context.user_data["message_id"]

    user_challenge = UserChallenge.objects.get(id=user_challenge_id)
    user_challenge.delete()

    context.bot.delete_message(
        chat_id=update.callback_query.message.chat_id, message_id=message_id)

    context.bot.send_message(chat_id=user_id, text="Quyidagi bosqichlardan birini tanlang", reply_markup=ReplyKeyboardMarkup([
        [consts.FIRST], [consts.SECOND], [consts.THIRD], [
            consts.FOURTH], [consts.FIFTH], [consts.BACK]
    ], resize_keyboard=True))

    return consts.SHARING_CHALLENGE


# def exam_start(update: Update, context: CallbackContext) -> None:
#     """
#     TODO:
#     - Pagination
#     """
#     exams = Exam.objects.all()
#     inline_keyboard = keyboards.exam_keyboard(exams)

#     if update.callback_query:
#         update.callback_query.message.edit_text(
#             text=static_text.exam_start, reply_markup=inline_keyboard,
#             parse_mode=ParseMode.HTML
#         )
#     else:
#         update.message.reply_text(
#             text=static_text.exam_start, reply_markup=inline_keyboard)


def leader(update: Update, context: CallbackContext) -> None:
    user_exams = UserExam.objects.all().order_by("-score")
    text = ""
    for index, user_exam in enumerate(user_exams):
        text += f"{index+1}. {user_exam.user} -  {user_exam.exam.title} - {user_exam.score} \n"
    update.message.reply_text(
        text=text)


def random_opponent(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data.split("-")
    user_challenge_id = data[1]
    created_user_challenge = UserChallenge.objects.get(id=user_challenge_id)
    from_user_id = data[2]

    possible_challenges = UserChallenge.objects.filter(
        is_active=True).filter(is_random_opponent=True).filter(opponent=None).exclude(user=User.objects.get(user_id=from_user_id))
    # print(f"possible_challenges===={possible_challenges}")

    if possible_challenges.count() == 0:
        created_user_challenge.is_random_opponent = True
        created_user_challenge.save()
        my_message = update.callback_query.edit_message_text("Hozircha siz uchun raqib yo'q. Raqib topilishi bilan sizga xabar jo'natamiz.", reply_markup=InlineKeyboardMarkup([
                                                             [InlineKeyboardButton("Bosh Sahifa", callback_data=f"home-page-{from_user_id}")]]))
        context.user_data["message_id"] = my_message.message_id
    else:
        created_user_challenge.delete()
        possible_challenge = possible_challenges.first()
        possible_challenge.opponent = User.objects.get(user_id=from_user_id)
        possible_challenge.save()
        user = User.objects.get(user_id=possible_challenge.user.user_id)
        opponent = User.objects.get(
            user_id=possible_challenge.opponent.user_id)
        created_challenge_info_user = context.bot_data[f"{user.user_id}"]["created_challenge"]
        created_challenge_info_opponent = context.bot_data[
            f"{opponent.user_id}"]["created_challenge"]
        context.bot.delete_message(
            chat_id=created_challenge_info_user[1], message_id=created_challenge_info_user[0])
        context.bot.delete_message(
            chat_id=created_challenge_info_opponent[1], message_id=created_challenge_info_opponent[0])
        context.bot.send_message(chat_id=user.user_id, text=f"Sizga tasodifiy raqib topildi. Sizga <a href='tg://user?id={opponent.user_id}'>{opponent.name}</a> raqiblik qiladi.Bellashuvni boshlash uchun \"Boshlash\" tugmasini bosing ", reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Boshlash", callback_data=f"challenge-confirmation-{possible_challenge.id}-start-user-{user.user_id}")]]), parse_mode=ParseMode.HTML)
        context.bot.send_message(chat_id=opponent.user_id, text=f"Sizga tasodifiy raqib topildi. Sizga <a href='tg://user?id={user.user_id}'>{user.name}</a> raqiblik qiladi .Bellashuvni boshlash uchun \"Boshlash\" tugmasini bosing ",
                                 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Boshlash", callback_data=f"challenge-confirmation-{possible_challenge.id}-start-opponent-{opponent.user_id}")]]), parse_mode=ParseMode.HTML)


def revansh(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data.split("-")
    challenge_id = data[1]
    from_user_id = data[2]
    to_user_id = data[3]

    user = User.objects.get(user_id=from_user_id)
    opponent = User.objects.get(user_id=to_user_id)
    challenge = Challenge.objects.get(id=challenge_id)

    context.bot.answer_callback_query(
        callback_query_id=query.id, text="So'rovingiz raqibingizga jo'natildi", show_alert=True)
    query.delete_message()

    user_challenge = challenge.create_user_challenge(from_user_id, challenge)
    user_challenge.opponent = opponent
    user_challenge.save()

    context.bot.send_message(chat_id=to_user_id, text="Raqibingiz siz bilan qayta bellashmoqchi. Bellashuvni qabul qilasizmi ?", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=consts.ACCEPT, callback_data=f"received-revansh-{consts.ACCEPT}-{user_challenge.user.user_id}-{user_challenge.id}")],
                                                                                                                                                                    [InlineKeyboardButton(
                                                                                                                                                                        text=consts.DECLINE, callback_data=f"received-revansh-{consts.DECLINE}-{user_challenge.user.user_id}-{user_challenge.id}")]
                                                                                                                                                                    ]))
    return consts.SHARING_CHALLENGE
