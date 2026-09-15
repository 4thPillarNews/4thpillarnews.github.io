import requests, json, os
from pathlib import Path

API_KEY = os.getenv("GNEWS_API_KEY")
FILE = Path("news.json")

old_data = []
if FILE.exists():
    try:
        old_data = json.loads(FILE.read_text(encoding='utf-8'))
    except:
        old_data = []

url = f"https://gnews.io/api/v4/top-headlines?category=general&lang=en&country=in&max=20&apikey={API_KEY}"

try:
    data = requests.get(url, timeout=30).json()
    articles = data.get("articles", [])
    
    if not articles:
        print("API empty, keeping old")
        exit(0)

    # nayi news banao
    new_news = []
    for a in articles:
        new_news.append({
            "title": a.get("title"),
            "description": a.get("description",""),
            "image": a.get("image",""),
            "url": a.get("url"),
            "publishedAt": a.get("publishedAt")
        })

    # purane URL ka set banao taaki duplicate na ho
    old_urls = set([n.get("url") for n in old_data])
    filtered_new = [n for n in new_news if n.get("url") not in old_urls]

    # UPAR nayi + NEECHE purani
    final = filtered_new + old_data
    
    # sirf 100 tak rakho taaki file badi na ho
    final = final[:100]

    FILE.write_text(json.dumps(final, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"Added {len(filtered_new)} on top, total {len(final)}")

except Exception as e:
    print(f"Error {e}")
