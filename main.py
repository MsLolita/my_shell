import asyncio
import ctypes
import os
import sys

from core.autoreger import AutoReger
from core.myshell import MyShell
from art import tprint

from inputs.config import KEYS_FILE_PATH, PROXIES_FILE_PATH, THREADS, CUSTOM_DELAY, EXCHANGE_POINTS_ONLY


def bot_info(name: str = ""):
    tprint(name)

    if sys.platform == 'win32':
        ctypes.windll.kernel32.SetConsoleTitleW(f"{name}")
    print("EnJoYeR's <crypto/> moves: https://t.me/+tdC-PXRzhnczNDli\n")


async def worker_task(key: str, proxy: str):
    myshell = MyShell(key)

    await myshell.define_proxy(proxy)
    await myshell.login()

    if EXCHANGE_POINTS_ONLY:
        is_ok = await myshell.exchange_points()
    else:
        is_ok = await myshell.chat_transaction_and_claim()

    myshell.logout()
    return is_ok


async def main():
    bot_info("MyShell_Daily")
    autoreger = AutoReger.get_accounts(KEYS_FILE_PATH, PROXIES_FILE_PATH)
    await autoreger.start(worker_task, THREADS, CUSTOM_DELAY)


if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())