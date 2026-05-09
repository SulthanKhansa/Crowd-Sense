# CrowdSense: Real-Time Human Detection & Monitoring System

Sistem monitoring jumlah pengunjung secara real-time yang mengintegrasikan Computer Vision (AI) dengan sistem manajemen database untuk kebutuhan analisis data kerumunan (crowd analytics).

## 🚀 Overview

CrowdSense dirancang untuk mengatasi tantangan monitoring kapasitas ruangan secara otomatis. Dengan memanfaatkan teknologi **Deep Learning (YOLOv11)** dan **Roboflow Inference SDK**, sistem ini mampu melakukan deteksi objek dengan latensi rendah pada perangkat dengan spesifikasi terbatas (CPU-only).

Sistem ini tidak hanya menampilkan visualisasi deteksi, tetapi juga melakukan sinkronisasi data secara asinkron ke database lokal untuk kebutuhan pelaporan atau integrasi ke dashboard eksternal.

## ✨ Key Features

- **Real-Time Detection**: Menggunakan arsitektur YOLOv11 Nano yang dioptimasi untuk kecepatan inferensi tinggi.
- **Threaded Architecture**: Pemisahan antara *Main UI Thread*, *Inference Thread*, dan *Database Thread* untuk menjamin FPS webcam tetap stabil (smooth) meskipun sedang melakukan request API atau query DB.
- **Asynchronous DB Sync**: Update data ke MySQL hanya terjadi jika ada perubahan jumlah objek (state change), guna mengoptimalkan performa database.
- **Adaptive Display**: Overlay HUD (Heads-Up Display) yang informatif, menampilkan jumlah orang dan status konektivitas database secara real-time.
- **Low-Light Optimization**: Konfigurasi threshold yang disesuaikan untuk kondisi cahaya minim (backlight).

## 🛠️ Tech Stack

- **Language**: Python 3.11
- **AI/ML**: Roboflow Inference SDK (YOLOv11 Architecture)
- **Computer Vision**: OpenCV
- **Database**: MySQL
- **Concurrency**: Python Threading API

## 🔄 System Flow

1. **Capture**: Program mengambil frame dari webcam secara real-time.
2. **Preprocessing**: Frame di-resize ke resolusi optimal untuk meminimalkan beban bandwidth upload.
3. **Inference (Threaded)**: Frame dikirim ke Roboflow Cloud API secara asinkron.
4. **Validation**: Hasil deteksi difilter berdasarkan confidence threshold dan target label.
5. **Storage**: Jika jumlah orang berubah, sistem memicu thread background untuk mengupdate tabel `visitor_monitor`.
6. **Visualization**: Rendering bounding box cerah (High-Visibility) dan HUD pada frame asli.

## 📦 Installation & Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/SulthanKhansa/Crowd-Sense.git
   cd Crowd-Sense
   ```

2. **Install Dependencies**
   ```bash
   pip install opencv-python inference-sdk mysql-connector-python
   ```

3. **Database Configuration**
   Siapkan tabel MySQL menggunakan query berikut:
   ```sql
   CREATE DATABASE crowdsense;
   USE crowdsense;
   CREATE TABLE visitor_monitor (
       id INT PRIMARY KEY AUTO_INCREMENT,
       current_count INT DEFAULT 0
   );
   INSERT INTO visitor_monitor (id, current_count) VALUES (1, 0);
   ```

4. **Environment Setup**
   Buka `main.py` dan sesuaikan konfigurasi berikut:
   - `ROBOFLOW_API_KEY`: API Key dari akun Roboflow Anda.
   - `DB_CONFIG`: Kredensial database MySQL lokal Anda.

## 🚀 Running the Application

```bash
python main.py
```
*Gunakan tombol 'q' untuk menghentikan aplikasi secara aman.*

---
Developed as a demonstration of integrating Edge AI with Centralized Data Management.
