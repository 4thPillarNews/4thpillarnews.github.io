import json, os, random
from datetime import datetime

if os.path.exists("news.json"):
    try:
        with open("news.json","r",encoding="utf-8") as f:
            data=json.load(f)
    except:
        data=[]
else:
    data=[]

cat_list = ["Ghaziabad","National","Sports","Business","Entertainment","International"]
img_list = [
    "https://images.unsplash.com/photo-1504711434969-e33886168f5c",
    "https://images.unsplash.com/photo-1524492412937-b28074a5d7da",
    "https://images.unsplash.com/photo-1461896836934-ffe607ba8211",
    "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3"
]

title_list = [
    "Ghaziabad me aaj subah bhari barish",
    "Sansad me naya bill pass hua",
    "Team India ki shandar jeet",
    "Sone ke daam me giravat",
    "Nayi film ka trailer release",
    "America me bhari toofan"
]

t = random.choice(title_list) + " " + datetime.now().strftime("%H:%M")
c = random.choice(cat_list)

data.append({
    "id": str(int(datetime.now().timestamp())),
    "title": t,
    "category": c,
    "image": random.choice(img_list),
    "date": datetime.now().strftime("%d %b %Y %I:%M %p"),
    "author": "Gaurav Sharma"
})

if len(data) > 500:
    data = data[-500:]

with open("news.json","w",encoding="utf-8") as f:
    json.dump(data,f,ensure_ascii=False,indent=2)
