import asyncio
import ctypes
import os

from core.autoreger import AutoReger
from core.myshell import MyShell
from art import tprint

from inputs.config import KEYS_FILE_PATH, PROXIES_FILE_PATH, THREADS, CUSTOM_DELAY


def bot_info(name: str = ""):
    tprint(name)

    if os.name == 'nt':
        ctypes.windll.kernel32.SetConsoleTitleW(f"{name}")
    print("EnJoYeR's <crypto/> moves: https://t.me/+tdC-PXRzhnczNDli\n")


async def worker_task(key: str, proxy: str):
    myshell = MyShell(key)

    await myshell.define_proxy(proxy)
    await myshell.login()
    is_ok = await myshell.chat_transaction_and_claim()
    myshell.logout()
    return is_ok


async def main():
    bot_info("MyShell_Daily")
    autoreger = AutoReger.get_accounts(KEYS_FILE_PATH, PROXIES_FILE_PATH)
    await autoreger.start(worker_task, THREADS, CUSTOM_DELAY)


if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
