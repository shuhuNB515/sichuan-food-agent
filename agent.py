import os
import json
import random


from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()
client = OpenAI(
    api_key=os.environ.get("API_KEY"),
    base_url=os.environ.get("BASE_URL")
)

DISH_DB = {
"麻婆豆腐": {
        "流派": "成都陈麻婆豆腐，清末同治年间陈刘氏所创",
        "风味": "麻、辣、烫、香、酥、嫩、鲜、活 八字箴言",
        "关键": "豆腐先用淡盐水焯过定型，牛肉臊子要酥香",
    },
    "宫保鸡丁": {
        "流派": "川菜系，源于丁宝桢家厨做法",
        "风味": "糊辣荔枝味，小甜小酸带糊辣壳香",
        "关键": "用鸡腿肉，油酥花生最后放才保持酥脆",
    },
    "回锅肉": {
        "流派": "以成都、德阳一带为代表，正宗用二刀肉",
        "风味": "酱香微辣，灯盏窝是灵魂",
        "关键": "豆瓣加甜面酱搭配，蒜苗断生即起锅",
    },
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "recommend_dish",
            "description": "根据口味偏好推荐川菜。当用户表达口味需求时调用，例如：想吃辣的、想清淡点、要下饭的。",
            "parameters": {
                "type": "object",
                "properties": {
                    "taste": {
                        "type": "string",
                        "description": "口味关键词，例如：麻辣、酸甜、微辣、下饭",
                    }
                },
                "required": ["taste"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "random_dish",
            "description": "随机挑选一道川菜。当用户犹豫不决、让你帮忙随便决定吃什么时调用。",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },

]


def query_dish_info(dish_name:str)->str:
    info = DISH_DB.get(dish_name)
    if info is None:
        return f"资料库中没有《{dish_name}》的记录"
    return json.dumps(info,ensure_ascii=False)

def recommend_dish(taste:str)->str:
    matched = [name for name,info in DISH_DB.items()
               if any(taste in tag for tag in info.get("标签",[]))]

    if not matched:
        return f"资料库里没有符合“{taste}“"
    return json.dumps({"推荐":matched},ensure_ascii=False)
def random_dish() -> str:
    name = random.choice(list(DISH_DB.keys()))
    info = DISH_DB[name]
    return json.dumps({"随机选中": name, "风味": info["风味"]}, ensure_ascii=False)

TOOLS_REGISTRY = {
    "query_dish_info": query_dish_info,
    "recommend_dish": recommend_dish,
    "random_dish": random_dish,
}
def run_agent(messages: list) -> str:
    while True:
        response = client.chat.completions.create(
            model=os.environ["MODEL_NAME"],
            messages=messages,
            tools=tools,
            timeout=60,
        )
        message = response.choices[0].message

        if not message.tool_calls:
            return message.content or "（这轮没有回复内容）"

        messages.append(message)
        for tool_call in message.tool_calls:
            args = json.loads(tool_call.function.arguments)
            name = tool_call.function.name
            print(f"  --> 决策：调用 {name}，参数 {args}")
            func = TOOLS_REGISTRY.get(name)
            result = func(**args) if func else f"工具 {name} 不存在"
            print(f"  <-- 结果：{result[:50]}……")
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })


messages: list = [
    {"role": "system", "content": "你是一个四川美食专家。只要用户的问题中提到任何具体菜名（如麻婆豆腐、回锅肉、宫保鸡丁等），你必须第一步先调用 query_dish_info 查询资料库，然后只基于查询结果回答菜品细节，禁止凭记忆描述菜品。与具体菜品无关的一般性问题才可直接回答。"},
]

print("四川美食Agent已上线（输入q退出）")
while True:
    user_input = input("\n你:")
    if user_input.strip() == "q":
        print("下次想吃啥再找我！")
        break
    if not user_input.strip():
        continue

    messages.append({"role": "user", "content": user_input})
    reply = run_agent(messages)
    print("Agent"+reply)
    messages.append({"role": "assistant", "content": reply})