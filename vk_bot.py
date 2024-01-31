import logging
import random

from environs import Env
import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import telegram
import redis

from parse_path import parse_question_path
from questions import get_random_question
from notifications import TelegramLogsHandler, handle_error


logger = logging.getLogger('Telegram logger')


def get_new_question(event, vk_api, redis_connect, keyboard, path):
    question, answer = get_random_question(path)
    redis_connect.set(event.user_id, answer)
    vk_api.messages.send(
        user_id=event.user_id,
        message=question,
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard()
    )


def give_up(event, vk_api, redis_connect, keyboard, path):
    vk_api.messages.send(
        user_id=event.user_id,
        message=f'Ответ: {redis_connect.get(event.user_id).decode()}',
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard()
    )
    get_new_question(event, vk_api, redis_connect, keyboard, path)


def reply(event, vk_api, redis_connect, keyboard):
    if event.text.lower() == redis_connect.get(event.user_id).decode().lower():
        vk_api.messages.send(
            user_id=event.user_id,
            message='Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос',
            random_id=random.randint(1, 1000),
            keyboard=keyboard.get_keyboard()
        )
    else:
        vk_api.messages.send(
            user_id=event.user_id,
            message='Неправильно… Попробуешь ещё раз?',
            random_id=random.randint(1, 1000),
            keyboard=kb.get_keyboard()
        )


def handle_event(event, vk_api, redis_connect, keyboard, questions_path):
    if event.text == 'Сдаться':
        give_up(event, vk_api, redis_connect, keyboard, questions_path)
    elif event.text == 'Новый вопрос':
        get_new_question(event, vk_api, redis_connect, keyboard, questions_path)
    else:
        reply(event, vk_api, redis_connect, keyboard)


if __name__ == "__main__":
    questions_path = parse_question_path()
    env = Env()
    env.read_env()
    redis_host = env.str('REDIS_HOST')
    redis_port = env.str('REDIS_POST')
    redis_password = env.str('REDIS_PASSWORD')
    redis_db = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password)
    vk_group_key = env.str('VK_GROUP_KEY')
    telegram_logs_token = env.str('TELEGRAM_LOGS_TOKEN')
    chat_id = env.int('TELEGRAM_CHAT_ID')
    tg_bot_logs = telegram.Bot(token=telegram_logs_token)
    logger.setLevel(logging.INFO)
    telegram_logs_handler = TelegramLogsHandler(
        tg_bot=tg_bot_logs,
        chat_id=chat_id
    )
    logger.addHandler(telegram_logs_handler)
    logger.info('Quiz bot запущен в vk')

    vk_session = vk.VkApi(token=vk_group_key)
    vk = vk_session.get_api()
    while True:
        try:
            longpoll = VkLongPoll(vk_session)
            kb = VkKeyboard()
            kb.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
            kb.add_button('Сдаться', color=VkKeyboardColor.SECONDARY)
            kb.add_line()
            kb.add_button('Мой счет')
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me and redis_db.exists(event.user_id):
                    handle_event(event, vk, redis_db, kb, questions_path)
                elif event.type == VkEventType.MESSAGE_NEW and event.to_me and not redis_db.exists(event.user_id):
                    vk.messages.send(
                        user_id=event.user_id,
                        message='Для получения вопроса нажми «Новый вопрос',
                        random_id=random.randint(1, 1000),
                        keyboard=kb.get_keyboard()
                    )

        except Exception as e:
            handle_error(e)
            continue
