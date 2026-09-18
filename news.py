from PIL import Image
import requests
from io import BytesIO

# Copyright-free image lana - Pexels/Unsplash se
def get_free_image(title):
    # title se keyword nikal ke copyright free image
    keyword = title.split()[0:2] # pehle 2 shabd
    keyword = "+".join(keyword)
    # Unsplash source - no API key needed, copyright free
    # Har baar same topic ki free image dega
    return f"https://source.unsplash.com/800x450/?{keyword},india,cricket,news"

def clean_image(image_url):
    try:
        r = requests.get(image_url, timeout=10)
        img = Image.open(BytesIO(r.content))
        w, h = img.size

        # Agar image pe logo hai (aksar top-right me hota hai - Hindustan, ABP etc)
        # to 12% top se aur right se crop kar de
        # aur phir wapas save kar

        # Check karna hai kya image me watermark area me zyada white/red logo hai?
        # Simple trick: top-right 20% ko crop karke hata do
        if w > 400:
            # logo mostly top-right me hota hai, to usko crop
            left = 0
            upper = int(h * 0.08) # upar se 8% hatao
            right = int(w * 0.92) # right se 8% hatao
            lower = h
            img = img.crop((left, upper, right, lower))

        return img
    except:
        return None

# Teri news fetch wali loop me ye use kar:
# OLD: n["image"] = article_img
# NEW:

if "hindustan" in article_img.lower() or "abp" in article_img.lower() or "jagran" in article_img.lower() or "bbc" in article_img.lower():
    # dusri site ka logo hai to direct free image le lo
    n["image"] = get_free_image(n["title"])
else:
    # apni image hai to crop karke logo area saaf kar do
    cleaned = clean_image(article_img)
    if cleaned:
        # apne server pe save karna hai to /tmp me
        n["image"] = article_img # ya cleaned ko upload karke uska link
    else:
        n["image"] = get_free_image(n["title"])
