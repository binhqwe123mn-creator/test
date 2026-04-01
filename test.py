import os
import sys
import time
import random
import string
import threading
import zipfile # Thêm thư viện này để tạo Proxy Extension
import requests
from datetime import datetime

# ================= 1. GIAO DIỆN & MÀU SẮC MỚI =================
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
except ImportError:
    print(f"{Colors.YELLOW}⏳ Đang tải các module cần thiết...{Colors.RESET}")
    os.system("pip install selenium requests")
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options

# ================= 2. CẤU HÌNH HỆ THỐNG & API =================
CHROMEDRIVER_PATH = "/usr/bin/chromedriver" 
CHROMIUM_PATH = "/usr/bin/chromium-browser"
WEBHOOK_URL = "https://discord.com/api/webhooks/1488214941952508034/HtMyQKYDWl6B2ptDJ08YhtgH4i3KxugZ7f8sJmlgONRR5f0XsNrdIXS_SDlLCJHPfQSE"
WEBHOOK_AVATAR = "https://i.pinimg.com/736x/9a/3b/53/9a3b53ce269a4e063fdefa2b1c3c938d.jpg"

# --- CẤU HÌNH PROXY OP.WTF ---
PROXY_HOST = "proxy.op.wtf"
PROXY_PORT = 32424
PROXY_USER = "res-us"
PROXY_PASS = "op-6a97bdb90865afff0d1a3d9a0c151db2e913d112a2091d53"

# Dictionary proxy dùng cho thư viện requests (lấy email)
req_proxies = {
    "http": f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}",
    "https": f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
}
# -----------------------------

# Danh sách URL API
API_1_URL = "https://api.mail.tm/domains"
API_2_URL = "https://api.mail.gw/domains"
API_3_URL = "http://api.guerrillamail.com/ajax.php?f=get_email_address"
API_4_URL = "https://dropmail.me/api/graphql/web-test-202510234Y4xI"

print_lock = threading.Lock()
working_apis = []

def log(msg, status="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    if status == "SUCCESS":
        prefix = f"{Colors.GREEN}[+] SUCCESS{Colors.RESET}"
    elif status == "ERROR":
        prefix = f"{Colors.RED}[-] ERROR  {Colors.RESET}"
    elif status == "WARN":
        prefix = f"{Colors.YELLOW}[!] WARNING{Colors.RESET}"
    elif status == "ACTION":
        prefix = f"{Colors.MAGENTA}[>] ACTION {Colors.RESET}"
    else:
        prefix = f"{Colors.CYAN}[*] INFO   {Colors.RESET}"
        
    with print_lock:
        print(f"{Colors.WHITE}[{ts}]{Colors.RESET} {prefix} | {msg}")

def gen_str(length=6): 
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))

