import feedparser, json, requests, re, os
from datetime import datetime
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

# --- TERA NAAM ---
REPORTER_NAME = "Gaurav Sharma"

BAD_WORDS = ["BBC","बीबीसी","BCC","द लेंस","The Lens","TheLens","लेंस","Aaj Tak","आज तक","ABP","NDTV","Zee","Republic","Amar Ujala","अमर उजाला","Jagran","दैनिक जागरण","Hindustan","भास्कर","Times","PTI","ANI","BBC News"]
BAD_SENTENCES = ["बाहरी साइटों","सामग्री के लिए जिम्मेदार","लिंक देने की","हमारी नीति","एपिसोड","वोटर ऑफ जनलिज्म","© 2026","News हिन्दी को चुनें"]

os.makedirs("images", exist_ok=True)

def full_news(url, idx):
    try:
        r = requests.get(url, timeout=20, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(r.text, 'lxml')
        img_path = f"images/news_{idx}.jpg"
        final_img_url = img_path
        try:
            best_img = None; max_size = 0
            for im in soup.find_all("img"):
                src = im.get("src","")
                if src.startswith("http") and len(src)>40 and "logo" not in src.lower():
                    w = int(im.get("width",0) or 0)
                    if w > max_size: max_size = w; best_img = src
            if not best_img:
                og = soup.find("meta", property="og:image")
                if og: best_img = og.get("content","")
            if best_img:
                img_data = requests.get(best_img, timeout=20).content
                im = Image.open(BytesIO(img_data))
                w,h = im.size
                if w < 300 or h < 200: raise Exception("small")
                cropped = im.crop((0,0,w,int(h*0.82)))
                cropped.save(img_path, quality=90)
            else: final_img_url = f"https://picsum.photos/seed/news{idx}/800/450"
        except: final_img_url = f"https://picsum.photos/seed/news{idx}/800/450"

        paras=[]
        for p in soup.find_all("p"):
            t=p.get_text().strip()
            if len(t)<70: continue
            if any(bad in t for bad in BAD_SENTENCES): continue
            for bad in BAD_WORDS:
                t=re.sub(re.escape(bad),"",t,flags=re.IGNORECASE)
            t=re.sub(r'\s{2,}',' ',t).strip()
            if len(t)>50: paras.append(t)
        
        text=" ".join(paras)
        words=text.split()
        mid=len(words)//2
        return final_img_url, " ".join(words[:mid]), " ".join(words[mid:])
    except:
        return f"https://picsum.photos/seed/news{idx}/800/450", "", ""

# --- MAIN LOGIC TERI REQUIREMENT WALA ---
old_news=[]
if os.path.exists("news.json"):
    try:
        with open("news.json","r",encoding="utf-8") as f:
            old_news=json.load(f)
    except: old_news=[]

old_titles={n['title'].strip().lower() for n in old_news}
today=datetime.now().strftime("%d %b %Y") # Ab se 13 Sep 2026 ayega
feed=feedparser.parse("https://feeds.bbci.co.uk/hindi/rss.xml")
new_items=[]

for entry in feed.entries[:10]:
    # puri news lo
    img,p1,p2=full_news(entry.link, len(old_news)+len(new_items))
    if len(p1)<100: continue
    title=entry.title
    for bad in BAD_WORDS:
        title=re.sub(re.escape(bad),"",title,flags=re.IGNORECASE)
    title=re.sub(r'\s{2,}',' ',title).strip().replace("- -","-").strip()
    if title.lower() in old_titles: continue

    new_items.append({
        "title":title, "para1":p1, "para2":p2, "para3":"", "para4":"",
        "image":img, "category":"Latest", "date":today,
        "reporter":REPORTER_NAME, "source":"4th Pillar News"
    })

# Nayi sabse upar, purani next page pe shift
final_news = new_items + old_news
for idx,n in enumerate(final_news):
    n['id']=idx
    n['link']=f"article.html?id={idx}"

# 500 ke baad last wali auto delete
final_news=final_news[:500]

with open('news.json','w',encoding='utf-8') as f:
    json.dump(final_news,f,ensure_ascii=False,indent=2)
print(f"Added {len(new_items)} new, Total {len(final_news)}")
