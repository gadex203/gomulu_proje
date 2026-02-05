# 🍓 Raspberry Pi 4 - Flask Sensör Kontrol Paneli

Raspberry Pi 4 üzerinde çalışan, HTTP tabanlı web sunucusu uygulaması. Bağlı sensörlerden gelen verileri web arayüzünde gösterir ve servo motor ile ultrasonik sensörü uzaktan kontrol etmenizi sağlar.

## 📋 Özellikler

- ✅ **Gerçek Zamanlı Sensör Verisi** - AJAX Polling ile 500ms aralıklarla güncelleme
- ✅ **Ultrasonik Mesafe Ölçümü** - HC-SR04 sensör ile mesafe ölçümü
- ✅ **Servo Motor Kontrolü** - 0°, 45°, 90°, 135°, 180° veya özel açı
- ✅ **IMU Verisi** - MPU-6050 mock verisi (gerçek entegrasyon için genişletilebilir)
- ✅ **Responsive Tasarım** - Mobil ve masaüstü uyumlu arayüz
- ✅ **Sensör Açma/Kapama** - Ultrasonik sensörü uzaktan kontrol

## 🔧 Donanım Bağlantıları

| Bileşen | Pin | GPIO |
|---------|-----|------|
| Servo Motor (Signal) | Pin 11 | GPIO 17 |
| Ultrasonik TRIG | Pin 16 | GPIO 23 |
| Ultrasonik ECHO | Pin 18 | GPIO 24 |

### Bağlantı Şeması

```
Raspberry Pi 4
    ┌─────────────────┐
    │                 │
    │  GPIO 17 ───────┼──► Servo Signal
    │  GPIO 23 ───────┼──► HC-SR04 TRIG
    │  GPIO 24 ◄──────┼─── HC-SR04 ECHO
    │                 │
    │  5V ────────────┼──► Servo VCC, HC-SR04 VCC
    │  GND ───────────┼──► Servo GND, HC-SR04 GND
    │                 │
    └─────────────────┘
```

> ⚠️ **Not:** HC-SR04'ün ECHO pini 5V çıkış verir. GPIO pinleri 3.3V toleranslıdır. Voltaj bölücü kullanmanız önerilir.

## 📁 Proje Yapısı

```
gomulu_proje/
├── app.py                  # Flask backend uygulaması
├── requirements.txt        # Python bağımlılıkları
├── README.md              # Bu dosya
├── templates/
│   └── index.html         # Web arayüzü HTML
└── static/
    ├── css/
    │   └── style.css      # Stil dosyası
    └── js/
        └── main.js        # JavaScript (AJAX Polling)
```

## 🚀 Kurulum

### 1. Raspberry Pi'de

```bash
# Projeyi klonlayın veya dosyaları kopyalayın
cd /home/pi/gomulu_proje

# Sanal ortam oluşturun (önerilir)
python3 -m venv venv
source venv/bin/activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Uygulamayı başlatın
python app.py
```

### 2. Geliştirme Ortamında (Windows/Mac/Linux)

RPi.GPIO kütüphanesi sadece Raspberry Pi'de çalışır. Geliştirme için simülasyon modu otomatik olarak aktif olur.

```bash
# Sanal ortam oluşturun
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# Flask'ı yükleyin (RPi.GPIO olmadan)
pip install Flask

# Uygulamayı başlatın
python app.py
```

## 🌐 Kullanım

1. Uygulamayı başlattıktan sonra tarayıcınızda açın:
   - **Yerel:** http://localhost:5000
   - **Ağdan:** http://[RASPBERRY_PI_IP]:5000

2. **Sensör Verileri:** Otomatik olarak 500ms'de bir güncellenir
3. **Servo Kontrol:** Butonlara tıklayarak servo açısını değiştirin
4. **Sensör Kontrolü:** "Sensörü Aç" / "Sensörü Kapat" butonları ile kontrol edin

## 🌍 Ngrok ile Uzaktan Erişim

Projeyi geliştirirken, Flask uygulamasına yerel ağ dışından erişmek için ngrok kullandım. Bu sayede Raspberry Pi'deki uygulamaya internet üzerinden herhangi bir cihazdan erişebiliyorum. 

### Adım 1: Ngrok Kurulumu

Raspberry Pi'de ngrok'u şu şekilde kurdum:

```bash
# Geçici dizine geçtim
cd /tmp

# ARM64 için ngrok'u indirdim (Raspberry Pi 4 için)
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm64.tgz

# Arşivi açtım
tar xvzf ngrok-v3-stable-linux-arm64.tgz

# Ngrok'u sistem yoluna taşıdım (her yerden erişilebilir olması için)
sudo mv ngrok /usr/local/bin

# Kurulumun başarılı olduğunu kontrol ettim
ngrok version
```


