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

def clean_source_name(text):
    text = re.sub(r'\s*-\s*(ABP Live|ABP News|BBC Hindi|BBC News|NDTV|Navbharat Times|Aaj Tak|Amar Ujala|Dainik Jagran|The Lallantop|Live Hindustan).*$', '', text, flags=re.I)
    text = re.sub(r'\s*\|\s*(ABP|BBC|Amar Ujala).*$', '', text, flags=re.I)
    text = re.sub(r'(ABP Live|ABP News|BBC Hindi|BBC|Amar Ujala|NDTV|Aaj Tak)', '', text, flags=re.I)
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'https?://\S+', '', text)
    return text.strip()

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
           
