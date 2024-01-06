import random
from asyncio import Semaphore, sleep, create_task, wait
from itertools import zip_longest

from core.utils import logger, file_to_list, str_to_file


class AutoReger:
    def __init__(self, accounts: list):
        self.accounts = accounts
        # random.shuffle(self.accounts)
        self.success = 0
        self.semaphore = None
        self.delay = None

    @classmethod
    def get_accounts(cls, *file_names: str):
        consumables = [file_to_list(file_name) for file_name in file_names]
        return cls(list(zip_longest(*consumables)))

    async def start(self, worker_func: callable, threads: int = 1, delay: tuple = (0, 0)):
        if not self.accounts:
            logger.error("No accounts found :(")
            return

        logger.info(f"Successfully grabbed {len(self.accounts)} accounts")

        self.semaphore = Semaphore(threads)
        self.delay = delay
        await self.define_tasks(worker_func)

        (logger.success if self.success else logger.warning)(
                   f"Successfully handled {self.success} accounts :)" if self.success
                   else "No accounts handled :( | Check logs in logs/out.log")

    async def define_tasks(self, worker_func: callable):
        await wait([create_task(self.worker(account, worker_func)) for account in self.accounts])

    async def worker(self, account: tuple, worker_func: callable):
        account_id = account[0][:15]
        is_success = False

        try:
            async with self.semaphore:
                await self.custom_delay()

                is_success = await worker_func(*account)
        except Exception as e:
            logger.error(f"{account_id} | not handled | error: {e}")

        self.success += int(is_success)
        AutoReger.logs(account_id, account, is_success)

    async def custom_delay(self):
        if self.delay[1] > 0:
            sleep_time = random.uniform(*self.delay)
            logger.info(f"Sleep for {sleep_time:.1f} seconds")
            await sleep(sleep_time)

    @staticmethod
    def logs(account_id: str, account: tuple, is_success: bool = False):
        if is_success:
            log_func = logger.success
            log_msg = "Claimed!"
            file_name = "success"
        else:
            log_func = logger.warning
            log_msg = "Failed!"
            file_name = "failed"

        file_msg = "|".join(str(x) for x in account)
        str_to_file(f"./logs/{file_name}.txt", file_msg)

        log_func(f"Account: {account_id}... {log_msg}")
