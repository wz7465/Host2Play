import os
import time
from xvfbwrapper import Xvfb
from DrissionPage import ChromiumPage, ChromiumOptions
import requests

# ======================
# Telegram
# ======================
def send_tg_photo(token, chat_id, photo_path, caption):
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    with open(photo_path, "rb") as f:
        requests.post(
            url,
            data={"chat_id": chat_id, "caption": caption},
            files={"photo": f},
            timeout=30
        )

# ======================
# Screenshot + Info
# ======================
def capture_page(url, save_path):
    vdisplay = Xvfb(width=1280, height=720)
    vdisplay.start()

    try:
        co = ChromiumOptions()
        co.set_browser_path('/usr/bin/google-chrome')
        co.set_argument('--no-sandbox')
        co.set_argument('--disable-dev-shm-usage')
        co.set_argument('--disable-gpu')
        co.set_argument('--disable-extensions')
        co.set_argument('--window-size=1280,720')
        co.auto_port()
        co.headless(False)

        page = ChromiumPage(co)

        page.get(url, retry=2)
        time.sleep(5)

        # -------------------------
        # 提取服务器名称（唯一正确方式）
        # -------------------------
        server_ele = page.ele('#serverName', timeout=3)
        server_name = server_ele.text.strip() if server_ele else "未知"

        # -------------------------
        # 提取到期时间（你要的是 Expires in）
        # -------------------------
        expire_ele = page.ele("text:Expires in", timeout=3)
        if expire_ele:
            expire = expire_ele.parent().text.replace("Expires in:", "").strip()
        else:
            expire = "未知"

        # -------------------------
        # 截图（干净）
        # -------------------------
        page.get_screenshot(path=save_path)
        page.quit()

        return server_name, expire

    finally:
        vdisplay.stop()

# ======================
# MAIN
# ======================
def main():
    tg_token = os.getenv("TG_BOT_TOKEN")
    tg_chat_id = os.getenv("TG_CHAT_ID")

    urls = [
        "https://host2play.gratis/server/renew?i=69899a6d-456b-4dd6-826b-1e29702db393"
    ]

    os.makedirs("output", exist_ok=True)

    for idx, url in enumerate(urls, 1):
        save_path = f"output/screenshot_{idx}.png"
        server_name, expire = capture_page(url, save_path)

        caption = (
            f"服务器：{server_name}\n"
            f"到期：{expire}\n"
            f"URL：{url}\n"
            f"请手动续期"
        )

        send_tg_photo(tg_token, tg_chat_id, save_path, caption)

if __name__ == "__main__":
    main()
