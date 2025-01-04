from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg
from collections import defaultdict
from datetime import datetime, timedelta
from math import ceil
import httpx
from .Config import config

if config.gemini_key is None:
    raise ValueError("未提供 Gemini API Key。")

__plugin_meta__ = PluginMetadata(
    name="群聊总结",
    description="分析群聊记录，生成讨论内容的总结。",
    usage="1.总结 [消息数量]\n总结改群以上数量的信息\n2.总结 [QQ号] [消息数量]\n总结指定人相关信息 ",
    type="application",
    homepage="https://github.com/StillMisty/nonebot_plugin_summary_group",
)

summary_group = on_command("总结", priority=5, block=True)

cool_down = defaultdict(lambda: datetime.now())


async def get_group_msg_history(
    bot: Bot, group_id: int, count: int
) -> list[dict[str, str]]:
    messages = await bot.get_group_msg_history(group_id=group_id, count=count)

    result = []
    for message in messages["messages"]:
        text_segments = [
            segment["data"]["text"].strip()
            for segment in message["message"]
            if segment["type"] == "text"
        ]

        # 如果没有文本内容则跳过
        if not text_segments:
            continue

        msg_content = "".join(text_segments)
        sender = message["sender"]["card"] or message["sender"]["nickname"]
        result.append({sender: msg_content})

    result.pop()  # 去除请求总结的命令

    return result


async def summary_history(messages: list[dict[str, str]], prompt: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{config.summary_model}:generateContent?key={config.gemini_key}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {"parts": [{"text": prompt}], "role": "user"},
            {"parts": [{"text": str(messages)}], "role": "user"},
        ]
    }

    async with httpx.AsyncClient(proxy=config.proxy, timeout=60) as client:
        try:
            response = await client.post(url, json=data, headers=headers)
            response.raise_for_status()

            result = response.json()

            return result["candidates"][0]["content"]["parts"][0]["text"]

        except httpx.TimeoutException:
            return "请求超时，请缩短总结消息数量或联系管理员调整超时时间"
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                return "API 调用次数已达上限，请稍后再试"
            return f"API请求失败 (HTTP {e.response.status_code})"
        except (httpx.RequestError, KeyError, ValueError) as e:
            return f"请求发生错误: {str(e)}"


def parse_command_args(args: Message):
    qq: int | None = None
    num: int | None = None
    for seg in args:
        if seg.type == "at":
            qq = seg.data["qq"]
        elif seg.type == "text" and seg.data["text"].strip().isdigit():
            num = int(seg.data["text"])
    return qq, num


@summary_group.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    # 解析消息中的@和数字
    qq, num = parse_command_args(args)

    # 如果没有数字或者@，则不处理
    if num is None and qq is None:
        return

    if num < config.summary_min_length or num > config.summary_max_length:
        await summary_group.finish(
            f"总结消息数量应在 {config.summary_min_length} 到 {config.summary_max_length} 之间。",
            at_sender=True,
        )

    # 冷却时间，针对人，而非群
    if config.summary_cool_down > 0:
        if (last_time := cool_down[event.user_id]) > datetime.now():
            await summary_group.finish(
                f"请等待 {ceil((last_time - datetime.now()).total_seconds())} 秒后再请求总结。",
                at_sender=True,
            )
        cool_down[event.user_id] = datetime.now() + timedelta(
            seconds=config.summary_cool_down
        )

    group_id = event.group_id
    messages = await get_group_msg_history(bot, group_id, num)
    if not messages:
        await summary_group.finish("未能获取到聊天记录。")

    if qq is None:
        # 总结整个群聊内容
        summary = await summary_history(
            messages, "请详细总结这个群聊的内容脉络，要有什么人说了什么，用中文回答。"
        )
    else:
        # 只针对某个用户的聊天内容进行总结
        member_info = await bot.get_group_member_info(group_id=group_id, user_id=qq)
        name: str = member_info["card"] or member_info["nickname"]
        summary = await summary_history(
            messages,
            f"请总结对话中与{name}相关的内容，用中文回答。",
        )

    await summary_group.finish(summary.strip())
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg
from .Config import config
import httpx

if config.gemini_key is None:
    raise ValueError("未提供 Gemini API Key。")

__plugin_meta__ = PluginMetadata(
    name="群聊总结",
    description="分析群聊记录，生成讨论内容的总结。",
    usage="1.总结 [消息数量]\n总结改群以上数量的信息\n2.总结 [QQ号] [消息数量]\n总结指定人相关信息 ",
    type="application",
    homepage="https://github.com/StillMisty/nonebot_plugin_summary_group",
)

summary_group = on_command("总结", priority=5, block=True)


async def get_group_msg_history(
    bot: Bot, group_id: int, count: int
) -> list[dict[str, str]]:
    messages = await bot.get_group_msg_history(group_id=group_id, count=count)
    result = []
    for message in messages["messages"]:
        msg = ""
        for i in message["message"]:
            if i["type"] == "text":
                msg += i["data"]["text"]
        if msg == "":
            continue

        sender = message["sender"]["card"] or message["sender"]["nickname"]
        result.append({sender: msg})

    result.pop()  # 去除请求总结的命令

    return result


async def summary_history(messages: list[dict[str, str]], prompt: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{config.summary_model}:generateContent?key={config.gemini_key}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {"parts": [{"text": prompt}], "role": "user"},
            {"parts": [{"text": str(messages)}], "role": "user"},
        ]
    }

    async with httpx.AsyncClient(proxy=config.proxy) as client:
        response = await client.post(url, json=data, headers=headers, timeout=20)

    if response.status_code == 429:
        return "API Key 已超出限制，请联系主人氪金。"

    response.raise_for_status()
    result = response.json()["candidates"][0]["content"]["parts"][0]["text"]
    return result


def parse_command_args(args: Message):
    qq: int | None = None
    num: int | None = None
    for seg in args:
        if seg.type == "at":
            qq = seg.data["qq"]
        elif seg.type == "text" and seg.data["text"].strip().isdigit():
            num = max(50, min(int(seg.data["text"]), 2000))
    return qq, num


@summary_group.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    # 解析消息中的@和数字
    qq, num = parse_command_args(args)

    # 如果没有数字或者@，则不处理
    if num is None and qq is None:
        return

    group_id = event.group_id
    messages = await get_group_msg_history(bot, group_id, num)
    if not messages:
        await summary_group.finish("未能获取到聊天记录。")

    if qq is None:
        # 总结整个群聊内容
        summary = await summary_history(
            messages, "请详细总结这个群聊的内容脉络，要有什么人说了什么，用中文回答。"
        )
    else:
        # 只针对某个用户的聊天内容进行总结
        member_info = await bot.get_group_member_info(group_id=group_id, user_id=qq)
        name: str = member_info["card"] or member_info["nickname"]
        summary = await summary_history(
            messages,
            f"请总结对话中与{name}相关的内容，用中文回答。",
        )

    await summary_group.finish(summary.strip())
