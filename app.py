#!/usr/bin/env python3
"""
Raspberry Pi 4 - Flask Web Sunucusu
Sensör Okuma, Servo Motor, DC Motor ve IMU Kontrolü
"""

from flask import Flask, render_template, jsonify, request
import time
import threading

# Modülleri içe aktar
import servo
import dcmotor
import imu
import dijital_metre

# Raspberry Pi üzerinde çalışıp çalışmadığını kontrol et
try:
    import RPi.GPIO as GPIO
    RPI_AVAILABLE = True
except ImportError:
    RPI_AVAILABLE = False
    print("UYARI: RPi.GPIO bulunamadı. Simülasyon modu aktif.")

app = Flask(__name__)

# ==================== PIN TANIMLARI ====================
# Tüm pin tanımları ilgili modüllerde yapılmaktadır:
# - servo.py: GPIO 18 (Servo PWM)
# - dcmotor.py: GPIO 16, 20, 21 (Motor kontrolü)
# - dijital_metre.py: GPIO 23, 24 (Ultrasonik sensör)
# - imu.py: I2C (SDA/SCL)

# ==================== GLOBAL DEĞİŞKENLER ====================
sensor_data = {
    "distance": 0.0,          # Ultrasonik sensör mesafe (cm)
    "imu": {
        "accel_x": 0.0,
        "accel_y": 0.0,
        "accel_z": 9.81,       # Mock değer (yerçekimi)
        "gyro_x": 0.0,
        "gyro_y": 0.0,
        "gyro_z": 0.0
    },
    "sensor_active": True,     # Ultrasonik sensör durumu
    "servo_angle": 90,         # Mevcut servo açısı
    "motor": {                 # DC Motor durumu
        "state": "stopped",
        "speed": 0,
        "is_running": False,
        "direction": None
    }
}

# Thread kilidi
data_lock = threading.Lock()

# Sensör okuma thread'i çalışıyor mu?
sensor_thread_running = False
sensor_thread = None


# ==================== GPIO KURULUMU ====================
def setup_gpio():
    """GPIO pinlerini ayarla"""
    
    # Servo modülünü başlat
    servo.setup_servo()
    
    # DC Motor modülünü başlat
    dcmotor.setup_motor()
    
    # IMU modülünü başlat
    imu.setup_imu()
    
    # Dijital metre (ultrasonik sensör) modülünü başlat
    dijital_metre.setup_sensor()
    
    if not RPI_AVAILABLE:
        print("GPIO kurulumu simüle ediliyor...")
        return
    
    print("Tüm GPIO modülleri başlatıldı.")


def cleanup_gpio():
    """GPIO kaynaklarını temizle"""
    
    # Servo modülünü temizle
    servo.cleanup_servo()
    
    # DC Motor modülünü temizle
    dcmotor.cleanup_motor()
    
    # IMU modülünü temizle
    imu.cleanup_imu()
    
    # Dijital metre modülünü temizle
    dijital_metre.cleanup_sensor()
    
    print("Tüm GPIO kaynakları temizlendi.")


# ==================== ULTRASONİK SENSÖR ====================
def measure_distance():
    """HC-SR04 ile mesafe ölç (dijital_metre modülünü kullanarak)"""
    return dijital_metre.measure_distance()


# ==================== IMU SENSÖR ====================
def read_imu_data():
    """
    MPU-6050 IMU verisi oku
    imu modülünü kullanarak gerçek veya simüle edilmiş veri döndürür
    """
    # imu modülünden veri al
    return imu.get_imu_data()


# ==================== SENSÖR OKUMA THREAD'İ ====================
def sensor_reading_loop():
    """Arka planda sensörleri sürekli oku"""
    global sensor_data, sensor_thread_running
    
    while sensor_thread_running:
        with data_lock:
            is_active = sensor_data["sensor_active"]
        
        if is_active:
            # Ultrasonik sensör oku
            distance = measure_distance()
            
            # IMU verisi oku
            imu_data = read_imu_data()
            
            with data_lock:
                sensor_data["distance"] = distance
                sensor_data["imu"] = imu_data
        
        time.sleep(0.3)  # 300ms aralıkla oku


