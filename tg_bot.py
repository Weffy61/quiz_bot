import logging
from enum import Enum, auto

import telegram
from telegram import Update
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, CallbackContext,
                          ConversationHandler)
from environs import Env
import redis

from notifications import TelegramLogsHandler, handle_error
from parse_path import parse_question_path
from questions import get_random_question


logger = logging.getLogger('Telegram logger')


class QuizState(Enum):
    QUESTION = auto()
    ANSWER = auto()


def start(update: Update, context: CallbackContext):
    user = update.effective_user
    kb_buttons = [['Новый вопрос', 'Сдаться'],
                  ['Мой счет']]
    reply_markup = telegram.ReplyKeyboardMarkup(kb_buttons)
    update.message.reply_markdown_v2(
        fr'Привет {user.mention_markdown_v2()}\! я бот для викторин\. Для получения вопроса нажми «Новый вопрос',
        reply_markup=reply_markup,
    )


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Данный бот написан в рамках учебного проекта devman.org')


def handle_new_question_request(update: Update, context: CallbackContext):
    try:
        redis_db: redis.Redis = context.bot_data.get('redis')
        questions_path = context.bot_data.get('questions_path')
        question, answer = get_random_question(questions_path)
        redis_db.set(update.effective_user.id, answer)
        update.message.reply_text(question)
        return QuizState.ANSWER
    except Exception as e:
        handle_error(e)


def give_up(update: Update, context: CallbackContext):
    try:
        redis_db: redis.Redis = context.bot_data.get('redis')
        update.message.reply_text(f'Ответ: {redis_db.get(update.effective_user.id).decode()}')
        handle_new_question_request(update, context)
    except Exception as e:
        handle_error(e)


def handle_solution_attempt(update: Update, context: CallbackContext):
    try:
        redis_db: redis.Redis = context.bot_data.get('redis')
        if update.message.text.lower() == redis_db.get(update.effective_user.id).decode().lower():
            update.message.reply_text('Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос')
            return ConversationHandler.END
        update.message.reply_text('Неправильно… Попробуешь ещё раз?')
        return QuizState.ANSWER
    except Exception as e:
        handle_error(e)


def main():
    questions_path = parse_question_path()
    env = Env()
    env.read_env()
    token = env.str('TELEGRAM_TOKEN')
    updater = Updater(token)
    redis_host = env.str('REDIS_HOST')
    redis_port = env.str('REDIS_POST')
    redis_password = env.str('REDIS_PASSWORD')
    telegram_logs_token = env.str('TELEGRAM_LOGS_TOKEN')
    chat_id = env.int('TELEGRAM_CHAT_ID')
    tg_bot_logs = telegram.Bot(token=telegram_logs_token)
    logger.setLevel(logging.INFO)
    telegram_logs_handler = TelegramLogsHandler(
        tg_bot=tg_bot_logs,
        chat_id=chat_id
    )
    logger.addHandler(telegram_logs_handler)
    logger.info('Quiz bot запущен в телеграм')
    redis_db = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^Новый вопрос$'), handle_new_question_request)],
        states={
            QuizState.QUESTION: [MessageHandler(Filters.regex('^Новый вопрос$'), handle_new_question_request)],
            QuizState.ANSWER: [
                MessageHandler(Filters.regex('^Новый вопрос$'), handle_new_question_request),
                MessageHandler(Filters.regex('^Сдаться$'), give_up),
                MessageHandler(Filters.text, handle_solution_attempt), ],
        },
        fallbacks=[],
    )
    dispatcher.bot_data['redis'] = redis_db
    dispatcher.bot_data['questions_path'] = questions_path
    dispatcher.add_handler(conv_handler)
    while True:
        try:
            updater.start_polling()
        except Exception as e:
            handle_error(e)


if __name__ == '__main__':
    main()
