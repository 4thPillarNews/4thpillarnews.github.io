import requests, os, re, json, hashlib, time, random
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
from urllib.parse import urljoin

JSON_PATH="news.json"
IMG_DIR="images"
FONT_PATH="NotoSansDevanagari.ttf"
os.makedirs(IMG_DIR, exist_ok=True)
HEADERS={"User-Agent":"Mozilla/5.0"}

# Font download ek baar
if not os.path.exists(FONT_PATH):
    try:
        u="https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf"
        open(FONT_PATH,'wb').write(requests.get(u,timeout=30).content)
    except: pass

# Category se icon ka pata chalega
CAT_ICONS={
    "National":"🇮🇳","Politics":"🏛️","Crime":"🚨","UP":"📍","Sports":"🏏","Business":"💼"
}

def rewrite(t):
    if not t: return ""
    if "Copyright" in t or "Living Media" in t: return ""
    return re.sub(r'\s+',' ',t).strip()

def is_hindi(t):
    return len(re.findall(r'[\u0900-\u097F]',t)) > 5

def make_generic_image(title, fid, category="National"):
    # Royalty free - khud se bana rahe hain, koi download nahi
    W,H=800,450
    # Dark blue theme tumhari site jaisa
    bg_colors=[(11,32,71),(25,25,112),(20,40,80)]
    bg=random.choice(bg_colors)
    img=Image.new('RGB',(W,H),bg)
    d=ImageDraw.Draw(img)

    # Halka pattern
    for i in range(0,W,40):
        d.line([(i,0),(0,i)],fill=(255,255,255,8),width=1)

    # Icon upar
    icon=CAT_ICONS.get(category,"📰")
    try:
        font_big=ImageFont.truetype(FONT_PATH,48)
        font_title=ImageFont.truetype(FONT_PATH,32)
        font_small=ImageFont.truetype(FONT_PATH,18)
    except:
        font_big=ImageFont.load_default()
        font_title=ImageFont.load_default()
        font_small=ImageFont.load_default()

    # Title ko 2 line me todna
    words=title.split()
    line1,line2="",""
    for w in words:
        if len(line1)<28: line1+=w+" "
        elif len(line2)<35: line2+=w+" "

    d.text((30,30),f"{icon} {category}",font=font_small,fill=(242,193,78))
    d.text((30,80),line1.strip(),font=font_title,fill=(255,255,255))
    d.text((30,130),line2.strip(),font=font_title,fill=(255,255,255))
    d.rectangle([(30,200),(760,205)],fill=(242,193,78))
    d.text((30,400),"THE 4TH PILLAR",font=font_small,fill=(200,200,200))

    path=f"{IMG_DIR}/{fid}.jpg"
    img.save(path,"JPEG",quality=90)
    return path

def get_article(link):
    try:
        s=BeautifulSoup(requests.get(link,headers=HEADERS,timeout=20).text,'html.parser')
        h1=s.find('h1')
        if not h1: return None
        title=rewrite(h1.get_text())
        if not is_hindi(title) or len(title)<12: return None
        cat="National"
        if "uttar-pradesh" in link: cat="UP"
        for p in s.find_all('p'):
            txt=rewrite(p.get_text())
            if 50 < len(txt) < 350:
                fid=hashlib.md5(link.encode()).hexdigest()[:10]
                img_path=make_generic_image(title,fid,cat)
                return {"id":fid,"title":title,"description":txt[:120]+"...","content":f"<p>{txt}</p>","image":img_path,"url":"#","publishedAt":time.strftime("%d %B %Y"),"author":"Gaurav Sharma","category":cat}
        return None
    except:
        return None

# Load old
try:
    old=json.load(open(JSON_PATH,encoding='utf-8'))
    if not isinstance(old,list): old=[]
except: old=[]
seen=set([x['id'] for x in old])
new=[]

for cat_url in ["https://www.aajtak.in/india","https://www.aajtak.in/uttar-pradesh"]:
    try:
        html=BeautifulSoup(requests.get(cat_url,headers=HEADERS,timeout=20).text,'html.parser')
        for a in html.find_all('a',href=True)[:40]:
            link=urljoin(cat_url,a['href'])
            if "aajtak.in" not in link or any(x in link for x in ["/video","/photo"]): continue
            art=get_article(link)
            if art and art['id'] not in seen:
                new.append(art); seen.add(art['id'])
            if len(new)>=12: break
    except: continue

final=new+old
# .gitkeep taaki folder push ho
if len([f for f in os.listdir(IMG_DIR) if f.endswith('.jpg')])==0 and len(final)==0:
    open(os.path.join(IMG_DIR,".gitkeep"),'w').write("")

json.dump(final[:40],open(JSON_PATH,'w',encoding='utf-8'),ensure_ascii=False,indent=2)
print(f"Created {len(new)} new generic images")
