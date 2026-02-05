#!/usr/bin/env python3
"""
IMU Sensör Modülü (MPU-6050)
Web arayüzünden IMU verilerini okumak için modül
I2C üzerinden MPU-6050 ile iletişim kurar
"""

import math
import time

# Raspberry Pi üzerinde çalışıp çalışmadığını kontrol et
try:
    import smbus
    SMBUS_AVAILABLE = True
except ImportError:
    SMBUS_AVAILABLE = False
    print("UYARI: smbus bulunamadı. IMU simülasyon modu aktif.")

# MPU-6050 I2C Adresi ve Register'lar
MPU6050_ADDR = 0x68
POWER_MGMT_1 = 0x6B
POWER_MGMT_2 = 0x6C

# Gyroscope register'ları
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47

# Accelerometer register'ları
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F

# Global değişkenler
bus = None
is_initialized = False

# Son okunan değerler (cache)
last_reading = {
    "accel_x": 0.0,
    "accel_y": 0.0,
    "accel_z": 9.81,
    "gyro_x": 0.0,
    "gyro_y": 0.0,
    "gyro_z": 0.0,
    "rotation_x": 0.0,
    "rotation_y": 0.0,
    "temperature": 25.0
}


def setup_imu():
    """IMU sensörünü başlat"""
    global bus, is_initialized
    
    if not SMBUS_AVAILABLE:
        print("IMU simülasyon modunda başlatıldı")
        is_initialized = True
        return True
    
    try:
        # I2C bus'ı aç (Raspberry Pi'de genellikle bus 1)
        bus = smbus.SMBus(1)
        
        # MPU-6050'yi uyandır (sleep modundan çıkar)
        bus.write_byte_data(MPU6050_ADDR, POWER_MGMT_1, 0)
        
        time.sleep(0.1)  # Başlatma için bekle
        
        is_initialized = True
        print("IMU (MPU-6050) başlatıldı.")
        return True
        
    except Exception as e:
        print(f"IMU başlatma hatası: {e}")
        print("IMU simülasyon moduna geçiliyor...")
        is_initialized = True  # Simülasyon modunda devam et
        return False


def cleanup_imu():
    """IMU kaynaklarını temizle"""
    global bus, is_initialized
    
    if bus:
        try:
            bus.close()
        except:
            pass
    
    is_initialized = False
    print("IMU kaynakları temizlendi.")


def read_byte(register):
    """Tek byte oku"""
    if not SMBUS_AVAILABLE or not bus:
        return 0
    return bus.read_byte_data(MPU6050_ADDR, register)


def read_word(register):
    """16-bit word oku (big-endian)"""
    if not SMBUS_AVAILABLE or not bus:
        return 0
    high = bus.read_byte_data(MPU6050_ADDR, register)
    low = bus.read_byte_data(MPU6050_ADDR, register + 1)
    return (high << 8) + low


def read_word_2c(register):
    """16-bit signed word oku (2's complement)"""
    val = read_word(register)
    if val >= 0x8000:
        return -((65535 - val) + 1)
    return val


def dist(a, b):
    """İki değerin Öklid mesafesi"""
    return math.sqrt((a * a) + (b * b))


def get_x_rotation(x, y, z):
    """X ekseni etrafındaki rotasyonu hesapla (derece)"""
    radians = math.atan2(x, dist(y, z))
    return -math.degrees(radians)


def get_y_rotation(x, y, z):
    """Y ekseni etrafındaki rotasyonu hesapla (derece)"""
    radians = math.atan2(y, dist(x, z))
    return math.degrees(radians)


def read_gyroscope():
    """
    Gyroscope değerlerini oku
    
    Returns:
        dict: x, y, z gyro değerleri (derece/saniye)
    """
    if not SMBUS_AVAILABLE or not bus or not is_initialized:
        # Simülasyon modu - rastgele değerler
        import random
        return {
            "x": round(random.uniform(-1, 1), 2),
            "y": round(random.uniform(-1, 1), 2),
            "z": round(random.uniform(-1, 1), 2)
        }
    
    try:
        # Ham gyro verilerini oku
        gyro_x = read_word_2c(GYRO_XOUT_H)
        gyro_y = read_word_2c(GYRO_YOUT_H)
        gyro_z = read_word_2c(GYRO_ZOUT_H)
        
        # Ölçekleme (±250°/s için 131 LSB/°/s)
        return {
            "x": round(gyro_x / 131.0, 2),
            "y": round(gyro_y / 131.0, 2),
            "z": round(gyro_z / 131.0, 2)
        }
    except Exception as e:
        print(f"Gyro okuma hatası: {e}")
        return {"x": 0.0, "y": 0.0, "z": 0.0}


