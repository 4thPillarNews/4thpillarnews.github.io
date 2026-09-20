import os, json, requests, re, random, shutil
from PIL import Image
from io import BytesIO
from datetime import datetime
import xml.etree.ElementTree as ET

if os.path.exists("images"):
    shutil.rmtree("images")
os.makedirs("images", exist_ok=True)

def get_keyword(title, cat):
    t = title.lower()
    if cat == "Sports":
        if "cricket" in t or "ipl" in t or "jaiswal" in t: return "cricket,stadium"
        if "football" in t: return "football"
        return "sports"
    if "railway" in t or "train" in t: return "indian,railway,train"
    if cat == "UP": return "uttar pradesh,india"
    if cat == "International": return "world,map"
    if cat == "Technology": return "technology"
    return cat

def get_image(keyword):
    try:
        url = f"https://loremflickr.com/800/450/{keyword}?lock={random.randint(1,9999)}"
        data = requests.get(url, timeout=20).content
        im = Image.open(BytesIO(data)).convert("RGB")
        return im
    except:
        return Image.new('RGB',(800,450),(30,30,30))

CATS = {"National":"National News India","International":"International News","Sports":"Sports News","Entertainment":"Entertainment Bollywood","Business":"Business News","Education":"Education News","World":"World News","UP":"Uttar Pradesh News","Technology":"Technology News"}

all_news=[]
for cat,q in CATS.items():
    url = f"https://news.google.com/rss/search?q={q.replace(' ','+')}&hl=hi&gl=IN&ceid=IN:hi"
    try:
        r = requests.get(url, timeout=15)
        root = ET.fromstring(r.content)
        for i,it in enumerate(root.findall(".//item")[:4]):
            title = re.sub('<[^>]+>', '', it.find("title").text or "").split(" - ")[0].strip()
            desc = re.sub('<[^>]+>', '', it.find("description").text or title).strip()
            if len(title) < 15: continue
            kw = get_keyword(title, cat)
            img = get_image(kw).resize((800,450))
            fname = f"{cat.lower()}_{i}_{random.randint(100,999)}.jpg"
            path = f"images/{fname}"
            img.save(path)
            all_news.append({"title":title,"description":desc,"desc":desc,"content":desc,"category":cat,"image":path,"img":path,"date":datetime.now().strftime("%d %B %Y"),"time":datetime.now().strftime("%d %B %Y"),"author":"Gaurav Sharma"})
    except:
        pass

with open("news.json","w",encoding="utf-8") as f:
    json.dump(all_news, f, ensure_ascii=False, indent=2)
