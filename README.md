# Crowd Sense

Sistem deteksi kerumunan orang secara real-time menggunakan webcam, Roboflow Inference API, dan database MySQL.

## Fitur

- Deteksi objek real-time via webcam (YOLOv11 Nano)
- Integrasi Roboflow Inference SDK
- Multithreading untuk performa video yang lancar
- Sinkronisasi jumlah deteksi ke MySQL
- Overlay HUD di layar

## Instalasi

```bash
pip install opencv-python inference-sdk mysql-connector-python
```

## Setup Database

```sql
CREATE DATABASE IF NOT EXISTS crowdsense;
USE crowdsense;

CREATE TABLE IF NOT EXISTS visitor_monitor (
    id INT PRIMARY KEY AUTO_INCREMENT,
    current_count INT DEFAULT 0
);

INSERT INTO visitor_monitor (id, current_count) VALUES (1, 0);
```

## Konfigurasi

Buka `main.py`, sesuaikan `ROBOFLOW_API_KEY` dan `DB_CONFIG`.

## Menjalankan

```bash
python main.py
```

Tekan `q` untuk keluar.
