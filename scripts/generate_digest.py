# scripts/generate_digest.py
import os
import json
import requests
from datetime import datetime

DAILY_MD_PATH = "output/daily.md"
SEEN_JSON_PATH = "state/seen.json"

# 从 seen.json 读取
with open(SEEN_JSON_PATH, "r", encoding="utf-8") as f:
    seen = json.load(f)

today = datetime.now().strftime("%Y-%m-%d")

# 收集当天新增论文
papers = []
for item in seen:
    # 如果 item 是 dict 并有 date
    if isinstance(item, dict) and item.get("date") == today:
        papers.append(f"- {item['title']} ({item['source']})")
    # 如果 item 是 str，则直接加入
    elif isinstance(item, str):
        papers.append(f"- {item}")

if not papers:
    print("No new entries today.")
    digest = "今日没有新增论文。"
else:
    print(f"Generating digest for {len(papers)} papers...")

    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    if not DEEPSEEK_API_KEY:
        raise ValueError("请设置环境变量 DEEPSEEK_API_KEY")

    papers_raw = "\n".join(papers)

    url = "https://api.deepseek.ai/v1/generate"
    payload = {
        "prompt": f"""
你是一名地球科学领域的专业科研助手。

下面是今天新增的论文列表，请你完成以下任务：

1）提炼今天新增论文的整体趋势  
2）用学术语言生成一个“今日论文晨报”，适合科研工作者快速阅读  
3）按主题自动分类（如构造、地球化学、地球动力学等）  
4）每篇论文总结一句话核心贡献  
5）最后附上原始条目列表

今天日期：{today}

以下是新增论文条目：

{papers_raw}

请严格输出 Markdown 格式。
""",
        "model": "text-summary"
    }
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        resp = requests.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        digest = resp.json().get("text", "未能生成摘要")
    except Exception as e:
        digest = f"摘要生成失败: {e}"

# 写入 daily.md
if os.path.exists(DAILY_MD_PATH):
    with open(DAILY_MD_PATH, "r", encoding="utf-8") as f:
        daily_md = f.read()
else:
    daily_md = ""

new_content = f"# Daily Paper Digest — {today}\n\n**今日新增论文**：{len(papers)}\n\n**摘要整理**：\n{digest}\n\n---\n\n"
new_content += daily_md

with open(DAILY_MD_PATH, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Markdown file updated.")
