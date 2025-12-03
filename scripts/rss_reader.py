import feedparser
import hashlib
import json
from datetime import datetime
from pathlib import Path

# === 配置 ===
RSS_FEEDS = [
    "http://www.nature.com/nature/current_issue/rss",
    "https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=science",
    "https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=sciadv",
    "https://www.nature.com/ngeo.rss",
    "https://www.nature.com/ncomms.rss",
    "https://www.nature.com/natrevearthenviron.rss",
    "https://www.pnas.org/action/showFeed?type=searchTopic&taxonomyCode=topic&tagCode=earth-sci",
    "https://www.annualreviews.org/rss/content/journals/earth/latestarticles?fmt=rss",
    "https://rss.sciencedirect.com/publication/science/00128252",
    "https://rss.sciencedirect.com/publication/science/0012821X",
    "https://agupubs.onlinelibrary.wiley.com/feed/19448007/most-recent",
    "https://agupubs.onlinelibrary.wiley.com/feed/21699356/most-recent",
    "https://agupubs.onlinelibrary.wiley.com/feed/15252027/most-recent",
    "https://rss.sciencedirect.com/publication/science/00167037",
]

OUTPUT_FILE = "output/daily.md"
SEEN_FILE = "state/seen.json"


def load_seen():
    """加载记录的已抓取文章ID"""
    if Path(SEEN_FILE).exists():
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_seen(seen_set):
    """保存已抓取的文章ID"""
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen_set), f)


def entry_id(entry):
    """使用 entry.link 作为唯一ID（hash后更安全）"""
    url = entry.get("link", "")
    return hashlib.sha256(url.encode()).hexdigest()


def fetch_new_entries():
    seen = load_seen()
    new_entries = []

    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            uid = entry_id(entry)

            # 未出现过 → 新文章
            if uid not in seen:
                new_entries.append(entry)
                seen.add(uid)

    save_seen(seen)
    return new_entries


def write_daily_md(entries):
    date_str = datetime.now().strftime("%Y-%m-%d")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(f"# 🌏 Daily Academic Digest — {date_str}\n\n")

        if not entries:
            f.write("No new articles today.\n")
            return

        for e in entries:
            title = e.get("title", "No Title")
            link = e.get("link", "")
            summary = e.get("summary", "").replace("\n", " ")

            f.write(f"## [{title}]({link})\n\n")
            f.write(f"{summary}\n\n---\n\n")


if __name__ == "__main__":
    entries = fetch_new_entries()
    write_daily_md(entries)