def read_accelerometer():
    """
    Accelerometer değerlerini oku
    
    Returns:
        dict: x, y, z ivme değerleri (g cinsinden)
    """
    if not SMBUS_AVAILABLE or not bus or not is_initialized:
        # Simülasyon modu - mock değerler
        import random
        return {
            "x": round(random.uniform(-0.1, 0.1), 3),
            "y": round(random.uniform(-0.1, 0.1), 3),
            "z": round(1.0 + random.uniform(-0.05, 0.05), 3)  # ~1g (yerçekimi)
        }
    
    try:
        # Ham ivme verilerini oku
        accel_x = read_word_2c(ACCEL_XOUT_H)
        accel_y = read_word_2c(ACCEL_YOUT_H)
        accel_z = read_word_2c(ACCEL_ZOUT_H)
        
        # Ölçekleme (±2g için 16384 LSB/g)
        return {
            "x": round(accel_x / 16384.0, 3),
            "y": round(accel_y / 16384.0, 3),
            "z": round(accel_z / 16384.0, 3)
        }
    except Exception as e:
        print(f"İvme okuma hatası: {e}")
        return {"x": 0.0, "y": 0.0, "z": 1.0}


def read_all():
    """
    Tüm IMU verilerini oku
    
    Returns:
        dict: Tüm sensör verileri
    """
    global last_reading
    
    # İvme verilerini oku
    accel = read_accelerometer()
    
    # Gyro verilerini oku
    gyro = read_gyroscope()
    
    # Rotasyon açılarını hesapla
    rotation_x = get_x_rotation(accel["x"], accel["y"], accel["z"])
    rotation_y = get_y_rotation(accel["x"], accel["y"], accel["z"])
    
    # Son okumayı güncelle
    last_reading = {
        "accel_x": accel["x"],
        "accel_y": accel["y"],
        "accel_z": accel["z"],
        "gyro_x": gyro["x"],
        "gyro_y": gyro["y"],
        "gyro_z": gyro["z"],
        "rotation_x": round(rotation_x, 2),
        "rotation_y": round(rotation_y, 2)
    }
    
    return last_reading


def get_imu_data():
    """
    Web API için IMU verisi döndür
    
    Returns:
        dict: IMU verileri (m/s² cinsinden ivme)
    """
    data = read_all()
    
    # g'den m/s²'ye çevir (1g = 9.81 m/s²)
    return {
        "accel_x": round(data["accel_x"] * 9.81, 3),
        "accel_y": round(data["accel_y"] * 9.81, 3),
        "accel_z": round(data["accel_z"] * 9.81, 3),
        "gyro_x": data["gyro_x"],
        "gyro_y": data["gyro_y"],
        "gyro_z": data["gyro_z"],
        "rotation_x": data["rotation_x"],
        "rotation_y": data["rotation_y"]
    }


def get_last_reading():
    """Son okunan değerleri döndür"""
    return last_reading


def calibrate():
    """
    IMU'yu kalibre et (basit offset kalibrasyonu)
    Not: Gerçek kalibrasyonda daha gelişmiş yöntemler kullanılmalı
    """
    if not is_initialized:
        return False
    
    print("IMU kalibrasyonu başlıyor...")
    print("Sensörü düz ve hareketsiz tutun...")
    
    samples = 100
    accel_sum = {"x": 0, "y": 0, "z": 0}
    gyro_sum = {"x": 0, "y": 0, "z": 0}
    
    for i in range(samples):
        accel = read_accelerometer()
        gyro = read_gyroscope()
        
        accel_sum["x"] += accel["x"]
        accel_sum["y"] += accel["y"]
        accel_sum["z"] += accel["z"]
        
        gyro_sum["x"] += gyro["x"]
        gyro_sum["y"] += gyro["y"]
        gyro_sum["z"] += gyro["z"]
        
        time.sleep(0.01)
    
    # Ortalama offset değerlerini hesapla
    accel_offset = {
        "x": accel_sum["x"] / samples,
        "y": accel_sum["y"] / samples,
        "z": (accel_sum["z"] / samples) - 1.0  # Z'de 1g bekliyoruz
    }
    
    gyro_offset = {
        "x": gyro_sum["x"] / samples,
        "y": gyro_sum["y"] / samples,
        "z": gyro_sum["z"] / samples
    }
    
    print(f"Kalibrasyon tamamlandı.")
    print(f"İvme offset: {accel_offset}")
    print(f"Gyro offset: {gyro_offset}")
    
    return {
        "accel_offset": accel_offset,
        "gyro_offset": gyro_offset
    }


# Modül doğrudan çalıştırılırsa test modu
if __name__ == '__main__':
    print("IMU (MPU-6050) Test Modu")
    print("=" * 40)
    
    try:
        setup_imu()
        
        print("\nIMU verileri okunuyor (Ctrl+C ile çıkış)...\n")
        
        while True:
            data = get_imu_data()
            
            print(f"İvme (m/s²): X={data['accel_x']:7.3f}  Y={data['accel_y']:7.3f}  Z={data['accel_z']:7.3f}")
            print(f"Gyro (°/s):  X={data['gyro_x']:7.2f}  Y={data['gyro_y']:7.2f}  Z={data['gyro_z']:7.2f}")
            print(f"Rotasyon:    X={data['rotation_x']:7.2f}°  Y={data['rotation_y']:7.2f}°")
            print("-" * 40)
            
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        print("\nTest sonlandırılıyor...")
    
    finally:
        cleanup_imu()