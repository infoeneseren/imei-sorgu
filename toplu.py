import os
import time
import pandas as pd
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, scrolledtext
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from twocaptcha import TwoCaptcha
import logging
import threading
from datetime import datetime

# Selenium ve WebDriver log'larını sustur
logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
os.environ['WDM_LOG_LEVEL'] = '0'  # WebDriver Manager log'larını sustur

# Chrome log'larını tamamen sustur
import sys
if sys.platform.startswith('win'):
    os.environ['CHROME_LOG_FILE'] = 'NUL'
else:
    os.environ['CHROME_LOG_FILE'] = '/dev/null'

# 2Captcha API Key
API_KEY = os.getenv('APIKEY_2CAPTCHA', 'YOUR-API-KEY')
solver = TwoCaptcha(API_KEY)

# Tarayıcı ayarları fonksiyonu
def get_chrome_options(use_headless=True):
    options = webdriver.ChromeOptions()
    
    if use_headless:
        options.add_argument('--headless')  # Tarayıcıyı gizli çalıştır
        log_message("Headless (gizli) mod aktif")
    else:
        options.add_argument('--start-maximized')
        log_message("Görünür mod aktif (Proxy siteleri için gerekli)")
    
    options.add_argument('--disable-gpu')  # Bazı sistemlerde gerekebilir
    options.add_argument('--no-sandbox')   # Bazı Linux sistemlerinde gerekebilir

    # Log'ları susturmak için ek parametreler
    options.add_argument('--disable-logging')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-plugins')
    options.add_argument('--disable-images')
    # JavaScript'i proxy site için gerekli olduğundan kaldırdık
    options.add_argument('--disable-default-apps')
    options.add_argument('--disable-background-timer-throttling')
    options.add_argument('--disable-backgrounding-occluded-windows')
    options.add_argument('--disable-renderer-backgrounding')
    options.add_argument('--disable-features=TranslateUI')
    options.add_argument('--disable-ipc-flooding-protection')
    options.add_argument('--log-level=3')  # Sadece fatal error'ları göster
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_experimental_option('useAutomationExtension', False)

    # Bot tespitini engellemek için ek ayarlar
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_settings.popups": 0,
        "profile.managed_default_content_settings.images": 2
    })
    
    # Proxy siteler için ek bot engelleme ayarları (sadece görünür modda)
    if not use_headless:
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=VizDisplayCompositor")
        # User agent'ı normal browser gibi ayarla
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    return options

# tkinter pencere
root = tk.Tk()
root.title("Reeder Toplu IMEI Sorgulama - Enes EREN Tarafından yapılmıştır.")
root.geometry("900x750")
root.configure(bg='#f8f9fa')

# Uygulama ikonunu ayarla
try:
    # .ico dosyasını kullan (Windows için en uygun)
    if os.path.exists('logo.png'):
        root.iconbitmap('logo.png')
    elif os.path.exists('app.png'):
        root.iconbitmap('app.png')
    else:
        print("İkon dosyası bulunamadı")
except Exception as e:
    print(f"İkon yüklenirken hata: {e}")

# Reeder tema renkleri
REEDER_GREEN = '#7CB342'      # Ana yeşil renk (logodaki yeşil)
REEDER_DARK_GREEN = '#689F39'  # Koyu yeşil
REEDER_LIGHT_GREEN = '#9CCC65' # Açık yeşil
REEDER_WHITE = '#FFFFFF'       # Beyaz
REEDER_GRAY = '#ECEFF1'        # Açık gri
REEDER_DARK_GRAY = '#455A64'   # Koyu gri
REEDER_TEXT = '#263238'        # Metin rengi

# Excel dosyası yolu
file_path = ''

# Global değişkenler
is_running = False
log_text = None
progress_bar = None
status_label = None

