import json

from agent_core import run_agent,trim_messages

SYSTEM_PROMPT = (
    "你是一个四川美食专家。只要用户的问题中提到任何具体菜名（如麻婆豆腐、回锅肉、宫保鸡丁等），"
    "你必须第一步先调用 query_dish_info 查询资料库，然后只基于查询结果回答菜品细节，禁止凭记忆描述菜品。"
    "用户表达口味偏好时用 recommend_dish 推荐，犹豫不决让你随机决定时用 random_dish。"
    "与具体菜品无关的一般性问题才可直接回答。"
)

HISTORY_FILE = "history.json"

def load_messages()->list:
    try:
        with open(HISTORY_FILE,"r",encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return [{"role":"system","content":SYSTEM_PROMPT}]

def save_messages(messages:list) -> None:
    with open(HISTORY_FILE,"w",encoding="utf-8") as f:
        json.dump(messages,f,ensure_ascii=False,indent=2)

def main():
    messages = load_messages()
    print("四川美食Agent已上线（输入q退出）")
    while True:
        user_input = input("你：")
        if user_input.strip() == "q":
            save_messages(messages)
            print("下次想吃啥再来找我")
            break
        if user_input.strip() == "清空":
            messages = [{"role":"system","content":SYSTEM_PROMPT}]
            save_messages(messages)
            print("记忆已清空，我门是初次见面。")
            continue
        if not user_input.strip():
            continue

        messages = trim_messages(messages)
        messages.append({"role":"user","content":user_input})
        print(f"当前历史条数：{len(messages)}")
        reply = run_agent(messages)
        print()
        messages.append({'role':"assistant","content":reply})
        save_messages(messages)

if __name__ == "__main__":
    main()