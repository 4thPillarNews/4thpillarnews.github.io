# FINAL - Tested
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
        url="https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf"
        open(FONT_PATH,'wb').write(requests.get(url,timeout=30).content)
    except: pass

MAP={"के अनुसार":"के मुताबिक","आधारित है":"पर निर्भर है","व्यवस्था है":"प्रणाली है","बताया गया है":"जानकारी दी गई है","इस दौरान":"इस बीच"}

def rewrite(t):
    if not t: return ""
    if "Copyright" in t or "Living Media" in t or "Syndications" in t: return ""
    for k,v in MAP.items(): t=t.replace(k,v)
    return re.sub(r'\s+',' ',t).strip()

def is_hindi(t):
    h=len(re.findall(r'[\u0900-\u097F]',t)); e=len(re.findall(r'[A-Za-z]',t))
    return h>6 and e<h

def make_img(title,fid):
    img=Image.new('RGB',(600,400),(11,32,71)); d=ImageDraw.Draw(img)
    try:
        f=ImageFont.truetype(FONT_PATH,22); sf=ImageFont.truetype(FONT_PATH,15)
    except: f=ImageFont.load_default(); sf=f
    d.text((20,170),title[:70],font=f,fill=(242,193,78))
    d.text((20,360),"The 4th Pillar News",font=sf,fill=(255,255,255))
    p=f"{IMG_DIR}/{fid}.jpg"; img.save(p); return p

def get_art(link):
    try:
        s=BeautifulSoup(requests.get(link,headers=HEADERS,timeout=15).text,'html.parser')
        title=rewrite(s.find('h1').get_text()) if s.find('h1') else ""
        if not is_hindi(title) or len(title)<15: return None
        paras=[]
        for p in s.find_all('p'):
            txt=rewrite(p.get_text())
            if 50 < len(txt) < 350: paras.append(txt)
        if not paras: return None
        fid=hashlib.md5(link.encode()).hexdigest()[:10]
        return {"id":fid,"title":title,"description":paras[0][:120]+"...","content":f"<p>{paras[0]}</p>","image":make_img(title,fid),"url":"#","publishedAt":time.strftime("%d %B %Y"),"author":"Gaurav Sharma","category":"National"}
    except: return None

data=json.load(open(JSON_PATH,encoding='utf-8')) if os.path.exists(JSON_PATH) else []
seen={x['id'] for x in data}
for cat in ["https://www.aajtak.in/india","https://www.aajtak.in/uttar-pradesh"]:
    try:
        html=BeautifulSoup(requests.get(cat,headers=HEADERS,timeout=15).text,'html.parser')
        for a in html.find_all('a',href=True)[:20]:
            link=urljoin(cat,a['href'])
            if 'aajtak.in' not in link: continue
            art=get_art(link)
            if art and art['id'] not in seen:
                data.insert(0,art); seen.add(art['id'])
    except: pass

json.dump(data[:40],open(JSON_PATH,'w',encoding='utf-8'),ensure_ascii=False,indent=2)
print("FINAL DONE")
