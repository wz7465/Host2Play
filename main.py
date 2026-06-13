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
    try:
        with open(photo_path, "rb") as f:
            resp = requests.post(
                url,
                data={"chat_id": chat_id, "caption": caption},
                files={"photo": f},
                timeout=30
            )
        resp.raise_for_status()
        print("[INFO] Telegram 发送成功")
    except Exception as e:
        print(f"[ERROR] Telegram 发送失败: {e}")

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

        print(f"[INFO] 打开页面: {url}")
        page.get(url, retry=2)
        time.sleep(5)

        # -------------------------
        # 提取服务器名称（最稳）
        # -------------------------
        server_line = page.ele("text:服务器", timeout=3)
        if server_line:
            server_name = server_line.text.split("：")[-1].strip()
        else:
            server_name = "未知"

        # -------------------------
        # 提取到期时间（最稳）
        # -------------------------
        expire_line = page.ele("text:Deletes on", timeout=3)
        if expire_line:
            expire = expire_line.parent().text.replace("Deletes on:", "").strip()
        else:
            expire = "未知"

        # -------------------------
        # 截图（干净）
        # -------------------------
        print(f"[INFO] 截图保存到: {save_path}")
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

        # Telegram caption（截图下面显示）
        caption = (
            f"服务器：{server_name}\n"
            f"到期：{expire}\n"
            f"URL：{url}\n"
            f"请手动续期"
        )

        send_tg_photo(tg_token, tg_chat_id, save_path, caption)

    print("[INFO] 全部完成")

if __name__ == "__main__":
    main()
