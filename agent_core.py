import json

from tools import TOOLS_REGISTRY, TOOL_SCHEMAS
from llm import client,MODEL_NAME


def run_agent(messages: list) -> str:
    while True:
        stream = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=TOOL_SCHEMAS,
            timeout=60,
            stream = True
        )

        content_parts:list=[]
        calls:dict = {}

        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta

            if delta.content:
                if not content_parts:
                    print("Agent:",end="",flush=True)
                print(delta.content,end="",flush=True)
                content_parts.append(delta.content)

            for tc in delta.tool_calls or []:
                slot = calls.setdefault(tc.index,{"id":"","name":"","args":""})
                if tc.id:
                    slot["id"] = tc.id
                if tc.function and tc.function.name:
                    slot["name"] += tc.function.name
                if tc.function and tc.function.arguments:
                    slot["args"] += tc.function.arguments

        if not calls:
            print()
            return "".join(content_parts) or "（这轮没有回复内容）"

        messages.append({
            "role":"assistant",
            "content":"".join(content_parts) or None,
            "tool_calls":[{
                "id":c["id"],
                "type":"function",
                "function":{"name":c["name"],"arguments":c["args"]},
            }
            for c in calls.values()],
        })

        for c in calls.values():
            print(f"-->决策：调用{c['name']},参数{c['args']}")
            func = TOOLS_REGISTRY.get(c["name"])
            args = json.loads(c["args"]) if c["args"] else{}
            result = func(**args) if func else f"工具{c['name']}不存在"
            print(f"<--结果：{result[:50]}")
            messages.append({
                "role":"tool",
                "tool_call_id":c["id"],
                "content":result,
            })

        # message = response.choices[0].message
        #
        # if not message.tool_calls:
        #     return message.content or "这轮没有回复内容"
        #
        # messages.append(message)
        # for tool_call in message.tool_calls:
        #     args = json.loads(tool_call.function.arguments)
        #     name = tool_call.function.name
        #     print(f"<--决策：调用{name},参数{args}")
        #     func = TOOLS_REGISTRY.get(name)
        #     result = func(**args) if func else f"工具{name}不存在"
        #     print(f"<--结果：{result[:50]}")
        #     messages.append({
        #         "role":"tool",
        #         "tool_call_id":tool_call.id,
        #         "content":result,
        #     })


MAX_HISTORY = 20

def _role(m)->str:
    return m["role"] if isinstance(m, dict) else m.role

def trim_messages(messages: list) -> list:
    if len(messages) <= MAX_HISTORY+1:
        return messages

    system,history = messages[0],messages[1:]
    trimmed = history[-MAX_HISTORY:]

    for i,m in enumerate(trimmed):
        if _role(m) == "user":
            return [system]+trimmed[i:]
    return [system]+trimmed