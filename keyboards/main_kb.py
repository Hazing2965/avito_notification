from vkbottle import Keyboard, KeyboardButtonColor, Callback


request_access_keyboard = (
    Keyboard(one_time=False, inline=True)
    .add(
        Callback("🔑 Запросить доступ", payload={"action": "request_access"}),
        color=KeyboardButtonColor.POSITIVE,
    )
    .get_json()
)

waiting_keyboard = Keyboard(one_time=False, inline=True).get_json()

notification_keyboard = (
    Keyboard(one_time=False, inline=False)
    .add(
        Callback("🔔 Включить уведомления", payload={"action": "notifications_on"}),
        color=KeyboardButtonColor.POSITIVE,
    )
    .add(
        Callback("🔕 Выключить уведомления", payload={"action": "notifications_off"}),
        color=KeyboardButtonColor.NEGATIVE,
    )
    .row()
    .add(
        Callback("📊 Статус", payload={"action": "status"}),
        color=KeyboardButtonColor.SECONDARY,
    )
    .get_json()
)


def admin_approval_keyboard(user_vk_id: int) -> str:
    return (
        Keyboard(one_time=False, inline=True)
        .add(
            Callback("✅ Дать доступ", payload={"action": "grant_access", "user_id": user_vk_id}),
            color=KeyboardButtonColor.POSITIVE,
        )
        .add(
            Callback("❌ Отказать", payload={"action": "deny_access", "user_id": user_vk_id}),
            color=KeyboardButtonColor.NEGATIVE,
        )
        .get_json()
    )
