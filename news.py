import requests, os, re, json, hashlib, time
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw
from urllib.parse import urljoin

JSON_PATH="news.json"
IMG_DIR="images"
os.makedirs(IMG_DIR, exist_ok=True)
HEADERS={"User-Agent":"Mozilla/5.0"}

CATEGORY_LINKS={
 "National":["https://www.aajtak.in/india"],
 "International":["https://www.aajtak.in/world"],
 "Technology":["https://www.aajtak.in/technology"],
 "Sports":["https://www.aajtak.in/sports"],
 "Business":["https://www.aajtak.in/business"]
}

def clean_all(t):
    if not t: return ""
    t=t.replace("Stay updated with us for all breaking news from India News and more news in Hindi.","")
    t=t.replace("विज्ञापन","").replace("ये भी पढ़ें","")
    t=re.sub(r'amarujala\.com|Read the latest|Get live|BBC|editorial|The 4th Pillar|By Gaurav|Sach Ka','',t,flags=re.I)
    t=re.sub(r'\s+',' ',t).strip()
    return t

def get_links(url):
    try:
        r=requests.get(url,headers=HEADERS,timeout=15)
        s=BeautifulSoup(r.text,'html.parser')
        out=[]
        for a in s.find_all('a',href=True):
            h=urljoin(url,a['href'])
            if ('aajtak.in' in h or 'abplive.com' in h) and len(h)>45:
                out.append(h)
        return list(set(out))[:5]
    except: return []

def get_data(url):
    try:
        r=requests.get(url,headers=HEADERS,timeout=15)
        s=BeautifulSoup(r.text,'html.parser')
        title=s.find('h1').get_text().strip() if s.find('h1') else ""
        title=clean_all(title)
        if len(title)<15: return None,None
        paras=[p.get_text().strip() for p in s.find_all('p') if len(p.get_text().strip())>60]
        content=""
        for p in paras[:4]:
            p=clean_all(p)
            if len(p)>30: content+=f"<p>{p}</p>\n"
        if len(re.findall(r'[A-Za-z]',content))>len(re.findall(r'[\u0900-\u097F]',content)): return None,None
        if len(content)<200: return None,None
        return title,content
    except: return None,None

def make_img(title,path,cat):
    img=Image.new('RGB',(800,450),(20,30,100))
    d=ImageDraw.Draw(img)
    d.text((30,150),title[:90],fill=(255,255,255))
    d.text((30,400),cat,fill=(255,215,0))
    img.save(path,"JPEG")
    return True

# OLD DATA LOAD + CLEAN
all_news=[]
if os.path.exists(JSON_PATH):
    try:
        old=json.load(open(JSON_PATH,'r',encoding='utf-8'))
        for item in old:
            item['content']=clean_all(item.get('content',''))
            item['description']=clean_all(item.get('description',''))
            all_news.append(item)
    except: all_news=[]

seen=set([x['id'] for x in all_news])

# NEW DATA
for cat,urls in CATEGORY_LINKS.items():
    for u in urls:
        for link in get_links(u):
            fid=hashlib.md5(link.encode()).hexdigest()[:10]
            if fid in seen: continue
            t,c=get_data(link)
            if not t: continue
            p=f"{IMG_DIR}/{fid}.jpg"
            make_img(t,p,cat)
            desc=re.sub(r'<[^>]+>','',c).split()[:25]
            all_news.insert(0,{"id":fid,"title":t,"description":" ".join(desc)+"...","content":c,"image":p,"url":"#","publishedAt":time.strftime("%d %B %Y"),"author":"Gaurav Sharma","category":cat})
            seen.add(fid)
            if len(all_news)>=40: break

json.dump(all_news[:40],open(JSON_PATH,'w',encoding='utf-8'),ensure_ascii=False,indent=2)
print("DONE",len(all_news))
