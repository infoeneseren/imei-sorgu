import os
import time
import pandas as pd
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from twocaptcha import TwoCaptcha
import requests
import base64

# 2Captcha API Key
API_KEY = os.getenv('APIKEY_2CAPTCHA', 'YOUR-API-KEY')
solver = TwoCaptcha(API_KEY)

# ApiTrueCaptcha bilgileri
APITRUECAPTCHA_USERID = "enese111905@gmail.com"
APITRUECAPTCHA_APIKEY = "RLDPgk9bM9Ggq5k82Fnv"

def solve_captcha_with_apitruecaptcha(image_path):
    """ApiTrueCaptcha servisi ile captcha çöz"""
    try:
        # Resmi base64'e çevir
        with open(image_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # API'ye istek gönder
        url = "https://api.apitruecaptcha.org/one/gettext"
        payload = {
            "userid": APITRUECAPTCHA_USERID,
            "apikey": APITRUECAPTCHA_APIKEY,
            "data": image_data,
            "case": "mixed",
            "numeric": False,
            "len_str": 5
        }
        
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'result' in result:
                return result['result']
        
        return None
    except Exception as e:
        print(f"ApiTrueCaptcha hatası: {e}")
        return None

def solve_captcha(image_path):
    """Captcha çözme fonksiyonu - önce 2Captcha, sonra ApiTrueCaptcha"""
    # Önce 2Captcha dene
    if API_KEY and API_KEY != 'YOUR-API-KEY':
        try:
            result = solver.normal(image_path)
            if result and 'code' in result:
                return result['code']
        except Exception as e:
            print(f"2Captcha hatası: {e}")
    
    # 2Captcha çalışmazsa ApiTrueCaptcha dene
    result = solve_captcha_with_apitruecaptcha(image_path)
    if result:
        return result
    
    # Her ikisi de çalışmazsa None döndür
    return None

# Tarayıcı ayarları (headless - görünmeden çalışacak)
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_argument('--headless')  # Tarayıcıyı gizli çalıştır
options.add_argument('--disable-gpu')  # Bazı sistemlerde gerekebilir
options.add_argument('--no-sandbox')   # Bazı Linux sistemlerinde gerekebilir

# tkinter pencere
root = tk.Tk()
root.title("Toplu IMEI Sorgulama")

# Excel dosyası yolu
file_path = ''

# Fonksiyon: Dosya seç
def select_file():
    global file_path
    file_path = filedialog.askopenfilename(filetypes=[("Excel Dosyası", "*.xlsx")])
    if file_path:
        lbl_file.config(text=f"Seçilen dosya: {os.path.basename(file_path)}")

# Fonksiyon: Sorgulamayı başlat
def start_query():
    if not file_path:
        messagebox.showerror("Hata", "Lütfen bir Excel dosyası seçin.")
        return

    try:
        imei_list = pd.read_excel(file_path)['IMEI'].dropna().tolist()
    except Exception as e:
        messagebox.showerror("Hata", f"Excel dosyasından IMEI okunamadı: {e}")
        return

    if not imei_list:
        messagebox.showerror("Hata", "Excel dosyasında IMEI bulunamadı.")
        return

    # Progress bar ayarları
    progress_bar['maximum'] = len(imei_list)
    progress_bar['value'] = 0

    results = []

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    for idx, imei_number in enumerate(imei_list, start=1):
        status_label.config(text=f"{imei_number} sorgulanıyor...")
        root.update_idletasks()

        try:
            driver.get('https://www.turkiye.gov.tr/imei-sorgulama')
            time.sleep(2)

            captcha_elements = driver.find_elements(By.CLASS_NAME, 'captchaImage')

            if captcha_elements:
                captcha_path = 'captcha.png'
                captcha_elements[0].screenshot(captcha_path)

                # Yeni captcha çözme fonksiyonunu kullan
                captcha_code = solve_captcha(captcha_path)
                
                if not captcha_code:
                    raise Exception("Captcha çözülemedi")

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

            results.append({
                'IMEI': imei_result,
                'Durum': durum,
                'Kaynak': kaynak,
                'Sorgu Tarihi': sorgu_tarihi,
                'Marka/Model': marka_model
            })

        except Exception as e:
            results.append({
                'IMEI': imei_number,
                'Durum': f"Hata: {e}",
                'Kaynak': '',
                'Sorgu Tarihi': '',
                'Marka/Model': ''
            })

        # Progress bar ilerlet
        progress_bar['value'] += 1
        root.update_idletasks()

    driver.quit()

    # Sorgu bitince kayıt yeri seçtir
    save_path = filedialog.asksaveasfilename(defaultextension='.xlsx',
                                             filetypes=[("Excel Dosyası", "*.xlsx")],
                                             title="Sonuçları Kaydet")

    if save_path:
        df = pd.DataFrame(results)
        df.to_excel(save_path, index=False)
        messagebox.showinfo("Tamamlandı", f"Sorgulamalar bitti! Sonuçlar kaydedildi:\n{save_path}")
    else:
        messagebox.showinfo("Bilgi", "Sonuçlar kaydedilmedi.")

# Arayüz elemanları
frame = tk.Frame(root, padx=20, pady=20)
frame.pack()

btn_select = tk.Button(frame, text="IMEI Listesini Seç", command=select_file)
btn_select.pack(pady=5)

lbl_file = tk.Label(frame, text="Henüz dosya seçilmedi.")
lbl_file.pack(pady=5)

btn_start = tk.Button(frame, text="Sorgulamayı Başlat", command=start_query)
btn_start.pack(pady=10)

progress_bar = ttk.Progressbar(frame, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(pady=10)

status_label = tk.Label(frame, text="Durum: Bekleniyor.")
status_label.pack(pady=5)

root.mainloop()