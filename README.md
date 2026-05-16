# CrowdSense: Cloud-Integrated Crowd Monitoring

Sistem monitoring jumlah orang secara real-time yang memanfaatkan **AI Vision** dan **Cloud Infrastructure** (Supabase & Roboflow).

## 🚀 Fitur Utama

- **Cloud Synchronization**: Sinkronisasi data real-time dengan **Supabase Cloud**.
- **IP Webcam Support**: Menggunakan kamera HP sebagai sensor nirkabel (Wireless Camera).
- **Portrait Optimization**: Tampilan sudah dioptimasi untuk posisi portrait (tegak) agar akurat mendeteksi manusia.
- **Visual Monitoring**: Menampilkan *Bounding Box* kuning dan jumlah orang langsung di layar laptop.
- **Asynchronous Processing**: Deteksi berjalan di background thread, sehingga video tetap lancar (smooth).
- **Auto-Reconnect**: Otomatis menyambung ulang jika koneksi WiFi/Hotspot ke HP terputus.

## 🛠️ Tech Stack

- **AI Model**: YOLOv11 (via Roboflow Inference SDK)
- **Backend**: Supabase Cloud (PostgreSQL)
- **Vision**: OpenCV & IP Webcam Stream
- **Language**: Python 3.11

## 📦 Instalasi & Persiapan

1. **Install Library**
   ```bash
   pip install opencv-python inference-sdk supabase postgrest
   ```

2. **Setup Supabase**
   Buat tabel `visitor_monitor` di SQL Editor Supabase:
   ```sql
   CREATE TABLE visitor_monitor (
       id INT PRIMARY KEY,
       current_count INT DEFAULT 0
   );
   INSERT INTO visitor_monitor (id, current_count) VALUES (1, 0);

   -- Izinkan akses publik (RLS)
   ALTER TABLE visitor_monitor ENABLE ROW LEVEL SECURITY;
   CREATE POLICY "Allow all" ON visitor_monitor FOR ALL USING (true) WITH CHECK (true);
   ```

3. **Konfigurasi Kamera**
   - Install aplikasi **IP Webcam** di HP.
   - Klik **Start Server** dan catat IP-nya (misal: `10.103.x.x`).
   - Masukkan IP tersebut ke variabel `IP_WEBCAM_URL` di file `main.py`.

## 🚀 Cara Menjalankan

1. Hubungkan HP dan Laptop ke WiFi/Hotspot yang sama.
2. Jalankan script utama:
   ```bash
   python main.py
   ```
3. Tekan **'q'** pada jendela video untuk berhenti.

---
*Developed for real-time crowd insights and analytics.*
