import asyncio
import json
import random
import secrets
import time

from better_proxy import Proxy
from wonderwords import RandomSentence
from curl_cffi.requests import AsyncSession
from fake_useragent import UserAgent

from inputs.config import MOBILE_PROXY_CHANGE_IP_LINK, MOBILE_PROXY
from .utils import Web3Utils, logger


class MyShell:
    def __init__(self, key: str, proxy: str = None):
        self.w3 = Web3Utils(key=key)
        # self.proxy = Proxy.from_str(proxy.strip()).as_url if proxy else None

        headers = {
            'authority': 'api.myshell.ai',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en',
            'content-type': 'application/json',
            'myshell-client-version': 'v1.5.4',
            'myshell-service-name': 'organics-api',
            'origin': 'https://app.myshell.ai',
            'platform': 'web',
            'referer': 'https://app.myshell.ai/',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'timestamp': str(int(time.time() * 1000)),
            'user-agent': UserAgent().random
        }

        self.session = AsyncSession(
            headers=headers,
            # proxies={"http": self.proxy, "https": self.proxy},
            impersonate="chrome110",
            verify=False,
            trust_env=True
        )

        self.proxy = None
        self.visitor_id = MyShell.get_visitor_id()

    async def define_proxy(self, proxy: str):
        if MOBILE_PROXY:
            await MyShell.change_ip()
            self.proxy = MOBILE_PROXY

        if proxy is not None:
            proxy = Proxy.from_str(proxy.strip()).as_url
            self.session.proxies.update({"http": proxy, "https": proxy})

    @staticmethod
    async def change_ip():
        async with AsyncSession() as session:
            await session.get(MOBILE_PROXY_CHANGE_IP_LINK)

    async def login(self):
        print((await self.session.get("http://httpbin.org/ip")).text)
        url = 'https://api.myshell.ai/auth/verifySignature'

        msg = await self.get_sign_msg()

        json_data = {
            'publicAddress': self.w3.acct.address,
            'signature': self.w3.get_signed_code(msg),
            'invitationCode': '',
            'botSharingCode': '',
            'visitorId': self.visitor_id,
        }

        headers = self.session.headers.copy()
        headers['myshell-service-name'] = ""
        headers['visitor-id'] = self.visitor_id

        response = await self.session.post(url, headers=headers, json=json_data)

        if auth_token := response.json().get("token"):
            self.upd_login_token(auth_token)

        return bool(auth_token)

    async def get_sign_msg(self):
        url = 'https://api.myshell.ai/auth/generateNonce'

        headers = self.session.headers.copy()
        headers['myshell-service-name'] = ""
        headers['visitor-id'] = self.visitor_id

        json_data = {
            'publicAddress': self.w3.acct.address,
        }

        response = await self.session.post(url, json=json_data, headers=headers)
        return response.json()["nonce"]

    def upd_login_token(self, token: str):
        self.session.headers["authorization"] = f"Bearer {token}"

    async def chat_and_claim(self):
        await self.chat_with_bot()
        await asyncio.sleep(3)
        return await self.claim_all()

    async def chat_with_bot(self):
        bot_ids = ["864", "4976", "6958", "1700067629"]
        random.shuffle(bot_ids)

        for bot_id in bot_ids:
            text = RandomSentence().sentence()
            response = await self.send_bot_msg(bot_id, text)
            logger.info(f"Sent message to bot: {text} | Answer: {response[:10]}...")
            await asyncio.sleep(random.uniform(20, 40))

    async def send_bot_msg(self, bot_id: str, msg: str):
        json_data = {
            'botId': bot_id,
            'conversation_scenario': 3,
            'message': msg,
            'messageType': 1,
        }

        response = await self.session.post('https://api.myshell.ai/v1/bot/chat/send_message', json=json_data)

        if "MESSAGE_REPLY_SSE_ELEMENT_EVENT_NAME_USER_SENT_MESSAGE_REPLIED" in response.text:
            return json.loads(response.text.split("data: ")[-1])["message"]["text"]

    async def claim_all(self):
        url = 'https://api.myshell.ai/v1/season/task/claim_all'

        response = await self.session.post(url)
        return response.json() == {}

    async def claim(self, task_id: str):
        json_data = {
            'taskId': task_id,
        }

        response = await self.session.post('https://api.myshell.ai/v1/season/task/claim', json=json_data)
        return response.json() == {}

    def logout(self):
        self.session.close()

    @staticmethod
    def get_visitor_id():
        segment = secrets.token_hex(7)
        return (f'{segment}-{secrets.token_hex(7)}-{secrets.token_hex(4)}'
            f'-{random.randint(100000, 999999)}-{segment}')