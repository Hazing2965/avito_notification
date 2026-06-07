from vkbottle.bot import Message
from vkbottle.dispatch.rules.abc import ABCRule


class LowerText(ABCRule[Message]):
    def __init__(self, texts: list[str] | str):
        if isinstance(texts, str):
            texts = [texts]
        self.texts = [t.lower() for t in texts]

    async def check(self, message: Message) -> bool:
        return (message.text or "").lower() in self.texts
