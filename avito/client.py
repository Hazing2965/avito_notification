import logging
import time
from dataclasses import dataclass

import aiohttp

logger = logging.getLogger(__name__)

AVITO_API_URL = "https://api.avito.ru"
AVITO_TOKEN_URL = "https://api.avito.ru/token"


@dataclass
class AvitoMessage:
    id: str
    text: str
    author_id: int
    created: int
    direction: str = ""


@dataclass
class AvitoChat:
    id: str
    last_message: AvitoMessage | None
    buyer_name: str = ""
    item_title: str = ""


class AvitoClient:
    def __init__(self, client_id: str, client_secret: str, user_id: int) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self.user_id: int = user_id
        self._access_token: str = ""
        self._token_expires_at: float = 0.0
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _ensure_token(self) -> None:
        # обновляем за 60 сек до истечения
        if time.monotonic() < self._token_expires_at - 60:
            return

        session = await self._get_session()
        async with session.post(
            AVITO_TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            },
        ) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise RuntimeError(f"Не удалось получить токен Avito ({resp.status}): {text}")
            data = await resp.json()

        self._access_token = data["access_token"]
        self._token_expires_at = time.monotonic() + data.get("expires_in", 86400)
        logger.info("Avito access_token получен, истекает через %d сек", data.get("expires_in", 86400))

    async def get_chats(self) -> list[AvitoChat]:
        await self._ensure_token()
        session = await self._get_session()
        url = f"{AVITO_API_URL}/messenger/v2/accounts/{self.user_id}/chats"

        async with session.get(
            url,
            headers={"Authorization": f"Bearer {self._access_token}"},
            params={"unread_only": "true"},
        ) as resp:
            if resp.status != 200:
                text = await resp.text()
                logger.error("Avito API ошибка %s: %s", resp.status, text)
                return []
            data = await resp.json()

        chats = []
        for raw in data.get("chats", []):
            last_msg = None
            buyer_name = ""
            if raw_msg := raw.get("last_message"):
                author_id = raw_msg.get("author_id", 0)
                last_msg = AvitoMessage(
                    id=str(raw_msg["id"]),
                    text=raw_msg.get("content", {}).get("text", ""),
                    author_id=author_id,
                    created=raw_msg.get("created", 0),
                    direction=raw_msg.get("direction", ""),
                )
                buyer_name = next(
                    (u.get("name", "") for u in raw.get("users", []) if u.get("id") == author_id),
                    "",
                )
            chats.append(AvitoChat(
                id=raw["id"],
                last_message=last_msg,
                buyer_name=buyer_name,
                item_title=raw.get("context", {}).get("value", {}).get("title", ""),
            ))

        logger.debug("Получено %d чатов из Avito", len(chats))
        return chats

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
