import requests
import json
import os
import re
import time
from bs4 import BeautifulSoup
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import textwrap

JSON_PATH = "news.json"
IMG_DIR = "images"
LOGO_PATH = "logo.png"
MAX_NEWS = 500
WORDS_MIN = 500
WORDS_MAX = 600

os.makedirs(IMG_DIR, exist_ok=True)

CATEGORY_LINKS = {
    "NCR": ["https://www.amarujala.com/delhi-ncr"],
    "National": ["https://www.abplive.com/news/india"],
    "International": ["https://www.bbc.com/hindi/international"],
    "Sports": ["https://www.abplive.com/sports"],
    "Entertainment": ["https://www.abplive.com/entertainment"],
    "Business": ["https://www.abplive.com/business"],
    "Technology": ["https://www.abplive.com/technology"]
}

def clean_source_name(title):
    # FIXED - single line regex, no bracket error
    title = re.sub(r'\s*-\s*(ABP Live|ABP News|BBC Hindi|BBC News|NDTV|Navbharat Times|Aaj Tak|Amar Ujala|Dainik Jagran).*$', '', title, flags=re.I)
    title = re.sub(r'\s*\|\s*.*$', '', title)
    title = re.sub(r'\[.*?\]$', '', title)
    return title.strip()

def create_big_image(title, filename, category):
    img = Image.new('RGB', (1080, 1080), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    try:
        font_title = ImageFont.truetype("arial.ttf", 48)
        font_cat = ImageFont.truetype("arialbd.ttf", 30)
        font_small = ImageFont.truetype("arial.ttf", 26)
        font_bold = ImageFont.truetype("arialbd.ttf", 28)
    except:
        font_title = ImageFont.load_default()
        font_cat = ImageFont.load_default()
        font_small = ImageFont.load_default()
        font_bold = ImageFont.load_default()

    cat_colors = {"NCR": (11, 32, 71),"National": (183, 28, 28),"International": (13, 71, 161),"Sports": (27, 94, 32),"Entertainment": (106, 27, 154),"Business": (62, 39, 35),"Technology": (0, 77, 64)}
    bg_color = cat_colors.get(category, (11, 32, 71))
    draw.rectangle([0, 0, 1080, 160], fill=bg_color)

    try:
        if os.path.exists(LOGO_PATH):
            logo = Image.open(LOGO_PATH).convert("RGBA")
            logo = logo.resize((100, 100))
            img.paste(logo, (30, 30), logo if logo.mode == 'RGBA' else None)
        elif os.path.exists("4thpillar24x7.jpg"):
            logo = Image.open("4thpillar24x7.jpg").convert("RGBA")
            logo = logo.resize((100, 100))
            img.paste(logo, (30, 30))
    except:
        pass

    draw.text((160, 40), f"{category.upper()} | The Fourth Pillar", fill=(255,255,255), font=font_bold)
    draw.text((160, 80), "Sach Ka Chautha Stambh | Gaurav Sharma", fill=(242, 193, 78), font=font_small)
    clean_title = clean_source_name(title)
    wrapped = textwrap.fill(clean_title, width=24)
    draw.text((50, 200), wrapped, fill=(0, 0, 0), font=font_title)
    draw.rectangle([50, 850, 300, 900], fill=bg_color)
    draw.text((70, 860), category.upper(), fill=(255,255,255), font=font_cat)
    draw.text((50, 920), datetime.now().strftime("%d %B %Y"), fill=(100,100,100), font=font_small)
    draw.text((50, 955), "By Gaurav Sharma | 4th Pillar News", fill=(100,100,100), font=font_small)
    img.save(filename, quality=95)
    return filename

def extract_500_600_words(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        r = requests.get(url, timeout=30, headers=headers)
        r.raise_for_status()
    except Exception as e:
        print(f"[FAIL] {url} -> {e}")
        return None, None, None
    soup = BeautifulSoup(r.text, 'html.parser')
    title = None
    for tag in ['h1', 'title']:
        t = soup.find(tag)
        if t:
            title = t.get_text(strip=True)
            if len(title) > 15:
                break
    if not title:
        return None, None, None
    title = clean_source_name(title)
    article_text = ""
    main_selectors = ['article', '.article', '#article', '.story', '.content', '.news-content', '.article-body']
    found_main = None
    for sel in main_selectors:
        found_main = soup.select_one(sel)
        if found_main and len(found_main.get_text()) > 300:
            break
    search_area = found_main if found_main else soup
    for p in search_area.find_all('p'):
        txt = p.get_text(strip=True)
        if len(txt) < 80:
            continue
        skip_words = ["subscribe", "follow us", "advertisement", "also read"]
        if any(w in txt.lower() for w in skip_words):
            continue
        article_text += txt + " "
        if len(article_text.split()) >= 620:
            break
    words = article_text.split()
    if len(words) < WORDS_MIN:
        print(f"[SKIP] {url} - Only {len(words)} words")
        return None, None, None
    words = words[:WORDS_MAX
