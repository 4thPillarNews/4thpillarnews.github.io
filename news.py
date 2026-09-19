import requests, json, os, re, hashlib
from bs4 import BeautifulSoup
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import textwrap

JSON_PATH = "news.json"
IMG_DIR = "images"
LOGO_PATH = "logo.png"
WORDS_MIN = 450
WORDS_MAX = 600

os.makedirs(IMG_DIR, exist_ok=True)

def clean_all(text):
    # Saare dusre channel + tera wala ganda footer hatao
    text = re.sub(r'ABP Live|ABP News|BBC Hindi|BBC News|NDTV|Navbharat Times|Aaj Tak|Amar Ujala|Dainik Jagran|Live Hindustan|The Lallantop', '', text, flags=re.I)
    text = re.sub(r'Desh se kisi khabar ke liye.*|4th pillar hinglish.*|The 4th Pillar Hinglish.*|padhe.*hinglish.*', '', text, flags=re.I)
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def clean_source_name(title):
    title = clean_all(title)
    title = re.sub(r'\s*-\s*.*$', '', title)
    title = re.sub(r'\s*\|\s*.*$', '', title)
    return title.strip()

def create_big_image(title, filename, category):
    img = Image.new('RGB', (1080, 1080), color=(255,255,255))
    draw = ImageDraw.Draw(img)
    try:
        font_title = ImageFont.truetype("arial.ttf", 42)
        font_bold = ImageFont.truetype("arialbd.ttf", 28)
        font_small = ImageFont.truetype("arial.ttf", 24)
    except:
        font_title = font_bold = font_small = ImageFont.load_default()
    bg = (11,32,71)
    draw.rectangle([0,0,1080,150], fill=bg)
    # logo
    try:
        for lp in ["logo.png","the4thpillarnews.jpg","4thpillar24x7.jpg"]:
            if os.path.exists(lp):
                logo = Image.open(lp).convert("RGBA").resize((90,90))
                img.paste(logo, (20,30), logo if logo.mode=='RGBA' else None)
                break
    except: pass
    draw.text((130,35), f"{category} | The Fourth Pillar", fill="white", font=font_bold)
    draw.text((130,75), "Sach Ka Chautha Stambh | Gaurav Sharma", fill=(242,193,78), font=font_small)
    wrapped = textwrap.fill(clean_source_name(title), width=26)
    draw.text((40,200), wrapped, fill="black", font=font_title)
    draw.rectangle([40,900,1030,1000], fill=bg)
    draw.text((50,925), "The Fourth Pillar News | Gaurav Sharma", fill="white", font=font_bold)
    img.save(filename, quality=90)
    return filename

def extract_500_600_words(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, timeout=25, headers=headers)
        r.raise_for_status()
    except:
        return None, None
    soup = BeautifulSoup(r.text, 'html.parser')
    title_tag = soup.find('h1')
    title = title_tag.get_text(strip=True) if title_tag else soup.title.get_text(strip=True)
    title = clean_source_name(title)
    
    full_text = ""
    for p in soup.find_all('p'):
        txt = p.get_text(strip=True)
        if len(txt) < 40: continue
        if any(x in txt.lower() for x in ["subscribe","follow us","advertisement","also read","desh se kisi","hinglish","download app","like us on"]):
            continue
        full_text += txt + " "
    
    words = full_text.split()
    if len(words) < WORDS_MIN:
        return None, None
    words = words[:WORDS_MAX]
    content = " ".join(words)
    content = clean_all(content)
    # 4-5 line nahi, pura elaborate paragraph banao
    elaborate = ""
    for i in range(0, len(words), 80):
        para = " ".join(words[i:i+80])
        elaborate += f"<p>{para}</p>\n"
    return title, elaborate

# --- MAIN LOOP ---
if os.path.exists(JSON_PATH):
    with open(JSON_PATH,'r',encoding='utf-8') as f:
        try: all_news = json.load(f)
        except: all_news = []
else:
    all_news = []

# yaha tera CATEGORY_LINKS wala loop same rahega bas is function ko call kar
# aur news item aise bana:
# title, elaborate = extract_500_600_words(link)
# if not title: continue
# img_path = create_big_image(title, f"{IMG_DIR}/{hashlib.md5(link.encode()).hexdigest()[:8]}.jpg", category)
# item = {
#   "id": hashlib.md5(link.encode()).hexdigest()[:8],
#   "title": title,
#   "description": " ".join(elaborate.replace('<p>','').replace('</p>','').split()[:30]),
#   "content": elaborate,
#   "image": img_path,
#   "url": "#",
#   "publishedAt": datetime.now().strftime("%d %B %Y, %I:%M %p"),
#   "author": "Gaurav Sharma",
#   "category": category,
#   "source": "The Fourth Pillar News"
# }
