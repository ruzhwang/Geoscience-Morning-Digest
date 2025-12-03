# scripts/fetch_rss.py
import feedparser
import json
import os
from datetime import datetime

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
    "https://rss.sciencedirect.com/publication/science/00167037"
]

SEEN_FILE = "state/seen.json"
OUTPUT_FILE = "output/daily.json"  # 可以先保存抓取数据，用于调试
today = datetime.now().strftime("%Y-%m-%d")

# -------------------------
# Load / Save Seen IDs
# -------------------------
def load_seen():
    if not os.path.exists(SEEN_FILE):
        return []
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            data = f.read().strip()
            if not data:
                return []
            return json.loads(data)
    except Exception as e:
        print(f"Error reading seen.json: {e}")
        return []

def save_seen(seen):
    os.makedirs(os.path.dirname(SEEN_FILE), exist_ok=True)
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(seen, f, indent=2, ensure_ascii=False)

# -------------------------
# Fetch New RSS Entries
# -------------------------
def fetch_new_entries():
    seen = load_seen()
    seen_uids = {p['uid'] for p in seen if 'uid' in p}
    new_entries = []
    total_fetched = 0

    for url in RSS_FEEDS:
        print(f"\nParsing feed: {url}")
        feed = feedparser.parse(url)
        source_name = feed.feed.get("title", "Unknown Source")
        entries = feed.entries
        print(f"  -> Found {len(entries)} entries from {source_name}")
        total_fetched += len(entries)

        for entry in entries:
            uid = entry.get("id") or entry.get("link")
            if not uid or uid in seen_uids:
                continue

            paper = {
                "uid": uid,
                "title": entry.get("title", "未知标题"),
                "source": source_name,
                "link": entry.get("link", ""),
                "summary": entry.get("summary", "").strip(),
                "authors": [a.get("name") for a in entry.get("authors", [])] if "authors" in entry else [],
                "date": today
            }

            new_entries.append(paper)
            seen.append(paper)
            seen_uids.add(uid)

    save_seen(seen)
    print(f"\n=== Summary ===")
    print(f"Total entries fetched: {total_fetched}")
    print(f"New entries added: {len(new_entries)}")
    return new_entries

# -------------------------
if __name__ == "__main__":
    new_entries = fetch_new_entries()
