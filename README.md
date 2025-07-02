# 📱 REEDER Toplu IMEI Sorgulama Sistemi

**Geliştirici:** Enes EREN  
**Marka:** Reeder  
**Versiyon:** 1.0.0  

---

## 📋 İçindekiler

- [Genel Bakış](#genel-bakış)
- [Özellikler](#özellikler)
- [Sistem Gereksinimleri](#sistem-gereksinimleri)
- [Kurulum](#kurulum)
- [Excel Dosyası Hazırlama](#excel-dosyası-hazırlama)
- [Kullanım Kılavuzu](#kullanım-kılavuzu)
- [Sorgulama Yöntemleri](#sorgulama-yöntemleri)
- [Hata Giderme](#hata-giderme)
- [Sık Sorulan Sorular](#sık-sorulan-sorular)
- [Teknik Detaylar](#teknik-detaylar)

---

## 🎯 Genel Bakış

REEDER Toplu IMEI Sorgulama Sistemi, Türkiye.gov.tr üzerinden toplu IMEI sorgulaması yapmanızı sağlayan profesyonel bir masaüstü uygulamasıdır. Enes EREN tarafından Reeder markası için özel olarak geliştirilmiştir.

Bu uygulama ile:
- ✅ Tek seferde yüzlerce IMEI sorgulayabilirsiniz
- ✅ İki farklı sorgulama yöntemi kullanabilirsiniz
- ✅ Canlı log takibi yapabilirsiniz
- ✅ Sonuçları Excel formatında kaydedebilirsiniz
- ✅ Modern ve kullanıcı dostu arayüze sahiptir

---

## ⭐ Özellikler

### 🔧 Temel Özellikler
- **Toplu IMEI Sorgulama**: Bir Excel dosyasından yüzlerce IMEI'yi otomatik sorgular
- **İki Sorgulama Yöntemi**: 2Captcha API veya Proxy Site yöntemi
- **Canlı İzleme**: Gerçek zamanlı log paneli ile işlem takibi
- **Otomatik Hata Yönetimi**: Teknik aksaklıklarda otomatik yeniden deneme
- **İlerleme Çubuğu**: Görsel ilerleme takibi
- **Excel Çıktı**: Sonuçları detaylı Excel dosyası olarak kaydetme

### 🎨 Kullanıcı Arayüzü
- **Reeder Teması**: Markanın yeşil renk paleti ile tasarlanmış modern arayüz
- **Kullanıcı Dostu**: Basit ve anlaşılır kontroller
- **Durdurma/Başlatma**: İstediğiniz zaman işlemi durdurup başlatabilirsiniz
- **Renkli Loglar**: Hata, başarı, uyarı mesajları farklı renklerle gösterilir

---

## 💻 Sistem Gereksinimleri

- **İşletim Sistemi**: Windows 10/11, macOS 10.14+, Linux Ubuntu 18.04+
- **RAM**: En az 4 GB (8 GB önerilir)
- **İnternet Bağlantısı**: Stabil internet bağlantısı gereklidir
- **Python**: 3.7 veya üzeri (sadece kaynak koddan çalıştırıyorsanız)

---

## 🚀 Kurulum

### 1. Hazır EXE Dosyası (Önerilen)
1. `Reeder_IMEI_Sorgulama.exe` dosyasını indirin
2. Dosyayı istediğiniz klasöre kopyalayın
3. Logo dosyalarını (`logo.ico`, `app.ico`) aynı klasöre koyun
4. Çift tıklayarak uygulamayı başlatın

### 2. Kaynak Koddan Çalıştırma
```bash
# Gerekli kütüphaneleri yükleyin
pip install -r requirements.txt

# Uygulamayı başlatın
python toplu.py
```

---

## 📊 Excel Dosyası Hazırlama

### ✅ Doğru Format
Excel dosyanız **mutlaka** aşağıdaki şekilde hazırlanmalıdır:

| IMEI              |
|-------------------|
| 123456789012345   |
| 987654321098765   |
| 456789123456789   |
| 789123456789123   |

### 📋 Önemli Kurallar
1. **Sütun Adı**: İlk satırdaki sütun adı mutlaka `IMEI` olmalıdır
2. **Veri Formatı**: IMEI'ler sayı formatında olmalıdır (metin olarak da kabul edilir)
3. **Boş Satırlar**: Boş IMEI satırları otomatik olarak atlanır
4. **Dosya Uzantısı**: `.xlsx` formatında olmalıdır (Excel 2007+)

### ❌ Yanlış Formatlar
```
# YANLIŞ - Sütun adı farklı
| IMEI_NO          |
| IMEI_NUMARASI    |
| Imei             |

# YANLIŞ - Birden fazla sütun
| IMEI              | Marka    |
| 123456789012345   | Samsung  |

# YANLIŞ - Başlık yok
| 123456789012345   |
| 987654321098765   |
```

---

## 📖 Kullanım Kılavuzu

### 1. Uygulamayı Başlatın
- `Reeder_IMEI_Sorgulama.exe` dosyasını çift tıklayın
- Reeder logolu ana ekran açılacaktır

### 2. Sorgulama Yöntemini Seçin
**Seçenek 1: 2Captcha Kullan**
- API key gerektirir
- Daha hızlı çalışır
- Gizli modda (headless) çalışır

**Seçenek 2: Proxy Site Kullan**
- API key gerektirmez (ÜCRETSİZ)
- Biraz daha yavaş
- Görünür modda çalışır

### 3. Excel Dosyasını Seçin
- "IMEI Listesini Seç" butonuna tıklayın
- Hazırladığınız Excel dosyasını seçin
- Dosya adı alt kısımda görünecektir

### 4. Sorgulamayı Başlatın
- "▶ Sorgulamayı Başlat" butonuna tıklayın
- Sağ panelde canlı logları izleyebilirsiniz
- İlerleme çubuğu mevcut durumu gösterecektir

### 5. Sonuçları Kaydedin
- Sorgulama bittiğinde kaydetme penceresi açılacaktır
- Dosya adını ve konumunu seçin
- Sonuçlar Excel formatında kaydedilecektir

---

## 🔄 Sorgulama Yöntemleri

### 🤖 2Captcha Yöntemi
```
Avantajları:
✅ Daha hızlı işlem
✅ Gizli modda çalışır
✅ Daha az sistem kaynağı kullanır

Dezavantajları:
❌ API key gerektirir (ücretli)
❌ 2Captcha hesabı açmanız gerekir
```

**2Captcha API Key Alma:**
1. [2captcha.com](https://2captcha.com) sitesine kayıt olun
2. Hesabınıza kredi yükleyin
3. API key'inizi alın
4. `toplu.py` dosyasında `API_KEY` değişkenini güncelleyin

### 🌐 Proxy Site Yöntemi (ÜCRETSİZ)
```
Avantajları:
✅ Tamamen ücretsiz
✅ API key gerektirmez
✅ Kurulum gerektirmez

Dezavantajları:
❌ Biraz daha yavaş
❌ Görünür modda çalışır
❌ Captcha durumunda yeni sekme açar
```

**Otomatik Özellikler:**
- Teknik aksaklık durumunda otomatik yeniden deneme
- Captcha tespit edildiğinde yeni sekme açma
- 5 kez deneme sonrası hata bildirimi

---

## 📤 Çıktı Formatı

Sorgulama tamamlandığında aşağıdaki sütunları içeren Excel dosyası oluşturulur:

| Sütun Adı      | Açıklama                           |
|----------------|-----------------------------------|
| IMEI           | Sorgulanan IMEI numarası         |
| Durum          | Cihazın kayıt durumu             |
| Kaynak         | Bilgi kaynağı                    |
| Sorgu Tarihi   | Sorgunun yapıldığı tarih         |
| Marka/Model    | Cihazın marka ve model bilgisi   |

### Örnek Çıktı:
| IMEI              | Durum           | Kaynak | Sorgu Tarihi | Marka/Model        |
|-------------------|----------------|--------|-------------|-------------------|
| 123456789012345   | Kayıtlı        | BTK    | 15.01.2024  | Samsung Galaxy S21 |
| 987654321098765   | Kayıtsız       | BTK    | 15.01.2024  | iPhone 13 Pro     |

---

## 🛠 Hata Giderme

### Sık Karşılaşılan Hatalar

**1. "Excel dosyasından IMEI okunamadı"**
```
Çözüm:
- Excel dosyasının .xlsx formatında olduğundan emin olun
- İlk sütun adının "IMEI" olduğunu kontrol edin
- Dosyada IMEI verisi olduğundan emin olun
```

**2. "Lütfen bir sorgulama yöntemi seçin"**
```
Çözüm:
- Sol panelden bir yöntem seçin (2Captcha veya Proxy Site)
- Radio button'lardan birini işaretleyin
```

**3. "Chrome başlatılamıyor"**
```
Çözüm:
- Chrome tarayıcısının güncel olduğundan emin olun
- Antivirüs programını geçici olarak devre dışı bırakın
- Uygulamayı yönetici olarak çalıştırın
```

**4. "İkon dosyası bulunamadı"**
```
Çözüm:
- logo.ico dosyasının uygulama ile aynı klasörde olduğundan emin olun
- Dosya adının tam olarak "logo.ico" olduğunu kontrol edin
```

### Log Renklerinin Anlamı

| Renk    | Anlamı          | Örnek Mesaj                    |
|---------|-----------------|-------------------------------|
| 🔵 Mavi  | Bilgi           | "2Captcha yöntemi seçildi"    |
| 🟢 Yeşil | Başarı          | "IMEI başarıyla sorgulandı"   |
| 🟡 Sarı  | Uyarı           | "Captcha tespit edildi"       |
| 🔴 Kırmızı | Hata          | "Max deneme sayısına ulaşıldı" |

---

## ❓ Sık Sorulan Sorular

**S: Kaç IMEI sorgulayabilirim?**
C: Sınır yoktur. Yüzlerce hatta binlerce IMEI sorgulayabilirsiniz.

**S: 2Captcha ücretli mi?**
C: Evet, 2Captcha ücretli bir servistir. Ancak Proxy Site yöntemi tamamen ücretsizdir.

**S: Sorgulamayı durdurabilir miyim?**
C: Evet, "Sorgulamayı Durdur" butonuna tıklayarak istediğiniz zaman durdurabilirsiniz.

**S: İnternet bağlantım kesilirse ne olur?**
C: Uygulama hata verecektir. İnternet bağlantınızı kontrol edip tekrar başlatın.

**S: Sonuçlar nereye kaydediliyor?**
C: Sorgulama bittiğinde sizden kaydetme konumu istenir. İstediğiniz yere kaydedebilirsiniz.

**S: Excel dosyam çok büyükse ne olur?**
C: Problem yoktur. Uygulama büyük dosyalarla da çalışır. Sadece işlem süresi uzar.

---

## 🔧 Teknik Detaylar

### Kullanılan Teknolojiler
- **Python 3.7+**: Ana programlama dili
- **Selenium WebDriver**: Web otomasyonu
- **Tkinter**: Grafik kullanıcı arayüzü
- **Pandas**: Excel dosyası işlemleri
- **Threading**: Çoklu işlem desteği
- **2Captcha API**: Captcha çözme servisi

### Güvenlik Özellikleri
- Bot tespitini engelleyen özel Chrome ayarları
- Proxy rotasyonu desteği
- Otomatik retry mekanizması
- Log temizleme özellikleri

### Performans Optimizasyonları
- Dinamik headless/visible mod
- WebDriverWait ile akıllı bekleme
- Gereksiz resource yüklemesini engelleme
- Bellek kullanımı optimizasyonu

---

## 📞 Destek ve İletişim

**Geliştirici:** Enes EREN  
**Marka:** Reeder  
**Versiyon:** 1.0.0  

Bu uygulama Reeder markası için özel olarak Enes EREN tarafından geliştirilmiştir.

---

## 📄 Lisans

Bu yazılım Reeder markası için özel olarak geliştirilmiştir. Ticari kullanım için Enes EREN ile iletişime geçiniz.

---

**Son Güncelleme:** Ocak 2024  
**Geliştirici:** Enes EREN  
**© 2024 Reeder - Tüm hakları saklıdır.** 
