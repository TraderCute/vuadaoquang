import os
import time
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
        # Lấy text từ phần tử topBalance trên giao diện, lọc bỏ dấu phẩy/chấm để biến thành số
        bal = driver.execute_script("return document.getElementById('topBalance').innerText;")
        if bal:
            return int(bal.replace(',', '').replace('.', '').strip())
        return 0
    except:
        return 0

# ================= MÔ-ĐUN CÀY NHIỆM VỤ HÀNG NGÀY (BẢN HACK CỬA SAU) =================
def do_daily_tasks(driver):
    logger("🎁 Bắt đầu càn quét nhiệm vụ hàng ngày...", "INFO")
    try:
        # 1. Điểm Danh
        logger("Đang kiểm tra sổ Điểm danh...", "TIME")
        is_checked_in = driver.execute_script("return document.getElementById('btnCheckin').disabled;")
        if not is_checked_in:
            ore_before = check_ore_balance(driver)
            driver.execute_script("document.getElementById('btnCheckin').click();")
            time.sleep(2)
            try: driver.execute_script("closeCustomAlert();")
            except: pass
            
            time.sleep(2) 
            ore_after = check_ore_balance(driver)
            logger(f"Đã điểm danh thành công! Lãi ròng: +{ore_after - ore_before} Quặng (Tổng: {ore_after})", "SUCCESS")
        else:
            logger("Hôm nay đã điểm danh rồi.", "WARNING")

        # 2. Xem Quảng Cáo (ĐÒN HACK API: XUYÊN THỦNG HỆ THỐNG)
        logger("Đang tìm mỏ Quảng Cáo...", "TIME")
        is_ad_ready = driver.execute_script("return !document.getElementById('btnWatchAd').disabled;")
        if is_ad_ready:
            ore_before = check_ore_balance(driver)
            logger(f"Phát hiện QC! (Đang có: {ore_before} Quặng). Bỏ qua Video, tung đòn Hack API...", "SUCCESS")
            
            # ĐÂY LÀ CHÂN LÝ: Đâm thẳng vào tim server, gọi API nhận thưởng mà không cần bật SDK quảng cáo!
            driver.execute_script("apiPost('/api/task-watchad');")
            
            # Chờ 3 giây cho máy chủ nó ngu ngơ cập nhật database
            time.sleep(3) 
            
            # Gọi hàm hệ thống của game để tải lại giao diện, cập nhật số dư mới
            driver.execute_script("initAppSystem(false);")
            time.sleep(2)
            
            try: driver.execute_script("closeCustomAlert();")
            except: pass
            
            ore_after = check_ore_balance(driver)
            profit = ore_after - ore_before
            if profit > 0:
                logger(f"Hack API QC thành công! Bú đẫm: +{profit} Quặng (Tổng tài sản: {ore_after})", "SUCCESS")
                
                # Hack xong thì khóa cái nút lại để khỏi gọi nhầm lần 2
                driver.execute_script("document.getElementById('btnWatchAd').disabled = true;")
            else:
                logger(f"Hack xịt! Dev nó vừa khóa cửa sau (Lãi 0). Tổng: {ore_after}", "ERROR")
        else:
            logger("QC đang chờ hồi chiêu (Hoặc đã hack xong rồi).", "WARNING")

    except Exception as e:
        logger(f"Lỗi khi làm nhiệm vụ: {str(e)}", "ERROR")

# ================= MÔ-ĐUN QUẢN LÝ HẦM MỎ (CHECK THỜI GIAN) =================
def manage_mining(driver):
    print("\n" + "="*40)
    print(" BÁO CÁO TÌNH TRẠNG HẦM MỎ")
    print("="*40)
    try:
        # 1. Kiểm tra trạng thái máy đang tắt
        is_inactive = driver.execute_script("return document.getElementById('miningNotActiveView').style.display !== 'none';")
        
        if is_inactive:
            logger("Máy đào đang tắt. Kích hoạt khởi động...", "WARNING")
            driver.execute_script("document.getElementById('btnStartMining').click();")
            time.sleep(3)
            try:
                driver.execute_script("closeCustomAlert();")
            except:
                pass
            logger("Đã khởi động máy đào thành công!", "SUCCESS")
            return

        # 2. Kiểm tra trạng thái máy đang chạy
        is_active = driver.execute_script("return document.getElementById('miningActiveView').style.display !== 'none';")
        
        if is_active:
            countdown = driver.execute_script("return document.getElementById('miningCountdown').innerText.trim();")
            logger(f"Trạng thái: Đang đào (Thời gian còn lại: {countdown})", "INFO")
            
            # Phân tích thời gian đếm ngược
            total_mins = 999
            if "ĐẦY" in countdown.upper() or countdown == "00:00:00":
                total_mins = 0
            else:
                try:
                    parts = countdown.split(':')
                    if len(parts) == 3: # Định dạng HH:MM:SS
                        total_mins = int(parts[0]) * 60 + int(parts[1])
                    elif len(parts) == 2: # Định dạng MM:SS
                        total_mins = int(parts[0])
                except:
                    pass
            
            # Chỉ thu hoạch khi còn <= 10 phút hoặc đã đầy
            if total_mins <= 10:
                ore_before = check_ore_balance(driver)
                logger(f"Đã đến thời điểm thu hoạch. Tiến hành lấy quặng... (Đang có: {ore_before})", "SUCCESS")
                
                driver.execute_script("document.getElementById('btnClaim').click();")
                time.sleep(3)
                try:
                    driver.execute_script("closeCustomAlert();")
                except:
                    pass
                
                time.sleep(2) 
                ore_after = check_ore_balance(driver)
                profit = ore_after - ore_before
                logger(f"Thu hoạch hoàn tất! Lãi ròng: +{profit} Quặng (Tổng: {ore_after})", "SUCCESS")
                
                # Bật lại máy ngay lập tức để chạy ca mới
                logger("Khởi động lại máy đào...", "INFO")
                driver.execute_script("document.getElementById('btnStartMining').click();")
                time.sleep(3)
                try:
                    driver.execute_script("closeCustomAlert();")
                except:
                    pass
            else:
                logger(f"Chưa đến giờ thu hoạch (còn > 10 phút). Bỏ qua để máy tiếp tục chạy.", "WARNING")

    except Exception as e:
        logger(f"Lỗi quản lý hầm mỏ: {str(e)}", "ERROR")
    print("="*40 + "\n")
# ================= ĐÒN ĐÁNH TỔNG HỢP =================
def main():
    logger("🚀 KHỞI ĐỘNG HỆ THỐNG AUTO ĐÀO QUẶNG V3.0 (KẾ TOÁN TRƯỞNG)", "SUCCESS")
    target_url = get_fresh_target_url()
    if not target_url:
        logger("Không lấy được URL, dừng hệ thống!", "ERROR")
        return
        
    driver = setup_driver()
    try:
        driver.get(target_url)
        logger("Chờ 10s để máy chủ đồng bộ dữ liệu...", "TIME")
        time.sleep(10) 
        
        do_daily_tasks(driver)
        manage_mining(driver)
        
        logger("🎉 HOÀN TẤT CHU TRÌNH! Hẹn gặp lại vào ca trực tiếp theo.", "SUCCESS")
        
    except Exception as err:
        logger(f"Lỗi hệ thống: {str(err)}", "ERROR")
        traceback.print_exc()
    finally:
        logger("🛑 Tự động đóng trình duyệt và rút êm...", "INFO")
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    main()
