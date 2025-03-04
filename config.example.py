# Токен бота. Замените на ваш реальный токен, полученный от BotFather в Telegram.
TOKEN = "YOUR_BOT_TOKEN_HERE"  # Пример: "123456789:ABCdefGhIJKlmNoPQRstuVWXyz"

# ID чатов, куда бот будет отправлять сообщения. Замените на реальные ID чатов.
CHAT_IDS = ["CHAT_ID_1", "CHAT_ID_2", "CHAT_ID_3"]  # Пример: ["123456789", "987654321"]

# URL-адреса
MAYAK_URL = "https://app.mayak.bz/users/sign_in"
WILDBERRIES_URL_TEMPLATE = "https://www.wildberries.ru/catalog/{}/detail.aspx"

# Данные для входа. Замените на реальные логин и пароль.
USERNAME = "your_username_here"  # Пример: "user@example.com"
PASSWORD = "your_password_here"  # Пример: "Str0ngP@ssw0rd"

# Список товаров для парсинга
# Список товаров для парсинга. Ключи — артикулы, значения — названия товаров.
ARTICLES = {
    123456789: "Пример товара 1",  # Замените на реальные артикулы и названия
    987654321: "Пример товара 2",
    456789123: "Пример товара 3"
}
# Пути к файлам
COOKIE_FILE = "Parser/web_driver/cookies.json"
EXTENSION_PATH = "Parser/extension/extension.xpi"  
OUTPUT_FILE = "Parser/output.json"

# Логирование
LOGGING_LEVEL = "INFO"