def start_sensor_thread():
    """Sensör okuma thread'ini başlat"""
    global sensor_thread, sensor_thread_running
    
    if not sensor_thread_running:
        sensor_thread_running = True
        sensor_thread = threading.Thread(target=sensor_reading_loop, daemon=True)
        sensor_thread.start()
        print("Sensör okuma thread'i başlatıldı.")


def stop_sensor_thread():
    """Sensör okuma thread'ini durdur"""
    global sensor_thread_running
    sensor_thread_running = False
    print("Sensör okuma thread'i durduruldu.")


# ==================== FLASK ROUTE'LARI ====================

@app.route('/')
def index():
    """Ana sayfa"""
    return render_template('index.html')


@app.route('/api/data', methods=['GET'])
def get_sensor_data():
    """Sensör verilerini JSON olarak döndür"""
    with data_lock:
        data = sensor_data.copy()
    return jsonify(data)


@app.route('/api/sensor/on', methods=['POST'])
def sensor_on():
    """Ultrasonik sensörü aktif et"""
    global sensor_data
    
    # dijital_metre modülünü kullanarak sensörü aktif et
    dijital_metre.set_active(True)
    
    with data_lock:
        sensor_data["sensor_active"] = True
    
    return jsonify({
        "success": True,
        "message": "Ultrasonik sensör aktif edildi",
        "sensor_active": True
    })


@app.route('/api/sensor/off', methods=['POST'])
def sensor_off():
    """Ultrasonik sensörü kapat"""
    global sensor_data
    
    # dijital_metre modülünü kullanarak sensörü kapat
    dijital_metre.set_active(False)
    
    with data_lock:
        sensor_data["sensor_active"] = False
        sensor_data["distance"] = 0.0  # Sensör kapalıyken 0 göster
    
    return jsonify({
        "success": True,
        "message": "Ultrasonik sensör kapatıldı",
        "sensor_active": False
    })


@app.route('/api/servo/move', methods=['POST'])
def move_servo():
    """Servo motoru belirtilen açıya getir"""
    global sensor_data
    data = request.get_json()
    
    if not data or 'angle' not in data:
        return jsonify({
            "success": False,
            "message": "Açı değeri gerekli"
        }), 400
    
    try:
        angle = int(data['angle'])
        if angle < 0 or angle > 180:
            return jsonify({
                "success": False,
                "message": "Açı 0-180 arasında olmalı"
            }), 400
        
        # servo.py modülünü kullan
        new_angle = servo.set_angle(angle)
        
        # Global state'i güncelle
        with data_lock:
            sensor_data["servo_angle"] = new_angle
        
        return jsonify({
            "success": True,
            "message": f"Servo {new_angle}° konumuna hareket etti",
            "angle": new_angle
        })
    
    except ValueError:
        return jsonify({
            "success": False,
            "message": "Geçersiz açı değeri"
        }), 400


# ==================== DC MOTOR API ====================

@app.route('/api/motor/forward', methods=['POST'])
def motor_forward():
    """DC Motoru ileri yönde çalıştır"""
    global sensor_data
    data = request.get_json() or {}
    speed = data.get('speed', 50)
    
    try:
        speed = int(speed)
        if speed < 0 or speed > 100:
            return jsonify({
                "success": False,
                "message": "Hız 0-100 arasında olmalı"
            }), 400
        
        status = dcmotor.forward(speed)
        
        with data_lock:
            sensor_data["motor"] = status
        
        return jsonify({
            "success": True,
            "message": f"Motor ileri hareket ediyor (Hız: %{speed})",
            "motor": status
        })
    
    except ValueError:
        return jsonify({
            "success": False,
            "message": "Geçersiz hız değeri"
        }), 400


