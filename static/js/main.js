/**
 * Raspberry Pi 4 - Web Kontrol Paneli
 * JavaScript - AJAX Polling ve Kontrol Fonksiyonları
 */

// ==================== GLOBAL DEĞİŞKENLER ====================
const POLLING_INTERVAL = 500; // 500ms polling aralığı
let pollingTimer = null;
let isConnected = false;

// ==================== SAYFA YÜKLENME ====================
document.addEventListener('DOMContentLoaded', function() {
    console.log('Raspberry Pi Kontrol Paneli başlatılıyor...');
    
    // İlk veri çekme
    fetchSensorData();
    
    // Polling başlat
    startPolling();
    
    // Enter tuşu ile servo açısı gönderme
    document.getElementById('custom-angle-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            moveServoCustom();
        }
    });
});

// ==================== POLLING FONKSİYONLARI ====================

/**
 * AJAX Polling'i başlat
 */
function startPolling() {
    if (pollingTimer) {
        clearInterval(pollingTimer);
    }
    
    pollingTimer = setInterval(fetchSensorData, POLLING_INTERVAL);
    console.log(`Polling başlatıldı (${POLLING_INTERVAL}ms aralıkla)`);
}

/**
 * Polling'i durdur
 */
function stopPolling() {
    if (pollingTimer) {
        clearInterval(pollingTimer);
        pollingTimer = null;
        console.log('Polling durduruldu');
    }
}

// ==================== VERİ ÇEKME ====================

/**
 * Sensör verilerini API'dan çek ve UI'ı güncelle
 */
function fetchSensorData() {
    fetch('/api/data', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Ağ hatası');
        }
        return response.json();
    })
    .then(data => {
        updateUI(data);
        setConnectionStatus(true);
    })
    .catch(error => {
        console.error('Veri çekme hatası:', error);
        setConnectionStatus(false);
    });
}

// ==================== UI GÜNCELLEME ====================

/**
 * Tüm UI elementlerini güncelle
 * @param {Object} data - API'dan gelen sensör verileri
 */
function updateUI(data) {
    // Mesafe değerini güncelle
    updateDistance(data.distance);
    
    // IMU verilerini güncelle
    updateIMU(data.imu);
    
    // Sensör durumunu güncelle
    updateSensorStatus(data.sensor_active);
    
    // Servo açısını güncelle
    updateServoAngle(data.servo_angle);
    
    // DC Motor durumunu güncelle
    if (data.motor) {
        updateMotorStatus(data.motor);
    }
    
    // Son güncelleme zamanını güncelle
    updateLastUpdateTime();
}

/**
 * Mesafe değerini güncelle
 * @param {number} distance - Mesafe (cm)
 */
function updateDistance(distance) {
    const element = document.getElementById('distance-value');
    if (element) {
        if (distance < 0) {
            element.textContent = 'HATA';
        } else {
            element.textContent = distance.toFixed(2);
        }
    }
}

/**
 * IMU verilerini güncelle
 * @param {Object} imu - IMU verileri
 */
function updateIMU(imu) {
    if (!imu) return;
    
    // İvme değerleri
    const accelX = document.getElementById('accel-x');
    const accelY = document.getElementById('accel-y');
    const accelZ = document.getElementById('accel-z');
    
    if (accelX) accelX.textContent = imu.accel_x.toFixed(3);
    if (accelY) accelY.textContent = imu.accel_y.toFixed(3);
    if (accelZ) accelZ.textContent = imu.accel_z.toFixed(3);
    
    // Gyro değerleri
    const gyroX = document.getElementById('gyro-x');
    const gyroY = document.getElementById('gyro-y');
    const gyroZ = document.getElementById('gyro-z');
    
    if (gyroX) gyroX.textContent = imu.gyro_x.toFixed(2);
    if (gyroY) gyroY.textContent = imu.gyro_y.toFixed(2);
    if (gyroZ) gyroZ.textContent = imu.gyro_z.toFixed(2);
    
    // Rotasyon değerleri (eğer varsa)
    if (imu.rotation_x !== undefined) {
        const rotationX = document.getElementById('rotation-x');
        const rotationY = document.getElementById('rotation-y');
        
        if (rotationX) rotationX.textContent = imu.rotation_x.toFixed(2);
        if (rotationY) rotationY.textContent = imu.rotation_y.toFixed(2);
    }
}

