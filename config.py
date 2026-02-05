#!/usr/bin/env python3
"""
Raspberry Pi GPIO Pin Yapılandırması
Tüm pin tanımlarının merkezi dosyası

DİKKAT: Bu dosyayı değiştirdikten sonra ilgili modülleri de güncellemeyi unutmayın!
"""

# ==================== SERVO MOTOR ====================
# SG90 veya benzeri servo motor
SERVO_PIN = 18          # PWM çıkışı
SERVO_BUTTON_PIN = 25   # Opsiyonel: Manuel kontrol butonu
SERVO_LED_PIN = 12      # Opsiyonel: Durum LED'i

# ==================== DC MOTOR (L298N) ====================
# L298N Motor Sürücü ile DC motor kontrolü
MOTOR_IN1 = 16          # Motor yön 1
MOTOR_IN2 = 20          # Motor yön 2
MOTOR_ENA = 21          # PWM hız kontrolü (Enable A)

# ==================== ULTRASONİK SENSÖR (HC-SR04) ====================
# HC-SR04 Ultrasonik mesafe sensörü
ULTRASONIC_TRIG = 23    # Trigger pini
ULTRASONIC_ECHO = 24    # Echo pini (voltaj bölücü kullanın!)

# ==================== IMU (MPU-6050) ====================
# I2C üzerinden bağlı (GPIO 2 = SDA, GPIO 3 = SCL)
MPU6050_ADDRESS = 0x68  # I2C adresi

# ==================== I2C PINLERI ====================
# Raspberry Pi'de sabit (değiştirilemez)
I2C_SDA = 2             # GPIO 2 - Data
I2C_SCL = 3             # GPIO 3 - Clock

# ==================== PIN KULLANIM ÖZETİ ====================
"""
GPIO  | Fonksiyon           | Modül
------|--------------------|--------------
2     | I2C SDA            | imu.py
3     | I2C SCL            | imu.py
12    | Servo LED          | servo.py (opsiyonel)
16    | DC Motor IN1       | dcmotor.py
18    | Servo PWM          | servo.py
20    | DC Motor IN2       | dcmotor.py
21    | DC Motor ENA       | dcmotor.py
23    | Ultrasonik TRIG    | dijital_metre.py
24    | Ultrasonik ECHO    | dijital_metre.py
25    | Servo Button       | servo.py (opsiyonel)

NOT: GPIO 23 ve 24 ultrasonik sensör için ayrılmıştır.
     Servo'nun buton ve LED'i farklı pinlere taşınmıştır.
"""

# ==================== PWM AYARLARI ====================
SERVO_PWM_FREQ = 50     # Hz (Servo için standart)
MOTOR_PWM_FREQ = 1000   # Hz (DC motor için)
