import cv2
import sys
import threading
import time
from supabase import create_client, Client
from inference_sdk import InferenceHTTPClient

# Pengaturan API & Database
SUPABASE_URL = "https://drzjjysywidmotyvqqsl.supabase.co"
SUPABASE_KEY = "sb_publishable_rzFvC1vVgkTQsycuu-uasA_xJLBRt5o"
IP_WEBCAM_URL = "http://10.103.74.210:8080/video"

# Pengaturan Model AI
ROBOFLOW_API_KEY = "E8SSwH8jSkrgBRyYTeBp"
MODEL_ID = "yolov11n-640"
CONFIDENCE_THRESHOLD = 0.10

# Konek ke Supabase
supabase: Client = None
try:
    if SUPABASE_URL != "YOUR_SUPABASE_URL":
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"[ERROR] Gagal konek Supabase: {e}")

# Fungsi buat kirim data ke cloud
def update_supabase(count):
    if not supabase: return
    try:
        supabase.table("visitor_monitor").update({"current_count": count}).eq("id", 1).execute()
        print(f"[DB] Terupdate: {count} orang")
    except Exception as e:
        print(f"[DB ERROR] {e}")

def main():
    # Inisialisasi Roboflow
    try:
        client = InferenceHTTPClient(api_url="https://detect.roboflow.com", api_key=ROBOFLOW_API_KEY)
    except Exception as e:
        print(f"[ERROR] API Roboflow: {e}"); sys.exit(1)

    # Buka stream kamera
    cap = cv2.VideoCapture(IP_WEBCAM_URL)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Variabel bantuan
    frame_count = 0
    INFER_EVERY = 10
    lock = threading.Lock()
    shared_predictions = []
    shared_person_count = 0
    is_inferring = False
    last_db_count = -1

    # Fungsi buat proses deteksi (jalan di background)
    def run_inference(frame_copy):
        nonlocal shared_person_count, shared_predictions, is_inferring, last_db_count
        try:
            result = client.infer(frame_copy, model_id=MODEL_ID)
            raw_preds = result.get('predictions', [])
            
            # Filter cuma buat manusia
            filtered = [p for p in raw_preds if p.get('class') == 'person' and p.get('confidence', 0) >= CONFIDENCE_THRESHOLD]
            count = len(filtered)
            
            with lock:
                shared_person_count = count
                shared_predictions = filtered

            # Cek kalau ada perubahan jumlah
            if count != last_db_count:
                last_db_count = count
                threading.Thread(target=update_supabase, args=(count,), daemon=True).start()
        except: pass
        finally:
            with lock: is_inferring = False

    print("[INFO] CrowdSense aktif. Tekan 'q' untuk berhenti.")

    try:
        while True:
            ret, raw_frame = cap.read()
            if not ret:
                cap.release(); time.sleep(2)
                cap = cv2.VideoCapture(IP_WEBCAM_URL); continue

            # Putar gambar biar portrait
            frame = cv2.rotate(raw_frame, cv2.ROTATE_90_CLOCKWISE)

            # Pemicu deteksi tiap interval frame
            if frame_count % INFER_EVERY == 0:
                with lock: should_infer = not is_inferring
                if should_infer:
                    with lock: is_inferring = True
                    threading.Thread(target=run_inference, args=(frame.copy(),), daemon=True).start()

            # Ambil data buat visualisasi
            with lock:
                current_preds = list(shared_predictions)
                current_count = shared_person_count

            # Gambar kotak deteksi
            for pred in current_preds:
                x, y, w, h = pred['x'], pred['y'], pred['width'], pred['height']
                x1, y1, x2, y2 = int(x-w/2), int(y-h/2), int(x+w/2), int(y+h/2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
                cv2.putText(frame, f"ORANG {pred['confidence']:.2f}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

            # Info jumlah orang di layar
            cv2.rectangle(frame, (0, 0), (220, 50), (0, 0, 0), -1)
            cv2.putText(frame, f"JUMLAH: {current_count}", (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)

            # Kecilin window buat preview
            fh, fw = frame.shape[:2]
            small_frame = cv2.resize(frame, (300, int(fh * (300/fw))))
            cv2.imshow("CrowdSense Monitoring", small_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'): break
            frame_count += 1
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n[INFO] Menutup aplikasi...")
    finally:
        cap.release(); cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
