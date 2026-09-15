import requests, json, os, hashlib, re
from pathlib import Path
from datetime import datetime

API_KEY = os.getenv("GNEWS_API_KEY")
FILE = Path("news.json")

old_data=[]
if FILE.exists():
    try: old_data=json.loads(FILE.read_text(encoding='utf-8'))
    except: old_data=[]

def clean(t): return re.sub(r'\s+',' ',t.lower()) if t else ""
old_titles=[clean(n.get("title","")) for n in old_data]
old_urls=set([n.get("url") for n in old_data])

url=f"https://gnews.io/api/v4/top-headlines?category=general&lang=hi&country=in&max=20&apikey={API_KEY}"
try:
    arts=requests.get(url,timeout=30).json().get("articles",[])
    new=[]
    for a in arts:
        t=a.get("title","").strip()
        if not t or a.get("url") in old_urls: continue
        if clean(t) in old_titles: continue
        if len(t)<20: continue
        
        img=a.get("image") or "./logo.png"
        hid=hashlib.md5(a.get("url","").encode()).hexdigest()[:10]
        try:
            dt=datetime.fromisoformat(a.get("publishedAt").replace("Z","+00:00"))
            pub=dt.strftime("%d %B %Y, %I:%M %p")
        except: pub=a.get("publishedAt","")

        desc=a.get("description","")
        content=f"<p><b>{t}</b></p><p>{desc}</p><p>Is khabar se jude har update ke liye The 4th Pillar News padhte rahein.</p>"

        new.append({"id":hid,"title":t,"description":desc,"content":content,"image":img,"url":a.get("url"),"publishedAt":pub,"author":"The 4th Pillar News Team","category":"Desh / Ghaziabad","source":a.get("source",{}).get("name","")})
        old_titles.append(clean(t))
    
    final=new+old_data
    final=final[:100]
    FILE.write_text(json.dumps(final,indent=2,ensure_ascii=False),encoding='utf-8')
    print(f"Added {len(new)}")
except Exception as e:
    print(e); exit(1)
