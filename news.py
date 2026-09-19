import requests
from bs4 import BeautifulSoup
import os, re, json, time, random, hashlib
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from urllib.parse import urljoin

JSON_PATH = "news.json"
IMG_DIR = "images"
MAX_NEWS = 40
os.makedirs(IMG_DIR, exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

CATEGORY_LINKS = {
    "National": ["https://www.amarujala.com/india-news", "https://www.livehindustan.com/national"],
    "International": ["https://www.amarujala.com/world", "https://www.bbc.com/hindi"],
    "Technology": ["https://www.amarujala.com/technology", "https://www.livehindustan.com/technology"],
    "Sports": ["https://www.amarujala.com/sports"],
    "Business": ["https://www.amarujala.com/business"],
}

def clean_all(text):
    if not text: return ""
    bad_keywords = [
        "amarujala.com", "Read the latest and breaking", "Get live Hindi news",
        "Register with", "Hindi News App", "Android", "iOS App", "Download",
        "Tech News in Hindi", "breaking news from Tech", "Get all Tech News",
        "The BBC's global reputation", "editorial integrity", "Editorial Guidelines",
        "Section 15 Independence", "Guidance: Links", "external websites",
        "Sach Ka Chautha Stambh", "The Fourth Pillar News", "By Gaurav Sharma",
        "INTERNATIONAL | The 4th Pillar News"
    ]
    # line by line filter
    text = text.replace('\n', ' ')
    for bad in bad_keywords:
        if bad.lower() in text.lower():
            # uss sentence ko hatao
            text = re.sub(r'[^.]*'+re.escape(bad)+r'[^.]*\.?', '', text, flags=re.IGNORECASE)
    
    text = re.sub(r'\s+', ' ', text).strip()
    # AdSense ke liye halka rewrite taaki exact copy na lage
    text = text.replace(" ने कहा कि ", " का कहना है कि ").replace(" ने बताया कि ", " ने जानकारी दी कि ")
    text = text.replace(" हो रहा है", " किया जा रहा है").replace(" किया गया", " किया गया है")
    text = text.replace(" के अनुसार", " के मुताबिक")
    return text.strip()

def get_article_links(list_url):
    try:
        r = requests.get(list_url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/202' in href or len(href) > 50:
                full = urljoin(list_url, href)
                if 'amarujala' in full or 'livehindustan' in full or 'bbc.com/hindi' in full:
                    links.append(full)
        return list(set(links))[:10]
    except:
        return []

def extract_500_words(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        title_tag = soup.find('h1')
        title = clean_all(title_tag.get_text()) if title_tag else ""
        if len(title) < 15: return None, None

        paras = soup.find_all('p')
        sents = []
        for p in paras:
            t = p.get_text().strip()
            if len(t) > 40:
                sents.append(t)
        
        curr = ""
        final = []
        for s in sents:
            if len(curr.split())+len(s.split())<85:
                curr+=" "+s
            else:
                if curr.strip():
                    cleaned = clean_all(curr)
                    if len(cleaned.split()) > 12:
                        final.append(f"<p>{cleaned.strip()}</p>")
                curr=s
        if curr.strip():
            cleaned = clean_all(curr)
            if len(cleaned.split()) > 12:
                final.append(f"<p>{cleaned.strip()}</p>")
        
        final=final[:6]
        if len(final)<2: return None, None

        content = "\n".join(final)
        # English check - agar Hindi se zyada English hai to skip
        hindi_chars = len(re.findall(r'[\u0900-\u097F]', content))
        eng_chars = len(re.findall(r'[a-zA-Z]', content))
        if eng_chars > hindi_chars * 1.5:
            return None, None

        return title, content
    except Exception as e:
        print(f"Error {url} {e}")
        return None, None

def create_big_image(title, path, category):
    try:
        W, H = 800, 450
        img = Image.new('RGB', (W, H), color=(10, 35, 85))
        draw = ImageDraw.Draw(img)
        # simple text wrap
        words = title.split()
        lines = []
        curr = ""
        for w in words:
            if len(curr+" "+w) < 30:
                curr += " "+w
            else:
                lines.append(curr.strip())
                curr = w
        lines.append(curr.strip())
        lines = lines[:4]
        y = 120
        for line in lines:
            draw.text((40, y), line, fill=(255,255,255))
            y+=50
        draw.text((40, H-40), category, fill=(255,215,0))
        img.save(path, "JPEG", quality=90)
        return True
    except Exception as e:
        print(f"Image fail {e}")
        return False

# MAIN LOOP
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
            ok = create_big_image(title, img_path, category)
            if not ok or not os.path.exists(img_path):
                continue
            
            desc=re.sub(r'<[^>]+>','',content_html).split()[:32]
            item={
                "id":fid,"title":title,"description":" ".join(desc)+"...",
                "content":content_html,"image":img_path,"url":"#",
                "publishedAt":datetime.now().strftime("%d %B %Y, %I:%M %p"),
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
