import os, requests, textwrap, random
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

FONT_URL = "https://github.com/google/fonts/raw/main/ofl/notosansdevanagari/NotoSansDevanagari-Bold.ttf"
FONT_PATH = "/tmp/NotoSans.ttf"
if not os.path.exists(FONT_PATH):
    r = requests.get(FONT_URL, timeout=30)
    open(FONT_PATH, 'wb').write(r.content)

def get_news_image(query="news"):
    # Copyright free images from Unsplash Source (no API key needed)
    # sketch / generic news type
    try:
        url = f"https://source.unsplash.com/800x450/?{query},news,india"
        resp = requests.get(url, timeout=15)
        img = Image.open(BytesIO(resp.content)).convert("RGB")
        return img
    except:
        # fallback agar net fail ho jaye
        return Image.new('RGB', (800,450), (20,20,20))

def create_image(title, filename):
    os.makedirs("images", exist_ok=True)
    
    # title se keyword nikal ke usi type ki image lao
    q = "news"
    if "चुनाव" in title or "election" in title.lower(): q = "election,voting"
    elif "पुलिस" in title or "अपराध" in title: q = "police,court"
    elif "मौसम" in title or "बारिश" in title: q = "weather,rain"
    elif "उत्तर प्रदेश" in title or "योगी" in title: q = "lucknow,uttar-pradesh"
    else: q = "newspaper,breaking-news"

    base = get_news_image(q)
    base = base.resize((800, 450))
    
    # upar kaala halka overlay taaki text padh sake
    overlay = Image.new('RGB', (800,450), (0,0,0))
    img = Image.blend(base, overlay, 0.4)

    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 800, 8], fill=(255, 193, 7))

    try:
        font_title = ImageFont.truetype(FONT_PATH, 38)
        font_brand = ImageFont.truetype(FONT_PATH, 18)
    except:
        font_title = ImageFont.load_default()
        font_brand = ImageFont.load_default()

    lines = textwrap.wrap(title, width=30)
    y = 180
    for line in lines[:3]:
        # text ke peeche halka shadow
        draw.text((42, y+2), line, font=font_title, fill="black")
        draw.text((40, y), line, font=font_title, fill="white")
        y += 55

    draw.text((40, 410), "4thPillarNews.com", font=font_brand, fill="#FFC107")
    
    path = f"images/{filename}"
    img.save(path)
    return path
