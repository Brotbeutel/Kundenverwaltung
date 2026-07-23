# smtp_server.py
"""
Lokaler SMTP-Server für Testzwecke (Modernisierte Version).
Fängt alle E-Mails ab und druckt sie direkt im Terminal aus.
"""
import asyncio
import logging
from aiosmtpd.controller import Controller

class ConsoleHandler:
    async def handle_DATA(self, server, session, envelope):
        print("\n" + "="*50)
        print("--- NEUE E-MAIL EMPFANGEN ---")
        print(f"Von: {envelope.mail_from}")
        print(f"An: {envelope.rcpt_tos}")
        print("\nInhalt:\n")
        try:
            text = envelope.content.decode('utf-8', errors='replace')
            print(text)
        except Exception as e:
            print(f"[Fehler beim Dekodieren: {e}]")
        print("="*50 + "\n")
        return '250 Message accepted for delivery'

async def main():
    handler = ConsoleHandler()
    controller = Controller(handler, hostname='127.0.0.1', port=1025)

    print("Starte lokalen Test-SMTP-Server auf 127.0.0.1:1025...")
    print("Alle gesendeten Mails werden hier unten im Terminal angezeigt!")
    controller.start()

    # Hält den Server am Laufen ohne veraltete event_loop Methoden
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        print("\nStoppe SMTP-Server...")
        controller.stop()

if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR) # Скрываем лишние системные логи INFO
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSMTP-Server manuell beendet.")
