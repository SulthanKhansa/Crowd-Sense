import cv2
import sys
import threading
import mysql.connector
from inference_sdk import InferenceHTTPClient

# Konfigurasi Database MySQL
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'crowdsense'
}

def update_db(count):
    """Update jumlah orang terdeteksi ke database MySQL (dijalankan di background thread)."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("UPDATE visitor_monitor SET current_count = %s WHERE id = 1", (count,))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"[DB] Updated current_count = {count}")
    except mysql.connector.Error as e:
        print(f"[DB ERROR] Gagal update database: {e}")

def test_db_connection():
    """Test koneksi ke database saat startup. Return True jika sukses."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT current_count FROM visitor_monitor WHERE id = 1")
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row is not None:
            print(f"[DB] Koneksi berhasil! current_count saat ini: {row[0]}")
            return True
        else:
            print("[DB WARNING] Tabel visitor_monitor kosong. Pastikan ada row dengan id=1.")
            return False
    except mysql.connector.Error as e:
        print(f"[DB ERROR] Gagal konek ke database: {e}")
        return False

def main():
    # Konfigurasi Roboflow Inference API
    ROBOFLOW_API_KEY = "YOUR_API_KEY"
    
    try:
        client = InferenceHTTPClient(
            api_url="https://detect.roboflow.com",
            api_key=ROBOFLOW_API_KEY
        )
    except Exception as e:
        print("[ERROR] Gagal menginisialisasi Inference HTTP Client.")
        print(f"Detail: {e}")
        sys.exit(1)

    # Test koneksi database saat startup
    db_connected = test_db_connection()


    # Inisialisasi Webcam
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[ERROR] Webcam tidak terdeteksi atau tidak dapat diakses.")
        print("Pastikan webcam tidak sedang digunakan oleh aplikasi lain.")
        sys.exit(1)

    # Resolusi untuk demo
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

    # Parameter Deteksi
    frame_count = 0
    INFER_EVERY = 10  

    TARGET_CLASSES = ['human', 'person', 'people', 'orang', 'body', 'man', 'woman']
    CONFIDENCE_THRESHOLD = 0.10

    # Shared state 
    lock = threading.Lock()
    shared_predictions = []
    shared_person_count = 0
    is_inferring = False
    last_db_count = -1  

    def run_inference(frame_copy):
        """Background thread: panggil API Roboflow + update DB jika count berubah."""
        nonlocal shared_predictions, shared_person_count, is_inferring, last_db_count
        try:
            result = client.infer(
                frame_copy, 
                model_id="yolov11n-640"
            )
            
            print(">>> API Terkoneksi & Merespon")

            raw_preds = result.get('predictions', [])

            # Filter berdasarkan confidence threshold
            filtered = [p for p in raw_preds if p.get('confidence', 0) >= CONFIDENCE_THRESHOLD]
            
            # Hitung semua objek yang terdeteksi
            count = len(filtered)

            if filtered:
                classes_found = [f"{p.get('class','?')} ({p.get('confidence',0):.0%})" for p in filtered]
                print(f"Objek terdeteksi: {classes_found}")

            print(f"Hasil: {count} objek terdeteksi")
            
            # Update shared state
            with lock:
                shared_predictions = filtered
                shared_person_count = count

            # Update database hanya jika jumlah berubah 
            if db_connected and count != last_db_count:
                last_db_count = count
                # Jalankan update DB di thread terpisah agar tidak blocking inference
                db_thread = threading.Thread(target=update_db, args=(count,), daemon=True)
                db_thread.start()

        except Exception as e:
            print(f"[WARNING] API Error: {e}")
        finally:
            with lock:
                is_inferring = False

    # Main Loop
    db_status = "Terkoneksi DB" if db_connected else "DB Tidak Terkoneksi"
    print(f"[INFO] Memulai deteksi real-time (threaded). Status: {db_status}")
    print("[INFO] Tekan 'q' untuk keluar.")

    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("[ERROR] Gagal membaca frame dari webcam.")
            break

        # Kirim frame ke background thread setiap INFER_EVERY frame
        if frame_count % INFER_EVERY == 0:
            with lock:
                should_infer = not is_inferring
            if should_infer:
                with lock:
                    is_inferring = True
                t = threading.Thread(target=run_inference, args=(frame.copy(),), daemon=True)
                t.start()
        
        frame_count += 1

        # Gambar bounding box dari hasil deteksi terakhir
        with lock:
            current_predictions = list(shared_predictions)
            current_count = shared_person_count

        box_color = (0, 255, 255) 
        frame_h, frame_w = frame.shape[:2]
        
        for pred in current_predictions:
            class_name_raw = pred.get('class', '')
            confidence = pred.get('confidence', 0)
            
            x = float(pred.get('x', 0))
            y = float(pred.get('y', 0))
            w = float(pred.get('width', 0))
            h = float(pred.get('height', 0))
            
            x1 = max(0, int(x - w / 2))
            y1 = max(0, int(y - h / 2))
            x2 = min(frame_w, int(x + w / 2))
            y2 = min(frame_h, int(y + h / 2))
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 3)
            
            label = f"{class_name_raw} {confidence:.0%}"
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            cv2.rectangle(frame, (x1, max(y1 - th - 10, 0)), (x1 + tw + 6, y1), (0, 0, 0), -1)
            cv2.putText(frame, label, (x1 + 2, max(y1 - 5, 15)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, box_color, 2)

        # Baris 1: Jumlah orang
        cv2.rectangle(frame, (10, 5), (300, 50), (0, 0, 0), -1)
        cv2.putText(frame, f"Jumlah Orang: {current_count}", (15, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)
        
        # Baris 2: Status database
        db_color = (0, 255, 0) if db_connected else (0, 0, 255)  # Hijau jika konek, Merah jika gagal
        cv2.rectangle(frame, (10, 55), (300, 85), (0, 0, 0), -1)
        cv2.putText(frame, f"Status: {db_status}", (15, 78),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, db_color, 2, cv2.LINE_AA)

        # Tampilkan window hasil
        cv2.imshow("Crowd Sense - Roboflow API", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[INFO] Menghentikan deteksi...")
            break

    # Bersihkan resource
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
