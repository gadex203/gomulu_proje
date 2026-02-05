#!/usr/bin/env python3
"""
Dijital Metre Modülü (HC-SR04 Ultrasonik Sensör)
Web arayüzünden mesafe ölçümü için modül
"""

import time

# Raspberry Pi üzerinde çalışıp çalışmadığını kontrol et
try:
    import RPi.GPIO as GPIO
    RPI_AVAILABLE = True
except ImportError:
    RPI_AVAILABLE = False
    print("UYARI: RPi.GPIO bulunamadı. Dijital metre simülasyon modu aktif.")

# GPIO pin tanımları (BCM numaralandırma)
TRIG_PIN = 23
ECHO_PIN = 24

# Global değişkenler
is_initialized = False
is_active = True
last_distance = 0.0

# Timeout değerleri
TIMEOUT = 0.1  # 100ms timeout


def setup_sensor():
    """Ultrasonik sensörü başlat"""
    global is_initialized
    
    if not RPI_AVAILABLE:
        print("Dijital metre simülasyon modunda başlatıldı")
        is_initialized = True
        return True
    
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Pin kurulumu
        GPIO.setup(TRIG_PIN, GPIO.OUT)
        GPIO.setup(ECHO_PIN, GPIO.IN)
        
        # TRIG pinini LOW yap
        GPIO.output(TRIG_PIN, False)
        
        # Sensörün hazır olması için bekle
        time.sleep(0.5)
        
        is_initialized = True
        print("HC-SR04 Ultrasonik Sensör başlatıldı.")
        return True
        
    except Exception as e:
        print(f"Sensör başlatma hatası: {e}")
        return False


def cleanup_sensor():
    """Sensör kaynaklarını temizle"""
    global is_initialized
    
    if not RPI_AVAILABLE:
        is_initialized = False
        return
    
    try:
        GPIO.cleanup([TRIG_PIN, ECHO_PIN])
        is_initialized = False
        print("Dijital metre kaynakları temizlendi.")
    except Exception as e:
        print(f"Sensör temizleme hatası: {e}")


def measure_distance():
    """
    Ultrasonik sensör ile mesafe ölç
    
    Returns:
        float: Mesafe (cm cinsinden), hata durumunda -1
    """
    global last_distance
    
    if not is_active:
        return 0.0
    
    if not RPI_AVAILABLE or not is_initialized:
        # Simülasyon modu - rastgele mesafe
        import random
        distance = round(random.uniform(5.0, 200.0), 2)
        last_distance = distance
        return distance
    
    try:
        # TRIG pinine 10µs pulse gönder
        GPIO.output(TRIG_PIN, True)
        time.sleep(0.00001)  # 10 mikrosaniye
        GPIO.output(TRIG_PIN, False)
        
        # ECHO pininin HIGH olmasını bekle
        pulse_start = time.time()
        timeout_start = pulse_start
        
        while GPIO.input(ECHO_PIN) == 0:
            pulse_start = time.time()
            if pulse_start - timeout_start > TIMEOUT:
                print("ECHO timeout (waiting for HIGH)")
                return -1
        
        # ECHO pininin LOW olmasını bekle
        pulse_end = time.time()
        timeout_start = pulse_end
        
        while GPIO.input(ECHO_PIN) == 1:
            pulse_end = time.time()
            if pulse_end - timeout_start > TIMEOUT:
                print("ECHO timeout (waiting for LOW)")
                return -1
        
        # Süreyi hesapla
        pulse_duration = pulse_end - pulse_start
        
        # Mesafeyi hesapla (ses hızı: 34300 cm/s, gidiş-dönüş için /2)
        # distance = (time * speed) / 2
        distance = (pulse_duration * 34300) / 2
        
        # Kalibre edilmiş değer (sensöre göre ayarlanabilir)
        distance = round(distance, 2)
        
        # Menzil kontrolü (2cm - 400cm)
        if distance < 2 or distance > 400:
            print(f"Menzil aşıldı: {distance}cm")
            return -1
        
        last_distance = distance
        return distance
        
    except Exception as e:
        print(f"Mesafe ölçüm hatası: {e}")
        return -1


def get_distance():
    """Mesafe ölç ve döndür (web API için wrapper)"""
    return measure_distance()


def get_last_distance():
    """Son ölçülen mesafeyi döndür"""
    return last_distance


def set_active(active):
    """
    Sensörü aktif/pasif yap
    
    Args:
        active: True ise sensör aktif, False ise pasif
    """
    global is_active
    is_active = active
    return is_active


def is_sensor_active():
    """Sensör aktif mi?"""
    return is_active


def get_status():
    """Sensör durumunu döndür"""
    return {
        "active": is_active,
        "initialized": is_initialized,
        "last_distance": last_distance,
        "pins": {
            "trig": TRIG_PIN,
            "echo": ECHO_PIN
        }
    }


def continuous_measure(callback=None, interval=0.5, duration=None):
    """
    Sürekli ölçüm yap
    
    Args:
        callback: Her ölçümde çağrılacak fonksiyon (distance parametresi alır)
        interval: Ölçümler arası süre (saniye)
        duration: Toplam süre (saniye), None ise süresiz
    """
    start_time = time.time()
    
    while True:
        if not is_active:
            time.sleep(interval)
            continue
        
        distance = measure_distance()
        
        if callback:
            callback(distance)
        else:
            if distance >= 0:
                print(f"Mesafe: {distance} cm")
            else:
                print("Ölçüm hatası")
        
        if duration and (time.time() - start_time) >= duration:
            break
        
        time.sleep(interval)


# Modül doğrudan çalıştırılırsa test modu
if __name__ == '__main__':
    print("HC-SR04 Dijital Metre Test Modu")
    print("=" * 40)
    
    try:
        setup_sensor()
        
        print("\nMesafe ölçümü yapılıyor (Ctrl+C ile çıkış)...\n")
        
        while True:
            distance = measure_distance()
            
            if distance >= 0:
                print(f"Mesafe: {distance} cm")
            else:
                print("Ölçüm hatası veya menzil aşıldı")
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\nTest sonlandırılıyor...")
    
    finally:
        cleanup_sensor()