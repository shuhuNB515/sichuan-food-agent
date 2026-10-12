import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# 聊天模型客户端：小米 MiMo
client = OpenAI(
    api_key=os.environ["API_KEY"],
    base_url=os.environ["BASE_URL"],
)
MODEL_NAME = os.environ["MODEL_NAME"]

# 向量模型客户端：百川，独立钥匙
embedding_client = OpenAI(
    api_key=os.environ["EMBEDDING_API_KEY"],
    base_url=os.environ["EMBEDDING_BASE_URL"],
)
EMBEDDING_MODEL = os.environ["EMBEDDING_MODEL"]