# Log fonksiyonu
def log_message(message, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    if log_text:
        log_text.config(state='normal')
        
        # Timestamp'i gri renkte ekle
        log_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Level'e göre renk belirle
        if level == "ERROR":
            log_text.insert(tk.END, f"{level}: ", "error")
        elif level == "WARNING":
            log_text.insert(tk.END, f"{level}: ", "warning")
        elif level == "SUCCESS":
            log_text.insert(tk.END, f"{level}: ", "success")
        else:
            log_text.insert(tk.END, f"{level}: ", "info")
        
        # Mesajı normal renkte ekle
        log_text.insert(tk.END, f"{message}\n", "message")
        
        log_text.see(tk.END)
        log_text.config(state='disabled')
    
    print(f"{level}: {message}")

# GUI güncelleme fonksiyonu
def update_gui(status_text=None, progress_value=None):
    if status_text and status_label:
        status_label.config(text=status_text)
    
    if progress_value is not None and progress_bar:
        progress_bar['value'] = progress_value
    
    root.update_idletasks()

# Fonksiyon: Dosya seç
def select_file():
    global file_path
    file_path = filedialog.askopenfilename(filetypes=[("Excel Dosyası", "*.xlsx")])
    if file_path:
        lbl_file.config(text=f"Seçilen dosya: {os.path.basename(file_path)}")

# Fonksiyon: Proxy üzerinden sorgu yap
def query_via_proxy(driver, imei_number):
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Yeni sekme aç ve önceki sekmeyi kapat (eğer birden fazla sekme varsa)
            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            
            # Croxyproxy'ye git
            log_message(f"Proxy sitesine gidiliyor... (Deneme {retry_count + 1}/{max_retries})")
            driver.get('https://www.croxyproxy.com')
            time.sleep(1)  # Bekleme süresini azalttık
            
            # URL input alanını bul ve türkiye.gov.tr URL'sini yaz
            url_input = driver.find_element(By.XPATH, '//*[@id="url"]')
            url_input.clear()
            url_input.send_keys('https://www.turkiye.gov.tr/imei-sorgulama')
            
            # Submit butonuna tıkla
            submit_button = driver.find_element(By.XPATH, '//*[@id="requestSubmit"]')
            submit_button.click()
            
            # Site tam yüklenene kadar bekle - IMEI input alanı görünene kadar bekle
            log_message("Türkiye.gov.tr sitesi yükleniyor...")
            try:
                # WebDriverWait ile IMEI input alanının yüklenmesini bekle
                wait = WebDriverWait(driver, 15)
                imei_input = wait.until(EC.presence_of_element_located((By.ID, 'txtImei')))
                
                # Element yüklendikten sonra görünür olmasını da bekle
                wait.until(EC.visibility_of_element_located((By.ID, 'txtImei')))
                log_message("Site başarıyla yüklendi!")
                
            except Exception as e:
                log_message(f"Site yüklenme timeout veya hata: {e}. Tekrar deneniyor...", "ERROR")
                retry_count += 1
                continue
            
            # IMEI input alanını bul ve IMEI'yi yaz (zaten yukarıda bulundu)
            imei_input.clear()
            imei_input.send_keys(imei_number)
            log_message(f"IMEI {imei_number} input alanına yazıldı")
            
            # Yeni xpath ile sorgula butonunu bul ve tıkla
            try:
                wait = WebDriverWait(driver, 10)
                sorgula_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/main/div/section/section[2]/form/div/input[1]')))
                sorgula_button.click()
                log_message("Sorgula butonuna tıklandı, sonuç bekleniyor...")
                
                # Sonuç sayfasının yüklenmesini bekle
                time.sleep(3)  # Sonuç için bekle
                
            except Exception as e:
                log_message(f"Sorgula butonuna tıklama hatası: {e}. Tekrar deneniyor...", "ERROR")
                retry_count += 1
                continue
            
            # Teknik aksaklık kontrol et
            error_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'teknik aksaklık') or contains(text(), 'Sistemde yaşanan bir teknik aksaklık')]")
            if error_elements:
                log_message(f"Teknik aksaklık hatası tespit edildi, tekrar deneniyor... ({retry_count + 1}/{max_retries})", "WARNING")
                retry_count += 1
                continue
            
            # Captcha kontrolü yap
            captcha_elements = driver.find_elements(By.CLASS_NAME, 'captchaImage')
            if captcha_elements:
                log_message(f"Captcha tespit edildi, yeni sekme açılıyor... ({retry_count + 1}/{max_retries})", "WARNING")
                # Yeni sekme aç
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[-1])
                retry_count += 1
                continue
            
            # Sonuçları çek
            result_container = driver.find_element(By.CLASS_NAME, 'resultContainer')
            data_elements = result_container.find_elements(By.TAG_NAME, 'dd')
            
            if len(data_elements) >= 5:
                imei_result = data_elements[0].text if len(data_elements) > 0 else ''
                durum = data_elements[1].text if len(data_elements) > 1 else ''
                kaynak = data_elements[2].text if len(data_elements) > 2 else ''
                sorgu_tarihi = data_elements[3].text if len(data_elements) > 3 else ''
                marka_model = data_elements[4].text if len(data_elements) > 4 else ''
                
                log_message(f"IMEI {imei_number} başarıyla sorgulandı!", "SUCCESS")
                return {
                    'IMEI': imei_result,
                    'Durum': durum,
                    'Kaynak': kaynak,
                    'Sorgu Tarihi': sorgu_tarihi,
                    'Marka/Model': marka_model
                }
            else:
                log_message(f"Sonuç verisi eksik, tekrar deneniyor... ({retry_count + 1}/{max_retries})", "WARNING")
                retry_count += 1
                continue
                
        except Exception as e:
            log_message(f"Hata oluştu: {e}, tekrar deneniyor... ({retry_count + 1}/{max_retries})", "ERROR")
            retry_count += 1
            time.sleep(1)
            continue
    
    # Max retry sayısına ulaşıldıysa hata döndür
    log_message(f"IMEI {imei_number} için max deneme sayısına ulaşıldı!", "ERROR")
    return {
        'IMEI': imei_number,
        'Durum': f"Max deneme sayısına ulaşıldı ({max_retries} deneme)",
        'Kaynak': '',
        'Sorgu Tarihi': '',
        'Marka/Model': ''
    }

