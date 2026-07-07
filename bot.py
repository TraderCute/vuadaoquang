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

# ================= MÔ-ĐUN CÀY NHIỆM VỤ HÀNG NGÀY =================
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
            try:
                driver.execute_script("closeCustomAlert();")
            except: pass
            
            time.sleep(1) # Chờ giao diện nhảy số
            ore_after = check_ore_balance(driver)
            profit = ore_after - ore_before
            logger(f"Đã điểm danh thành công! Thu nhập: +{profit} Quặng (Tổng tài sản: {ore_after})", "SUCCESS")
        else:
            logger("Hôm nay đã điểm danh rồi.", "WARNING")

        # 2. Xem Quảng Cáo (Trick Lỏ Click Siêu Tốc)
        logger("Đang tìm nút Xem Quảng Cáo...", "TIME")
        is_ad_ready = driver.execute_script("return !document.getElementById('btnWatchAd').disabled;")
        if is_ad_ready:
            ore_before = check_ore_balance(driver)
            logger(f"Phát hiện mỏ QC! (Đang có: {ore_before} Quặng). Đang bật video...", "SUCCESS")
            driver.execute_script("document.getElementById('btnWatchAd').click();")
            
            time.sleep(1.5) 
            
            logger("Tung trick lỏ: Click bừa để bypass quảng cáo...", "INFO")
            try:
                ActionChains(driver).move_by_offset(100, 100).click().perform()
            except Exception:
                driver.execute_script("document.body.click();")
            
            time.sleep(3) 
            
            try:
                driver.execute_script("closeCustomAlert();")
            except: pass
            
            time.sleep(1) # Chờ giao diện nhảy số
            ore_after = check_ore_balance(driver)
            profit = ore_after - ore_before
            logger(f"Bú đẫm QC siêu tốc! Lãi ròng: +{profit} Quặng (Tổng tài sản: {ore_after})", "SUCCESS")
        else:
            logger("QC đang chờ hồi chiêu (Hoặc đã xem hết).", "WARNING")

    except Exception as e:
        logger(f"Lỗi khi làm nhiệm vụ: {str(e)}", "ERROR")

# ================= MÔ-ĐUN QUẢN LÝ HẦM MỎ (TỐI GIẢN + KIỂM TOÁN) =================
def manage_mining(driver):
    print("\n" + "="*40)
    print("⛏️ BÁO CÁO TÌNH TRẠNG HẦM MỎ")
    print("="*40)
    try:
        # 1. Kiểm tra trạng thái máy chạy (để hốt quặng)
        is_active = driver.execute_script("return document.getElementById('miningActiveView').style.display !== 'none';")
        
        if is_active:
            ore_before = check_ore_balance(driver)
            logger(f"Phát hiện máy đang chạy, tiến hành thu hoạch... (Đang có: {ore_before} Quặng)", "INFO")
            driver.execute_script("document.getElementById('btnClaim').click();")
            time.sleep(3)
            try:
                driver.execute_script("closeCustomAlert();")
            except: pass
            
            time.sleep(2) # Chờ giao diện nhảy số
            ore_after = check_ore_balance(driver)
            profit = ore_after - ore_before
            logger(f"Đã xẻ thịt xong mỏ quặng! Lãi ròng: +{profit} Quặng (Tổng tài sản: {ore_after})", "SUCCESS")
        
        # 2. Kiểm tra trạng thái tắt (sau khi thu hoạch xong, máy tự động đóng)
        is_inactive = driver.execute_script("return document.getElementById('miningNotActiveView').style.display !== 'none';")
        
        if is_inactive:
            logger("Máy đào đang tắt. Kích hoạt điện để cày ca mới...", "WARNING")
            driver.execute_script("document.getElementById('btnStartMining').click();")
            time.sleep(3)
            try:
                driver.execute_script("closeCustomAlert();")
            except: pass
            logger("✅ Đã khởi động máy đào thành công!", "SUCCESS")
        else:
            logger("Máy vẫn đang nhả quặng tằng tằng.", "INFO")

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
