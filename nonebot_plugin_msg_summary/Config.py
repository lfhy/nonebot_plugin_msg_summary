from nonebot import get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    summary_ai_key: str | None = None  # ai接口密钥
    summary_ai_endpoint: str = "https://api.chatanywhere.tech" # ai请求地址
    summary_ai_api: str = "/v1/chat/completions" # ai请求接口
    summary_ai_model: str = "gpt-4o-mini"  # 总结模型名称
    proxy: str | None = None  # 代理设置
    summary_max_length: int = 2000  # 总结最大长度
    summary_min_length: int = 50  # 总结最小长度
    summary_cool_down: int = 0  # 总结冷却时间（0即无冷却，针对人，而非群）


config = get_plugin_config(Config)
