import asyncio
import sys

import qrcode
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

from config import TG_API_ID, TG_API_HASH, SESSION_PATH


async def main():
    client = TelegramClient(SESSION_PATH, TG_API_ID, TG_API_HASH)
    await client.connect()

    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"Уже авторизован как {me.first_name} (@{me.username})")
        await client.disconnect()
        return

    qr_login = await client.qr_login()

    while True:
        # Render QR code in terminal
        print("\nОтсканируйте QR-код в Telegram:")
        print("Настройки -> Устройства -> Подключить устройство\n")
        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L)
        qr.add_data(qr_login.url)
        qr.print_ascii(invert=True)

        try:
            await qr_login.wait(timeout=30)
            break
        except asyncio.TimeoutError:
            # Token expired, recreate QR
            print("\nQR-код истёк, генерирую новый...")
            await qr_login.recreate()
        except SessionPasswordNeededError:
            password = input("\nВведите пароль двухфакторной аутентификации: ")
            await client.sign_in(password=password)
            break

    me = await client.get_me()
    print(f"\nУспешно авторизован как {me.first_name} (@{me.username})")
    print(f"Сессия сохранена в {SESSION_PATH}.session")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
