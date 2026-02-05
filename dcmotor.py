#!/usr/bin/env python3
"""
DC Motor Kontrol Modülü
Web arayüzünden gelen komutlarla DC motoru kontrol eder
L298N Motor Sürücü ile çalışır
"""

import time

# Raspberry Pi üzerinde çalışıp çalışmadığını kontrol et
try:
    import RPi.GPIO as GPIO
    RPI_AVAILABLE = True
except ImportError:
    RPI_AVAILABLE = False
    print("UYARI: RPi.GPIO bulunamadı. DC Motor simülasyon modu aktif.")

# GPIO pin tanımları (BCM numaralandırma)
# L298N Motor Sürücü bağlantıları
MOTOR1_IN1 = 16      # Motor 1 Giriş 1 (Yön)
MOTOR1_IN2 = 20      # Motor 1 Giriş 2 (Yön)
MOTOR1_ENA = 21      # Motor 1 Enable (PWM ile hız kontrolü)

# Global değişkenler
motor_pwm = None
is_initialized = False
current_state = "stopped"  # stopped, forward, backward
current_speed = 0          # 0-100 arası hız


def setup_motor():
    """DC Motor GPIO kurulumunu yap"""
    global motor_pwm, is_initialized
    
    if not RPI_AVAILABLE:
        print("DC Motor simülasyon modunda başlatıldı")
        is_initialized = True
        return True
    
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Motor pinlerini ayarla
        GPIO.setup(MOTOR1_IN1, GPIO.OUT)
        GPIO.setup(MOTOR1_IN2, GPIO.OUT)
        GPIO.setup(MOTOR1_ENA, GPIO.OUT)
        
        # PWM başlat (Enable pin için)
        motor_pwm = GPIO.PWM(MOTOR1_ENA, 1000)  # 1000 Hz frekans
        motor_pwm.start(0)
        
        # Motoru durdur
        GPIO.output(MOTOR1_IN1, GPIO.LOW)
        GPIO.output(MOTOR1_IN2, GPIO.LOW)
        
        is_initialized = True
        print("DC Motor GPIO kurulumu tamamlandı.")
        return True
        
    except Exception as e:
        print(f"DC Motor kurulum hatası: {e}")
        return False


def cleanup_motor():
    """DC Motor GPIO kaynaklarını temizle"""
    global motor_pwm, is_initialized
    
    if not RPI_AVAILABLE:
        is_initialized = False
        return
    
    try:
        # Önce motoru durdur
        stop()
        
        if motor_pwm:
            motor_pwm.stop()
        
        # Motor pinlerini temizle
        GPIO.cleanup([MOTOR1_IN1, MOTOR1_IN2, MOTOR1_ENA])
        is_initialized = False
        print("DC Motor kaynakları temizlendi.")
    except Exception as e:
        print(f"DC Motor temizleme hatası: {e}")


def set_speed(speed):
    """
    Motor hızını ayarla
    
    Args:
        speed: Hız değeri (0-100)
    
    Returns:
        int: Ayarlanan hız değeri
    """
    global current_speed
    
    # Hızı sınırla (0-100)
    speed = max(0, min(100, int(speed)))
    
    if RPI_AVAILABLE and motor_pwm and is_initialized:
        motor_pwm.ChangeDutyCycle(speed)
    
    current_speed = speed
    print(f"Motor hızı: %{speed}")
    return speed


def forward(speed=50):
    """
    Motoru ileri yönde çalıştır
    
    Args:
        speed: Hız değeri (0-100), varsayılan 50
    
    Returns:
        dict: Motor durumu
    """
    global current_state
    
    if RPI_AVAILABLE and is_initialized:
        GPIO.output(MOTOR1_IN1, GPIO.HIGH)
        GPIO.output(MOTOR1_IN2, GPIO.LOW)
    else:
        print("[SİMÜLASYON] Motor ileri hareket ediyor...")
    
    set_speed(speed)
    current_state = "forward"
    print(f"Motor ileri hareket ediyor (Hız: %{speed})")
    
    return get_status()


def backward(speed=50):
    """
    Motoru geri yönde çalıştır
    
    Args:
        speed: Hız değeri (0-100), varsayılan 50
    
    Returns:
        dict: Motor durumu
    """
    global current_state
    
    if RPI_AVAILABLE and is_initialized:
        GPIO.output(MOTOR1_IN1, GPIO.LOW)
        GPIO.output(MOTOR1_IN2, GPIO.HIGH)
    else:
        print("[SİMÜLASYON] Motor geri hareket ediyor...")
    
    set_speed(speed)
    current_state = "backward"
    print(f"Motor geri hareket ediyor (Hız: %{speed})")
    
    return get_status()


def stop():
    """
    Motoru durdur
    
    Returns:
        dict: Motor durumu
    """
    global current_state, current_speed
    
    if RPI_AVAILABLE and is_initialized:
        GPIO.output(MOTOR1_IN1, GPIO.LOW)
        GPIO.output(MOTOR1_IN2, GPIO.LOW)
        if motor_pwm:
            motor_pwm.ChangeDutyCycle(0)
    else:
        print("[SİMÜLASYON] Motor durduruluyor...")
    
    current_state = "stopped"
    current_speed = 0
    print("Motor durduruldu")
    
    return get_status()


def brake():
    """
    Motoru frenle (hızlı durdurma)
    
    Returns:
        dict: Motor durumu
    """
    global current_state, current_speed
    
    if RPI_AVAILABLE and is_initialized:
        # Her iki pini de HIGH yaparak frenleme
        GPIO.output(MOTOR1_IN1, GPIO.HIGH)
        GPIO.output(MOTOR1_IN2, GPIO.HIGH)
        time.sleep(0.1)
        # Sonra durdur
        GPIO.output(MOTOR1_IN1, GPIO.LOW)
        GPIO.output(MOTOR1_IN2, GPIO.LOW)
        if motor_pwm:
            motor_pwm.ChangeDutyCycle(0)
    else:
        print("[SİMÜLASYON] Motor frenleniyor...")
    
    current_state = "stopped"
    current_speed = 0
    print("Motor frenlendi")
    
    return get_status()


def get_status():
    """
    Motor durumunu döndür
    
    Returns:
        dict: Motor durum bilgileri
    """
    return {
        "state": current_state,
        "speed": current_speed,
        "is_running": current_state != "stopped",
        "direction": current_state if current_state != "stopped" else None
    }


def get_current_state():
    """Mevcut motor durumunu döndür"""
    return current_state


def get_current_speed():
    """Mevcut motor hızını döndür"""
    return current_speed


# Modül doğrudan çalıştırılırsa test modu
if __name__ == '__main__':
    print("DC Motor Test Modu")
    print("=" * 40)
    
    try:
        setup_motor()
        
        # Test hareketi
        print("\nMotor test ediliyor...")
        
        print("\n1. İleri hareket (3 saniye)...")
        forward(75)
        time.sleep(3)
        
        print("\n2. Durdur (1 saniye)...")
        stop()
        time.sleep(1)
        
        print("\n3. Geri hareket (3 saniye)...")
        backward(75)
        time.sleep(3)
        
        print("\n4. Frenle...")
        brake()
        
        print("\nTest tamamlandı.")
        
    except KeyboardInterrupt:
        print("\nTest sonlandırılıyor...")
    
    finally:
        cleanup_motor()