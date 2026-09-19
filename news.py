import requests
import json
import os
import re
import time
import random
from bs4 import BeautifulSoup
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import textwrap

# ========== TERI TO-DO LIST SE CONFIG ==========
JSON_PATH = "news.json"
IMG_DIR = "images"
LOGO_PATH = "the4thpillarnews.jpg"
MAX_NEWS = 500
WORDS_MIN = 500
WORDS_MAX = 600

os.makedirs(IMG_DIR, exist_ok=True)

# Category ke hisab se links - NCR, National, International, Sports, Entertainment, Business, Technology
CATEGORY_LINKS = {
    "NCR": [
        "https://www.amarujala.com/delhi-ncr",
        "https://www.jagran.com/delhi-ncr",
    ],
    "National": [
        "https://www.abplive.com/news/india",
        "https://navbharattimes.indiatimes.com/india",
    ],
    "International": [
        "https://www.bbc.com/hindi/international",
        "https://www.abplive.com/news/world",
    ],
    "Sports": [
        "https://www.abplive.com/sports",
        "https://navbharattimes.indiatimes.com/sports",
    ],
    "Entertainment": [
        "https://www.abplive.com/entertainment",
        "https://navbharattimes.indiatimes.com/entertainment",
    ],
    "Business": [
        "https://www.abplive.com/business",
        "https://navbharattimes.indiatimes.com/business",
    ],
    "Technology": [
        "https://www.abplive.com/technology",
        "https://navbharattimes.indiatimes.com/technology",
    ]
}

def clean_source_name(title):
    title = re.sub(r'\s*-\s*(ABP Live|ABP News|BBC Hindi|BBC News|NDTV|Navbharat Times|Aaj Tak|Amar Ujala|Dainik Jagran|Live Hindustan|The Lallantop|Jagran|ABP).*$', '', title, flags=re.I)
    title = re.sub(r'\s*\|\s*(ABP|BBC|NDTV|NBT|Amar Ujala).*$', '', title
