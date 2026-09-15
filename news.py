import requests, os, json
from datetime import datetime, timedelta

API_KEY = os.getenv("GNEWS_API_KEY")
categories = ["nation", "world", "sports", "entertainment", "business", "general"]

hindi_months = {
    "January":"जनवरी", "February":"फरवरी", "March":"मार्च", "April":"अप्रैल",
    "May":"मई", "June":"जून", "July":"जुलाई", "August":"अगस्त",
    "September":"सितंबर", "October":"अक्टूबर", "November":"नवंबर", "December":"दिसंबर"
}

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
            if a["url"] not in old_urls:
                # Time fix - IST Hindi
                try:
                    utc = datetime.fromisoformat(a["publishedAt"].replace("Z", "+00:00"))
                    ist = utc + timedelta(hours=5, minutes=30)
                    eng_month = ist.strftime("%B")
                    hin_month = hindi_months.get(eng_month, eng_month)
                    hindi_time = ist.strftime(f"%d {hin_month} %Y, %I:%M %p")
                except:
                    hindi_time = a.get("publishedAt","")

                # News content fix - kabhi khali na rahe
                desc = a.get("description") or a.get("content") or a.get("title") or ""
                if len(desc) < 20:
                    desc = a.get("title","")
                
                # Re-written in Hindi style
                rewritten = f"{a['title']} को लेकर बड़ी अपडेट सामने आई है। {desc[:300]} यह खबर देश-दुनिया से जुड़ी अहम जानकारी दे रही है। अधिक जानकारी के लिए पूरी खबर पढ़ें।"

                fresh.append({
                    "title": a["title"],
                    "description": rewritten,
                    "image": a.get("image"),
                    "url": a["url"],
                    "publishedAt": hindi_time,
                    "author": "Gaurav Sharma",
                    "category": cat,
                    "source": a["source"]["name"]
                })
                old_urls.add(a["url"])
    except Exception as e:
        print(f"Error in {cat}: {e}")
        continue

final_list = fresh + old_news
final_list = final_list[:500]

with open("news.json", "w", encoding="utf-8") as f:
    json.dump(final_list, f, ensure_ascii=False, indent=2)

print(f"Added {len(fresh)}, Total {len(final_list)}")
