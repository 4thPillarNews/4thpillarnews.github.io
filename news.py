
import json
import os
from datetime import datetime

today = datetime.now().strftime("%d %b %Y")
JSON_FILE = "news.json"
MAX_NEWS = 500

# Agar file hai to purani news load kar
if os.path.exists(JSON_FILE):
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        try:
            old_news = json.load(f)
        except:
            old_news = []
else:
    old_news = []

# Teri To-Do List ki category se 1 nayi news auto add hogi har 2 min
# Ye sample hai, tu isko RSS se bhi jod sakta hai par AI nahi hai
new_item = {
    "id": int(datetime.now().timestamp()),
    "category": "Ghaziabad",
    "title": f"गाजियाबाद अपडेट - {today} {datetime.now().strftime('%H:%M')}",
    "date": today,
    "author": "Gaurav Sharma",
    "reporter": "Gaurav Sharma",
    "location": "Ghaziabad",
    "image": "https://images.pexels.com/photos/159711/books-bookstore-book-reading-159711.jpeg",
    "para1": "गाजियाबाद से इस वक्त की बड़ी खबर।",
    "para2": "स्थानीय प्रशासन ने जानकारी दी।",
    "para3": "लोगों ने इस फैसले का स्वागत किया।",
    "para4": "आगे और अपडेट आएगा।",
    "para5": "क्षेत्र में चर्चा बनी हुई है।",
    "para6": f"रिपोर्ट: Gaurav Sharma | The 4th Pillar News | {today}"
}

# Nayi news ko list me add kar
all_news = old_news + [new_item]

# 500 se zyada ho to sabse purani 1 delete
if len(all_news) > MAX_NEWS:
    all_news = all_news[-MAX_NEWS:]

# ID fix kar de
for i, n in enumerate(all_news):
    n['id'] = i+1
    n['date'] = today
    n['author'] = "Gaurav Sharma"
    n['reporter'] = "Gaurav Sharma"

with open(JSON_FILE, "w", encoding="utf-8") as f:
    json.dump(all_news, f, ensure_ascii=False, indent=2)

print(f"Updated: {today} Total: {len(all_news)}")
