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
API_ID = int(os.environ.get("API_ID", "35833310")) 
API_HASH = os.environ.get("API_HASH", "aeef412b2f9b3e1b34a0fa4e0ed7473e")
TG_SESSION = os.environ.get("TG_SESSION", "1BVtsOJMBu7DB5gpd8cJHNZqlAYL1LR24eLAfVzzVNZ789Z2UZ00023WlR41VT9gHMdLsxDoC_9B-9bug0vhwCL1Bz25wDyMxT-To4dW4rB99Zgc45SymBosYTcCyO6gq-IryoRaERb_s2JSyDn9IqX-mE7EhUQNOHMXYt4X0TjJbgPQ2eX_Px-Mg2_cyTgQ57bXOhM9HBBvfCx9lfIsL8wg7d0IoUciFcKNvbfPaHNcPI2VuxVgMAVohQdgi2iZ-OklvvuSqC2ywlpVCMPnMfxP68ONTqcV9z40T5g7FeLXWy8OYiWD9LzYCbVVZ0piTOH1TgUdE-R-QYVg-k7QuCc3LB4TrG7A=")

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
    
    # Vẫn chặn rác nhưng thả cửa cho SDK Monetag hoạt động để game nó trả thưởng
    driver.execute_cdp_cmd('Network.enable', {})
    driver.execute_cdp_cmd('Network.setBlockedURLs', {
        'urls': ['*ruksoutsaishu.com*', '*popunder*']
    })
    return driver     

# ================= MÔ-ĐUN CÀY NHIỆM VỤ HÀNG NGÀY =================
def do_daily_tasks(driver):
    logger("🎁 Bắt đầu càn quét nhiệm vụ hàng ngày...", "INFO")
    try:
        # 1. Điểm Danh (Dựa trên ID btnCheckin từ mã nguồn)
        logger("Đang kiểm tra sổ Điểm danh...", "TIME")
        is_checked_in = driver.execute_script("return document.getElementById('btnCheckin').disabled;")
        if not is_checked_in:
            driver.execute_script("document.getElementById('btnCheckin').click();")
            time.sleep(2)
            try:
                driver.execute_script("closeCustomAlert();")
                logger("Đã điểm danh thành công!", "SUCCESS")
            except:
                pass
        else:
            logger("Hôm nay đã điểm danh rồi.", "WARNING")

        # 2. Xem Quảng Cáo (Dùng Trick Lỏ Click 1s)
        logger("Đang tìm nút Xem Quảng Cáo...", "TIME")
        is_ad_ready = driver.execute_script("return !document.getElementById('btnWatchAd').disabled;")
        if is_ad_ready:
            logger("Phát hiện mỏ Quảng Cáo! Đang bật video...", "SUCCESS")
            driver.execute_script("document.getElementById('btnWatchAd').click();")
            
            # Chờ 1.5 giây để SDK Monetag load xong form ẩn
            time.sleep(1.5) 
            
            # Tung đòn chí mạng: Mô phỏng click vật lý vào tọa độ (100, 100) trên màn hình
            logger("Tung trick lỏ: Click bừa để bypass quảng cáo...", "INFO")
            try:
                ActionChains(driver).move_by_offset(100, 100).click().perform()
            except Exception:
                # Nếu lỗi tọa độ thì xài dự phòng click thẳng vào body
                driver.execute_script("document.body.click();")
            
            # Chờ 3s cho Monetag gửi tín hiệu Callback về máy chủ game
            time.sleep(3) 
            
            try:
                driver.execute_script("closeCustomAlert();")
                logger("Đã nhận thưởng từ Quảng Cáo siêu tốc!", "SUCCESS")
            except:
                pass
        else:
            logger("QC đang chờ hồi chiêu (Hoặc đã xem hết).", "WARNING")

    except Exception as e:
        logger(f"Lỗi khi làm nhiệm vụ: {str(e)}", "ERROR")

# ================= MÔ-ĐUN QUẢN LÝ HẦM MỎ (TỐI GIẢN) =================
def manage_mining(driver):
    print("\n" + "="*40)
    print("⛏️ BÁO CÁO TÌNH TRẠNG HẦM MỎ")
    print("="*40)
    try:
        # 1. Kiểm tra xem máy có đang ở trạng thái hiển thị nút Thu Hoạch không
        is_active = driver.execute_script("return document.getElementById('miningActiveView').style.display !== 'none';")
        
        if is_active:
            logger("Phát hiện máy đang chạy, tiến hành thu hoạch quặng...", "INFO")
            driver.execute_script("document.getElementById('btnClaim').click();")
            time.sleep(3)
            try:
                driver.execute_script("closeCustomAlert();")
                logger("Đã thu hoạch quặng cất vào kho!", "SUCCESS")
            except:
                pass
            time.sleep(2)
        
        # 2. Kiểm tra xem máy có đang tắt không (sau khi thu hoạch xong, máy sẽ tự chuyển về trạng thái tắt)
        is_inactive = driver.execute_script("return document.getElementById('miningNotActiveView').style.display !== 'none';")
        
        if is_inactive:
            logger("Máy đào đang tắt. Kích hoạt khởi động...", "WARNING")
            driver.execute_script("document.getElementById('btnStartMining').click();")
            time.sleep(3)
            try:
                driver.execute_script("closeCustomAlert();")
            except:
                pass
            logger("✅ Đã khởi động máy đào cho ca mới!", "SUCCESS")
        else:
            logger("Máy vẫn đang trong phiên đào ổn định.", "INFO")

    except Exception as e:
        logger(f"Lỗi quản lý hầm mỏ: {str(e)}", "ERROR")
    print("="*40 + "\n")

# ================= ĐÒN ĐÁNH TỔNG HỢP =================
def main():
    logger("🚀 KHỞI ĐỘNG HỆ THỐNG AUTO ĐÀO QUẶNG V2.0 (SOURCE-BASED)", "SUCCESS")
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
