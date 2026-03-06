# Telegram MCP Server

MCP сервер для подключения личного Telegram аккаунта к Claude Code. Позволяет читать чаты, отправлять сообщения и считать активность пользователей прямо из CLI.

## Требования

- Python 3.10+
- Telegram API ключи ([my.telegram.org](https://my.telegram.org) → API development tools)

## Установка

```bash
cd /home/claude/telegram-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Настройка

### 1. API ключи

Заполни `.env`:

```env
TG_API_ID=12345678
TG_API_HASH=abcdef1234567890abcdef1234567890
```

### 2. Авторизация

```bash
source .venv/bin/activate
python auth.py
```

- В терминале появится QR-код
- Открой Telegram на телефоне → **Настройки → Устройства → Подключить устройство**
- Отсканируй QR-код камерой
- Если включена 2FA — введи пароль в терминале

Сессия сохранится в `sessions/telegram_mcp.session`. Повторная авторизация не нужна, пока сессия активна.

### 3. Подключение к Claude Code

В `~/.claude.json` в секции `mcpServers` добавь:

```json
"telegram": {
  "type": "stdio",
  "command": "/home/claude/telegram-mcp/.venv/bin/python",
  "args": ["/home/claude/telegram-mcp/server.py"],
  "env": {
    "TG_API_ID": "12345678",
    "TG_API_HASH": "abcdef1234567890abcdef1234567890"
  }
}
```

Перезапусти Claude Code — сервер `telegram` появится в списке MCP.

## Инструменты

| Инструмент | Параметры | Описание |
|---|---|---|
| `get_chats` | `limit` (default: 50) | Список диалогов: имя, id, тип, непрочитанные |
| `get_messages` | `chat_id`, `limit` (default: 20) | Последние сообщения из чата |
| `send_message` | `chat_id`, `text` | Отправить сообщение в чат |
| `count_user_messages` | `chat_id`, `user_id` | Количество сообщений пользователя за сегодня |

`chat_id` принимает как числовой ID (например `123456789`), так и username (например `@durov`).

## Примеры использования в Claude Code

```
> Покажи мои чаты
> Прочитай последние 10 сообщений из чата 123456789
> Отправь "Привет!" в @username
> Сколько сообщений написал пользователь 987654321 в чате 123456789 сегодня?
```

## Структура проекта

```
telegram-mcp/
├── auth.py            # QR-авторизация в терминале
├── server.py          # MCP сервер (FastMCP + Telethon)
├── config.py          # Загрузка TG_API_ID, TG_API_HASH, путь к сессии
├── requirements.txt   # Зависимости
├── .env               # API ключи (не коммитится)
├── .gitignore
└── sessions/          # Файлы сессии Telethon (не коммитится)
```

## Устранение неполадок

**Сервер не запускается** — убедись, что сессия создана (`python auth.py`) и ключи указаны в `env` секции MCP конфига.

**Сессия истекла** — запусти `python auth.py` повторно для переавторизации.

**`SessionPasswordNeededError`** — включена двухфакторная аутентификация. Введи пароль при запросе в `auth.py`.
