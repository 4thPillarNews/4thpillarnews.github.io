import requests, os, json
from datetime import datetime, timedelta

API_KEY = os.getenv("GNEWS_API_KEY")
categories = ["nation", "world", "sports", "entertainment", "business"]

hindi_months = {"January":"जनवरी","February":"फरवरी","March":"मार्च","April":"अप्रैल","May":"मई","June":"जून","July":"जुलाई","August":"अगस्त","September":"सितंबर","October":"अक्टूबर","November":"नवंबर","December":"दिसंबर"}

try:
    with open("news.json", "r", encoding="utf-8") as f:
        old_news = json.load(f)
except:
    old_news = []

old_urls = {n.get("url") for n in old_news}
fresh = []

for cat in categories:
    url = f"https://gnews.io/api/v4/top-headlines?category={cat}&lang=hi&country=in&max=10&apikey={API_KEY}"
    try:
        data = requests.get(url).json()
        for a in data.get("articles", []):
            if a["url"] in old_urls: continue

            # Time fix
            try:
                utc = datetime.fromisoformat(a["publishedAt"].replace("Z", "+00:00"))
                ist = utc + timedelta(hours=5, minutes=30)
                hm = hindi_months.get(ist.strftime("%B"), ist.strftime("%B"))
                hindi_time = ist.strftime(f"%d {hm} %Y, %I:%M %p IST")
            except:
                hindi_time = a["publishedAt"]

            # ORIGINAL news only - no AI
            original_text = a.get("description") or a.get("content") or ""
            original_text = original_text.split("... [")[0] # GNews ka cut hata diya

            fresh.append({
                "title": a["title"],
                "description": original_text, # Yahi original hai
                "image": a.get("image"),
                "url": a["url"],
                "publishedAt": hindi_time,
                "author": "Gaurav Sharma",
                "category": cat,
                "source": a["source"]["name"]
            })
            old_urls.add(a["url"])
    except: continue

final_list = fresh + old_news
final_list = final_list[:500]

with open("news.json", "w", encoding="utf-8") as f:
    json.dump(final_list, f, ensure_ascii=False, indent=2)

print(f"Added {len(fresh)}")
