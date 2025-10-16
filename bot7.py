# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# ТОКЕН БОТА - ЗАМЕНИТЕ НА СВОЙ!
BOT_TOKEN = "8322357889:AAGmu3y8_2YZ-s_sE__7A_pNSa-q_hwKh2I"

# Создаем бота
bot = telebot.TeleBot(BOT_TOKEN)

# Файл блокировки для предотвращения множественных запусков
LOCK_FILE = "bot.lock"


def create_lock_file():
    """Создает файл блокировки"""
    try:
        with open(LOCK_FILE, 'w') as f:
            f.write(str(os.getpid()))
        return True
    except:
        return False


def remove_lock_file():
    """Удаляет файл блокировки"""
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
    except:
        pass


def check_single_instance():
    """Проверяет, что запущен только один экземпляр бота"""
    if os.path.exists(LOCK_FILE):
        logging.error("Бот уже запущен! Завершите предыдущий экземпляр.")
        return False
    return create_lock_file()


# База данных
def init_db():
    conn = sqlite3.connect('hearts.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            hearts INTEGER DEFAULT 0,
            username TEXT,
            last_daily_message TEXT
        )
    ''')
    conn.commit()
    conn.close()
    logging.info("База данных инициализирована")


# Получить количество сердец
def get_hearts(user_id):
    conn = sqlite3.connect('hearts.db')
    cursor = conn.cursor()
    cursor.execute('SELECT hearts FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    if result:
        hearts = result[0]
    else:
        hearts = 0
        cursor.execute('INSERT INTO users (user_id, hearts, username) VALUES (?, ?, ?)',
                       (user_id, hearts, ""))
        conn.commit()
    conn.close()
    return hearts


# Добавить сердце
def add_heart(user_id, username):
    conn = sqlite3.connect('hearts.db')
    cursor = conn.cursor()
    hearts = get_hearts(user_id) + 1
    cursor.execute('UPDATE users SET hearts = ?, username = ? WHERE user_id = ?',
                   (hearts, username, user_id))
    conn.commit()
    conn.close()
    return hearts


# Мотивационные фразы для Ольги (расширенный список)
MOTIVATIONAL_PHRASES = [
    "Привет, солнышко моё! ☀️ Пусть твой день будет ярким и счастливым!",
    "Доброе утро, моя прекрасная Олечка! 💫 Ты справишься со всеми задачами сегодня!",
    "Проснись, моя радость! 🌷 Сегодня тебя ждет много прекрасного!",
    "Привет, котёнок мой! 🐱 Удачного дня и помни - я всегда о тебе думаю!",
    "Утро доброе, моя умничка! 🌟 Пусть сегодня все получается легко!",
    "Просыпайся, моя хорошая! 💖 Этот день создан для тебя!",
    "Привет, зайка моя! 🐰 Улыбнись, и весь мир улыбнется тебе в ответ!",
    "Доброе утро, Олечка! 🌸 Ты самая красивая и умная!",
    "Проснись, солнце! 🌞 Сегодня твой день сиять!",
    "Привет, моя лапочка! 💕 Ты делаешь мир лучше!",
    "Доброе утро, радость моя! ✨ Пусть сегодня исполнятся твои желания!",
    "Просыпайся, умница! 🌼 Ты можешь всё, что захочешь!",
    "Привет, рыбка моя! 🐠 Плыви по жизни уверенно!",
    "Утро доброе, моё счастье! 💝 Сегодня будет много приятных моментов!",
    "Проснись, прелесть! 🌹 Ты уникальна и неповторима!",
    "Привет, птичка моя! 🐦 Лети к своим мечтам!",
    "Доброе утро, звёздочка! ⭐️ Свети ярко сегодня!",
    "Просыпайся, бусинка! 📿 Ты драгоценность!",
    "Привет, муза моя! 🎨 Вдохновляй всех вокруг!",
    "Доброе утро, тигрица! 🐯 Будь смелой и сильной!",
    "Проснись, фея моя! 🧚‍♀️ Твори волшебство сегодня!",
    "Привет, принцесса! 👑 Носи корону с гордостью!",
    "Доброе утро, чемпионка! 🏆 Ты победишь все трудности!",
    "Просыпайся, радуга! 🌈 Неси цвет в этот мир!",
    "Привет, пчелка моя! 🐝 Трудись усердно, но отдыхай!",
    "Доброе утро, бабочка! 🦋 Превращайся в лучшую себя!",
    "Проснись, конфетка! 🍬 Будь сладкой и любимой!",
    "Привет, героиня! 🦸‍♀️ Спасай мир своей добротой!",
    "Доброе утро, волшебница! 🔮 Твои мечты сбываются!",
    "Просыпайся, сокровище! 💎 Ты бесценна!",
    "Привет, радость моя! 😊 Твое присутствие делает мир лучше!",
    "Доброе утро, моя хорошая! 🌞 Пусть день принесет только приятные сюрпризы!",
    "Проснись, красавица! 🌸 Твоя улыбка - самое ценное сокровище!",
    "Привет, мой ангелочек! 👼 Ты приносишь в мою жизнь столько света!",
    "Утро доброе, моя умничка! 💖 Сегодня все будет так, как ты захочешь!",
    "Просыпайся, солнышко! 🌅 Новый день - новые возможности для счастья!",
    "Привет, моя ненаглядная! 💕 Ты самое лучшее, что случилось в моей жизни!",
    "Доброе утро, моя прекрасная! ✨ Ты заслуживаешь всего самого лучшего!",
    "Проснись, моя любимая! 🌹 Каждый день с тобой - это подарок!",
    "Привет, сердечко мое! 💘 Ты наполняешь мою жизнь смыслом!",
    "Доброе утро, моя королева! 👑 Прави свой день с уверенностью!",
    "Просыпайся, моя мечта! 🌠 Ты можешь достичь всего, о чем мечтаешь!",
    "Привет, моё счастье! 😍 Твое присутствие делает любой день праздником!",
    "Доброе утро, моя радость! 💫 Пусть сегодняшний день будет волшебным!",
    "Проснись, моя хорошая! 🌼 Ты сильнее, чем думаешь, и красивее, чем представляешь!",
    "Привет, моя бусинка! 💎 Ты уникальна и неповторима!",
    "Доброе утро, моя звёздочка! ⭐️ Свети так, чтобы все видели твою красоту!",
    "Просыпайся, моя муза! 🎨 Вдохновляй всех вокруг сегодня своей энергией!",
    "Привет, моя тигрица! 🐯 Будь смелой и решительной сегодня!",
    "Доброе утро, моя фея! 🧚‍♀️ Твори волшебство своими добрыми делами!",
]

# Сообщения для разных времен
TIME_MESSAGES = {
    14: "Я тебя люблю ❤️",
    18: "Ты самая яркая ✨",
    20: "Приятных тебе снов 🌙💫",
    3: "Знаю что ты спишь, просто люблю тебя 😴💕"
}

# Триггеры и ответы
TRIGGERS = {
    "мне плохо": "Боже мой, малышка что случилось 😢 Я всегда рядом и поддержу тебя, не важно в сети я или нет ❤️ Позвони мне и расскажи мне все что на душе, я всегда готов выслушать и помочь тебе 💕 Ты не одна, я с тобой всегда, даже на расстоянии 🤗",

    "мне скучно": "Ох, скучно? Давай развеем скуку вместе! 😄 Вот тебе ссылка на смешные анекдоты: https://www.anekdot.ru\nНадеюсь, они поднимут тебе настроение! 💫 А еще можешь позвонить мне - вместе всегда веселее! 🎉",

    "я тебя люблю": "Я тебя люблю как 30000 раз до луны и обратно! 🌙🚀💫 Моя любовь к тебе безгранична как вселенная и ярче чем миллион солнц! ☀️💖 Ты - самое дорогое, что есть в моей жизни, и я бесконечно благодарен за каждую секунду с тобой! 💕",

    "скучно": "Если скучно, давай я подниму тебе настроение! 😊 Вот смешные анекдоты: https://www.anekdot.ru\nИ помни - ты всегда можешь позвонить мне! 📞💕",

    "грустно": "Милый мой человечек, не грусти 🥺 Я здесь для тебя! Хочешь, расскажу тебе как сильно ты меняешь мир к лучшему просто своим существованием? 💫 Ты - лучик света в этом мире! 🌞",

    "устала": "Моя хорошая, ты так много стараешься! 🥺 Помни, что отдых - это тоже важная работа 💕 Приляг, отдохни, а я буду думать о тебе и посылать тебе силы и энергию! ✨ Ты заслуживаешь самого лучшего отдыха! 🌙"
}


# Основная клавиатура (всегда видна)
def create_main_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = telebot.types.KeyboardButton("Проверить сердечки 💕")
    button2 = telebot.types.KeyboardButton("Информация ℹ️")
    keyboard.add(button1, button2)
    return keyboard


# Клавиатура для подтверждения мотивации
def create_motivation_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = telebot.types.KeyboardButton("Мотивация принята! 💖")
    keyboard.add(button)
    return keyboard


# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    user_id = message.from_user.id

    get_hearts(user_id)

    if user_name and "ольга" in user_name.lower():
        bot.send_message(
            message.chat.id,
            f"Привет, моя любимая Олечка! 💖\n"
            f"Я буду с тобой всегда - днем и ночью! 🌞🌙\n"
            f"Мотивация в 10:00, а в течение дня - приятные сюрпризы! ✨\n"
            f"Бот работает в АВТОНОМНОМ режиме 24/7! 🚀",
            reply_markup=create_main_keyboard()
        )
    else:
        bot.send_message(
            message.chat.id,
            "Привет! Этот бот создан специально для Ольги 💕",
            reply_markup=create_main_keyboard()
        )


# Обработка кнопки "Информация"
@bot.message_handler(func=lambda message: message.text == "Информация ℹ️")
def show_info(message):
    info_text = """
🤖 **ИНФОРМАЦИЯ О БОТЕ**

💝 **Автономный режим 24/7:**
• Бот работает постоянно на сервере
• Не требует включенного компьютера
• Отправляет сообщения автоматически

🕐 **Расписание сообщений:**
• 10:00 - Утренняя мотивация 💫
• 14:00 - Приятное сообщение ❤️  
• 18:00 - Вечерний комплимент ✨
• 20:00 - Пожелание на ночь 🌙
• 03:00 - Ночное сообщение 😴

🎁 **Система подарков:**
• Каждые 50 сердец - специальный подарок!
• 50❤️, 100❤️, 150❤️, 200❤️ и так до 1000❤️

💬 **Бот реагирует на слова:**
• "мне плохо" - поддержка и забота 🤗
• "мне скучно" или "скучно" - развлечения 😄  
• "я тебя люблю" - романтичный ответ 💕
• "грустно" - утешение и мотивация 🌟
• "устала" - забота об отдыхе 💤

💕 **Цель бота:** 
Напоминать Олечке каждый день о том, какая она особенная, любимая и важная! ✨
    """
    bot.send_message(message.chat.id, info_text, reply_markup=create_main_keyboard())


# Обработка кнопки "Мотивация принята!"
@bot.message_handler(func=lambda message: message.text == "Мотивация принята! 💖")
def accept_motivation(message):
    user_id = message.from_user.id
    username = message.from_user.first_name

    hearts = add_heart(user_id, username)

    # Проверка достижений
    milestone_message = ""
    if hearts % 50 == 0 and hearts > 0:
        milestone_message = f"\n\n🎉 ПОЗДРАВЛЯЮ! Ты набрала {hearts} сердец! 🎉\nОбратись к мужу за подарком! 💝"

    # Случайный комплимент после принятия мотивации
    compliments = [
        "Ты сегодня просто невероятна! 🌟",
        "Как же мне повезло с тобой! 💕",
        "Твоя улыбка делает мой день лучше! 😊",
        "Ты справишься с любыми задачами! 💪",
        "Ты вдохновляешь меня каждый день! ✨",
        "С тобой возможно всё! 🚀",
        "Ты - моя самая большая гордость! 🌟",
        "Как же я тебя люблю! ❤️"
    ]

    compliment = random.choice(compliments)

    bot.send_message(
        message.chat.id,
        f"Отлично! Мотивация принята! 💖\n"
        f"Твой счёт: {hearts} сердец\n"
        f"{compliment}{milestone_message}",
        reply_markup=create_main_keyboard()
    )


# Обработка кнопки "Проверить сердечки"
@bot.message_handler(func=lambda message: message.text == "Проверить сердечки 💕")
def check_hearts(message):
    user_id = message.from_user.id
    hearts = get_hearts(user_id)

    next_gift = 50 - (hearts % 50)
    if next_gift == 50:
        next_gift = 0

    if hearts >= 1000:
        status = "🏆 Ты достигла максимума! Ты чемпионка!"
    elif hearts >= 500:
        status = "🌟 Невероятно! Ты на полпути к вершине!"
    elif hearts >= 100:
        status = "💫 Отлично продвигаешься!"
    else:
        status = "💕 Продолжай в том же духе!"

    # Случайное мотивирующее сообщение
    motivators = [
        "Каждое сердечко - это твоя маленькая победа! 🎯",
        "Ты собираешь не просто сердечки, а частички нашей любви! 💞",
        "С каждым днем ты становишься все сильнее! 💪",
        "Твоя целеустремленность восхищает! 🌟",
        "Я так горжусь тобой! 🥰",
        "Ты - пример для подражания! 👑",
        "Твоя настойчивость вдохновляет! ✨"
    ]

    motivator = random.choice(motivators)

    bot.send_message(
        message.chat.id,
        f"💕 **Твой текущий счёт:** {hearts} сердец!\n"
        f"🎁 **До следующего подарка:** {next_gift} сердец\n"
        f"✨ **Статус:** {status}\n"
        f"💫 **{motivator}**",
        reply_markup=create_main_keyboard()
    )


# Обработка триггерных сообщений
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id
    text = message.text.lower()

    # Проверяем триггеры
    for trigger, response in TRIGGERS.items():
        if trigger in text:
            bot.send_message(message.chat.id, response, reply_markup=create_main_keyboard())
            return

    # Если не триггер, но имя Ольга - отвечаем мило
    user_name = message.from_user.first_name
    if user_name and "ольга" in user_name.lower():
        cute_responses = [
            "Я тебя слышу, солнышко! 💫",
            "Всегда рад твоим сообщениям! 💕",
            "Ты - самое лучшее, что есть в моей жизни! 🌟",
            "Как же я люблю наши разговоры! 💖",
            "Твое сообщение сделало мой день лучше! ✨",
            "Обожаю получать сообщения от тебя! 😊",
            "Ты наполняешь мою жизнь смыслом! 💫"
        ]
        response = random.choice(cute_responses)
        bot.send_message(message.chat.id, response, reply_markup=create_main_keyboard())
    else:
        bot.send_message(
            message.chat.id,
            "Используй кнопки ниже для управления ботом! 💕",
            reply_markup=create_main_keyboard()
        )


# Функция для отправки сообщений по расписанию
def send_scheduled_messages():
    last_sent_hours = {}  # Для отслеживания отправленных сообщений по часам

    while True:
        try:
            now = datetime.now()
            current_hour = now.hour
            current_minute = now.minute

            # Проверяем все времена для отправки (в начале часа)
            if current_minute == 0:
                if current_hour in TIME_MESSAGES and last_sent_hours.get(current_hour) != now.day:
                    logging.info(f"Отправка сообщения для времени {current_hour}:00")

                    conn = sqlite3.connect('hearts.db')
                    cursor = conn.cursor()
                    cursor.execute('SELECT user_id FROM users')
                    users = cursor.fetchall()
                    conn.close()

                    message_text = TIME_MESSAGES[current_hour]

                    for user_tuple in users:
                        user_id = user_tuple[0]
                        try:
                            bot.send_message(user_id, message_text, reply_markup=create_main_keyboard())
                            logging.info(f"Сообщение в {current_hour}:00 отправлено пользователю {user_id}")
                        except Exception as e:
                            logging.error(f"Ошибка отправки пользователю {user_id}: {e}")

                    last_sent_hours[current_hour] = now.day

            # Ежедневная мотивация в 10:00
            if current_hour == 10 and current_minute == 0 and last_sent_hours.get('motivation') != now.day:
                logging.info("Отправка ежедневных мотивационных сообщений...")

                conn = sqlite3.connect('hearts.db')
                cursor = conn.cursor()
                cursor.execute('SELECT user_id FROM users')
                users = cursor.fetchall()
                conn.close()

                for user_tuple in users:
                    user_id = user_tuple[0]
                    try:
                        phrase = random.choice(MOTIVATIONAL_PHRASES)
                        bot.send_message(user_id, phrase, reply_markup=create_motivation_keyboard())
                        logging.info(f"Мотивация отправлена пользователю {user_id}")
                    except Exception as e:
                        logging.error(f"Ошибка отправки мотивации {user_id}: {e}")

                last_sent_hours['motivation'] = now.day
                time.sleep(60)  # Ждем минуту чтобы не отправлять повторно

            time.sleep(30)  # Проверяем каждые 30 секунд

        except Exception as e:
            logging.error(f"Ошибка в scheduled_messages: {e}")
            time.sleep(60)


# Запуск бота с обработкой ошибок
def run_bot():
    # Проверяем, что запущен только один экземпляр
    if not check_single_instance():
        logging.error("Не удалось запустить бота: уже запущен другой экземпляр!")
        print("❌ ОШИБКА: Бот уже запущен! Завершите предыдущую версию.")
        sys.exit(1)

    try:
        logging.info("Запуск бота в автономном режиме...")
        init_db()

        # Запускаем поток для расписания сообщений
        schedule_thread = threading.Thread(target=send_scheduled_messages)
        schedule_thread.daemon = True
        schedule_thread.start()

        logging.info("🤖 Бот запущен в АВТОНОМНОМ режиме 24/7!")
        print("=" * 60)
        print("🤖 БОТ ЗАПУЩЕН В АВТОНОМНОМ РЕЖИМЕ!")
        print("💫 Теперь он будет работать постоянно")
        print("🕐 Расписание: 10:00, 14:00, 18:00, 20:00, 03:00")
        print("⏹️ Для остановки нажмите Ctrl+C")
        print("=" * 60)

        # Основной цикл бота с перезапуском при ошибках
        while True:
            try:
                bot.polling(none_stop=True, interval=1, timeout=60)
            except Exception as e:
                logging.error(f"Ошибка polling: {e}")
                logging.info("Перезапуск polling через 10 секунд...")
                time.sleep(10)

    except Exception as e:
        logging.error(f"Критическая ошибка бота: {e}")
    finally:
        # Всегда удаляем файл блокировки при завершении
        remove_lock_file()
        logging.info("Бот остановлен")


if __name__ == "__main__":
    # Обработка Ctrl+C для graceful shutdown
    try:
        run_bot()
    except KeyboardInterrupt:
        print("\n🛑 Остановка бота...")
        remove_lock_file()
        print("👋 Бот остановлен!")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        remove_lock_file()
