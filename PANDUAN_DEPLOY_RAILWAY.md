# 🚀 Panduan Deploy SiRAPI ke Railway (Anti-Lag untuk 200 User)

Paket ini berisi file siap pakai agar aplikasi **SiRAPI (`App.py`)** langsung berjalan di **Railway (Server Singapura)** tanpa mengubah cara kerja Anda di GitHub maupun Google Sheets.

## Isi File Dalam Paket Ini
1. `App.py` — Versi terbaru (`App-v4.py`) yang sudah ditambah:
   - Pembacaan otomatis `GCP_JSON` dari **Railway Variables** (tetap kompatibel dengan Streamlit Cloud & laptop lokal).
   - Optimasi **Batch Read Google Sheets** (1x tarikan API untuk semua sheet, hemat kuota hingga 8x agar 200 teknisi tidak kena Error 429).
2. `Dockerfile` & `railway.toml` — Otomatis dikenali Railway (sudah termasuk **Tesseract OCR** untuk analisa nota & foto Eceran AI).
3. `requirements.txt` — Daftar library Python yang bersih & ringan.
4. `.streamlit/config.toml` — Pengaturan khusus server produksi (matikan *file watcher*, optimasi upload foto & WebSocket).

---

## Langkah 1 — Upload File ke Repo GitHub SiRAPI Anda yang Sudah Ada
Anda **TIDAK perlu membuat repo baru** dan **TIDAK perlu upload ulang** file Excel (`Hasil_910_Site.xlsx`, `Site ID Sidata Pangkalanbun.xlsx`, `lonlat tim.xlsx`, `NAMA NOP PANGKALANBUN.xlsx`, `NIK NOP PLK.xlsx`, CSV Nopol, dan Logo `.webp`).

1. Ekstrak `sirapi-railway-ready.zip`.
2. Buka repositori GitHub SiRAPI Anda yang sekarang dipakai Streamlit.
3. Upload/timpa file berikut ke repo GitHub tersebut:
   - `App.py` (timpa yang lama)
   - `requirements.txt` (timpa yang lama)
   - `Dockerfile` (file baru)
   - `railway.toml` (file baru)
   - `.dockerignore` (file baru)
   - Folder `.streamlit/config.toml` (file baru)
4. Klik **Commit changes**.

> **Aman:** Aplikasi Streamlit Cloud lama Anda tetap jalan normal karena `App.py` ini tetap mendukung `st.secrets`!

---

## Langkah 2 — Buat Project di Railway & Hubungkan GitHub
1. Buka **[railway.app](https://railway.app)** lalu login menggunakan akun **GitHub** Anda.
2. Klik tombol **+ New Project** → pilih **Deploy from GitHub repo**.
3. Pilih repositori GitHub **SiRAPI** Anda.
4. Railway akan otomatis mendeteksi `Dockerfile` dan `railway.toml`, lalu mulai mem-build server.

---

## Langkah 3 — Pasang Kunci Google Sheets (`GCP_JSON`) di Railway
1. Klik kotak layanan (Service) SiRAPI Anda di dashboard Railway.
2. Buka tab **Variables** di bagian atas.
3. Klik **+ New Variable**:
   - **Variable Name:** `GCP_JSON`
   - **Value:** Copy-paste seluruh isi JSON Google Service Account Anda (sama persis dengan isi `gcp_json` di Streamlit Secrets, mulai dari `{` sampai `}`).
4. Klik **Add** (Railway akan otomatis restart & menerapkan kunci).

---

## Langkah 4 — Pindahkan Server ke Singapura (Biar Kencang di Kalimantan)
1. Masih di Service SiRAPI Anda, klik tab **Settings**.
2. Cari bagian **Deploy** → **Region**.
3. Ubah ke **`Southeast Asia (Singapore)`**.

---

## Langkah 5 — Buat Link Web Resmi SiRAPI
1. Di tab **Settings** → cari bagian **Networking** → **Public Networking**.
2. Klik tombol **Generate Domain**.
3. Jika ditanya port, biarkan default atau isi **`8501`**.
4. Railway langsung memberikan link aktif (misal `https://sirapi-kut.up.railway.app`) — Anda juga bisa mengubah nama subdomainnya sesuai keinginan.

---

## Tips Produksi untuk 200 Teknisi Lapangan
- **Cek Pemakaian RAM:** Di tab **Metrics** Railway, Anda bisa memantau grafik RAM & CPU secara *real-time*. Untuk 200 user, biasanya pemakaian RAM berkisar **600 MB – 1,8 GB** (jauh lebih lega daripada Streamlit Cloud yang mentok 1 GB).
- **Update Kode Kedepannya:** Sama persis seperti dulu — cukup edit `App.py` di GitHub lalu **Commit changes**, Railway otomatis *redeploy* dalam ± 1–2 menit.
- **Link HP Teknisi:** Bagikan link dengan akhiran `/?view=hp` (contoh: `https://sirapi-kut.up.railway.app/?view=hp`) agar di HP teknisi langsung terbuka dalam mode tampilan HP 1 kolom yang rapi.
