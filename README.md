# 四川美食 Agent

基于 Function Calling + RAG 的川菜顾问：查菜谱、按口味推荐、随机选菜、字面/语义双检索，
自带行为评测集，支持终端与 Web 两种界面。

## 功能一览

| 工具 | 能力 | 示例问法 |
|---|---|---|
| query_dish_info | 查菜（别名/错字容错） | 肺片怎么做 |
| recommend_dish | 标签口味推荐 | 想吃点不辣的 |
| random_dish | 随机选菜（支持数量） | 随便来三个 |
| search_dishes | 跨字段字面搜索 | 有什么菜是用牛肉做的 |
| find_by_meaning | 语义检索（RAG） | 深夜加班想吃点方便又暖胃的 / 张师傅的家规是什么 |

## 架构

```mermaid
flowchart TD
    A[main.py 入口/对话循环] --> B[agent_core.py Agent循环+流式+记忆裁剪]
    A2[app.py Gradio Web界面] --> B
    B --> C[tools.py 工具函数+schema+注册表]
    C --> D[dish_data.py 加载器]
    C --> E[rag.py 向量检索]
    D --> F[(knowledge/dishes.json)]
    E --> F
    E --> G[(knowledge/docs/*.md)]
    E --> H[llm.py 双客户端]
    B --> H
    H --> I[小米 MiMo 聊天模型]
    H --> J[百川 Baichuan-Text-Embedding]
    K[eval.py 评测 6/6] --> B
