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

# 2Captcha API Key
API_KEY = os.getenv('APIKEY_2CAPTCHA', 'YOUR-API-KEY')
solver = TwoCaptcha(API_KEY)

# Tarayıcı ayarları
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

# Fonksiyon: Proxy üzerinden sorgu yap
def query_via_proxy(driver, imei_number, retry_count=0):
    max_retries = 3
    
    try:
        # Croxyproxy'ye git
        driver.get('https://www.croxyproxy.com')
        time.sleep(2)
        
        # URL input alanını bul ve türkiye.gov.tr URL'sini yaz
        url_input = driver.find_element(By.XPATH, '//*[@id="url"]')
        url_input.clear()
        url_input.send_keys('https://www.turkiye.gov.tr/imei-sorgulama')
        
        # Submit butonuna tıkla
        submit_button = driver.find_element(By.XPATH, '//*[@id="requestSubmit"]')
        submit_button.click()
        
        time.sleep(3)
        
        # IMEI input alanını bul ve IMEI'yi yaz
        imei_input = driver.find_element(By.ID, 'txtImei')
        imei_input.clear()
        imei_input.send_keys(imei_number)
        
        # Sorgula butonunu bul ve tıkla
        sorgula_button = driver.find_element(By.CLASS_NAME, 'submitButton')
        sorgula_button.click()
        
        time.sleep(3)
        
        # Captcha kontrolü yap
        captcha_elements = driver.find_elements(By.CLASS_NAME, 'captchaImage')
        
        if captcha_elements and retry_count < max_retries:
            # Captcha varsa tekrar proxy'ye git
            return query_via_proxy(driver, imei_number, retry_count + 1)
        
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
        if retry_count < max_retries:
            time.sleep(2)
            return query_via_proxy(driver, imei_number, retry_count + 1)
        else:
            return {
                'IMEI': imei_number,
                'Durum': f"Hata: {e}",
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

# Fonksiyon: Sorgulamayı başlat
def start_query():
    if not file_path:
        messagebox.showerror("Hata", "Lütfen bir Excel dosyası seçin.")
        return
    
    # Seçilen yöntemi kontrol et
    selected_method = method_var.get()
    if selected_method == 0:
        messagebox.showerror("Hata", "Lütfen bir sorgulama yöntemi seçin.")
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

        if selected_method == 1:  # 2Captcha
            result = query_with_2captcha(driver, imei_number)
        else:  # Proxy Site
            result = query_via_proxy(driver, imei_number)
        
        results.append(result)

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

# Yöntem seçimi
method_frame = tk.Frame(frame)
method_frame.pack(pady=10)

tk.Label(method_frame, text="Sorgulama Yöntemi Seçin:", font=("Arial", 12, "bold")).pack()

method_var = tk.IntVar()

radio1 = tk.Radiobutton(method_frame, text="2Captcha Kullan (API Key Gerekli)", 
                       variable=method_var, value=1)
radio1.pack(anchor="w", padx=20)

radio2 = tk.Radiobutton(method_frame, text="Proxy Site Kullan (CroxyProxy)", 
                       variable=method_var, value=2)
radio2.pack(anchor="w", padx=20)

# Dosya seçme
btn_select = tk.Button(frame, text="IMEI Listesini Seç", command=select_file)
btn_select.pack(pady=10)

lbl_file = tk.Label(frame, text="Henüz dosya seçilmedi.")
lbl_file.pack(pady=5)

btn_start = tk.Button(frame, text="Sorgulamayı Başlat", command=start_query)
btn_start.pack(pady=10)

progress_bar = ttk.Progressbar(frame, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(pady=10)

status_label = tk.Label(frame, text="Durum: Bekleniyor.")
status_label.pack(pady=5)

root.mainloop()