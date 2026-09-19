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

CATEGORY_LINKS = {
    "NCR": ["https://www.amarujala.com/delhi-ncr", "https://www.livehindustan.com/ncr/new-delhi"],
    "National": ["https://www.abplive.com/news/india", "https://www.amarujala.com/india-news"],
    "International": ["https://www.bbc.com/hindi/international", "https://www.abplive.com/news/world"],
    "Sports": ["https://www.abplive.com/sports", "https://www.amarujala.com/sports"],
    "Entertainment": ["https://www.abplive.com/entertainment", "https://www.amarujala.com/entertainment"],
    "Business": ["https://www.abplive.com/business", "https://www.amarujala.com/business"],
    "Technology": ["https://www.abplive.com/technology", "https://www.amarujala.com/technology"],
    "Education": ["https://www.amarujala.com/education", "https://www.livehindustan.com/career"]
}

def clean_all(text):
    if not text: return ""
    text = re.sub(r'ABP Live|ABP News|BBC Hindi|Aaj Tak|Amar Ujala|Live Hindustan|Dainik Jagran', '', text, flags=re.I)
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
            if any(x in href for x in ['.com/', '/news/', '/india', '/world', '/sports', '/entertainment', '/business', '/technology', '/education', '/cricket', '/delhi']):
                if len(href)>50 and href not in links and 'video' not in href:
                    links.append(href)
            if len(links)>=10: break
        return links
    except: return []

def is_author_bio(t):
    low = t.lower()
    bad = ["we use cookies", "personalize content", "by clicking", "about the author", "author bio", "holds a degree", "is a graduate", "has done his", "is currently working", "has experience", "subscribe", "follow us", "advertisement", "download app", "like us on", "facebook", "twitter"]
    if any(b in low for b in bad):
        return True
    # Hindi bio check without quotes
    if "मैं यानी" in t or "हिस्सा हूं" in t or "हिस्सा हूँ" in t or "परास्नातक" in t or "माखनलाल" in t or "चतुर्वेदी" in t or "पकड़ मजबूत" in t or "जाना जाता" in t:
        return True
    if t.count("मैं") >= 3:
        return True
    return False

def extract_500_words(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, timeout=20, headers=headers)
        r.raise_for_status()
    except: return None, None
    soup = BeautifulSoup(r.text, 'html.parser')
    h1 = soup.find('h1')
    title = h1.get_text(strip=True) if h1 else (soup.title.get_text(strip=True) if soup.title else "")
    if len(title)<15: return None, None
    title = clean_title(title)

    paras_raw=[]
    for p in soup.find_all('p'):
        t=p.get_text(strip=True)
        if len(t)<60: continue
        if is_author_bio(t): continue
        paras_raw.append(t)

    if len(paras_raw)<4: return None, None
    paras_raw = paras_raw[:-1] if len(paras_raw)>5 else paras_raw
    
    full_text=" ".join(paras_raw)
    if len(full_text.split())<WORDS_MIN: return None, None

    sentences=re.split(r'(?<=[.!?।])\s+', full_text)
    final=[]
    curr=""
    for s in sentences:
        s=s.strip()
        if not s: continue
        if is_author_bio(s): continue
        if len(curr.split())+len(s.split())<85:
            curr+=" "+s
        else:
            if curr.strip(): final.append(f"<p>{clean_all(curr).strip()}</p>")
            curr=s
    if curr.strip(): final.append(f"<p>{clean_all(curr).strip()}</p>")
    
    final=final[:6]
    if len(final)<3: return None, None
    return title, "\n".join(final)

all_news=[]
if os.path.exists(JSON_PATH):
    try:
        with open(JSON_PATH,'r',encoding='utf-8') as f: all_news=json.load(f)
    except: all_news=[]
seen=set([n.get('id','') for n in all_news])

for category, list_urls in CATEGORY_LINKS.items():
    for list_url in list_urls:
        for link in get_article_links(list_url):
            fid=hashlib.md5(link.encode()).hexdigest()[:10]
            if fid in seen: continue
            title, content_html = extract_500_words(link)
            if not title or not content_html: continue
            img_path=f"{IMG_DIR}/{fid}.jpg"
            create_big_image(title, img_path, category)
            desc=re.sub(r'<[^>]+>','',content_html).split()[:32]
            item={
                "id":fid,"title":title,"description":" ".join(desc)+"...","content":content_html,
                "image":img_path,"url":"#","publishedAt":datetime.now().strftime("%d %B %Y, %I:%M %p"),
                "author":"Gaurav Sharma","category":category,"source":"The Fourth Pillar News"
            }
            all_news.insert(0,item)
            seen.add(fid)
            time.sleep(0.4)
            if len(all_news)>=MAX_NEWS: break
        if len(all_news)>=MAX_NEWS: break
    if len(all_news)>=MAX_NEWS: break

all_news=all_news[:MAX_NEWS]
with open(JSON_PATH,'w',encoding='utf-8') as f:
    json.dump(all_news,f,ensure_ascii=False,indent=2)
print(f"DONE {len(all_news)}")
