from nonebot import get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    gemini_key: str | None = None  # gemini接口密钥
    summary_model: str = "gemini-1.5-flash"  # gemini模型名称
    proxy: str | None = None  # 代理设置


config = get_plugin_config(Config)
