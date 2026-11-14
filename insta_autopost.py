import json, os, sys, time
from datetime import datetime
from zoneinfo import ZoneInfo
import requests

API = "https://graph.facebook.com/v21.0"
USER_ID = os.environ.get("IG_USER_ID")
TOKEN = os.environ.get("IG_ACCESS_TOKEN")
TZ = ZoneInfo("Asia/Dhaka")

def create_container(image_url, caption):
    r = requests.post(f"{API}/{USER_ID}/media",
        data={"image_url": image_url, "caption": caption, "access_token": TOKEN}, timeout=30)
    r.raise_for_status()
    return r.json()["id"]

def publish(cid):
    r = requests.post(f"{API}/{USER_ID}/media_publish",
        data={"creation_id": cid, "access_token": TOKEN}, timeout=30)
    r.raise_for_status()
    return r.json()["id"]

def main():
    if not USER_ID or not TOKEN:
        sys.exit("IG_USER_ID ও IG_ACCESS_TOKEN সেট করুন")
    with open("posts.json", encoding="utf-8") as f:
        posts = json.load(f)
    now = datetime.now(TZ).replace(tzinfo=None)
    changed = False
    for p in posts:
        if p.get("posted"):
            continue
        when = datetime.strptime(p["scheduled_time"], "%Y-%m-%d %H:%M")
        if when > now:
            continue
        try:
            cid = create_container(p["image_url"], p["caption"])
            time.sleep(5)
            p["media_id"] = publish(cid)
            p["posted"] = True
            changed = True
            print("পোস্ট হয়েছে:", p["media_id"])
        except requests.HTTPError as e:
            print("ব্যর্থ:", e.response.text)
    if changed:
        with open("posts.json", "w", encoding="utf-8") as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
