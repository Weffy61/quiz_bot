import logging
from enum import Enum, auto

import telegram
from telegram import Update, ForceReply
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, CallbackContext,
                          ConversationHandler)
from environs import Env
import redis

from questions import get_randon_question

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


class QuizState(Enum):
    QUESTION = auto()
    ANSWER = auto()


def start(update: Update, context: CallbackContext):
    user = update.effective_user
    kb_buttons = [['Новый вопрос', 'Сдаться'],
                  ['Мой счет']]
    reply_markup = telegram.ReplyKeyboardMarkup(kb_buttons)
    update.message.reply_markdown_v2(
        fr'Привет {user.mention_markdown_v2()}\! я бот для викторин. Для получения вопроса нажми «Новый вопрос',
        reply_markup=reply_markup,
    )


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Данный бот написан в рамках учебного проекта devman.org')


def handle_new_question_request(update: Update, context: CallbackContext):
    redis_db: redis.Redis = context.bot_data.get('redis')
    question, answer = get_randon_question()
    redis_db.set(update.effective_user.id, answer)
    update.message.reply_text(question)
    return QuizState.ANSWER


def give_up(update: Update, context: CallbackContext):
    redis_db: redis.Redis = context.bot_data.get('redis')
    update.message.reply_text(f'Ответ: {redis_db.get(update.effective_user.id).decode()}')
    handle_new_question_request(update, context)


def handle_solution_attempt(update: Update, context: CallbackContext):
    redis_db: redis.Redis = context.bot_data.get('redis')
    if update.message.text.lower() == redis_db.get(update.effective_user.id).decode().lower():
        update.message.reply_text('Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос')
        return ConversationHandler.END
    update.message.reply_text('Неправильно… Попробуешь ещё раз?')
    return QuizState.ANSWER


def main() -> None:
    env = Env()
    env.read_env()
    token = env.str('TELEGRAM_TOKEN')
    updater = Updater(token)
    redis_host = env.str('REDIS_HOST')
    redis_port = env.str('REDIS_POST')
    redis_password = env.str('REDIS_PASSWORD')
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
                MessageHandler(Filters.regex('^Сдаться$'), give_up),
                MessageHandler(Filters.text, handle_solution_attempt), ],
        },
        fallbacks=[],
    )
    dispatcher.bot_data['redis'] = redis_db
    dispatcher.add_handler(conv_handler)

    updater.start_polling()


if __name__ == '__main__':
    main()
