import requests, json, os, re, hashlib, time
from bs4 import BeautifulSoup
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import textwrap

JSON_PATH = "news.json"
IMG_DIR = "images"
MAX_NEWS = 500
WORDS_MIN = 450
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

def clean_all(text):
    if not text: return ""
    text = re.sub(r'ABP Live|ABP News|BBC Hindi|BBC News|NDTV|Navbharat Times|Aaj Tak|Amar Ujala|Dainik Jagran|Live Hindustan|The Lallantop|आज तक|एबीपी', '', text, flags=re.I)
    text = re.sub(r'Is Ghaziabad.*|Desh khabar se jude.*|The 4th Pillar.*padhte rahein.*|Is Desh.*|Is Khabar.*', '', text, flags=re.I)
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def clean_source_name(title):
    title = clean_all(title)
    title = re.sub(r'\s*-\s*(ABP|BBC|NDTV|Amar Ujala).*$', '', title, flags=re.I)
    title = re.sub(r'\s*\|\s*.*$', '', title)
    title = re.sub(r'\[.*?\]', '', title)
    return title.strip()

def create_big_image(title, filename, category):
    img = Image.new('RGB', (1080, 1080), color=(255,255,255))
    draw = ImageDraw.Draw(img)
    try:
        font_title = ImageFont.truetype("arial.ttf", 44)
        font_cat = ImageFont.truetype("arialbd.ttf", 30)
        font_small = ImageFont.truetype("arial.ttf", 24)
        font_bold = ImageFont.truetype("arialbd.ttf", 26)
    except:
        font_title = font_cat = font_small = font_bold = ImageFont.load_default()

    bg_color = (11, 32, 71)
    draw.rectangle([0, 0, 1080, 150], fill=bg_color)

    try:
        for name in ["logo.png", "the4thpillarnews.jpg", "4thpillar24x7.jpg", "4thpillar24x7.png"]:
            if os.path.exists(name):
                logo = Image.open(name).convert("RGBA")
                logo = logo.resize((90, 90))
                img.paste(logo, (25, 30), logo if logo.mode == 'RGBA' else None)
                break
    except: pass

    draw.text((130, 35), f"{category.upper()} | The Fourth Pillar", fill=(255,255,255), font=font_bold)
    draw.text((130, 75), "Sach Ka Chautha Stambh | Gaurav Sharma", fill=(242, 193, 78), font=font_small)
    
    ct = clean_source_name(title)
    wrapped = textwrap.fill(ct, width=25)
    draw.text((40, 200), wrapped, fill=(0,0,0), font=font_title)
    
    draw.rectangle([40, 850, 320, 900], fill=bg_color)
    draw.text((60, 860), category.upper(), fill=(255,255,255), font=font_cat)
    draw.text((40, 920), datetime.now().strftime("%d %B %Y"), fill=(100,100,100), font=font_small)
    draw.text((40, 955), "By Gaurav Sharma | 4th Pillar News", fill=(100,100,100), font=font_small)
    img.save(filename, quality=90)
    return filename

def get_article_links(list_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(list_url, timeout=15, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if not href.startswith('http'):
                if href.startswith('/'):
                    base = '/'.join(list_url.split('/')[:3])
                    href = base + href
                else: continue
            if any(x in href for x in ['/news/', '/sports/', '/entertainment/', '/business/', '/technology/', '/delhi', '/international']):
                if len(href) > 40 and href not in links:
                    links.append(href)
            if len(links) >= 15: break
        return links
    except: return []

def extract_500_words(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, timeout=20, headers=headers)
        r.raise_for_status()
    except: return None, None
    soup = BeautifulSoup(r.text, 'html.parser')
    
    h1 = soup.find('h1')
    title = h1.get_text(strip=True) if h1 else (soup.title.get_text(strip=True) if soup.title else "")
    if len(title) < 15: return None, None
    title = clean_source_name(title)

    text = ""
    for p in soup.find_all('p'):
        t = p.get_text(strip=True)
        if len(t) < 50: continue
        low = t.lower()
        if any(b in low for b in ["subscribe","follow us","advertisement","also read","desh se kisi","hinglish","download app","like us","facebook","twitter","instagram"]):
            continue
        text += t + " "

    words = text.split()
    if len(words) < WORDS_MIN: return None, None
    words = words[:WORDS_MAX]
    full = " ".join(words)
    full = clean_all(full)
    
    # elaborate paragraphs
    paras = []
    for i in range(0, len(words), 90):
        chunk = " ".join(words[i:i+90])
        paras.append(f"<p>{chunk}.</p>")
    content_html = "\n".join(paras)
    
    return title, content_html

# MAIN
all_news = []
if os.path.exists(JSON_PATH):
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            all_news = json.load(f)
    except: all_news = []

seen_urls = set([n.get('url','') for n in all_news])

for category, list_urls in CATEGORY_LINKS.items():
    for list_url in list_urls:
        article_links = get_article_links(list_url)
        for link in article_links:
            if link in seen_urls: continue
            print(f"[{category}] {link}")
            title, content_html = extract_500_words(link)
            if not title or not content_html: continue
            
            file_id = hashlib.md5(link.encode()).hexdigest()[:10]
            img_path = f"{IMG_DIR}/{file_id}.jpg"
            create_big_image(title, img_path, category)
            
            item = {
                "id": file_id,
                "title": title,
                "description": " ".join(content_html.replace('<p>','').replace('</p>','').split()[:32]) + "...",
                "content": content_html,
                "image": img_path,
                "url": "#",
                "publishedAt": datetime.now().strftime("%d %B %Y, %I:%M %p"),
                "author": "Gaurav Sharma",
                "category": category,
                "source": "The Fourth Pillar News"
            }
            all_news.insert(0, item)
            seen_urls.add(link)
            time.sleep(1)
            if len(all_news) >= MAX_NEWS: break
        if len(all_news) >= MAX_NEWS: break

all_news = all_news[:MAX_NEWS]
with open(JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(all_news, f, ensure_ascii=False, indent=2)

print(f"Done: {len(all_news)} news")