# Fonksiyon: 2Captcha ile sorgu yap
def query_with_2captcha(driver, imei_number):
    try:
        driver.get('https://www.turkiye.gov.tr/imei-sorgulama')
        time.sleep(2)

        captcha_elements = driver.find_elements(By.CLASS_NAME, 'captchaImage')

        if captcha_elements:
            captcha_path = 'captcha.png'
            captcha_elements[0].screenshot(captcha_path)

            result = solver.normal(captcha_path)
            captcha_code = result['code']

            captcha_input = driver.find_element(By.ID, 'captcha_name')
            captcha_input.clear()
            captcha_input.send_keys(captcha_code)

        imei_input = driver.find_element(By.ID, 'txtImei')
        imei_input.clear()
        imei_input.send_keys(imei_number)

        sorgula_button = driver.find_element(By.CLASS_NAME, 'submitButton')
        sorgula_button.click()

        time.sleep(3)

        # Sonuçları çek
        result_container = driver.find_element(By.CLASS_NAME, 'resultContainer')
        data_elements = result_container.find_elements(By.TAG_NAME, 'dd')

        imei_result = data_elements[0].text if len(data_elements) > 0 else ''
        durum = data_elements[1].text if len(data_elements) > 1 else ''
        kaynak = data_elements[2].text if len(data_elements) > 2 else ''
        sorgu_tarihi = data_elements[3].text if len(data_elements) > 3 else ''
        marka_model = data_elements[4].text if len(data_elements) > 4 else ''

        return {
            'IMEI': imei_result,
            'Durum': durum,
            'Kaynak': kaynak,
            'Sorgu Tarihi': sorgu_tarihi,
            'Marka/Model': marka_model
        }

    except Exception as e:
        return {
            'IMEI': imei_number,
            'Durum': f"Hata: {e}",
            'Kaynak': '',
            'Sorgu Tarihi': '',
            'Marka/Model': ''
        }

