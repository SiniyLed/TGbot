import logging
import re
import paramiko
import psycopg2
import os
import json

from dotenv import load_dotenv
from telegram import ForceReply, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Application, CommandHandler, Updater, ContextTypes, MessageHandler, filters,
                          ConversationHandler, CallbackContext, CallbackQueryHandler)

#Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

EMAIL, PHONE = range(2)
ADD_PHONE, ASK_ADD_PHONE = range(2)

load_dotenv()

# Регулярные выражения
EMAIL_PATTERN = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
PHONE_PATTERN = r'(?:\+7|8)[\s-]?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}'
PASSWORD_REGEX = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()])[A-Za-z\d!@#$%^&*()]{8,}$"

# Настройки подключения к серверу
SSH_HOST = os.getenv('RM_HOST')
SSH_PORT = os.getenv('RM_PORT')
SSH_USER = os.getenv('RM_USER')
SSH_PASSWORD = os.getenv('RM_PASSWORD')
TOKEN = os.getenv('TOKEN')

# Обработчик команды /start
async def start(update: Update, context) -> None:
    await update.message.reply_text(
        "Привет! Я многофункциональный бот. Если Вы хотите узнать, что я умею, введите команду /help")


# Обработчик команды /help
async def help_command(update: Update, context) -> None:
    await update.message.reply_text(
        "Мои команды:\n"
        "/start - начать диалог\n"
        "/find_email - найти email в тексте\n"
        "/find_phone_number - найти номер телефона в тексте\n"
        "/verify_password - проверка пароля на сложность\n"
        "/get_release - сбор информации о системе\n"
        "/get_uname - сбор информации о времени работы\n"
        "/get_uptime - сбор информации о состоянии файловой системы\n"
        "/get_df - Сбор информации о состоянии оперативной памяти\n"
        "/get_free - Сбор информации о производительности системы\n"
        "/get_mpstat - Сбор информации о работающих в данной системе пользователях\n"
        "/get_w - Сбор логов\n"
        "/get_auths - Последние 10 входов в систему\n"
        "/get_critical - Последние 5 критических события\n"
        "/get_ps - Сбор информации о запущенных процессах\n"
        "/get_ss - Сбор информации об используемых портах\n"
        "/get_apt_list - Сбор информации об установленных пакетах\n"
        "/search_package <имя_пакета> - Поиск информации о пакете, название которого будет запрошено у пользователя\n"
        "/get_services - Сбор информации о запущенных сервисах\n"
        "/get_repl_logs - Вывод логов из psql\n"
        "/get_emails - Вывод бд с email\n"
        "/get_phone_number - Вывод бд с номерами телефонов")


# Обработчик команды /find_email
async def find_email(update: Update, context) -> int:
    await update.message.reply_text("Отправьте текст, в котором нужно найти email-адреса.")
    return EMAIL  # Переход на следующий этап — ожидание текста


# Обработчик команды /find_phone_number
async def find_phone_number(update: Update, context) -> int:
    await update.message.reply_text("Отправьте текст, в котором нужно найти номера телефонов.")
    return PHONE  # Переход на следующий этап — ожидание текста


# Обработчик текста для поиска email
async def handle_email(update: Update, context) -> int:
    text = update.message.text
    emails = re.findall(EMAIL_PATTERN, text)

    if emails:
        button_msg = InlineKeyboardButton("Сохранить в БД", callback_data=json.dumps(("email", emails)))
        inline_keyboard = InlineKeyboardMarkup([[button_msg]])
        await update.message.reply_text(f"Найденные email-адреса:\n" + "\n".join(emails), reply_markup=inline_keyboard)
        print(emails)
    else:
        await update.message.reply_text("Email-адреса не найдены.")

    return ConversationHandler.END  # Завершение разговора


# Обработчик текста для поиска номера телефона
async def handle_phone_number(update: Update, context) -> int:
    text = update.message.text
    phone_numbers = re.findall(PHONE_PATTERN, text)

    if phone_numbers:
        button_msg = InlineKeyboardButton("Сохранить в БД", callback_data=json.dumps(("phone", phone_numbers)))
        inline_keyboard = InlineKeyboardMarkup([[button_msg]])
        await update.message.reply_text(f"Найденные номера телефонов:\n" + "\n".join(phone_numbers), reply_markup=inline_keyboard)
        print(phone_numbers)

    else:
        await update.message.reply_text("Номера телефонов не найдены.")

    return ConversationHandler.END  # Завершение разговора


async def fetch_to_db(update: Update, context):
    dbname = os.getenv('DB_DATABASE')
    dbuser = os.getenv('DB_USER')
    dbpassword = os.getenv('DB_PASSWORD')
    dbhost = os.getenv('DB_HOST')
    data = json.loads(update.callback_query.data)
    print(data)

    if (data[0] == "phone"):
        try:
            connection = psycopg2.connect(dbname=dbname, user=dbuser, password=dbpassword, host=dbhost)
            cursor = connection.cursor()

            for phone_numbers in data[1]:
                cursor.execute("INSERT INTO phone(phone_number) VALUES (%s)", (phone_numbers,))

            connection.commit()
            cursor.close()
            connection.close()
            button_msg = InlineKeyboardButton(
                "Номера телефонов успешно сохранены в базу данных.",
                 callback_data=json.dumps(("phone", data[1]))
            )
            inline_keyboard = InlineKeyboardMarkup([[button_msg]])
            await update.callback_query.edit_message_reply_markup(inline_keyboard)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            button_msg = InlineKeyboardButton(
                "Не удалось сохранить номера телефонов в базу данных.",
                callback_data=json.dumps(("phone", data[1]))
            )
            inline_keyboard = InlineKeyboardMarkup([[button_msg]])
            await update.callback_query.edit_message_reply_markup(inline_keyboard)
    elif (data[0] == "email"):
        try:
            connection = psycopg2.connect(dbname=dbname, user=dbuser, password=dbpassword, host=dbhost)
            cursor = connection.cursor()

            for emails in data[1]:
                cursor.execute("INSERT INTO email(email) VALUES (%s)", (emails,))

            connection.commit()
            cursor.close()
            connection.close()
            button_msg = InlineKeyboardButton(
                "Почтовые адреса успешно сохранены в базу данных.",
                callback_data=json.dumps(("email", data[1]))
            )
            inline_keyboard = InlineKeyboardMarkup([[button_msg]])
            await update.callback_query.edit_message_reply_markup(inline_keyboard)

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            button_msg = InlineKeyboardButton(
                "Не удалось сохранить почтовые адреса в базу данных.",
                callback_data=json.dumps(("email", data[1]))
            )
            inline_keyboard = InlineKeyboardMarkup([[button_msg]])
            await update.callback_query.edit_message_reply_markup(inline_keyboard)


# Обработчик команды отмены
async def cancel(update: Update, context) -> int:
    await update.message.reply_text("Операция отменена.")
    return ConversationHandler.END


# Функция для проверки сложности пароля
def check_password_complexity(password):
    if re.match(PASSWORD_REGEX, password):
        return 'Пароль сложный'
    else:
        return 'Пароль простой'


# Команда /verify_password
async def verify_password(update: Update, context):
    await update.message.reply_text("Пожалуйста, введите пароль для проверки.")


# Обработка сообщения с паролем
async def handle_password(update: Update, context):
    password = update.message.text
    result = check_password_complexity(password)
    await update.message.reply_text(result)


def execute_ssh_command(command):
    try:
        # Устанавливаем SSH соединение
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SSH_HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASSWORD)

        # Выполнение команды
        stdin, stdout, stderr = ssh.exec_command(command)
        result = stdout.read().decode('utf-8') or stderr.read().decode('utf-8')

        # Закрываем соединение
        ssh.close()
        return result.strip()
    except Exception as e:
        return f"Ошибка: {str(e)}"