@app.route('/api/motor/backward', methods=['POST'])
def motor_backward():
    """DC Motoru geri yönde çalıştır"""
    global sensor_data
    data = request.get_json() or {}
    speed = data.get('speed', 50)
    
    try:
        speed = int(speed)
        if speed < 0 or speed > 100:
            return jsonify({
                "success": False,
                "message": "Hız 0-100 arasında olmalı"
            }), 400
        
        status = dcmotor.backward(speed)
        
        with data_lock:
            sensor_data["motor"] = status
        
        return jsonify({
            "success": True,
            "message": f"Motor geri hareket ediyor (Hız: %{speed})",
            "motor": status
        })
    
    except ValueError:
        return jsonify({
            "success": False,
            "message": "Geçersiz hız değeri"
        }), 400


@app.route('/api/motor/stop', methods=['POST'])
def motor_stop():
    """DC Motoru durdur"""
    global sensor_data
    
    status = dcmotor.stop()
    
    with data_lock:
        sensor_data["motor"] = status
    
    return jsonify({
        "success": True,
        "message": "Motor durduruldu",
        "motor": status
    })


@app.route('/api/motor/brake', methods=['POST'])
def motor_brake():
    """DC Motoru frenle"""
    global sensor_data
    
    status = dcmotor.brake()
    
    with data_lock:
        sensor_data["motor"] = status
    
    return jsonify({
        "success": True,
        "message": "Motor frenlendi",
        "motor": status
    })


@app.route('/api/motor/speed', methods=['POST'])
def motor_set_speed():
    """DC Motor hızını ayarla"""
    global sensor_data
    data = request.get_json()
    
    if not data or 'speed' not in data:
        return jsonify({
            "success": False,
            "message": "Hız değeri gerekli"
        }), 400
    
    try:
        speed = int(data['speed'])
        if speed < 0 or speed > 100:
            return jsonify({
                "success": False,
                "message": "Hız 0-100 arasında olmalı"
            }), 400
        
        new_speed = dcmotor.set_speed(speed)
        
        with data_lock:
            sensor_data["motor"]["speed"] = new_speed
        
        return jsonify({
            "success": True,
            "message": f"Motor hızı %{new_speed} olarak ayarlandı",
            "speed": new_speed
        })
    
    except ValueError:
        return jsonify({
            "success": False,
            "message": "Geçersiz hız değeri"
        }), 400


@app.route('/api/motor/status', methods=['GET'])
def motor_get_status():
    """DC Motor durumunu döndür"""
    status = dcmotor.get_status()
    return jsonify(status)


@app.route('/api/status', methods=['GET'])
def get_status():
    """Sistem durumunu döndür"""
    return jsonify({
        "rpi_available": RPI_AVAILABLE,
        "sensor_thread_running": sensor_thread_running,
        "gpio_pins": {
            "servo": servo.SERVO_PIN,
            "motor_in1": dcmotor.MOTOR1_IN1,
            "motor_in2": dcmotor.MOTOR1_IN2,
            "motor_ena": dcmotor.MOTOR1_ENA,
            "trig": dijital_metre.TRIG_PIN,
            "echo": dijital_metre.ECHO_PIN
        }
    })


# ==================== UYGULAMA BAŞLATMA ====================

if __name__ == '__main__':
    try:
        # GPIO kurulumu
        setup_gpio()
        
        # Sensör thread'ini başlat
        start_sensor_thread()
        
        # Servo'yu başlangıç pozisyonuna getir (90 derece)
        servo.set_angle(90)
        
        print("\n" + "="*50)
        print("Flask Web Sunucusu Başlatılıyor...")
        print("URL: http://0.0.0.0:5000")
        print("="*50 + "\n")
        
        # Flask uygulamasını başlat
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    
    except KeyboardInterrupt:
        print("\nUygulama kapatılıyor...")
    
    finally:
        stop_sensor_thread()
        cleanup_gpio()
        print("Uygulama sonlandırıldı.")
