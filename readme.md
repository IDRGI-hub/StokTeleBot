# Telegram Bot для мониторинга остатков товаров на Wildberries

Этот бот предназначен для автоматического сбора данных об остатках товаров на Wildberries через парсинг с использованием Selenium. Результаты отправляются в Telegram-чат.

## Особенности

- Авторизация на платформе Mayak для доступа к данным.
- Парсинг информации о товарах с Wildberries.
- Использование Selenium в Docker-контейнере для изоляции среды.
- Интеграция с Telegram для отправки уведомлений.
- Сохранение данных в формате JSON и HTML.

## Технологии

- **Python 3.9+**
- **Selenium** — для автоматизации браузера.
- **Aiogram** — для работы с Telegram API.
- **Docker** — для контейнеризации приложения.
- **BeautifulSoup4** — для парсинга HTML.

## Установка и запуск

### Предварительные требования

- Установите [Docker](https://docs.docker.com/get-docker/) и [Docker Compose](https://docs.docker.com/compose/install/).

### Шаги

1. **Клонируйте репозиторий**:
   ```bash
   git clone https://github.com/IDRGI-hub/StokTeleBot
   cd StokTeleBot
   ```

2. **Настройте конфигурацию**:
   - Создайте файл `config.py` на основе `config.example.py`.
   - Заполните токен бота, данные для входа на Mayak и список артикулов.

3. **Соберите и запустите контейнеры**:
   ```bash
   docker-compose up -d --build
   ```

4. **Проверьте логи**:
   ```bash
   docker-compose logs -f
   ```

## Настройка

### Параметры `config.py`

| Переменная               | Описание                                                                 |
|--------------------------|-------------------------------------------------------------------------|
| `TOKEN`                  | Токен вашего Telegram-бота.                                             |
| `CHAT_IDS`               | Список ID чатов для отправки уведомлений.                               |
| `MAYAK_URL`              | URL для авторизации на Mayak.                                           |
| `WILDBERRIES_URL_TEMPLATE` | Шаблон URL товаров Wildberries (например, `https://www.wildberries.ru/catalog/{}/detail.aspx`). |
| `USERNAME`, `PASSWORD`   | Данные для входа на Mayak.                                              |
| `ARTICLES`               | Словарь с артикулами и названиями товаров.                              |
| `COOKIE_FILE`            | Путь к файлу с куками для авторизации.                                  |
| `EXTENSION_PATH`         | Путь к расширению Firefox (если требуется).                             |
| `OUTPUT_FILE`            | Путь к файлу для сохранения результатов.                                |

## Структура проекта

```
project/
├── app/
│   ├── hendlers.py       # Обработчики Telegram-команд
│   └── keyboards.py      # Клавиатуры для бота
├── Parser/
│   └── Parser.py         # Логика парсинга
├── config.py             # Конфигурационные параметры
├── main.py               # Точка входа
├── Dockerfile            # Конфигурация Docker-образа
├── docker-compose.yml    # Конфигурация Docker Compose
└── requirements.txt      # Зависимости Python
```

## Пример использования

После запуска бот будет:
1. Авторизовываться на Mayak.
2. Собирать данные об остатках товаров.
3. Формировать отчет и отправлять его в Telegram.

![Пример сообщения](https://4.downloader.disk.yandex.ru/preview/18db477a9feb5ecd41767898eb5df2759b32aa437fc39ced3797a8eeddf2211c/inf/ILwrTam0Dr_LQyDtPkPgq_IKbVF03AnTGF8YWKKnTgRcywzB0KwARvzJxuh2b26KRohJ6eq1I3ev2BXPLTjzfg%3D%3D?uid=294545757&filename=%D0%91%D0%B5%D0%B7%20%D0%B8%D0%BC%D0%B5%D0%BD%D0%B8.png&disposition=inline&hash=&limit=0&content_type=image%2Fpng&owner_uid=294545757&tknv=v2&size=1912x954)

## Локализация ошибок

### Частые проблемы и решения

1. **Ошибка SSL**:
   - Обновите сертификаты: 
     ```bash
     sudo apt update && sudo apt install --reinstall ca-certificates
     ```
   - Убедитесь, что время на сервере корректно.

2. **Проблемы с Selenium Server**:
   - Увеличьте `shm_size` в `docker-compose.yml` до `4g`.
   - Убедитесь, что порты 4444 и 7900 не заблокированы.

3. **Расширения Firefox**:
   - Убедитесь, что путь к `.xpi`-файлу указан верно в `config.py`.

## Лицензия

Этот проект распространяется под лицензией [MIT](LICENSE).

---

**Автор**: IDRGI-hub  
**Контакты**: [Telegram](https://t.me/metaagrar)
