import os, requests, json, time, random
from datetime import datetime, timedelta, timezone

API_KEY = os.environ.get("GNEWS_API_KEY")
if not API_KEY:
    raise Exception("GNEWS_API_KEY nahi mila!")

CATEGORIES = {
    "National": "भारत राष्ट्रीय समाचार",
    "International": "अंतरराष्ट्रीय समाचार",
    "Sports": "खेल क्रिकेट",
    "Business": "बिजनेस शेयर बाजार",
    "Entertainment": "बॉलीवुड मनोरंजन"
}

INTROS = [
    "नोएडा से गौरव शर्मा की रिपोर्ट के अनुसार,",
    "फोर्थ पिलर न्यूज़ को प्राप्त जानकारी के मुताबिक,",
    "सूत्रों के हवाले से बड़ी खबर सामने आई है,",
    "दिल्ली-एनसीआर के लिए यह खबर बेहद महत्वपूर्ण है,",
]

def to_ist(utc_str):
    try:
        dt = datetime.fromisoformat(utc_str.replace("Z","+00:00"))
        ist = dt.astimezone(timezone(timedelta(hours=5, minutes=30)))
        return ist.strftime("%d %b %Y %I:%M %p IST")
    except:
        return datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime("%d %b %Y %I:%M %p IST")

def rewrite(title, desc, cat, source):
    if not desc: desc = title
    intro = random.choice(INTROS)
    p1 = f"{intro} {desc}"
    p2 = f"{source} की रिपोर्ट के अनुसार, इस घटना का सीधा असर आम जनता पर देखने को मिल सकता है। विशेषज्ञों का मानना है कि आने वाले समय में इससे जुड़ी और भी बड़ी जानकारी सामने आ सकती है।"
    p3 = f"फोर्थ पिलर न्यूज़ के लिए गौरव शर्मा की इस विशेष रिपोर्ट में हम आपको बता रहे हैं कि इस {cat} खबर के पीछे की असली वजह क्या है और इसका नोएडा, दिल्ली सहित पूरे देश पर क्या प्रभाव पड़ेगा। हमारी टीम लगातार इस खबर पर नजर बनाए हुए है।"
    full = f"{p1}\n\n{p2}\n\n{p3}"
    return title.strip(), full

seen = set()
dict_data = {}
list_data = []

print("Fetching started...")

for cat_name, query in CATEGORIES.items():
    try:
        url = f"https://gnews.io/api/v4/search?q={query}&lang=hi&country=in&max=10&apikey={API_KEY}"
        arts = requests.get(url, timeout=20).json().get("articles", [])
        cat_list = []
        for a in arts:
            raw_title = a.get("title","").strip()
            if not raw_title or raw_title in seen:
                continue
            seen.add(raw_title)

            title, content = rewrite(raw_title, a.get("description",""), cat_name, a.get("source",{}).get("name","राष्ट्रीय मीडिया"))
            
            item = {
                "id": len(list_data) + 1,
                "title": title,
                "content": content,
                "description": content, # detail page ke liye dono me same
                "image": a.get("image") or "https://images.unsplash.com/photo-1504711434969-e33886168f5c",
                "publishedAt": to_ist(a.get("publishedAt","")),
                "pubDate": to_ist(a.get("publishedAt","")),
                "source": a.get("source",{}).get("name","4th Pillar News"),
                "url": a.get("url"),
                "category": cat_name,
                "author": "Gaurav Sharma"
            }
            cat_list.append(item)
            list_data.append(item)
        dict_data[cat_name] = cat_list
        print(f"{cat_name}: {len(cat_list)} done")
        time.sleep(1)
    except Exception as e:
        print(f"Error {cat_name}: {e}")

# Dono jagah save taaki site pakka padh le
os.makedirs("data", exist_ok=True)
with open("data/news.json", "w", encoding="utf-8") as f:
    json.dump(dict_data, f, ensure_ascii=False, indent=2)
with open("news.json", "w", encoding="utf-8") as f:
    json.dump(list_data, f, ensure_ascii=False, indent=2)
with open("data/news_list.json", "w", encoding="utf-8") as f:
    json.dump(list_data, f, ensure_ascii=False, indent=2)

print(f"TOTAL {len(list_data)} news saved with IST time")