/**
 * Sensör durumunu güncelle
 * @param {boolean} isActive - Sensör aktif mi?
 */
function updateSensorStatus(isActive) {
    const statusBadge = document.getElementById('sensor-status');
    const btnOn = document.getElementById('btn-sensor-on');
    const btnOff = document.getElementById('btn-sensor-off');
    
    if (statusBadge) {
        if (isActive) {
            statusBadge.textContent = 'AKTİF';
            statusBadge.className = 'status-badge status-active';
        } else {
            statusBadge.textContent = 'KAPALI';
            statusBadge.className = 'status-badge status-inactive';
        }
    }
    
    // Buton durumlarını güncelle
    if (btnOn) btnOn.disabled = isActive;
    if (btnOff) btnOff.disabled = !isActive;
}

/**
 * Servo açısını güncelle ve görsel animasyonu uygula
 * @param {number} angle - Servo açısı (0-180)
 */
function updateServoAngle(angle) {
    const angleValue = document.getElementById('servo-angle-value');
    const servoArm = document.getElementById('servo-arm');
    
    if (angleValue) {
        angleValue.textContent = angle;
    }
    
    if (servoArm) {
        // Servo kolunu döndür (90 derece merkez)
        const rotation = angle - 90;
        servoArm.style.transform = `translateX(-50%) rotate(${rotation}deg)`;
    }
}

/**
 * DC Motor durumunu güncelle
 * @param {Object} motor - Motor durum bilgileri
 */
function updateMotorStatus(motor) {
    const statusBadge = document.getElementById('motor-status');
    const directionEl = document.getElementById('motor-direction');
    const speedEl = document.getElementById('motor-speed-value');
    
    if (statusBadge) {
        if (motor.is_running) {
            statusBadge.textContent = motor.state === 'forward' ? 'İLERİ' : 'GERİ';
            statusBadge.className = 'status-badge status-active';
        } else {
            statusBadge.textContent = 'DURDURULDU';
            statusBadge.className = 'status-badge status-inactive';
        }
    }
    
    if (directionEl) {
        const directionText = {
            'forward': 'İleri ➡️',
            'backward': '⬅️ Geri',
            'stopped': '-'
        };
        directionEl.textContent = directionText[motor.state] || '-';
    }
    
    if (speedEl) {
        speedEl.textContent = motor.speed;
    }
}

/**
 * Son güncelleme zamanını güncelle
 */
function updateLastUpdateTime() {
    const element = document.getElementById('last-update');
    if (element) {
        const now = new Date();
        element.textContent = now.toLocaleTimeString('tr-TR');
    }
}

/**
 * Bağlantı durumunu güncelle
 * @param {boolean} connected - Bağlı mı?
 */
function setConnectionStatus(connected) {
    const element = document.getElementById('connection-status');
    
    if (isConnected !== connected) {
        isConnected = connected;
        
        if (element) {
            if (connected) {
                element.textContent = 'Bağlı';
                element.className = 'status-value connected';
            } else {
                element.textContent = 'Bağlantı Yok';
                element.className = 'status-value disconnected';
            }
        }
    }
}

// ==================== KONTROL FONKSİYONLARI ====================

/**
 * Ultrasonik sensörü aç/kapat
 * @param {boolean} turnOn - Açmak için true, kapatmak için false
 */
function sensorControl(turnOn) {
    const endpoint = turnOn ? '/api/sensor/on' : '/api/sensor/off';
    const action = turnOn ? 'açılıyor' : 'kapatılıyor';
    
    console.log(`Sensör ${action}...`);
    
    fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('İstek başarısız');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showNotification(data.message, 'success');
            updateSensorStatus(data.sensor_active);
        } else {
            showNotification(data.message || 'Bir hata oluştu', 'error');
        }
    })
    .catch(error => {
        console.error('Sensör kontrol hatası:', error);
        showNotification('Sensör kontrol edilemedi!', 'error');
    });
}