# Hàm tạo Extension ảo cho Chrome để vượt ải Proxy Auth
def create_proxy_extension():
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy", "tabs", "unlimitedStorage", "storage",
            "<all_urls>", "webRequest", "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """
    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
              singleProxy: { scheme: "http", host: "%s", port: parseInt(%s) },
              bypassList: ["localhost"]
            }
          };
    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
    function callbackFn(details) {
        return { authCredentials: { username: "%s", password: "%s" } };
    }
    chrome.webRequest.onAuthRequired.addListener(
                callbackFn, {urls: ["<all_urls>"]}, ['blocking']
    );
    """ % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)

    plugin_file = 'proxy_auth_plugin.zip'
    with zipfile.ZipFile(plugin_file, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    return plugin_file

# ================= 3. HỆ THỐNG QUẢN LÝ 4 API EMAIL =================
def check_all_apis():
    log("Đang kiểm tra tình trạng kết nối 4 API Email (Qua Proxy)...", "ACTION")
    global working_apis
    apis = {"API 1": API_1_URL, "API 2": API_2_URL, "API 3": API_3_URL, "API 4": API_4_URL}
    
    for name, url in apis.items():
        try:
            if name == "API 4":
                payload = {"query": 'mutation { introduceSession { id } }'}
                r = requests.post(url, json=payload, proxies=req_proxies, timeout=15)
            else:
                r = requests.get(url, proxies=req_proxies, timeout=15)
                
            if r.status_code in [200, 201]:
                log(f"Máy chủ {name} hoạt động tốt!", "SUCCESS")
                working_apis.append(name)
            else:
                log(f"Máy chủ {name} phản hồi lỗi {r.status_code}", "ERROR")
        except:
            log(f"Máy chủ {name} không phản hồi (Bị chặn/Sập)", "ERROR")
            
    if not working_apis:
        log("Tất cả API đều chết! Tool sẽ dùng Mail dự phòng.", "WARN")
        working_apis = ["BACKUP"]

def get_api_email():
    selected_api = random.choice(working_apis)
    password = f"Shiroko{gen_str(4)}!@#12"
    
    try:
        if selected_api == "API 1":
            r = requests.get(API_1_URL, proxies=req_proxies, timeout=10).json()
            domain = r['hydra:member'][0]['domain']
            email = f"shiroko_{gen_str(5)}@{domain}"
            return email, password, "API 1"
            
        elif selected_api == "API 2":
            r = requests.get(API_2_URL, proxies=req_proxies, timeout=10).json()
            domain = r['hydra:member'][0]['domain']
            email = f"shiroko_{gen_str(5)}@{domain}"
            return email, password, "API 2"
            
        elif selected_api == "API 3":
            r = requests.get(API_3_URL, proxies=req_proxies, timeout=10).json()
            email = r['email_addr']
            return email, password, "API 3"
            
        elif selected_api == "API 4":
            payload = {"query": 'mutation { introduceSession { addresses { address } } }'}
            r = requests.post(API_4_URL, json=payload, proxies=req_proxies, timeout=10).json()
            email = r["data"]["introduceSession"]["addresses"][0]["address"]
            return email, password, "API 4"
            
    except Exception as e:
        pass
        
    domains = ["sharebot.net", "teihu.com", "mailtowin.com"]
    email = f"shir_{gen_str(4)}_{random.randint(10,99)}@{random.choice(domains)}"
    return email, password, "BACKUP"

# ================= 4. CORE AUTO - CHUẨN KHÔNG CẦN CHỈNH =================
def run_referral_loop(ref_link):
    ref_code = ref_link.split("ref=")[-1] if "ref=" in ref_link else ref_link.strip()
    
    opts = Options()
    # Chú ý: Cần đổi từ --headless thành --headless=new để extension proxy hoạt động
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.binary_location = CHROMIUM_PATH
    
    opts.add_argument("--window-size=390,844") 
    opts.add_argument("user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1")

    # Nhúng file Proxy Extension vừa tạo vào Chrome
    proxy_plugin = create_proxy_extension()
    opts.add_extension(proxy_plugin)

    driver = None
    success_count = 0
    
    while True:
        try:
            log("-" * 50, "INFO")
            log("Khởi động phiên làm việc mới (Với OP.WTF Proxy)...", "ACTION")
            driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=opts)
            wait = WebDriverWait(driver, 25)
            
            # Check IP (Tùy chọn, bác có thể bỏ qua nếu muốn)
            # driver.get("https://api.ipify.org")
            # log(f"IP hiện tại: {driver.find_element(By.TAG_NAME, 'body').text}", "INFO")

            email, password, api_name = get_api_email()
            log(f"Tạo thành công Email từ {api_name}: {email[:10]}...", "ACTION")
            
            log(f"Truy cập: /signup?ref={ref_code}", "ACTION")
            driver.get(f"https://proxifly.dev/signup?ref={ref_code}")
            time.sleep(5) 
            
            driver.execute_script("""
                let btns = document.querySelectorAll('button');
                for(let b of btns) { if(b.innerText.includes('I Understand')) b.click(); }
            """)

            log("Đang tiêm dữ liệu vào Form...", "ACTION")
            email_box = wait.until(EC.presence_of_element_located((By.NAME, "email")))
            email_box.send_keys(email)
            
            pass_box = driver.find_element(By.NAME, "password")
            pass_box.send_keys(password)
            time.sleep(1)
            
            log("Click [Create Account]...", "ACTION")
            driver.execute_script("""
                let btns = document.querySelectorAll('button');
                for(let b of btns) {
                    if(b.innerText.includes('Create Account')) {
                        b.click(); return;
                    }
                }
            """)
            
            log("Đợi Server duyệt tài khoản...", "WAIT")
            time.sleep(12)
            
            log("Chuyển hướng trang Account...", "ACTION")
            driver.get("https://proxifly.dev/account")
            time.sleep(5)
            
            log("Truy cập mục [API Keys]...", "ACTION")
            driver.execute_script("""
                let els = document.querySelectorAll('*');
                for(let e of els) {
                    if(e.innerText === 'API Keys') {
                        e.click(); return;
                    }
                }
            """)
            time.sleep(5)
            
            log("Quét vùng nhớ tìm Private Key...", "ACTION")
            api_key = driver.execute_script("""
                let inputs = document.querySelectorAll('input');
                for (let i of inputs) {
                    let val = i.value.trim();
                    if (val.length >= 40 && i.type !== 'hidden' && !val.includes('@')) {
                        return val;
                    }
                }
                return null;
            """)
                    
            if api_key:
                success_count += 1
                log(f"LỤM KEY THẬT THÀNH CÔNG: {api_key[:12]}*** | Tổng: {success_count}", "SUCCESS")
                
                requests.post(WEBHOOK_URL, json={
                    "username": "Shiroko Auto",
                    "avatar_url": WEBHOOK_AVATAR,
                    "embeds": [{
                        "title": "🎉 SHIROKO ĐÃ LẤY ĐÚNG PRIVATE API KEY!",
                        "color": 3066993, 
                        "fields": [
                            {"name": f"📧 Nguồn Email ({api_name})", "value": f"`{email}`", "inline": True},
                            {"name": "🔑 Mật khẩu", "value": f"`{password}`", "inline": True},
                            {"name": "🚀 Private API Key (Chuẩn 100%)", "value": f"```text\n{api_key}\n```", "inline": False}
                        ],
                        "footer": {"text": f"Ref: {ref_code} | Tổng lụm: {success_count}"}
                    }]
                })
            else:
                log("Không tìm thấy Key hợp lệ (Có thể bị kẹt hoặc web lag).", "ERROR")

            log("Đóng luồng, nghỉ 5s trước vòng lặp mới...", "INFO")
            driver.quit()
            driver = None
            time.sleep(5)
            
        except Exception as e:
            err = str(e).split('\n')[0][:50]
            log(f"Crash: {err}", "ERROR")
            if driver:
                try: driver.quit()
                except: pass
                driver = None
            time.sleep(3)

# ================= 5. MENU KHỞI ĐỘNG =================
def print_banner():
    os.system("clear")
    banner = f"""{Colors.CYAN}
   ███████╗██╗  ██╗██╗██████╗  ██████╗ ██╗  ██╗ ██████╗ 
   ██╔════╝██║  ██║██║██╔══██╗██╔═══██╗██║ ██╔╝██╔═══██╗
   ███████╗███████║██║██████╔╝██║   ██║█████╔╝ ██║   ██║
   ╚════██║██╔══██║██║██╔══██╗██║   ██║██╔═██╗ ██║   ██║
   ███████║██║  ██║██║██║  ██║╚██████╔╝██║  ██╗╚██████╔╝
   ╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝
{Colors.MAGENTA}  >> SHIROKO APEX V4 - POWERED BY GEMINI PRO <<
{Colors.WHITE}  --------------------------------------------------
    * Tích hợp 4 hệ thống API Mail (Ẩn Domain)
    * Giao diện Terminal Monitor v4.0
    * Fix lỗi đọc nhầm User ID (Lọc >= 40 ký tự)
  --------------------------------------------------{Colors.RESET}
"""
    print(banner)

def main():
    print_banner()
    
    # Check 4 API trước khi chạy
    check_all_apis()
    
    print()
    raw_ref = input(f"{Colors.YELLOW}[?] Dán mã Ref của bác (Ví dụ: pNYHIv6J): {Colors.RESET}").strip()
    
    print(f"\n{Colors.GREEN}[!] HỆ THỐNG ĐÃ SẴN SÀNG.{Colors.RESET}")
    print(f"{Colors.CYAN}[!] Vui lòng bật VPN trước khi tiếp tục.{Colors.RESET}")
    input(f"{Colors.YELLOW}[>] Nhấn [ENTER] để phóng phi thuyền... {Colors.RESET}")
    
    threading.Thread(target=run_referral_loop, args=(raw_ref,), daemon=True).start()
    while True: time.sleep(1)

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: 
        print(f"\n{Colors.RED}[!] Đã ngắt kết nối an toàn!{Colors.RESET}")
