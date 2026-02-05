#!/usr/bin/env python3
"""
Servo Motor Kontrol Modülü
Web arayüzünden gelen komutlarla servo motoru kontrol eder
"""

import time

# Raspberry Pi üzerinde çalışıp çalışmadığını kontrol et
try:
    import RPi.GPIO as GPIO
    RPI_AVAILABLE = True
except ImportError:
    RPI_AVAILABLE = False
    print("UYARI: RPi.GPIO bulunamadı. Servo simülasyon modu aktif.")

# GPIO pin tanımları
SERVO_PIN = 18
BUTTON_PIN = 25  # Opsiyonel: Manuel kontrol butonu (dijital_metre ile çakışma önlendi)
LED_PIN = 12     # Opsiyonel: Durum LED'i (dijital_metre ile çakışma önlendi)

# Global değişkenler
servo_pwm = None
current_angle = 90  # Mevcut servo açısı
is_initialized = False


def setup_servo():
    """Servo motor GPIO kurulumunu yap"""
    global servo_pwm, is_initialized
    
    if not RPI_AVAILABLE:
        print("Servo simülasyon modunda başlatıldı")
        is_initialized = True
        return True
    
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Servo motor pini (PWM çıkışı)
        GPIO.setup(SERVO_PIN, GPIO.OUT)
        servo_pwm = GPIO.PWM(SERVO_PIN, 50)  # 50 Hz frekans
        servo_pwm.start(0)
        
        # Opsiyonel: Buton ve LED pinleri
        GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(LED_PIN, GPIO.OUT)
        GPIO.output(LED_PIN, GPIO.LOW)
        
        is_initialized = True
        print("Servo GPIO kurulumu tamamlandı.")
        return True
        
    except Exception as e:
        print(f"Servo kurulum hatası: {e}")
        return False


def cleanup_servo():
    """Servo GPIO kaynaklarını temizle"""
    global servo_pwm, is_initialized
    
    if not RPI_AVAILABLE:
        is_initialized = False
        return
    
    try:
        if servo_pwm:
            servo_pwm.stop()
        # Sadece servo ile ilgili pinleri temizle
        GPIO.cleanup([SERVO_PIN, BUTTON_PIN, LED_PIN])
        is_initialized = False
        print("Servo kaynakları temizlendi.")
    except Exception as e:
        print(f"Servo temizleme hatası: {e}")


def angle_to_duty_cycle(angle):
    """
    Açıyı duty cycle değerine çevir
    0-180 derece -> 2-12% duty cycle (yaklaşık)
    """
    return 2 + (angle / 18)


def set_angle(angle):
    """
    Servo motoru belirtilen açıya getir
    
    Args:
        angle: Hedef açı (0-180 derece)
    
    Returns:
        int: Gerçekleştirilen açı değeri
    """
    global current_angle
    
    # Açıyı sınırla (0-180)
    angle = max(0, min(180, int(angle)))
    
    if RPI_AVAILABLE and servo_pwm and is_initialized:
        try:
            duty = angle_to_duty_cycle(angle)
            servo_pwm.ChangeDutyCycle(duty)
            time.sleep(0.5)  # Servo'nun hareket etmesi için bekle
            servo_pwm.ChangeDutyCycle(0)  # Titreşimi önle
            
            # LED ile göster (opsiyonel)
            if angle > 0:
                GPIO.output(LED_PIN, GPIO.HIGH)
            else:
                GPIO.output(LED_PIN, GPIO.LOW)
                
        except Exception as e:
            print(f"Servo hareket hatası: {e}")
    else:
        # Simülasyon modu
        print(f"[SİMÜLASYON] Servo {angle}° konumuna hareket ediyor...")
        time.sleep(0.3)
    
    current_angle = angle
    print(f"Servo açısı: {angle}°")
    return angle


def get_current_angle():
    """Mevcut servo açısını döndür"""
    return current_angle


def move_to_position(position):
    """
    Önceden tanımlı pozisyonlara hareket et
    
    Args:
        position: 'min', 'center', 'max' veya açı değeri
    
    Returns:
        int: Gerçekleştirilen açı değeri
    """
    positions = {
        'min': 0,
        'center': 90,
        'max': 180,
        'left': 0,
        'middle': 90,
        'right': 180
    }
    
    if isinstance(position, str) and position.lower() in positions:
        return set_angle(positions[position.lower()])
    elif isinstance(position, (int, float)):
        return set_angle(int(position))
    else:
        print(f"Geçersiz pozisyon: {position}")
        return current_angle


def sweep(start=0, end=180, step=10, delay=0.1):
    """
    Servo'yu belirtilen aralıkta süpür
    
    Args:
        start: Başlangıç açısı
        end: Bitiş açısı
        step: Adım büyüklüğü
        delay: Her adım arası bekleme (saniye)
    """
    if start < end:
        angles = range(start, end + 1, step)
    else:
        angles = range(start, end - 1, -step)
    
    for angle in angles:
        set_angle(angle)
        time.sleep(delay)
    
    return current_angle


def check_button():
    """
    Fiziksel butonu kontrol et
    
    Returns:
        bool: Butona basılıysa True
    """
    if not RPI_AVAILABLE or not is_initialized:
        return False
    
    try:
        return GPIO.input(BUTTON_PIN) == GPIO.HIGH
    except:
        return False


# Modül doğrudan çalıştırılırsa test modu
if __name__ == '__main__':
    print("Servo Motor Test Modu")
    print("=" * 40)
    
    try:
        setup_servo()
        
        # Test hareketi
        print("\nServo test ediliyor...")
        set_angle(0)
        time.sleep(1)
        set_angle(90)
        time.sleep(1)
        set_angle(180)
        time.sleep(1)
        set_angle(90)
        
        # Buton kontrolü (opsiyonel)
        print("\nButon kontrolü test ediliyor (5 saniye)...")
        for i in range(50):
            if check_button():
                print("Butona basıldı!")
                set_angle(180)
            time.sleep(0.1)
        
        print("\nTest tamamlandı.")
        
    except KeyboardInterrupt:
        print("\nTest sonlandırılıyor...")
    
    finally:
        cleanup_servo()