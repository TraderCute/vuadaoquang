import os
import time
import json
import traceback
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon import functions

# ================= CẤU HÌNH BẢO MẬT TỪ GITHUB SECRETS =================
API_ID = int(os.environ.get("API_ID", 12345678)) 
API_HASH = os.environ.get("API_HASH", "api_hash_cua_ong_vao_day")
TG_SESSION = os.environ.get("TG_SESSION", "chuoi_string_session_cua_ong_vao_day")

BOT_USERNAME = 'VuaDaoQuang_Bot' 
WEBAPP_URL = 'https://vdq.builderminiapp.online/'

# ================= BỘ NHỚ KẾ TOÁN (MỚI THÊM) =================
bot_stats = {
    "checkin_profit": 0,
    "ad_profit": 0,
    "mining_profit": 0
}

# ================= MÔ-ĐUN LẤY LINK TỰ ĐỘNG =================
def get_fresh_target_url():
    logger("Đang gọi Telegram API để lấy link WebApp Đào Quặng mới nhất...", "INFO")
    try:
        with TelegramClient(StringSession(TG_SESSION), API_ID, API_HASH) as client:
            result = client(functions.messages.RequestWebViewRequest(
                peer=BOT_USERNAME,
                bot=BOT_USERNAME,
                platform='android',
                from_bot_menu=False,
                url=WEBAPP_URL
            ))
            logger("Đã lấy thành công link WebApp với auth_date mới!", "SUCCESS")
            return result.url
    except Exception as e:
        logger(f"Lỗi khi móc link từ Telegram: {str(e)}", "ERROR")
        return None

def logger(msg, level="INFO"):
    now = datetime.now().strftime("%H:%M:%S")
    icons = {"INFO": "🔵", "SUCCESS": "🟢", "WARNING": "🟠", "ERROR": "🔴", "TIME": "⏳"}
    print(f"[{now}] {icons.get(level, '⚫')} {msg}")

def setup_driver():
    logger("Khởi động cỗ máy khai khoáng (Chế độ Server Đám Mây)...", "INFO")
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new') 
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--log-level=3')
    options.add_argument('--mute-audio')
    
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(450, 900)
    
    driver.execute_cdp_cmd('Network.enable', {})
    driver.execute_cdp_cmd('Network.setBlockedURLs', {
        'urls': ['*ruksoutsaishu.com*', '*popunder*']
    })
    return driver     

# ================= KẾ TOÁN TRƯỞNG: SOI TÀI KHOẢN =================
def check_ore_balance(driver):
    try:
        bal = driver.execute_script("return document.getElementById('topBalance').innerText;")
        if bal:
            return int(bal.replace(',', '').replace('.', '').strip())
        return 0
    except:
        return 0

# ================= MÔ-ĐUN GHI SỔ DATABASE (MỚI THÊM) =================
def save_database():
    global bot_stats
    today = datetime.now().strftime("%Y-%m-%d")
    db_file = "database.json"
    
    # 1. Đọc sổ cũ (nếu có)
    try:
        with open(db_file, "r") as f:
            db = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        db = {}
        
    # 2. Tạo trang mới cho ngày hôm nay
    if today not in db:
        db[today] = {"runs": 0, "total_profit": 0, "ad_profit": 0, "mining_profit": 0}
        
    # 3. Tính tổng lãi ca này
    profit = bot_stats["checkin_profit"] + bot_stats["ad_profit"] + bot_stats["mining_profit"]
    
    # 4. Cộng dồn số liệu
    db[today]["runs"] += 1
    db[today]["total_profit"] += profit
    db[today]["ad_profit"] += bot_stats["ad_profit"]
    db[today]["mining_profit"] += bot_stats["mining_profit"]
    
    # 5. Lưu đè ra file
    with open(db_file, "w") as f:
        json.dump(db, f, indent=4)
    
    logger(f"💾 Đã chốt sổ Kế toán vào File 'database.json'. Lãi ca này: +{profit} Quặng", "SUCCESS")

