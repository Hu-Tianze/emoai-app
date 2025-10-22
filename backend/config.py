# config.py
# 配置和全局客户端
import os
from openai import OpenAI

# 0. 配置 NVIDIA 客户端
NV_API_KEY = os.getenv("NV_API_KEY", "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").strip()
try:
    NV_API_KEY.encode("ascii")
except Exception as e:
    raise ValueError("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") from e

client = OpenAI(
    api_key=NV_API_KEY,
    base_url="https://integrate.api.nvidia.com/v1"
)