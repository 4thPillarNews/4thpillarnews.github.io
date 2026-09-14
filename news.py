import json, os, random, hashlib
from datetime import datetime

# --- Category wise alag images taaki same photo na dikhe ---
CAT_IMAGES = {
    "Ghaziabad": [
        "https://images.unsplash.com/photo-1570129477492-45c003edd2be",
        "https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b",
        "https://images.unsplash.com/photo-1449824913935-59a10b8d2000"
    ],
    "National": [
        "https://images.unsplash.com/photo-1524492412937-b28074a5d7da",
        "https://images.unsplash.com/photo-1587474260584-136574528ed5",
        "https://images.unsplash.com/photo-1532375810709-75b1da00537c"
    ],
    "International": [
        "https://images.unsplash.com/photo-1521295121783-8a321d551ad2",
        "https://images.unsplash.com/photo-1504711434969-e33886168f5c",
        "https://images.unsplash.com/photo-1495020689067-958852a7765e"
    ],
    "Sports": [
        "https://images.unsplash.com/photo-1461896836934-ffe607ba8211",
        "https://images.unsplash.com/photo-1574629810360-214f3770bf2d",
        "https://images.unsplash.com/photo-1543351611-58f69d7c1781"
    ],
    "Entertainment": [
        "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba",
        "https://images.unsplash.com/photo-1517604931442-7e0c8ed2963d",
        "https://images.unsplash.com/photo-1478720568477-152d9b164e26"
    ],
    "Business": [
        "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3",
        "https://images.unsplash.com/photo-1559526324-4f8172775ed6",
        "https://images.unsplash.com/photo-1460925895917-afdab827c52f"
    ]
}

def get_image(category):
    return random.choice(CAT_IMAGES.get
