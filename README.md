# Quiz бот

Телеграм и vk бот мини-игра - викторина.

## Установка

```commandline
git clone https://github.com/Weffy61/quiz_bot.git
```

## Установка зависимостей
Переход в директорию с исполняемым файлом

```commandline
cd quiz_bot
```

Установка
```commandline
pip install -r requirements.txt
```

## Предварительная подготовка

### Подготовка vk

Создайте группу в [vk](vk.com), получите [API для сообщений сообществ](https://dev.vk.com/ru/api/community-messages/getting-started?ref=old_portal), установите права доступа для сообщений 
сообщества. Включите сообщения сообщества в настройках группы. Также в настройках сообщения включиите возможности ботов.  

### Подготовка telegram

Создайте 2 ботов в [botfather](https://t.me/BotFather). 1-ый бот будет отвечать на вопросы, 2-ой бот будет 
использоваться для мониторинга состояния бота в vk и 1-ого бота.

### Подготовка Redis
[Установите](https://timeweb.cloud/tutorials/redis/ustanovka-i-nastrojka-redis-dlya-raznyh-os) Redis, 
либо воспользуйтесь [облачным сервисом](https://redis.com). Получите адрес, порт и пароль.

## Создание и настройка .env

Создайте в корне папки `quiz_bot` файл `.env`. Откройте его для редактирования любым текстовым редактором
и запишите туда данные в таком формате: `ПЕРЕМЕННАЯ=значение`.
Доступны следующие переменные:
 - TELEGRAM_TOKEN - ваш телеграм бот API ключ(бот, который отвечает на вопросы).
 - VK_GROUP_KEY - Ваш vk API ключ(для бота, который отвечает на вопросы).
 - TELEGRAM_LOGS_TOKEN - ваш телеграм бот API ключ(бот, который отправляет уведомления в личку/канал/чат, при наличии, 
каких-либо ошибок, а также уведомление о старте бота).
 - TELEGRAM_CHAT_ID - ваш telegram id  куда вы будете получать уведомления о  состоянии бота. Для получаения отпишите в 
[бота](https://telegram.me/userinfobot).
 - REDIS_HOST - ваш Redis адрес
 - REDIS_POST - ваш Redis порт
 - REDIS_PASSWORD - ваш Redis пароль


## Запуск телеграм бота

```commandline
python tg_bot.py --path
```
Аргументы:  

- --path - путь к файлу с вопросами. По умолчанию берется файл `questions/1vs1200.txt`

Пример работы телеграм бота:  
![telegram example](https://dvmn.org/filer/canonical/1569215494/324/)

Образец бота:
https://t.me/quiz_dvmnq_bot

## Запуск бота в vk

```commandline
python vk_bot.py --path
```

Аргументы:  

- --path - путь к файлу с вопросами. По умолчанию берется файл `questions/1vs1200.txt`

Пример работы vk бота:

![vk example](https://dvmn.org/filer/canonical/1569215498/325/)

Образец бота:
https://vk.com/club224499765
