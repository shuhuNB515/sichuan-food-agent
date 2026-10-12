import time

from agent_core import run_agent
from main import SYSTEM_PROMPT

CASES = [
    {
        "名称": "别名救回：肺片 → 夫妻肺片",
        "输入": "肺片怎么做",
        "必须调用": ["query_dish_info"],
        "回答含": ["夫妻肺片"],
    },
    {
        "名称": "否定式需求路由",
        "输入": "想吃点不辣的",
        "必须调用": ["recommend_dish"],
        "回答含": ["开水白菜"],
        "回答禁含": ["宫保鸡丁"],
    },
{
        "名称": "标签盲区走语义检索",
        "输入": "深夜加班，想吃点方便又暖胃的",
        "必须调用": ["find_by_meaning"],
    },
    {
        "名称": "库外菜诚实承认",
        "输入": "辣子鸡丁怎么做",
        "必须调用": ["query_dish_info"],
        "回答含": ["没有"],
},
    {
        "名称": "常识问题不查库",
        "输入": "川菜有什么整体特点？",
        "禁止调用": ["query_dish_info", "search_dishes", "find_by_meaning", "recommend_dish", "random_dish"],
    },
{
        "名称": "数量理解：来三个",
        "输入": "随便来三个",
        "必须调用": ["random_dish"],
    },
]

def get_tool_trace(messages:list)->list[str]:
    names=[]
    for m in messages:
        if isinstance(m,dict) and m.get("tool_calls"):
            names += [tc["function"]["name"] for tc in m["tool_calls"]]
    return names

def run_case(case:dict)->bool:
    print(f"\n{'=' * 50}\n案例:{case['名称']}\n输入:{case['输入']}")
    messages = [
        {"role":"system","content":SYSTEM_PROMPT},
        {"role":"user","content":case["输入"]},
    ]

    reply = run_agent(messages) or ""
    trace = get_tool_trace(messages)
    all_pass = True
    for tool in case.get("必须调用", []):
        ok = tool in trace
        all_pass = all_pass and ok
        print(f"  [{'通过' if ok else '失败'}] 应调用 {tool}（实际：{trace or '无'}）")
    for tool in case.get("禁止调用", []):
        ok = tool not in trace
        all_pass = all_pass and ok
        print(f"  [{'通过' if ok else '失败'}] 不应调用 {tool}")
    for kw in case.get("回答含", []):
        ok = kw in reply
        all_pass = all_pass and ok
        print(f"  [{'通过' if ok else '失败'}] 回答应含「{kw}」")
    for kw in case.get("回答禁含", []):
        ok = kw not in reply
        all_pass = all_pass and ok
        print(f"  [{'通过' if ok else '失败'}] 回答应避开「{kw}」")
    return all_pass

def main():
    results = []
    for case in CASES:
        results.append((case["名称"], run_case(case)))
        time.sleep(2)
    print(f"\n{'=' * 50}\n体检报告")
    for name,ok in results:
        print(f"{'通过'if ok else '失败'}  {name}")
    passed = sum(ok for _,ok in results)
    print(f"\n总分：{passed}/{len(CASES)}")

if __name__ == "__main__":
    main()