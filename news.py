import requests, os, re, json, hashlib, time
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
from urllib.parse import urljoin

JSON_PATH="news.json"
IMG_DIR="images"
FONT_PATH="NotoSansDevanagari.ttf"
os.makedirs(IMG_DIR, exist_ok=True)
HEADERS={"User-Agent":"Mozilla/5.0"}

if not os.path.exists(FONT_PATH):
    try:
        open(FONT_PATH,'wb').write(requests.get("https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf",timeout=30).content)
    except: pass

REPLACE={"के अनुसार":"के मुताबिक","आधारित है":"पर निर्भर है","बताया गया है":"जानकारी दी गई है"}

def rewrite(t):
    if not t or "Copyright" in t or "Living Media" in t: return ""
    for k,v in REPLACE.items(): t=t.replace(k,v)
    return re.sub(r'\s+',' ',t).strip()

def is_hindi(t):
    return len(re.findall(r'[\u0900-\u097F]',t)) > 8

def make_img(title,fid):
    img=Image.new('RGB',(600,400),(11,32,71))
    d=ImageDraw.Draw(img)
    try: f=ImageFont.truetype(FONT_PATH,22)
    except: f=ImageFont.load_default()
    d.text((20,160),title[:70],font=f,fill=(242,193,78))
    p=f"{IMG_DIR}/{fid}.jpg"; img.save(p); return p

def get_article(link):
    try:
        s=BeautifulSoup(requests.get(link,headers=HEADERS,timeout=20).text,'html.parser')
        title=rewrite(s.find('h1').get_text()) if s.find('h1') else ""
        if not is_hindi(title) or len(title)<15: return None
        txt=""
        for p in s.find_all('p'):
            t=rewrite(p.get_text())
            if 60 < len(t) < 400: txt=t; break
        if not txt: return None
        fid=hashlib.md5(link.encode()).hexdigest()[:10]
        return {"id":fid,"title":title,"description":txt[:120]+"...","content":f"<p>{txt}</p>","image":make_img(title,fid),"url":"#","publishedAt":time.strftime("%d %B %Y"),"author":"Gaurav Sharma","category":"National"}
    except: return None

try:
    old=json.load(open(JSON_PATH,encoding='utf-8'))
except:
    old=[]
seen=set([x['id'] for x in old])
new=[]

for cat in ["https://www.aajtak.in/india","https://www.aajtak.in/uttar-pradesh"]:
    try:
        html=BeautifulSoup(requests.get(cat,headers=HEADERS,timeout=20).text,'html.parser')
        for a in html.find_all('a',href=True)[:25]:
            link=urljoin(cat,a['href'])
            if "aajtak.in" not in link: continue
            art=get_article(link)
            if art and art['id'] not in seen:
                new.append(art); seen.add(art['id'])
    except: pass

final=new+old
json.dump(final[:40],open(JSON_PATH,'w',encoding='utf-8'),ensure_ascii=False,indent=2)