### Adım 2: Ngrok Hesabı ve Token Yapılandırması

1. [ngrok.com](https://ngrok.com) adresinden ücretsiz hesap oluşturdum
2. Giriş yaptıktan sonra Dashboard'a gittim
3. **Your Authtoken** bölümünden token'ımı kopyaladım
4. Raspberry Pi'de terminalde şu komutu çalıştırdım (token'ı kendi token'ınızla değiştirin):

```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN_BURAYA
```

Bu işlem token'ı `~/.ngrok2/ngrok.yml` dosyasına kaydeder ve ngrok'un çalışması için gereklidir.

### Adım 3: Flask Uygulamasını Başlatma

Önce Flask uygulamamı başlattım:

```bash
cd /home/pi/gomulu_proje
python app.py
```

Uygulama `http://localhost:5000` adresinde çalışmaya başladı.

### Adım 4: Ngrok Tüneli Oluşturma

Flask uygulaması çalışırken, **yeni bir terminal penceresi** açtım ve şu komutu çalıştırdım:

```bash
ngrok http 5000
```

Ngrok başladığında terminalde şuna benzer bir çıktı gördüm:

```
ngrok                                                                        

Session Status                online
Account                       [hesap adınız]
Version                       3.x.x
Region                        Europe (eu)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123-def456.ngrok-free.app -> http://localhost:5000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

**Önemli:** `Forwarding` satırındaki URL (örneğin `https://abc123-def456.ngrok-free.app`) artık uygulamanıza internet üzerinden erişim sağlayan URL'nizdir!

### Adım 5: Uygulamaya Erişim

Artık herhangi bir cihazdan (telefon, tablet, başka bir bilgisayar) bu URL'yi tarayıcıda açarak uygulamanıza erişebilirsiniz:

- **Ngrok URL:** `https://abc123-def456.ngrok-free.app`
- Bu URL'yi açtığınızda, Flask uygulamanızın ana sayfası görünecek
- Tüm sensör verileri ve kontroller bu URL üzerinden çalışacak

### Sonuç

Bu adımları tamamladıktan sonra:
- ✅ Flask uygulamanız yerel olarak `localhost:5000` adresinde çalışıyor
- ✅ Ngrok tüneli sayesinde internet üzerinden erişilebilir bir URL'niz var
- ✅ Bu URL'yi herhangi bir cihazdan açarak uygulamanıza erişebilirsiniz
- ✅ Sensör verilerini görüntüleyebilir, servo motoru kontrol edebilirsiniz

### Ek Notlar

- **Geçici URL:** Ücretsiz ngrok planında her başlatmada farklı bir URL alırsınız. Kalıcı URL için ngrok Dashboard'dan ücretsiz domain alabilirsiniz.
- **Ngrok Web Arayüzü:** `http://127.0.0.1:4040` adresinden ngrok'un web arayüzüne erişebilir, istekleri izleyebilirsiniz.
- **Güvenlik:** Ngrok URL'nizi paylaşmayın, çünkü ücretsiz plan ile herkes erişebilir. Üretim ortamında mutlaka şifre koruması ekleyin.

## 📡 API Endpoints

| Endpoint | Metod | Açıklama |
|----------|-------|----------|
| `/` | GET | Ana sayfa (Web UI) |
| `/api/data` | GET | Tüm sensör verilerini döndür |
| `/api/sensor/on` | POST | Ultrasonik sensörü aktif et |
| `/api/sensor/off` | POST | Ultrasonik sensörü kapat |
| `/api/servo/move` | POST | Servo açısını değiştir |
| `/api/status` | GET | Sistem durumunu döndür |






## ⚙️ Konfigürasyon

`app.py` dosyasındaki pin tanımlarını düzenleyebilirsiniz:

```python
SERVO_PIN = 17          # Servo motor GPIO pini
TRIG_PIN = 23           # Ultrasonik sensör TRIG pini
ECHO_PIN = 24           # Ultrasonik sensör ECHO pini
```

## 📱 Ekran Görüntüleri

Web arayüzü şu bileşenleri içerir:

1. **Ultrasonik Sensör Kartı** - Mesafe değeri ve sensör durumu
2. **IMU Sensör Kartı** - İvme ve gyro değerleri
3. **Servo Kontrol Kartı** - Açı butonları ve özel açı girişi
4. **Sistem Durumu** - Bağlantı ve son güncelleme bilgisi



## 📄 Lisans

Bu proje eğitim amaçlı geliştirilmiştir.

---

