import requests, os, re, json, time, hashlib, random
from bs4 import BeautifulSoup
from datetime import datetime
from PIL import Image, ImageDraw
from urllib.parse import urljoin

JSON_PATH = "news.json"
IMG_DIR = "images"
MAX_NEWS = 40
os.makedirs(IMG_DIR, exist_ok=True)
HEADERS = {"User-Agent": "Mozilla/5.0"}

CATEGORY_LINKS = {
    "National": ["https://www.amarujala.com/india-news"],
    "International": ["https://www.amarujala.com/world"],
    "Technology": ["https://www.amarujala.com/technology"],
    "Sports": ["https://www.amarujala.com/sports"],
    "Business": ["https://www.amarujala.com/business"],
}

# Adsense ke liye rewrite dictionary
REWRITE_MAP = {
    "ने कहा कि": "का कहना है कि", "बताया कि": "जानकारी दी कि",
    "हो रहा है": "किया जा रहा है", "किया गया": "किया गया है",
    "के अनुसार": "के मुताबिक", "बड़ी खबर": "अहम खबर",
    "जानकारी के मुताबिक": "सूत्रों के अनुसार", "कहा गया": "बताया गया"
}

def clean_all(text):
    if not text: return ""
    # Kachra lines jo site pe footer me aati hain
    bad = ["amarujala.com", "Read the latest", "Get live Hindi news", "Register with", 
           "Hindi News App", "Download", "Android", "iOS", "Tech News", "BBC", 
           "editorial integrity", "Guidance", "Section 15", "Sach Ka", "4th Pillar News", "By Gaurav"]
    for b in bad:
        if b.lower() in text.lower():
            text = re.sub(r'[^.]*'+re.escape(b)+r'[^.]*', '', text, flags=re.IGNORECASE)
    
    text = re.sub(r'\s+', ' ', text).strip()
    # Adsense unique ke liye words change
    for k,v in REWRITE_MAP.items():
        text = text.replace(k, v)
    return text

def get_article_links(list_url):
    try:
        r = requests.get(list_url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        links=[]
        for a in soup.find_all('a', href=True):
            href=urljoin(list_url, a['href'])
            if 'amarujala.com' in href and len(href)>60:
                links.append(href)
        return list(set(links))[:8]
    except: return []

def extract_500_words(url):
    try:
        r=requests.get(url, headers=HEADERS, timeout=15)
        soup=BeautifulSoup(r.text,'html.parser')
        title=soup.find('h1').get_text().strip() if soup.find('h1') else ""
        title=clean_all(title)
        if len(title)<15: return None,None
        
        paras=[]
        for p in soup.find_all('p'):
            t=p.get_text().strip()
            if len(t)>50 and 'amarujala' not in t.lower() and 'read the' not in t.lower():
                paras.append(t)
        
        curr=""; final=[]
        for s in paras:
            if len((curr+" "+s).split())<85:
                curr+=" "+s
            else:
                if curr.strip():
                    c=clean_all(curr)
                    if len(c.split())>12: final.append(f"<p>{c}</p>")
                curr=s
        if curr.strip():
            c=clean_all(curr)
            if len(c.split())>12: final.append(f"<p>{c}</p>")
        
        final=final[:5] # 5 para max
        if len(final)<2: return None,None
        
        content="\n".join(final)
        # Full english check - skip
        if len(re.findall(r'[a-zA-Z]', content)) > len(re.findall(r'[\u0900-\u097F]', content)):
            return None,None
            
        return title, content
    except: return None,None

def create_big_image(title, path, category):
    try:
        img=Image.new('RGB', (800,450), (11,32,90))
        d=ImageDraw.Draw(img)
        # Title wrap
        words=title.split(); lines=[]; cur=""
        for w in words:
            if len(cur+" "+w)<28:
                cur+=" "+w
            else:
                lines.append(cur.strip()); cur=w
        lines.append(cur.strip())
        y=100
        for l in lines[:4]:
            d.text((35,y), l, fill=(255,255,255)); y+=55
        d.text((35,400), category.upper(), fill=(255,215,0))
        img.save(path, "JPEG", quality=88)
        return True
    except: return False

# MAIN
all_news=[]
if os.path.exists(JSON_PATH):
    try:
        with open(JSON_PATH,'r',encoding='utf-8') as f: all_news=json.load(f)
    except: all_news=[]
seen=set([n.get('id','') for n in all_news])

for cat, urls in CATEGORY_LINKS.items():
    for list_url in urls:
        for link in get_article_links(list_url):
            fid=hashlib.md5(link.encode()).hexdigest()[:10]
            if fid in seen: continue
            title, html = extract_500_words(link)
            if not title or not html: continue
            img_path=f"{IMG_DIR}/{fid}.jpg"
            if not create_big_image(title, img_path, cat): continue
            desc=re.sub(r'<[^>]+>','',html).split()[:30]
            all_news.insert(0,{
                "id":fid,"title":title,"description":" ".join(desc)+"...",
                "content":html,"image":img_path,"url":"#",
                "publishedAt":datetime.now().strftime("%d %B %Y, %I:%M %p"),
                "author":"Gaurav Sharma","category":cat,"source":"The Fourth Pillar News"
            })
            seen.add(fid); time.sleep(0.5)
            if len(all_news)>=MAX_NEWS: break
        if len(all_news)>=MAX_NEWS: break
    if len(all_news)>=MAX_NEWS: break

all_news=all_news[:MAX_NEWS]
with open(JSON_PATH,'w',encoding='utf-8') as f:
    json.dump(all_news,f,ensure_ascii=False,indent=2)
print(f"DONE {len(all_news)}")
