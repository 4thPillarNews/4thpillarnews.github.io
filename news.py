import requests, json, os, re, hashlib, time
from bs4 import BeautifulSoup
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import textwrap

JSON_PATH = "news.json"
IMG_DIR = "images"
MAX_NEWS = 500
WORDS_MIN = 400

os.makedirs(IMG_DIR, exist_ok=True)

# AB SE HAR CATEGORY ME 3 SOURCE - ABP AKELA NAHI
CATEGORY_LINKS = {
    "NCR": ["https://www.amarujala.com/delhi-ncr", "https://www.livehindustan.com/ncr/new-delhi", "https://www.jagran.com/delhi/new-delhi-city-latest-news.html"],
    "National": ["https://www.abplive.com/news/india", "https://www.amarujala.com/india-news", "https://www.livehindustan.com/national"],
    "International": ["https://www.bbc.com/hindi/international", "https://www.abplive.com/news/world", "https://www.amarujala.com/world-news"],
    "Sports": ["https://www.abplive.com/sports", "https://www.amarujala.com/sports", "https://www.livehindustan.com/cricket"],
    "Entertainment": ["https://www.abplive.com/entertainment", "https://www.amarujala.com/entertainment", "https://www.jagran.com/entertainment-latest-news.html"],
    "Business": ["https://www.abplive.com/business", "https://www.amarujala.com/business", "https://www.livehindustan.com/business"],
    "Technology": ["https://www.abplive.com/technology", "https://www.amarujala.com/technology", "https://www.jagran.com/technology-latest-news.html"],
    "Education": ["https://www.amarujala.com/education", "https://www.livehindustan.com/career", "https://www.abplive.com/education"]
}

def clean_all(text):
    if not text: return ""
    text = re.sub(r'ABP Live|ABP News|BBC Hindi|Aaj Tak|Amar Ujala|Live Hindustan|Dainik Jagran|The Lallantop|Navbharat Times', '', text, flags=re.I)
    text = re.sub(r'Is Ghaziabad.*|Desh khabar.*|The 4th Pillar.*padhte rahein.*', '', text, flags=re.I)
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    return re.sub(r'\s+', ' ', text).strip()

def clean_title(title):
    title = clean_all(title)
    return re.sub(r'\s*-\s*.*$|\s*\|\s*.*$|\[.*?\]', '', title).strip()

def create_big_image(title, filename, category):
    img = Image.new('RGB', (1080,1080), (255,255,255))
    draw = ImageDraw.Draw(img)
    try:
        ft = ImageFont.truetype("arial.ttf",48)
        fb = ImageFont.truetype("arialbd.ttf",28)
        fs = ImageFont.truetype("arial.ttf",26)
    except:
        ft=fb=fs=ImageFont.load_default()
    draw.rectangle([0,0,1080,160], fill=(11,32,71))
    try:
        for name in ["logo.png","the4thpillarnews.jpg","4thpillar24x7.jpg"]:
            if os.path.exists(name):
                lg = Image.open(name).convert("RGBA").resize((100,100))
                img.paste(lg,(20,30), lg if lg.mode=='RGBA' else None)
                break
    except: pass
    draw.text((140,40), f"{category.upper()} | The Fourth Pillar News", fill="white", font=fb)
    draw.text((140,85), "Sach Ka Chautha Stambh | Gaurav Sharma", fill=(242,193,78), font=fs)
    draw.text((40,210), textwrap.fill(clean_title(title), width=24), fill="black", font=ft)
    draw.rectangle([40,860,350,910], fill=(11,32,71))
    draw.text((60,870), category.upper(), fill="white", font=fb)
    draw.text((40,930), datetime.now().strftime("%d %B %Y"), fill=(80,80,80), font=fs)
    draw.text((40,965), "By Gaurav Sharma | The 4th Pillar News", fill=(80,80,80), font=fs)
    img.save(filename, quality=92)
    return filename

def get_article_links(list_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(list_url, timeout=15, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        links=[]
        for a in soup.find_all('a', href=True):
            href=a['href']
            if not href.startswith('http'):
                if href.startswith('/'):
                    base='/'.join(list_url.split('/')[:3])
                    href=base+href
                else: continue
            if any(x in href for x in ['.com/', '/news/', '/india', '/world', '/sports', '/entertainment', '/business', '/technology', '/education', '/cricket', '/delhi', '/bollywood']):
                if len(href)>50 and href not in links and 'video' not in href and 'live-tv' not in href:
                    links.append(href)
            if len(links)>=12: break
        return links
    except: return []

def is_author_bio(para_text):
    low = para_text.lower()
    # UNIVERSAL BIO DETECTOR - kisi bhi naam ka bio katega
    bio_keywords = [
        "we use cookies", "personalize content", "by clicking",
        "मैं यानी", "मैं टेक", "मेरा इंटरेस्ट", "का हिस्सा हूं", "हिस्सा हूँ", "करता हूं", "करती हूं",
        "मेरी पकड़", "पसंद है", "जाना जाता हूं", "जाना जाता हूँ", "लिखने के लिए जाना",
        "परास्नातक", "माखनलाल", "चतुर्वेदी", "पत्रकारिता", "विश्वविद्यालय", "उत्तीर्ण",
        "about the author", "author bio", "holds a degree", "is a graduate", "has done his", "has done her",
        "is currently working", "has experience", "based in", "born in", "is passionate about",
        "इंटरेस्ट काफी ज्यादा", "डिजिटल सेक्शन", "सोशल मीडिया", "स्मार्टफोन लॉन्च"
    ]
    # agar para me 2 se zyada bio keyword ya "मैं" 3 baar aaye to bio hai
    count = sum(1 for k in bio_keywords if k in low)
    if count >= 1: return True
    if low.count("मैं") >= 3: return True
    if low.count("
