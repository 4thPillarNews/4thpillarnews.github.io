import os
import requests
import json
import time
import random
from datetime import datetime

API_KEY = os.environ.get("GNEWS_API_KEY")
if not API_KEY:
    raise Exception("GNEWS_API_KEY secret nahi mila!")

CATEGORIES = {
    "National": "भारत राष्ट्रीय समाचार",
    "International": "अंतरराष्ट्रीय समाचार",
    "Sports": "खेल क्रिकेट",
    "Business": "बिजनेस शेयर बाजार",
    "Entertainment": "बॉलीवुड मनोरंजन"
}

REWRITE_INTROS = [
    "नोएडा से गौरव शर्मा की रिपोर्ट के अनुसार,",
    "फोर्थ पिलर न्यूज़ को प्राप्त जानकारी के मुताबिक,",
    "सूत्रों के हवाले से बड़ी खबर सामने आई है,",
    "दिल्ली-एनसीआर के लिए यह खबर बेहद महत्वपूर्ण है,"
]

def rewrite_news(original_title, original_desc, category, source_name):
    if not original_desc:
        original_desc = original_title
        
    intro = random.choice(REWRITE_INTROS)
    new_title = original_title.strip()
    
    para1 = f"{intro} {original_desc}"
    para2 = f"{source_name} की रिपोर्ट के अनुसार, इस घटना का सीधा असर आम जनता पर देखने को मिल सकता है। विशेषज्ञों का मानना है कि आने वाले दिनों में इससे जुड़ी और भी बड़ी जानकारी सामने आ सकती है।"
    para3 = f"फोर्थ पिलर न्यूज़ के लिए गौरव शर्मा की इस विशेष रिपोर्ट में हम आपको बता रहे हैं कि इस {category} खबर के पीछे की असली वजह क्या है और इसका नोएडा, दिल्ली सहित पूरे देश पर क्या प्रभाव पड़ेगा। हमारी टीम लगातार इस खबर पर नजर बनाए हुए है।"
    
    full_content = f"{para1}\n\n{para2}\n\n{para3}\n\nस्रोत: {source_name}"
    return new_title, full_content

all_news = {}
print("खबरें लाना शुरू...")

for cat_name, query in CATEGORIES.items():
    try:
        url = f"https://gnews.io/api/v4/search?q={query}&lang=hi&country=in&max=10&apikey={API_KEY}"
        res = requests.get(url, timeout=20).json()
        articles = res.get("articles", [])
        cat_news = []
        for art in articles:
            title, content = rewrite_news(art.get("title",""), art.get("description",""), cat_name, art.get("source",{}).get("name","राष्ट्रीय मीडिया"))
            cat_news.append({
                "title": title,
                "content": content,
                "image": art.get("image"),
                "publishedAt": art.get("publishedAt", datetime.now().isoformat()),
                "source": art.get("source",{}).get("name"),
                "url": art.get("url"),
                "category": cat_name
            })
        all_news[cat_name] = cat_news
        print(f"{cat_name} : {len(cat_news)} खबरें तैयार")
        time.sleep(2)
    except Exception as e:
        print(f"Error in {cat_name}: {e}")

os.makedirs("data", exist_ok=True)
with open("data/news.json", "w", encoding="utf-8") as f:
    json.dump(all_news, f, ensure_ascii=False, indent=2)

print("पूरी हिंदी में news.json तैयार!")