# Fonksiyon: Sorgulamayı arka planda çalıştır
def run_query_thread():
    global is_running
    
    try:
        imei_list = pd.read_excel(file_path)['IMEI'].dropna().tolist()
    except Exception as e:
        log_message(f"Excel dosyasından IMEI okunamadı: {e}", "ERROR")
        messagebox.showerror("Hata", f"Excel dosyasından IMEI okunamadı: {e}")
        is_running = False
        btn_start.config(state='normal', text="▶ Sorgulamayı Başlat", bg=REEDER_GREEN)
        return

    if not imei_list:
        log_message("Excel dosyasında IMEI bulunamadı", "ERROR")
        messagebox.showerror("Hata", "Excel dosyasında IMEI bulunamadı.")
        is_running = False
        btn_start.config(state='normal', text="▶ Sorgulamayı Başlat", bg=REEDER_GREEN)
        return

    # Progress bar ayarları
    progress_bar['maximum'] = len(imei_list)
    progress_bar['value'] = 0
    
    log_message(f"Toplam {len(imei_list)} IMEI sorgulanacak")
    log_message("Chrome tarayıcısı başlatılıyor...")

    results = []

    # Seçilen yönteme göre Chrome ayarlarını belirle
    selected_method = method_var.get()
    
    if selected_method == 1:  # 2Captcha - headless kullanabilir
        chrome_options = get_chrome_options(use_headless=True)
        log_message("2Captcha yöntemi seçildi - Headless mod kullanılacak")
    else:  # Proxy Site - görünür mod gerekli
        chrome_options = get_chrome_options(use_headless=False)
        log_message("Proxy Site yöntemi seçildi - Görünür mod kullanılacak (proxy siteler headless'ta düzgün çalışmıyor)")

    # Chrome Service'i log seviyesi ile oluştur
    service = Service(ChromeDriverManager().install())
    service.log_level = 'FATAL'  # Sadece kritik hataları göster
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    log_message("Tarayıcı başarıyla başlatıldı!")

    for idx, imei_number in enumerate(imei_list, start=1):
        if not is_running:  # Durdurma kontrolü
            break
            
        update_gui(f"({idx}/{len(imei_list)}) {imei_number} sorgulanıyor...", None)
        log_message(f"IMEI {idx}/{len(imei_list)}: {imei_number} işleniyor...")

        if selected_method == 1:  # 2Captcha
            result = query_with_2captcha(driver, imei_number)
        else:  # Proxy Site
            result = query_via_proxy(driver, imei_number)
        
        results.append(result)

        # Progress bar ilerlet
        update_gui(f"({idx}/{len(imei_list)}) {imei_number} tamamlandı - Durum: {result.get('Durum', 'Bilinmiyor')}", idx)
        log_message(f"IMEI {imei_number} sonucu: {result.get('Durum', 'Bilinmiyor')}")

    driver.quit()
    log_message("Tarayıcı kapatıldı")

    if is_running:  # Eğer kullanıcı durdurmadıysa kaydetme ekranını göster
        # Sorgu bitince kayıt yeri seçtir
        update_gui("Sorgulama tamamlandı! Kaydetme konumu seçiliyor...", None)
        
        save_path = filedialog.asksaveasfilename(defaultextension='.xlsx',
                                                 filetypes=[("Excel Dosyası", "*.xlsx")],
                                                 title="Sonuçları Kaydet")

        if save_path:
            df = pd.DataFrame(results)
            df.to_excel(save_path, index=False)
            log_message(f"Sonuçlar kaydedildi: {save_path}", "SUCCESS")
            messagebox.showinfo("Tamamlandı", f"Sorgulamalar bitti! Sonuçlar kaydedildi:\n{save_path}")
        else:
            log_message("Sonuçlar kaydedilmedi", "WARNING")
            messagebox.showinfo("Bilgi", "Sonuçlar kaydedilmedi.")
    
    # UI'ı sıfırla
    is_running = False
    btn_start.config(state='normal', text="▶ Sorgulamayı Başlat", bg=REEDER_GREEN)
    update_gui("İşlem tamamlandı.", progress_bar['maximum'])

# Fonksiyon: Sorgulamayı başlat
def start_query():
    global is_running
    
    if is_running:
        # Durdur
        is_running = False
        btn_start.config(text="▶ Sorgulamayı Başlat", bg=REEDER_GREEN)
        log_message("Sorgulama kullanıcı tarafından durduruldu", "WARNING")
        return
    
    if not file_path:
        messagebox.showerror("Hata", "Lütfen bir Excel dosyası seçin.")
        return
    
    # Seçilen yöntemi kontrol et
    selected_method = method_var.get()
    if selected_method == 0:
        messagebox.showerror("Hata", "Lütfen bir sorgulama yöntemi seçin.")
        return

    # Başlat
    is_running = True
    btn_start.config(state='normal', text="⏸ Sorgulamayı Durdur", bg=REEDER_DARK_GREEN)
    
    # Log'u temizle
    if log_text:
        log_text.config(state='normal')
        log_text.delete(1.0, tk.END)
        log_text.config(state='disabled')
    
    log_message("Sorgulama başlatıldı!")
    
    # Arka plan thread'i başlat
    thread = threading.Thread(target=run_query_thread, daemon=True)
    thread.start()

# Arayüz elemanları
main_frame = tk.Frame(root, bg='#f8f9fa')
main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

# Reeder başlık paneli
header_frame = tk.Frame(main_frame, bg=REEDER_GREEN, height=80)
header_frame.pack(fill=tk.X, pady=(0, 20))
header_frame.pack_propagate(False)

