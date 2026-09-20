import os, json, requests, re, random, shutil
from PIL import Image
from io import BytesIO
from datetime import datetime
import xml.etree.ElementTree as ET

# AAJ PURANI DELETE
if os.path.exists("images"):
    shutil.rmtree("images")
os.makedirs("images", exist_ok=True)

def get_smart_keyword(title, category):
    t = title.lower()

    # 1. SPORTS - Detail me
    if category == "Sports":
        if any(x in t for x in ["cricket", "ipl", "jaiswal", "kohli", "rohit", "bcci", "test", "odi", "t20"]):
            return "cricket,stadium,players"
        if any(x in t for x in ["football", "fifa", "messi", "ronaldo"]):
            return "football,stadium"
        if "tennis" in t: return "tennis,court"
        if "hockey" in t: return "hockey,stadium"
        if "kabaddi" in t: return "kabaddi,sports"
        return "sports,stadium"

    # 2. RAILWAY / TRAIN / TRANSPORT
    if any(x in t for x in ["railway", "rail", "train", "metro", "vande bharat"]):
        return "indian,railway,train"

    # 3. UP / STATE WISE SKETCH
    if category == "UP" or "uttar pradesh" in t:
        if "lucknow" in t: return "lucknow,uttar pradesh"
        if "kanpur" in t: return "kanpur,city"
        if "ayodhya" in t: return "ayodhya,temple"
        if "varanasi" in t: return "varanasi,ghat"
        return "uttar pradesh,india,map"

    # 4. NATIONAL / STATE
    if "delhi" in t: return "delhi,india gate"
    if "mumbai" in t or "maharashtra" in t: return "mumbai,city"
    if "bihar" in t: return "bihar,india"
    if "punjab" in t: return "punjab,india"
    if "kashmir" in t: return "kashmir,mountains"

    # 5. INTERNATIONAL - Country based
    if category == "International" or category == "World":
        if "america" in t or "usa" in t: return "america,usa,flag"
        if "pakistan" in t: return "pakistan,flag"
        if "china" in t: return "china,great wall"
        if "russia" in t: return "russia,moscow"
        if "uk" in t or "britain" in t or "england" in t: return "london,uk"
        if "dubai" in t or "uae" in t: return "dubai,uae"
        if "israel" in t: return "israel,flag"
        return "world,map,international"

    # 6. OTHER CATEGORIES
    if category == "Technology":
        if "ai" in t: return "artificial intelligence,technology"
        if "phone" in t or "mobile" in t: return "smartphone,technology"
        if "isro" in t or "space" in t: return "isro,space,rocket"
        return "technology,computer"
    if category == "Business":
        return "business,stock market,finance"
    if category == "Entertainment":
        return "bollywood,movie,theatre"
    if category == "Education":
        return "education,school,students"

    return f"{category},india"

def get_image(keyword):
    try:
        # loremflickr royalty-free + relevant
        url = f"https://loremflickr.com/800/450/{keyword}?lock={random.randint(1,10000)}"
        data = requests.get(url, timeout=20).content
        img = Image.open(BytesIO(data)).convert("RGB")
        return img
    except:
        return Image.new('RGB',(800,450),(30,30,30))

def fetch_news():
    CATS = {"National": "National News India","International": "International News","Sports": "Sports News","Entertainment": "Entertainment Bollywood","Business": "Business News","Education": "Education News","World": "World News","UP": "Uttar Pradesh News","Technology": "Technology News"}
    all_items=[]
    for cat, q in CATS.items():
        url = f"https://news.google.com/rss/search?q={q.replace(' ','+')}&hl=hi&gl=IN&ceid=IN:hi"
        try:
            r = requests.get(url, timeout=15)
            root = ET.fromstring(r.content)
            for i, it in enumerate(root.findall(".//item")[:4]):
                title = re.sub('<[^>]+>', '', it.find("title").text or "")
                desc = re.sub('<[^>]+>', '', it.find("description").text or title)
                title = title.split(" - ")[0]
                if len(title) < 15: continue
                all_items.append({"title":title.strip(),"desc":desc.strip(),"cat":cat,"idx":i})
        except: pass
    return all_items

news_raw = fetch_news()
all_news=[]
for n in news_raw:
    keyword = get_smart_keyword(n["title"], n["cat"])
    print(f"{n['cat']} | {n['title'][:30]} -> KEYWORD: {keyword}")
    pil_img = get_image(keyword)
    pil_img = pil_img.resize((800,450))
    fname = f"{n['cat'].lower()}_{n['idx']}_{random.randint(100,999)}.jpg"
    path = f"images/{fname}"
    pil