/**
 * Servo motoru belirtilen açıya getir
 * @param {number} angle - Hedef açı (0-180)
 */
function moveServo(angle) {
    console.log(`Servo ${angle}° konumuna hareket ettiriliyor...`);
    
    fetch('/api/servo/move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ angle: angle })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('İstek başarısız');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showNotification(data.message, 'success');
            updateServoAngle(data.angle);
        } else {
            showNotification(data.message || 'Bir hata oluştu', 'error');
        }
    })
    .catch(error => {
        console.error('Servo kontrol hatası:', error);
        showNotification('Servo kontrol edilemedi!', 'error');
    });
}

/**
 * Özel açı girişinden servo'yu hareket ettir
 */
function moveServoCustom() {
    const input = document.getElementById('custom-angle-input');
    const angle = parseInt(input.value);
    
    if (isNaN(angle)) {
        showNotification('Geçerli bir açı girin!', 'error');
        return;
    }
    
    if (angle < 0 || angle > 180) {
        showNotification('Açı 0-180 arasında olmalı!', 'error');
        return;
    }
    
    moveServo(angle);
}

// ==================== DC MOTOR KONTROL ====================

/**
 * DC Motor kontrol fonksiyonu
 * @param {string} action - Aksiyon: 'forward', 'backward', 'stop', 'brake'
 */
function motorControl(action) {
    const speedSlider = document.getElementById('motor-speed');
    const speed = speedSlider ? parseInt(speedSlider.value) : 50;
    
    const endpoints = {
        'forward': '/api/motor/forward',
        'backward': '/api/motor/backward',
        'stop': '/api/motor/stop',
        'brake': '/api/motor/brake'
    };
    
    const endpoint = endpoints[action];
    if (!endpoint) {
        showNotification('Geçersiz motor komutu!', 'error');
        return;
    }
    
    console.log(`Motor: ${action} (Hız: ${speed}%)`);
    
    const body = (action === 'forward' || action === 'backward') 
        ? JSON.stringify({ speed: speed }) 
        : null;
    
    fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: body
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('İstek başarısız');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showNotification(data.message, 'success');
            if (data.motor) {
                updateMotorStatus(data.motor);
            }
        } else {
            showNotification(data.message || 'Bir hata oluştu', 'error');
        }
    })
    .catch(error => {
        console.error('Motor kontrol hatası:', error);
        showNotification('Motor kontrol edilemedi!', 'error');
    });
}

/**
 * Motor hızını ayarla
 * @param {number} speed - Hız (0-100)
 */
function setMotorSpeed(speed) {
    const speedSlider = document.getElementById('motor-speed');
    if (speedSlider) {
        speedSlider.value = speed;
        updateSpeedDisplay(speed);
    }
}

/**
 * Hız göstergesini güncelle
 * @param {number} value - Hız değeri
 */
function updateSpeedDisplay(value) {
    const display = document.getElementById('speed-display');
    if (display) {
        display.textContent = value;
    }
}

// ==================== BİLDİRİM SİSTEMİ ====================

/**
 * Bildirim göster
 * @param {string} message - Bildirim mesajı
 * @param {string} type - Bildirim tipi (success, error, info)
 */
function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    
    if (!notification) return;
    
    // Önceki sınıfları temizle
    notification.className = 'notification';
    notification.classList.add(type);
    notification.textContent = message;
    
    // Göster
    notification.classList.remove('hidden');
    notification.classList.add('show');
    
    // 3 saniye sonra gizle
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.classList.add('hidden');
        }, 300);
    }, 3000);
}

// ==================== YARDIMCI FONKSİYONLAR ====================

/**
 * Sayfa kapanırken temizlik yap
 */
window.addEventListener('beforeunload', function() {
    stopPolling();
});

/**
 * Sayfa görünürlüğü değiştiğinde polling'i yönet
 */
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        // Sayfa gizliyken polling'i durdur (pil tasarrufu)
        stopPolling();
    } else {
        // Sayfa görünür olduğunda polling'i tekrar başlat
        fetchSensorData();
        startPolling();
    }
});
