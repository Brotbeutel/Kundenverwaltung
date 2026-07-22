# smtp_server.py
"""
Локальный SMTP-сервер для тестирования отправки писем.
Ловит все письма от Flask-Mail и выводит их прямо в консоль.
 
Запуск:
    python smtp_server.py
"""
import asyncio
import logging
from aiosmtpd.controller import Controller
 
class ConsoleHandler:
    async def handle_DATA(self, server, session, envelope):
        print("\n" + "="*50)
        print(f"--- NEUE E-MAIL EMPFANGEN ---")
        print(f"Von: {envelope.mail_from}")
        print(f"An: {envelope.rcpt_tos}")
        print(f"Inhalt:\n")
        # Декодируем содержимое письма для вывода на экран
        text = envelope.content.decode('utf-8', errors='replace')
        print(text)
        print("="*50 + "\n")
        return '250 Message accepted for delivery'
 
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    # Запускаем локально на порту 1025 (соответствует настройкам в config.py)
    handler = ConsoleHandler()
    controller = Controller(handler, hostname='127.0.0.1', port=1025)
    print("Starte lokalen Test-SMTP-Server auf 127.0.0.1:1025...")
    print("Alle gesendeten Mails werden hier unten im Terminal angezeigt!")
    controller.start()
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        print("\nStoppe SMTP-Server...")
        controller.stop()