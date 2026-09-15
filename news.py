import requests, os, json
from datetime import datetime, timedelta

API_KEY = os.getenv("GNEWS_API_KEY")
categories = ["nation", "world", "sports", "entertainment", "business", "general"]

try:
    with open("news.json", "r", encoding="utf-8") as f:
        old_news = json.load(f)
except:
    old_news = []

old_urls = {n.get("url") for n in old_news}
fresh = []

for cat in categories:
    url = f"https://gnews.io/api/v4/top-headlines?category={cat}&lang=hi&country=in&max=5&apikey={API_KEY}"
    try:
        data = requests.get(url).json()
        for a in data.get("articles", []):
            if a["url"] not in old_urls:
                # Time ko Hindi IST me convert
                utc_time = datetime.fromisoformat(a["publishedAt"].replace("Z", "+00:00"))
                ist_time = utc_time + timedelta(hours=5, minutes=30)
                hindi_time = ist_time.strftime("%d %B %Y, %I:%M %p")
                # Hindi months
                hindi_time = hindi_time.replace("September","सितंबर").replace("January","जनवरी").replace("February","फरवरी").replace("March","मार्च").replace("April","अप्रैल").replace("May","मई").replace("June","जून").replace("July","जुलाई").replace("August","अगस्त").replace("October","अक्टूबर").replace("November","नवंबर").replace("December","दिसंबर")

                # Re-written - copy paste nahi
                rewritten_desc = f"{a['title']} के बारे में बड़ी खबर। {a['description'][:150]}... पूरी जानकारी के लिए पढ़ें।"

                fresh.append({
                    "title": a["title"],
                    "description": rewritten_desc,
                    "original_description": a["description"],
                    "image": a.get("image"),
                    "url": a["url"],
                    "publishedAt": hindi_time,
                    "actualTime": a["publishedAt"],
                    "author": "Gaurav Sharma",
                    "category": cat,
                    "source": a["source"]["name"]
                })
                old_urls.add(a["url"])
    except:
        continue

final_list = fresh + old_news
final_list = final_list[:500]

with open("news.json", "w", encoding="utf-8") as f:
    json.dump(final_list, f, ensure_ascii=False, indent=2)

print(f"Added {len(fresh)}, Total {len(final_list)}")