# Reeder logo ve başlık
logo_frame = tk.Frame(header_frame, bg=REEDER_GREEN)
logo_frame.pack(expand=True, fill=tk.BOTH)

title_label = tk.Label(logo_frame, text="REEDER", 
                      font=("Arial", 24, "bold"), bg=REEDER_GREEN, fg=REEDER_WHITE)
title_label.pack(side=tk.LEFT, padx=20, pady=15)

subtitle_label = tk.Label(logo_frame, text="Toplu IMEI Sorgulama Sistemi", 
                         font=("Arial", 14), bg=REEDER_GREEN, fg=REEDER_WHITE)
subtitle_label.pack(side=tk.LEFT, padx=(0, 20), pady=15)

# Geliştirici bilgisi
dev_label = tk.Label(logo_frame, text="Developed by Enes EREN", 
                    font=("Arial", 10, "italic"), bg=REEDER_GREEN, fg=REEDER_LIGHT_GREEN)
dev_label.pack(side=tk.RIGHT, padx=20, pady=15)

# Sol frame (Kontroller)
left_frame = tk.Frame(main_frame, bg=REEDER_WHITE, relief=tk.SOLID, bd=1)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))

# Sağ frame (Log)
right_frame = tk.Frame(main_frame, bg=REEDER_WHITE, relief=tk.SOLID, bd=1)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

# Sol frame içeriği
control_frame = tk.Frame(left_frame, bg=REEDER_WHITE, padx=25, pady=25)
control_frame.pack(fill=tk.BOTH, expand=True)

# Yöntem seçimi
method_frame = tk.LabelFrame(control_frame, text="■ Sorgulama Yöntemi", 
                            font=("Segoe UI", 11, "bold"), bg=REEDER_WHITE, fg=REEDER_TEXT,
                            relief=tk.FLAT, bd=2, highlightbackground=REEDER_GREEN, highlightthickness=1)
method_frame.pack(fill=tk.X, pady=(0, 20))

method_var = tk.IntVar()

# Radio button çerçevesi
radio_frame = tk.Frame(method_frame, bg=REEDER_WHITE)
radio_frame.pack(fill=tk.X, padx=15, pady=15)

radio1 = tk.Radiobutton(radio_frame, text="» 2Captcha Kullan (API Key Gerekli)", 
                       variable=method_var, value=1, bg=REEDER_WHITE, fg=REEDER_TEXT,
                       font=("Segoe UI", 10), selectcolor=REEDER_LIGHT_GREEN,
                       activebackground=REEDER_GRAY, activeforeground=REEDER_TEXT)
radio1.pack(anchor="w", pady=8)

radio2 = tk.Radiobutton(radio_frame, text="» Proxy Site Kullan (CroxyProxy)", 
                       variable=method_var, value=2, bg=REEDER_WHITE, fg=REEDER_TEXT,
                       font=("Segoe UI", 10), selectcolor=REEDER_LIGHT_GREEN,
                       activebackground=REEDER_GRAY, activeforeground=REEDER_TEXT)
radio2.pack(anchor="w", pady=8)

# Dosya seçimi
file_frame = tk.LabelFrame(control_frame, text="■ Dosya Seçimi", 
                          font=("Segoe UI", 11, "bold"), bg=REEDER_WHITE, fg=REEDER_TEXT,
                          relief=tk.FLAT, bd=2, highlightbackground=REEDER_GREEN, highlightthickness=1)
file_frame.pack(fill=tk.X, pady=(0, 20))

btn_select = tk.Button(file_frame, text="» IMEI Listesini Seç", command=select_file,
                      bg=REEDER_GREEN, fg=REEDER_WHITE, font=("Segoe UI", 11, "bold"),
                      relief=tk.FLAT, padx=25, pady=12, cursor="hand2",
                      activebackground=REEDER_DARK_GREEN, activeforeground=REEDER_WHITE)
btn_select.pack(pady=15)

lbl_file = tk.Label(file_frame, text="Henüz dosya seçilmedi.", 
                   bg=REEDER_WHITE, fg=REEDER_DARK_GRAY, font=("Segoe UI", 9))
lbl_file.pack(pady=(0, 15))

# Kontrol butonları
control_buttons_frame = tk.Frame(control_frame, bg=REEDER_WHITE)
control_buttons_frame.pack(fill=tk.X, pady=(0, 20))