# Обработчики команд

async def get_release(update: Update, context: CallbackContext) -> None:
    result = execute_ssh_command('cat /etc/os-release')
    await update.message.reply_text(result)


async def get_uname(update: Update, context: CallbackContext) -> None:
    result = execute_ssh_command('uname -a')
    await update.message.reply_text(result)


async def get_uptime(update: Update, context: CallbackContext) -> None:
    result = execute_ssh_command('uptime')
    await update.message.reply_text(result)


async def get_df(update: Update, context: CallbackContext) -> None:
    result = execute_ssh_command('df -h')
    await update.message.reply_text(result)


async def get_free(update: Update, context: CallbackContext) -> None:
    result = execute_ssh_command('free -h')
    await update.message.reply_text(result)


async def get_mpstat(update: Update, context: CallbackContext) -> None:
    result = execute_ssh_command('mpstat')
    await update.message.reply_text(result)


async def get_w(update: Update, context: CallbackContext) -> None:
    result = execute_ssh_command('w')
    await update.message.reply_text(result)


async def get_auths(update: Update, context: CallbackContext) -> None:
    result = execute_ssh_command('tail -n 10 /var/log/auth.log')
    await update.message.reply_text(result)


async def get_critical(update: Update, context: CallbackContext) -> None:
    result = execute_ssh_command('journalctl -p crit -n 5')
    await update.message.reply_text(result)


