# import os
# from dotenv import load_dotenv
#
# loaded = load_dotenv()
# print("是否找到并加载 .env：", loaded)
# print("API_KEY =", repr(os.environ.get("API_KEY")))
# print("BASE_URL =", repr(os.environ.get("BASE_URL")))
from dish_data import DISH_DB

REQUIRED = {"类别", "流派", "风味", "关键", "食材", "标签"}
for name, info in DISH_DB.items():
    missing = REQUIRED - set(info.keys())
    if missing:
        print(f"{name} 缺少：{missing}")
