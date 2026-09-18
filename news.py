import requests, json, os, hashlib, re
from pathlib import Path
from datetime import datetime

API_KEY = os.getenv("GNEWS_API_KEY")
FILE = Path("news.json")

old_data = []
if FILE.exists():
    try:
        old_data = json.loads(FILE.read_text(encoding='utf-8'))
        if not isinstance(old_data, list): old_data=[]
    except: old_data=[]

def clean(t): return re.sub(r'\s+',' ',t.lower()).strip() if t else ""
old_titles = [clean(n.get("title","")) for n in old_data]
old_urls = set([n.get("url") for n in old_data if n.get("url")])

# Saari categories jo chahiye
CATEGORIES = {
    "general": "Ghaziabad / Desh",
    "world": "International",
    "nation": "Desh",
    "business": "Business",
    "entertainment": "Entertainment",
    "sports": "Sports",
    "technology": "Technology",
    "science": "Science"
}

all_new = []

for g_cat, my_cat in CATEGORIES.items():
    url = f"https://gnews.io/api/v4/top-headlines?category={g_cat}&lang=hi&country=in&max=10&apikey={API_KEY}"
    try:
        arts = requests.get(url, timeout=30).json().get("articles", [])
        for a in arts:
            title = a.get("title","").strip()
            article_url = a.get("url","").strip()
            if not title or not article_url: continue
            if article_url in old_urls: continue
            if clean(title) in old_titles: continue
            if len(title) < 20: continue

            img = a.get("image") or "./logo.png"
            hid = hashlib.md5(article_url.encode()).hexdigest()[:10]
            try:
                dt = datetime.fromisoformat(a.get("publishedAt","").replace("Z","+00:00"))
                pub = dt.strftime("%d %B %Y, %I:%M %p")
            except: pub = a.get("publishedAt","")

            desc = a.get("description","") or title
            content = f"<p><b>{title}</b></p><p>{desc}</p><p>Is {my_cat} khabar se jude har update ke liye The 4th Pillar News padhte rahein.</p>"

            all_new.append({
                "id": hid,
                "title": title,
                "description": desc,
                "content": content,
                "image": img,
                "url": article_url,
                "publishedAt": pub,
                "author": "Gaurav Sharma",
                "category": my_cat,
                "source": "The 4th Pillar News"
            })
            old_titles.append(clean(title))
            old_urls.add(article_url)
    except Exception as e:
        print(f"Error in {g_cat}: {e}")
        continue

final = all_new + old_data
final = final[:500]
FILE.write_text(json.dumps(final, indent=2, ensure_ascii=False), encoding='utf-8')
print(f"Added {len(all_new)} total. New total {len(final)}")