async def get_ps(update: Update, context: CallbackContext) -> None:
    result = execute_ssh_command('ps aux')
    await update.message.reply_text(result)


async def get_ss(update: Update, context: CallbackContext) -> None:
    result = execute_ssh_command('ss -tuln')
    await update.message.reply_text(result)


async def get_apt_list(update: Update, context: CallbackContext) -> None:
    result = execute_ssh_command('apt list --installed')
    await update.message.reply_text(result)


async def search_package(update: Update, context: CallbackContext) -> None:
    if len(context.args) == 0:
        await update.message.reply_text("Введите название пакета: /search_package <имя_пакета>")
        return
    package_name = context.args[0]
    result = execute_ssh_command(f'apt list --installed | grep {package_name}')
    await update.message.reply_text(result)


async def get_services(update: Update, context: CallbackContext) -> None:
    result = execute_ssh_command('systemctl list-units --type=service')
    await update.message.reply_text(result)

async def get_repl_logs(update: Update, context: CallbackContext) -> None:
    result = execute_ssh_command('cat  /var/log/postgresql/postgresql-16-main.log')
    await update.message.reply_text(result)


def load_emails():
    dbname = os.getenv('DB_DATABASE')
    dbuser = os.getenv('DB_USER')
    dbpassword = os.getenv('DB_PASSWORD')
    dbhost = os.getenv('DB_HOST')
    try:
        connection = psycopg2.connect(dbname=dbname, user=dbuser, password=dbpassword, host=dbhost)
        cursor = connection.cursor()
        cursor.execute("SELECT email FROM email")
        return [elem[0] for elem in cursor.fetchall()]
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)



# Обработчик команды /get_emails
async def get_emails(update: Update, context: CallbackContext) -> None:
    emails = load_emails()
    if emails:
        await update.message.reply_text("\n".join(emails))
    else:
        await update.message.reply_text("Нет доступных email-адресов.")


def load_phone():
    dbname = os.getenv('DB_DATABASE')
    dbuser = os.getenv('DB_USER')
    dbpassword = os.getenv('DB_PASSWORD')
    dbhost = os.getenv('DB_HOST')
    try:
        connection = psycopg2.connect(dbname=dbname, user=dbuser, password=dbpassword, host=dbhost)
        cursor = connection.cursor()
        cursor.execute("SELECT phone_number FROM phone")
        return [elem[0] for elem in cursor.fetchall()]
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# Обработчик команды /get_phone_number
async def get_phone_number(update: Update, context: CallbackContext) -> None:
    phone_number = load_phone()
    if phone_number:
        await update.message.reply_text("\n".join(phone_number))
    else:
        await update.message.reply_text("Нет доступных телефонов.")


def main() -> None:
    """Start the bot."""
    application = Application.builder().token(TOKEN).build()

    conv_handler_email = ConversationHandler(
        entry_points=[CommandHandler("find_email", find_email)],
        states={
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_email)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )



    conv_handler_phone = ConversationHandler(
        entry_points=[CommandHandler("find_phone_number", find_phone_number)],
        states={
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone_number)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    # conv_handler_add_phone = ConversationHandler(
    #     entry_points=[CommandHandler("", )]
    # )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(conv_handler_email)
    application.add_handler(conv_handler_phone)
    # application.add_handler(conv_handler_add_phone)
    application.add_handler(CommandHandler("verify_password", verify_password))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("get_release", get_release))
    application.add_handler(CommandHandler("get_uname", get_uname))
    application.add_handler(CommandHandler("get_uptime", get_uptime))
    application.add_handler(CommandHandler("get_df", get_df))
    application.add_handler(CommandHandler("get_free", get_free))
    application.add_handler(CommandHandler("get_mpstat", get_mpstat))
    application.add_handler(CommandHandler("get_w", get_w))
    application.add_handler(CommandHandler("get_auths", get_auths))
    application.add_handler(CommandHandler("get_critical", get_critical))
    application.add_handler(CommandHandler("get_ps", get_ps))
    application.add_handler(CommandHandler("get_ss", get_ss))
    application.add_handler(CommandHandler("get_apt_list", get_apt_list))
    application.add_handler(CommandHandler("search_package", search_package))
    application.add_handler(CommandHandler("get_services", get_services))
    application.add_handler(CommandHandler('get_repl_logs', get_repl_logs))
    application.add_handler(CommandHandler("get_emails", get_emails))
    application.add_handler(CommandHandler('get_phone_number', get_phone_number))

    application.add_handler(CallbackQueryHandler(fetch_to_db))

    #Запуск бота
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_password))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
