import gradio as gr

from agent_core import run_agent
from main import SYSTEM_PROMPT


def chat(message: str, history: list) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history
    messages.append({"role": "user", "content": message})
    reply = run_agent(messages)
    return reply


demo = gr.ChatInterface(
    fn=chat,
    title="四川美食 Agent",
    description="能查资料库、按口味推荐、随机选菜、语义搜菜的川菜顾问",
    examples=[
        "麻婆豆腐怎么做",
        "想吃点不辣的",
        "随便来三个",
        "深夜加班，想吃点方便又暖胃的",
        "有什么菜是用牛肉做的",
    ],
)

if __name__ == "__main__":
    demo.launch(share=True)