# ================= MÔ-ĐUN CÀY NHIỆM VỤ HÀNG NGÀY =================
def do_daily_tasks(driver):
    global bot_stats
    logger("🎁 Bắt đầu càn quét nhiệm vụ hàng ngày...", "INFO")
    try:
        is_checked_in = driver.execute_script("return document.getElementById('btnCheckin').disabled;")
        if not is_checked_in:
            ore_before = check_ore_balance(driver)
            driver.execute_script("document.getElementById('btnCheckin').click();")
            time.sleep(2)
            try: driver.execute_script("closeCustomAlert();")
            except: pass
            
            time.sleep(2) 
            ore_after = check_ore_balance(driver)
            profit = ore_after - ore_before
            bot_stats["checkin_profit"] = profit # Lưu vào bộ nhớ
            logger(f"Đã điểm danh thành công! Lãi ròng: +{profit} Quặng (Tổng: {ore_after})", "SUCCESS")
        else:
            logger("Hôm nay đã điểm danh rồi.", "WARNING")

        is_ad_ready = driver.execute_script("return !document.getElementById('btnWatchAd').disabled;")
        if is_ad_ready:
            ore_before = check_ore_balance(driver)
            logger(f"Phát hiện QC! (Đang có: {ore_before} Quặng). Tung đòn Hack API...", "SUCCESS")
            
            driver.execute_script("apiPost('/api/task-watchad');")
            time.sleep(3) 
            driver.execute_script("initAppSystem(false);")
            time.sleep(2)
            
            try: driver.execute_script("closeCustomAlert();")
            except: pass
            
            ore_after = check_ore_balance(driver)
            profit = ore_after - ore_before
            if profit > 0:
                bot_stats["ad_profit"] = profit # Lưu vào bộ nhớ
                logger(f"Hack API QC thành công! Bú đẫm: +{profit} Quặng", "SUCCESS")
                driver.execute_script("document.getElementById('btnWatchAd').disabled = true;")
            else:
                logger(f"Hack xịt! Lãi 0.", "ERROR")
        else:
            logger("QC đang chờ hồi chiêu.", "WARNING")

    except Exception as e:
        logger(f"Lỗi khi làm nhiệm vụ: {str(e)}", "ERROR")

# ================= MÔ-ĐUN QUẢN LÝ HẦM MỎ =================
def manage_mining(driver):
    global bot_stats
    print("\n" + "="*40)
    print(" BÁO CÁO TÌNH TRẠNG HẦM MỎ")
    print("="*40)
    try:
        is_inactive = driver.execute_script("return document.getElementById('miningNotActiveView').style.display !== 'none';")
        if is_inactive:
            logger("Máy đào đang tắt. Kích hoạt khởi động...", "WARNING")
            driver.execute_script("document.getElementById('btnStartMining').click();")
            time.sleep(3)
            try: driver.execute_script("closeCustomAlert();")
            except: pass
            return

        is_active = driver.execute_script("return document.getElementById('miningActiveView').style.display !== 'none';")
        if is_active:
            countdown = driver.execute_script("return document.getElementById('miningCountdown').innerText.trim();")
            
            total_mins = 999
            if "ĐẦY" in countdown.upper() or countdown == "00:00:00":
                total_mins = 0
            else:
                try:
                    parts = countdown.split(':')
                    if len(parts) == 3: total_mins = int(parts[0]) * 60 + int(parts[1])
                    elif len(parts) == 2: total_mins = int(parts[0])
                except: pass
            
            if total_mins <= 10:
                ore_before = check_ore_balance(driver)
                driver.execute_script("document.getElementById('btnClaim').click();")
                time.sleep(3)
                try: driver.execute_script("closeCustomAlert();")
                except: pass
                
                time.sleep(2) 
                ore_after = check_ore_balance(driver)
                profit = ore_after - ore_before
                bot_stats["mining_profit"] = profit # Lưu vào bộ nhớ
                logger(f"Thu hoạch hoàn tất! Lãi ròng: +{profit} Quặng", "SUCCESS")
                
                driver.execute_script("document.getElementById('btnStartMining').click();")
                time.sleep(3)
                try: driver.execute_script("closeCustomAlert();")
                except: pass
            else:
                logger(f"Chưa đến giờ thu hoạch. Bỏ qua.", "WARNING")
    except Exception as e:
        logger(f"Lỗi quản lý hầm mỏ: {str(e)}", "ERROR")
    print("="*40 + "\n")

# ================= ĐÒN ĐÁNH TỔNG HỢP =================
def main():
    logger("🚀 KHỞI ĐỘNG HỆ THỐNG AUTO ĐÀO QUẶNG V3.0 (CÓ KẾ TOÁN LƯU FILE)", "SUCCESS")
    target_url = get_fresh_target_url()
    if not target_url:
        return
        
    driver = setup_driver()
    try:
        driver.get(target_url)
        time.sleep(10) 
        
        do_daily_tasks(driver)
        manage_mining(driver)
        
        # CHỐT SỔ VÀO DATABASE.JSON TẠI ĐÂY 👇
        save_database()
        
        logger("🎉 HOÀN TẤT CHU TRÌNH!", "SUCCESS")
        
    except Exception as err:
        logger(f"Lỗi hệ thống: {str(err)}", "ERROR")
        traceback.print_exc()
    finally:
        try: driver.quit()
        except: pass

if __name__ == "__main__":
    main()
