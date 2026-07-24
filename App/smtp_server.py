# smtp_server.py
"""
Local SMTP test server (modernized version).
Captures all emails and prints them directly to the terminal.
"""
import asyncio
import logging
from aiosmtpd.controller import Controller

class ConsoleHandler:
    async def handle_DATA(self, server, session, envelope):
        print("\n" + "="*50)
        print("--- NEW EMAIL RECEIVED ---")
        print(f"From: {envelope.mail_from}")
        print(f"To: {envelope.rcpt_tos}")
        print("\nContent:\n")
        try:
            text = envelope.content.decode('utf-8', errors='replace')
            print(text)
        except Exception as e:
            print(f"[Decode error: {e}]")
        print("="*50 + "\n")
        return '250 Message accepted for delivery'

async def main():
    handler = ConsoleHandler()
    controller = Controller(handler, hostname='127.0.0.1', port=1025)

    print("Starting local test SMTP server on 127.0.0.1:1025...")
    print("All sent emails will be shown in this terminal window.")
    controller.start()

    # Keep the server running without relying on deprecated event loop methods
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        print("\nStopping SMTP server...")
        controller.stop()

if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)  # Suppress noisy INFO logs
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSMTP server stopped manually.")
