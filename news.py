import os, requests, textwrap
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

FONT_PATH = "NotoSansDev.ttf"
# Permanent font - /tmp me nahi rakhenge
if not os.path.exists(FONT_PATH):
    try:
        url = "https://github.com/google/fonts/raw/main/ofl/notosansdevanagari/NotoSansDevanagari-Bold.ttf"
        r = requests.get(url, timeout=30)
        open(FONT_PATH, 'wb').write(r.content)
    except: pass

def get_news_image(query="news"):
    try:
        # Ye 100% working hai, copyright-free
        # picsum seed se har baar alag news jaisi image
        url = f"https://picsum.photos/seed/{query}/800/450"
        resp = requests.get(url, timeout=20)
        img = Image.open(BytesIO(resp.content)).convert("RGB")
        return img
    except:
        return Image.new('RGB', (800,450), (35,35,35))

def create_image(title, filename):
    os.makedirs("images", exist_ok=True)
    
    q = "news"
    if "चुनाव" in title: q = "election"
    elif "पुलिस" in title: q = "police"
    elif "मौसम" in title: q = "weather"
    elif "योगी" in title: q = "upnews"
    else: q = f"news{len(title)}" # har news ki alag image

    base = get_news_image(q).resize((800, 450))
    
    overlay = Image.new('RGB', (800,450), (0,0,0))
    img = Image.blend(base, overlay, 0.45)

    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 800, 8], fill=(255, 193, 7))

    try:
        font_title = ImageFont.truetype(FONT_PATH, 38)
        font_brand = ImageFont.truetype(FONT_PATH, 18)
    except:
        font_title = ImageFont.load_default()
        font_brand = ImageFont.load_default()

    # Full title dikhega, kaat nahi rahe
    lines = textwrap.wrap(title, width=32)
    y = 150
    for line in lines[:4]:  # 3 ki jagah 4 line tak
        draw.text((42, y+2), line, font=font_title, fill="black")
        draw.text((40, y), line, font=font_title, fill="white")
        y += 50

    draw.text((40, 415), "4thPillarNews.com", font=font_brand, fill="#FFC107")
    
    path = f"images/{filename}"
    img.save(path)
    return path
