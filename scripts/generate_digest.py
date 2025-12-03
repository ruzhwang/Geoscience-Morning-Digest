# scripts/generate_digest.py
import os
import json
from datetime import datetime
from openai import OpenAI

# -------------------
DAILY_MD_PATH = "output/daily.md"
SEEN_JSON_PATH = "state/seen.json"

today = datetime.now().strftime("%Y-%m-%d")

# -------------------
# 读取记录
with open(SEEN_JSON_PATH, "r", encoding="utf-8") as f:
    seen = json.load(f)

# 严格筛选今日新增
papers_data = [p for p in seen if isinstance(p, dict) and p.get("date") == today]

# -------------------
digest_text = ""
if papers_data:
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    if not DEEPSEEK_API_KEY:
        raise ValueError("请设置环境变量 DEEPSEEK_API_KEY")
    
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
    
    # 构建输入
    papers_brief = "\n".join([f"{p.get('title','未知标题')} ({p.get('source','未知期刊')})" for p in papers_data])
    
    system_prompt = (
        "你是一名地球科学领域的科研助手。\n"
        "请根据以下论文列表生成 Markdown 格式的日报。\n"
        "格式要求：\n"
        "1. 整体趋势提炼，6-8 点。\n"
        "2. 按主题自动分类，表格形式，列：主题 | 代表论文 | 备注。\n"
        "3. 每篇论文一句话核心贡献。\n"
        "4. 不要保留原始条目列表。"
    )
    user_prompt = f"今天日期：{today}\n新增论文列表：\n{papers_brief}"

    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            stream=False
        )
        ai_content = resp.choices[0].message.content
    except Exception as e:
        ai_content = f"摘要生成失败: {e}"
    
    # 构建固定模板
    digest_text = f"""
### 1. 整体趋势提炼
{ai_content.split('###')[0].strip()}

### 2. 按主题自动分类
{ai_content.split('###')[1].strip() if '###' in ai_content else '暂无分类'}

### 3. 每篇论文一句话核心贡献
{ai_content.split('###')[2].strip() if len(ai_content.split('###'))>2 else '暂无核心贡献'}
"""
else:
    digest_text = "今日没有新增论文。"

# -------------------
# 写入 Markdown
new_content = f"# Daily Paper Digest — {today}\n\n" \
              f"**今日新增论文**：{len(papers_data)}\n\n" \
              f"**摘要整理**：\n{digest_text}\n"

with open(DAILY_MD_PATH, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Markdown file更新完成。")
