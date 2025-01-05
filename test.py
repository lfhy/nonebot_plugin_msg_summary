import httpx

ENDPOINT="https://api.chatanywhere.tech"
API="/v1/chat/completions"
KEY="sksksksksk" 

MSG=[
    {
        "user1":"hello",
    },
    {
        "user2":"world",
    },
]

PROMPT="请详细总结这个群聊的内容脉络，要有什么人说了什么，用中文回答。"

def summary_history(messages: list[dict[str, str]], prompt: str) -> str:
    url = f"{ENDPOINT}{API}"
    headers = {"Content-Type": "application/json","Authorization":f"Bearer {KEY}"}
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"content": prompt, "role": "user"},
            {"content": str(messages), "role": "user"},
        ]
    }
    print(data)
    with httpx.Client() as client:
        try:
            response = client.post(url, json=data, headers=headers)
            response.raise_for_status()

            result = response.json()

            return result["choices"][0]["message"]["content"]

        except httpx.TimeoutException:
            return "请求超时，请缩短总结消息数量或联系管理员调整超时时间"
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                return "API 调用次数已达上限，请稍后再试"
            return f"API请求失败 (HTTP {e.response.status_code})"
        except (httpx.RequestError, KeyError, ValueError) as e:
            return f"请求发生错误: {str(e)}"

print(summary_history(MSG,PROMPT))