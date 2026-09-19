import requests, json, os, re, hashlib, time
from bs4 import BeautifulSoup
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import textwrap

JSON_PATH = "news.json"
IMG_DIR = "images"
MAX_NEWS = 500
WORDS_MIN = 480
WORDS_MAX = 600

os.makedirs(IMG_DIR, exist_ok=True)

CATEGORY_LINKS = {
    "NCR": ["https://www.amarujala.com/delhi-ncr", "https://www.livehindustan.com/ncr"],
    "National": ["https://www.abplive.com/news/india", "https://www.aajtak.in/india"],
    "International": ["https://www.bbc.com/hindi/international", "https://www.abplive.com/news/world"],
    "Sports": ["https://www.abplive.com/sports", "https://www.aajtak.in/sports"],
    "Entertainment": ["https://www.abplive.com/entertainment", "https://www.aajtak.in/entertainment"],
    "Business": ["https://www.abplive.com/business"],
    "Technology": ["https://www.abplive.com/technology", "https://www.aajtak.in/technology"]
}

def clean_all(text):
    if not text: return ""
    text = re.sub(r'ABP Live|ABP News|BBC Hindi|BBC News|NDTV|Navbharat Times|Aaj Tak|Amar Ujala|Dainik Jagran|Live Hindustan|The Lallantop|आज तक|एबीपी न्यूज़|Amar Ujala', '', text, flags=re.I)
    text = re.sub(r'Is Ghaziabad.*|Desh khabar se jude.*|The 4th Pillar.*padhte rahein.*|Is Desh.*|Is khabar.*|4th pillar hinglish.*', '', text, flags=re.I)
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def clean_title(title):
    title = clean_all(title)
    title = re.sub(r'\s*-\s*.*$', '', title)
    title = re.sub(r'\s*\|\s*.*$', '', title)
    title = re.sub(r'\[.*?\]', '', title)
    return title.strip()

def create_big_image(title, filename, category):
    img = Image.new('RGB', (1080, 1080), color=(255,255,255))
    draw = ImageDraw.Draw(img)
    try:
        font_title = ImageFont.truetype("arial.ttf", 48)
        font_cat = ImageFont.truetype("arialbd.ttf", 32)
        font_small = ImageFont.truetype("arial.ttf", 26)
        font_bold = ImageFont.truetype("arialbd.ttf", 28)
    except:
        font_title = font_cat = font_small = font_bold = ImageFont.load_default()

    draw.rectangle([0, 0, 1080, 160], fill=(11, 32, 71))
    try:
        for name in ["logo.png", "the4thpillarnews.jpg", "4thpillar24x7.jpg", "4thpillar24x7.png", "logo.jpg"]:
            if os.path.exists(name):
                lg = Image.open(name).convert("RGBA")
                lg = lg.resize((100, 100))
                img.paste(lg, (20, 30), lg if lg.mode == 'RGBA' else None)
                break
    except: pass

    draw.text((140, 40), f"{category.upper()} | The Fourth Pillar News", fill=(255,255,255), font=font_bold)
    draw.text((140, 85), "Sach Ka Chautha Stambh | Gaurav Sharma", fill=(242, 193, 78), font=font_small)
    
    wrapped = textwrap.fill(clean_title(title), width=24)
    draw.text((40, 210), wrapped, fill=(0,0,0), font=font_title)
    
    draw.rectangle([40, 860, 350, 910], fill=(11, 32, 71))
    draw.text((60, 870), category.upper(), fill=(255,255,255), font=font_cat)
    draw.text((40, 930), datetime.now().strftime("%d %B %Y"), fill=(80,80,80), font=font_small)
    draw.text((40, 965), "By Gaurav Sharma | The 4th Pillar News", fill=(80,80,80), font=font_small)
    img.save(filename, quality=92)
    return filename

def get_article_links(list_url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
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
            if any(x in href for x in ['/india-news/', '/news/', '/sports/', '/entertainment/', '/business/', '/technology/', '/world-news/', '/delhi', '/international', '/cricket', '/bollywood']):
                if len(href) > 50 and href not in links and '.com' in href:
                    links.append(href)
            if len(links) >= 12: break
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
    title = clean_title(title)

    full_text = ""
    for p in soup.find_all('p'):
        t = p.get_text(strip=True)
        if len(t) < 60: continue
        low = t.lower()
        if any(b in low for b in ["subscribe","follow us","advertisement","also read","desh se kisi","hinglish","download app","like us on","facebook","twitter","watch:","click here"]):
            continue
        full_text += t + " "

    words = full_text.split()
    if len(words) < WORDS_MIN: return None, None
    words = words[:WORDS_MAX]
    
    paras = []
    for i in range(0, len(words), 95):
        chunk = " ".join(words[i:i+95])
        chunk = clean_all(chunk)
        paras.append(f"<p>{chunk}.</p>")
    content_html = "\n".join(paras)
    return title, content_html

# LOAD OLD BANK - 500 news safe rahegi
all_news = []
if os.path.exists(JSON_PATH):
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            all_news = json.load(f)
    except: all_news = []

seen = set([n.get('id','') for n in all_news])

for category, list_urls in CATEGORY_LINKS.items():
    for list_url in list_urls:
        article_links = get_article_links(list_url)
        for link in article_links:
            fid = hashlib.md5(link.encode()).hexdigest()[:10]
            if fid in seen: continue
            title, content_html = extract_500_words(link)
            if not title or not content_html: continue
            
            img_path = f"{IMG_DIR}/{fid}.jpg"
            create_big_image(title, img_path, category)
            
            desc_words = re.sub(r'<[^>]+>', '', content_html).split()[:32]
            item = {
                "id": fid,
                "title": title,
                "description": " ".join(desc_words) + "...",
                "content": content_html,
                "image": img_path,
                "url": "#",
                "publishedAt": datetime.now().strftime("%d %B %Y, %I:%M %p"),
                "author": "Gaurav Sharma",
                "category": category,
                "source": "The Fourth Pillar News"
            }
            all_news.insert(0, item)
            seen.add(fid)
            print(f"ADDED {category}: {title[:50]}")
            time.sleep(0.8)
            if len(all_news) >= MAX_NEWS: break
        if len(all_news) >= MAX_NEWS: break
    if len(all_news) >= MAX_NEWS: break

all_news = all_news[:MAX_NEWS]

# FINAL CLEAN - purani me bhi agar Aaj Tak bacha ho to hata de
for n in all_news:
    n['title'] = clean_title(n['title'])
    n['source'] = "The Fourth Pillar News"
    n['author'] = "Gaurav Sharma"
    n['url'] = "#"
    # agar image original wali hai to apni bana de
    if 'aajtak' in n.get('image','').lower() or 'abp' in n.get('image','').lower() or 'http' in n.get('image',''):
        new_path = f"{IMG_DIR}/{n['id']}.jpg"
        create_big_image(n['title'], new_path, n.get('category','National'))
        n['image'] = new_path

with open(JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(all_news, f, ensure_ascii=False, indent=2)

print(f"FINAL BANK: {len(all_news)} news")
