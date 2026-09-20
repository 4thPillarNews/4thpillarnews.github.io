import os, json, requests, re
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import datetime
import xml.etree.ElementTree as ET

# Font ek baar download
FONT_FILE = "NotoSansDev.ttf"
if not os.path.exists(FONT_FILE):
    try:
        url = "https://github.com/google/fonts/raw/main/ofl/notosansdevanagari/NotoSansDevanagari-Bold.ttf"
        open(FONT_FILE, 'wb').write(requests.get(url, timeout=20).content)
    except: pass

def make_image(category, filename):
    os.makedirs("images", exist_ok=True)
    try:
        # Har category ki alag real photo - blue box khatam
        r = requests.get(f"https://picsum.photos/seed/{category}{filename}/800/450", timeout=20)
        base = Image.open(BytesIO(r.content)).convert("RGB").resize((800,450))
    except:
        base = Image.new('RGB', (800,450), (25,25,40))

    final = Image.blend(base, Image.new('RGB',(800,450),(0,0,0)), 0.4)
    draw = ImageDraw.Draw(final)
    draw.rectangle([0,0,800,10], fill=(255,193,7))

    try:
        font = ImageFont.truetype(FONT_FILE, 45)
        font2 = ImageFont.truetype(FONT_FILE, 18)
    except:
        font = ImageFont.load_default()
        font2 = font

    # Image pe sirf Category likhega - UP, NATIONAL, SPORTS - dibbe nahi ayenge
    draw.text((30,180), category.upper(), font=font, fill="white", stroke_width=2, stroke_fill="black")
    draw.text((30,415), "The Fourth Pillar News", font=font2, fill="#FFC107")

    path = f"images/{filename}"
    final.save(path)
    return path

def get_news_for_category(category, q):
    # Google News RSS - bina API key ke world wide news
    url = f"https://news.google.com/rss/search?q={q}&hl=hi&gl=IN&ceid=IN:hi"
    try:
        r = requests.get(url, timeout=15)
        root = ET.fromstring(r.content)
        items = []
        for item in root.findall(".//item")[:4]: # har category ki 4 news
            title = item.find("title").text
            desc = item.find("description").text if item.find("description") is not None else title
            # HTML tag hatao
            desc = re.sub('<[^<]+?>', '', desc)[:200]
            items.append({
                "title": title.split(" - ")[0],
                "desc": desc,
                "category": category
            })
        return items
    except:
        return [{"title": f"{category} की ताजा खबर","desc": f"{category} से जुड़ी बड़ी खबर...","category": category}]

# ---- MAIN ----
CATEGORIES = {
    "National": "National News India",
    "International": "International World News",
    "Sports": "Sports News",
    "Entertainment": "Entertainment Bollywood",
    "Business": "Business Share Market",
    "Education": "Education Jobs",
    "World": "World News",
    "UP": "Uttar Pradesh News",
    "Technology": "Technology"
}

all_news = []
for cat, query in CATEGORIES.items():
    news_items = get_news_for_category(cat, query.replace(" ","+"))
    for i, n in enumerate(news_items):
        img_name = f"{cat.lower()}_{i}_{datetime.now().strftime('%d%m%H%M')}.jpg"
        img_path = make_image(cat, img_name)
        all_news.append({
            "title": n["title"],
            "description": n["desc"] + "...",
            "category": cat,
            "image": img_path,
            "date": datetime.now().strftime("20 September 2026 | Gaurav Sharma")
        })

# news.json save
with open("news.json", "w", encoding="utf-8") as f:
    json.dump(all_news, f, ensure_ascii=False, indent=2)

print(f"Done - {len(all_news)} news with all categories")
