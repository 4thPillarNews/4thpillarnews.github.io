import requests, os, json
from datetime import datetime, timedelta

API_KEY = os.getenv("GNEWS_API_KEY")
categories = ["nation", "world", "sports", "entertainment", "business"]
hindi_months = {"January":"जनवरी","February":"फरवरी","March":"मार्च","April":"अप्रैल","May":"मई","June":"जून","July":"जुलाई","August":"अगस्त","September":"सितंबर","October":"अक्टूबर","November":"नवंबर","December":"दिसंबर"}

try:
    with open("news.json", "r", encoding="utf-8") as f:
        old_news = json.load(f)
except: old_news = []

old_urls = {n.get("url") for n in old_news}
fresh = []

for cat in categories:
    url = f"https://gnews.io/api/v4/top-headlines?category={cat}&lang=hi&country=in&max=10&apikey={API_KEY}"
    try:
        r = requests.get(url, timeout=20).json()
        for a in r.get("articles", []):
            if a["url"] in old_urls: continue

            # Time - sahi IST
            utc = datetime.fromisoformat(a["publishedAt"].replace("Z", "+00:00"))
            ist = utc + timedelta(hours=5, minutes=30)
            hm = hindi_months.get(ist.strftime("%B"), ist.strftime("%B"))
            hindi_time = ist.strftime(f"%d {hm} %Y, %H:%M") # 24hr - jaise 15 सितंबर 2026, 15:30

            original = a.get("description") or a.get("content") or a.get("title") or ""
            original = original.split("... [")[0].strip()

            fresh.append({
                "title": a["title"],
                "description": original,
                "content": original,
                "image": a.get("image"),
                "url": a["url"],
                "publishedAt": hindi_time,
                "author": "Gaurav Sharma",
                "category": cat,
                "source": a["source"]["name"]
            })
            old_urls.add(a["url"])
    except Exception as e:
        print(e)
        continue

final_list = fresh + old_news
final_list = final_list[:500]

with open("news.json", "w", encoding="utf-8") as f:
    json.dump(final_list, f, ensure_ascii=False, indent=2)

print(f"Added: {len(fresh)}, Total: {len(final_list)}")