btn_start = tk.Button(control_buttons_frame, text="▶ Sorgulamayı Başlat", command=start_query,
                     bg=REEDER_GREEN, fg=REEDER_WHITE, font=("Segoe UI", 12, "bold"),
                     relief=tk.FLAT, padx=40, pady=15, cursor="hand2",
                     activebackground=REEDER_DARK_GREEN, activeforeground=REEDER_WHITE)
btn_start.pack(fill=tk.X)

# Progress bar
progress_frame = tk.LabelFrame(control_frame, text="■ İlerleme Durumu", 
                              font=("Segoe UI", 11, "bold"), bg=REEDER_WHITE, fg=REEDER_TEXT,
                              relief=tk.FLAT, bd=2, highlightbackground=REEDER_GREEN, highlightthickness=1)
progress_frame.pack(fill=tk.X, pady=(0, 20))

# Progress bar style'ını Reeder temasına göre ayarla
style = ttk.Style()
style.theme_use('clam')
style.configure("Reeder.Horizontal.TProgressbar", 
                background=REEDER_GREEN,
                troughcolor=REEDER_GRAY,
                borderwidth=0, lightcolor=REEDER_GREEN, darkcolor=REEDER_GREEN)

progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", mode="determinate",
                              style="Reeder.Horizontal.TProgressbar")
progress_bar.pack(fill=tk.X, padx=15, pady=15)

status_label = tk.Label(progress_frame, text="Durum: Bekleniyor...", 
                       bg=REEDER_WHITE, fg=REEDER_TEXT, font=("Segoe UI", 10))
status_label.pack(pady=(0, 15))

# İpucu
tip_frame = tk.LabelFrame(control_frame, text="! Kullanım İpuçları", 
                         font=("Segoe UI", 10, "bold"), bg=REEDER_WHITE, fg=REEDER_DARK_GRAY,
                         relief=tk.FLAT, bd=2, highlightbackground=REEDER_LIGHT_GREEN, highlightthickness=1)
tip_frame.pack(fill=tk.X)

tip_text = """✓ Proxy yönteminde captcha çıktığında otomatik yeni sekme açılır
✓ Proxy yöntemi görünür modda çalışır (daha güvenilir)
✓ 2Captcha yöntemi gizli modda çalışır (daha hızlı)
✓ İşlemi istediğiniz zaman durdurabilirsiniz
✓ Canlı logları sağ panelden takip edebilirsiniz"""

tip_label = tk.Label(tip_frame, text=tip_text,
                    font=("Segoe UI", 9), bg=REEDER_WHITE, fg=REEDER_DARK_GRAY, 
                    justify=tk.LEFT, wraplength=300)
tip_label.pack(padx=15, pady=12)

# Sağ frame - Log paneli
log_frame = tk.LabelFrame(right_frame, text="■ Canlı İşlem Logları", 
                         font=("Segoe UI", 11, "bold"), bg=REEDER_WHITE, fg=REEDER_TEXT,
                         relief=tk.FLAT, bd=2, highlightbackground=REEDER_GREEN, highlightthickness=1)
log_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

# Log text widget
log_text = scrolledtext.ScrolledText(log_frame, height=30, width=55, 
                                    bg=REEDER_TEXT, fg=REEDER_WHITE, 
                                    font=("Consolas", 10),
                                    state='disabled', relief=tk.FLAT,
                                    insertbackground=REEDER_GREEN)
log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Log renk taglerini Reeder temasına göre ayarla
log_text.tag_configure("timestamp", foreground=REEDER_GRAY)
log_text.tag_configure("error", foreground="#FF6B6B", font=("Consolas", 10, "bold"))
log_text.tag_configure("warning", foreground="#FFB74D", font=("Consolas", 10, "bold"))
log_text.tag_configure("success", foreground=REEDER_LIGHT_GREEN, font=("Consolas", 10, "bold"))
log_text.tag_configure("info", foreground="#64B5F6", font=("Consolas", 10, "bold"))
log_text.tag_configure("message", foreground=REEDER_WHITE)

# Başlangıç mesajı
log_message("═══════════════════════════════════════")
log_message(">> REEDER IMEI Sorgulama Sistemi", "INFO")
log_message(">> Developed by Enes EREN", "INFO")  
log_message("═══════════════════════════════════════")
log_message("Sistem başarıyla başlatıldı!", "SUCCESS")
log_message(">> Lütfen bir Excel dosyası seçin ve sorgulama yöntemini belirleyin")

root.mainloop()