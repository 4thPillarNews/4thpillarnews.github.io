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

NEWS_POOL = [
    ("Ghaziabad","गाजियाबाद में इंदिरापुरम रोड पर नया फ्लाईओवर बनेगा","https://images.unsplash.com/photo-1570129477492-45c003edd2be"),
    ("Ghaziabad","गाजियाबाद नगर निगम ने स्वच्छता अभियान शुरू किया","https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b"),
    ("National","संसद में आज नया विधेयक पारित हुआ","https://images.unsplash.com/photo-1524492412937-b28074a5d7da"),
    ("National","दिल्ली मेट्रो के समय में कल से बदलाव होगा","https://images.unsplash.com/photo-1587474260584-136574528ed5"),
    ("Sports","टीम इंडिया ने टी20 मैच में शानदार जीत दर्ज की","https://images.unsplash.com/photo-1461896836934-ffe607ba8211"),
    ("Business","सोने के दाम में 1000 रुपये की गिरावट","https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3"),
    ("Entertainment","बॉलीवुड की नई फिल्म ने 100 करोड़ कमाए","https://images.unsplash.com/photo-1489599849927-2ee91cede3ba"),
    ("International","संयुक्त राष्ट्र में भारत ने अपना पक्ष रखा","https://images.unsplash.com/photo-1521295121783-8a321d551ad2"),
]

cat, title, img = random.choice(NEWS_POOL)
data.append({
    "id": str(int(datetime.now().timestamp())),
    "title": title,
    "category": cat,
    "image": img,
    "date": datetime.now().strftime("%d %b %Y %I:%M %p"),
    "author": "Gaurav Sharma"
})

if len(data) > 500:
    data = data[-500:]

with open("news.json","w",encoding="utf-8") as f:
    json.dump(data,f,ensure_ascii=False,indent=2)
