import json
import random
import difflib

from dish_data import DISH_DB
from rag import semantic_search


ALIAS = {
    "肺片": "夫妻肺片",
    "宫爆鸡丁": "宫保鸡丁",
    "麻婆豆付": "麻婆豆腐",
}

def query_dish_info(dish_name: str) -> str:
    name = ALIAS.get(dish_name,dish_name)

    if name in DISH_DB:
        return json.dumps(DISH_DB[name],ensure_ascii=False)

    substring = [n for n in DISH_DB if name in n or n in name]
    if len(substring) == 1:
        return json.dumps(DISH_DB[substring[0]],ensure_ascii=False)
    if substring:
        return json.dumps({"未精准命中": name, "候选":substring},ensure_ascii=False)

    close = difflib.get_close_matches(name,DISH_DB.keys(),n =3,cutoff=0.5)
    if close:
        return json.dumps({"未精准命中":name,"你可能相查":close},ensure_ascii=False)
    return f"资料库中没有《{dish_name}》的记录"


def recommend_dish(taste: str) -> str:
    matched = [name for name,info in DISH_DB.items()
               if any(taste in tag for tag in info.get("标签",[]))]
    if not matched:
        return f"资料库里面没有符合‘{taste}’口味的菜"
    return json.dumps({"推荐":matched},ensure_ascii=False)

def random_dish(count:int = 1) -> str:
    names = list(DISH_DB.keys())
    picked = random.sample(names,k=min(count,len(names)))
    result = [{"菜品":n,"风味":DISH_DB[n]["风味"]} for n in picked]
    return json.dumps({"随机选中":result},ensure_ascii=False)

def search_dishes(keyword:str)->str:
    hits = []
    for name,info in DISH_DB.items():
        haystack = (name + info["类别"] + info["风味"] + info["关键"]
                    + "".join(info["食材"]) + "".join(info["标签"]))
        if keyword in haystack:
            hits.append({"菜名":name,"类别":info["类别"],"风味":info["风味"]})
    if not hits:
        return (f"全库搜索没有找到包含“{keyword}”的内容。"
                "注意：本工具只搜菜品条目。若要找的是菜谱文档、店规、资料中的内容，"
                "请改用 find_by_meaning 工具进行语义检索。")
    return json.dumps({"命中数":len(hits),"结果":hits},ensure_ascii=False)

def find_by_meaning(description:str)->str:
    results = semantic_search(description,top_k=3)
    return json.dumps({"语义检索结果":results},ensure_ascii=False)

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "query_dish_info",
            "description": "查询一道川菜的权威资料。支持常见简称和别名；查不到时会返回候选菜名，请把候选转告用户。",
            "parameters": {
                "type": "object",
                "properties": {
                    "dish_name": {
                        "type": "string",
                        "description": "要查询的川菜名称，例如：麻婆豆腐",
                    }
                },
                "required": ["dish_name"],
            },
        },
    },
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
                        "description": "口味关键词，例如：麻辣、酸甜、微辣、下饭、清淡",
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
            "description": "随机挑选一道或多道川菜。当用户犹豫不决、让你帮忙随便决定吃什么时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "count": {
                        "type": "integer",
                        "description": "想随机挑选的菜品数量；用户说'来三个'就传 3，没说数量可传 1",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_dishes",
            "description": "跨字段搜索川菜：可按食材（如牛肉、花生）、类别（小吃/凉菜/汤菜/甜品/热菜）、口味关键词搜。当用户没有明确指定菜名、而是描述某种特征时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "搜索关键词，例如：牛肉、凉菜、花生、甜品",
                    }
                },
                "required": ["keyword"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "find_by_meaning",
            "description": "按语义模糊搜索川菜知识库（含菜品档案和文档资料，如店规、烹饪知识文章）。当用户用自然语言描述想吃的东西、询问某类资料内容、或没有明确菜名时调用，例如：适合配啤酒的菜、张师傅的家规、夏天解暑的甜品。注意：本工具不擅长处理'不要辣'这类否定表述，遇到否定式口味需求请改用 recommend_dish 传正面标签（如：清淡）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "对想吃的菜的自然语言描述",
                    }
                },
                "required": ["description"],
            },
        },
    },

]


TOOLS_REGISTRY = {
    "query_dish_info": query_dish_info,
    "recommend_dish": recommend_dish,
    "random_dish": random_dish,
    "search_dishes": search_dishes,
    "find_by_meaning": find_by_meaning,
}

