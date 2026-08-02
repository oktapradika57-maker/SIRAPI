import streamlit as st
import pandas as pd
import gspread
import json
import requests
import base64
from google.oauth2.service_account import Credentials
from datetime import datetime
import time

# ==========================================
# 0. KONFIGURASI TAMPILAN & HALAMAN
# ==========================================
st.set_page_config(
    page_title="Portal Operasional & Keuangan", 
    page_icon="💼", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS agar tampilan lebih profesional dan rapi
st.markdown("""
    <style>
        .main { background-color: #f8f9fa; }
        .stButton>button { width: 100%; border-radius: 6px; font-weight: bold; height: 45px; }
        .stTextInput>div>div>input, .stSelectbox>div>div>select, .stTextArea>div>div>textarea { border-radius: 6px; }
        div.stAlert { border-radius: 6px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. KONFIGURASI UTAMA (IMGBB & SPREADSHEET)
# ==========================================
IMGBB_API_KEY = "5f2dd705015f8b5beb348cbd04e7c215"
SPREADSHEET_ID = "1HvgVicTWwO4RMQI6ZR3Mu3IgGicwjcLZl9mDN1auvJU"

# Nama Tab Sheet sesuai permintaan Anda
SHEET_REQUEST = "Form Request Dana"        
SHEET_PJB = "Form PJB"                     

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# ==========================================
# 2. DATA MASTER (DROPDOWNS)
# ==========================================
LIST_NAMA = [
    "ADI BOWO SANTOSO", "AHMAD", "AHMAD MUZAKIR", "AHMAD SETIAWAN", "ALFI SYAHRI", 
    "ARMADI", "AULIA RAHMAN", "DARLI SUTANTO", "DIDI RIYADI", "FAHMI", "FRANS EJHA ADITYA", 
    "GYLLBRHED ALFARY LOLOMSAIT", "HARUN NURASYID", "HORY YUSMANTO", "INDRA", 
    "JAMES JIMBRIS TAMAILANG", "JUMADI", "KHILAL DAWAI KATIRI", "LEONARD HARA", "M. RIFANI", 
    "MUHAMMAD MUKHLIS", "MUHAMMAD MUKTI", "MUNAWIR AHMAD", "MURJANI", "NURHAYAT", 
    "OKY BANGKIT PAMUNGKAS", "PRADILA KANDI", "PUJIANTO", "PUTRA WARDANA", 
    "REYNALDI RICARDO PUTRA", "RIKI HIDAYAT", "RIKO SETIADI", "SAILILLAH", "SARUL SAPUTRA", 
    "SARWONO", "TAKLIM", "TIVIANSYAH", "TRISNO SUSANTO", "YAHYA MUHAMAD"
]
LIST_KEPERLUAN = [
    "Tshoot", "Backup", "Support", "PM", "Program BCP", "Program Quikwin", 
    "Program G348T", "Pengiriman Material SPMS", "Pembelian Material"
]

# ==========================================
# 3. FUNGSI KONEKSI & UTILITAS
# ==========================================
@st.cache_resource
def get_credentials():
    try:
        creds_json = st.secrets["gcp_json"]
        with open("credentials.json", "w") as f:
            f.write(creds_json)
        return Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
    except Exception as e:
        st.error(f"Gagal memuat kredensial: {e}")
        st.stop()

def upload_to_imgbb(file):
    if file is None: 
        return ""
    try:
        url = "https://api.imgbb.com/1/upload"
        file_bytes = file.getvalue()
        payload = {
            "key": IMGBB_API_KEY,
            "image": base64.b64encode(file_bytes).decode("utf-8")
        }
        response = requests.post(url, data=payload)
        result = response.json()
        
        if result.get("success"):
            return result["data"]["url"]
        else:
            err_msg = result.get('error', {}).get('message', 'Gagal upload')
            st.error(f"ImgBB Error ({file.name}): {err_msg}")
            return ""
    except Exception as e:
        st.error(f"Gagal menghubungkan ke ImgBB untuk {file.name}: {e}")
        return ""

def append_data(sheet_name, data, credentials):
    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    
    try:
        sheet = spreadsheet.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        existing = [w.title for w in spreadsheet.worksheets()]
        raise Exception(f"Tab '{sheet_name}' tidak ditemukan! Tab yang tersedia di Spreadsheet Anda: {existing}")
        
    sheet.append_row(data)

def get_data_request(tiket, credentials):
    """Mencari tiket berdasarkan Kolom D (Indeks 3) secara aman"""
    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    
    try:
        sheet = spreadsheet.worksheet(SHEET_REQUEST)
    except gspread.exceptions.WorksheetNotFound:
        raise Exception(f"Tab '{SHEET_REQUEST}' tidak ditemukan di Google Sheets.")
        
    rows = sheet.get_all_values()
    if not rows or len(rows) < 2:
        return None
        
    for row in rows[1:]:
        # Kolom D adalah indeks ke-3 (Nomor Tiket SWFM)
        if len(row) > 3 and str(row[3]).strip().upper() == str(tiket).strip().upper():
            return {
                "NOP": row[2] if len(row) > 2 else "",               # Kolom C
                "Cluster": row[4] if len(row) > 4 else "",           # Kolom E
                "Nama": row[5] if len(row) > 5 else "",              # Kolom F
                "Role": row[6] if len(row) > 6 else "",              # Kolom G
                "Site ID": row[7] if len(row) > 7 else "",           # Kolom H
                "Keperluan Dana": row[8] if len(row) > 8 else "",    # Kolom I
                "Jenis BBM": row[10] if len(row) > 10 else "",       # Kolom K
                "Deskripsi": row[11] if len(row) > 11 else "",       # Kolom L
                "Plat": row[16] if len(row) > 16 else ""             # Kolom Q
            }
    return None

# ==========================================
# 4. SIDEBAR NAVIGASI
# ==========================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2942/2942813.png", width=80)
st.sidebar.title("Portal Operasional")
st.sidebar.markdown("---")
menu = st.sidebar.radio("📌 Pilih Menu Formulir:", ["📝 Form Request Dana", "✅ Form PJB Operasional"])

# ==========================================
# MENU 1: FORM REQUEST DANA
# ==========================================
if menu == "📝 Form Request Dana":
    st.title("📝 Pengajuan Form Request Dana")
    st.markdown("Silakan lengkapi formulir di bawah ini. Data akan langsung terekam ke Google Sheets & terhubung ke sistem PJB.")
    
    with st.form("form_request_dana"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📌 Informasi Pekerjaan")
            tanggal = st.date_input("Tanggal Pengajuan")
            nop = st.selectbox("NOP", ["Palangkaraya"])
            tiket = st.text_input("Nomor Tiket SWFM (cth: BPS-2026-000000034391)")
            cluster = st.selectbox("Cluster", ["Palangkaraya", "Barito Raya"])
            nama = st.selectbox("Nama Petugas", LIST_NAMA)
            role = st.selectbox("Role", ["PM", "TE", "MBP", "CME"])
            site_id = st.text_input("Site ID")
            keperluan = st.selectbox("Keperluan Dana", LIST_KEPERLUAN)
            kebutuhan = st.number_input("Kebutuhan Dana (Rp)", min_value=0, step=1000)
            deskripsi = st.text_area("Deskripsi Pekerjaan (Jabarkan secara lengkap)")
            
        with col2:
            st.subheader("🚗 Kendaraan & Lokasi")
            jns_bbm = st.selectbox("Jenis BBM", ["Mobil", "motor", "genset"])
            km_awal = st.text_input("KM Awal (Tulis 0 jika tidak req bbm)", value="0")
            plat = st.text_input("Plat Mobil/Motor")
            
            st.markdown("**Koordinat Keberangkatan & Tujuan**")
            lat_berangkat = st.text_input("Lat Keberangkatan (-1.2654 / tulis 0)", value="0")
            long_berangkat = st.text_input("Long Keberangkatan (116.8253 / tulis 0)", value="0")
            lat_tujuan = st.text_input("Lat Tujuan (-1.2654 / tulis 0)", value="0")
            long_tujuan = st.text_input("Long Tujuan (116.8253 / tulis 0)", value="0")
            
            st.markdown("**💳 Informasi Transfer**")
            rek_penerima = st.selectbox("Rekening Penerima", ["BNI", "BCA", "MANDIRI", "BRI"])
            no_rek = st.text_input("Nomor Rekening / E-Wallet")
            nominal_tf = st.number_input("Total Nominal ditransfer (Rp)", min_value=0, step=1000)
            
        st.markdown("---")
        st.subheader("📸 Upload Bukti / Evidence (Format Gambar)")
        c_up1, c_up2 = st.columns(2)
        with c_up1:
            foto_km = st.file_uploader("Kolom U: Foto KM Awal", type=["jpg", "png", "jpeg"])
        with c_up2:
            foto_evidance = st.file_uploader("Kolom V: Foto Kendaraan / Evidence", type=["jpg", "png", "jpeg"])
        
        st.markdown("")
        submit_req = st.form_submit_button("🚀 Kirim Request Dana", type="primary")
        
        if submit_req:
            if not tiket.strip():
                st.error("Nomor Tiket SWFM wajib diisi!")
            else:
                with st.spinner("Mengunggah foto ke cloud & merekam data ke Spreadsheet..."):
                    try:
                        url_km = upload_to_imgbb(foto_km)
                        url_evid = upload_to_imgbb(foto_evidance)
                        
                        creds = get_credentials()
                        waktu = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        tgl_str = tanggal.strftime("%d/%m/%Y")
                        
                        # Susunan Kolom A sampai X secara presisi
                        data_req = [
                            waktu,          # A: Timestamp
                            tgl_str,        # B: Tanggal
                            nop,            # C: NOP
                            tiket,          # D: Nomor Tiket SWFM
                            cluster,        # E: Cluster
                            nama,           # F: Nama
                            role,           # G: Role
                            site_id,        # H: Site ID
                            keperluan,      # I: Keperluan Dana
                            kebutuhan,      # J: Kebutuhan dana
                            jns_bbm,        # K: Jenis BBM
                            deskripsi,      # L: Deskripsi Pekerjaan
                            km_awal,        # M: KM Awal
                            "",             # N: Kosong / Pemisah
                            lat_berangkat,  # O: Lat keberangkatan
                            long_berangkat, # P: Long Keberangkatan
                            plat,           # Q: Plat Mobil/Motor
                            rek_penerima,   # R: Rekening Penerima
                            no_rek,         # S: Nomor Rekening
                            nominal_tf,     # T: Total Nominal ditransfer
                            url_km,         # U: Foto KM Awal
                            url_evid,       # V: Foto Kendaraan/Evidence
                            lat_tujuan,     # W: Lat Tujuan
                            long_tujuan     # X: Long Tujuan
                        ]
                        
                        append_data(SHEET_REQUEST, data_req, creds)
                        st.success(f"✅ Berhasil! Data Request Dana dengan Tiket **{tiket}** tersimpan ke sheet '{SHEET_REQUEST}'.")
                    except Exception as e:
                        st.error(f"Gagal menyimpan data: {e}")

# ==========================================
# MENU 2: FORM PJB OPERASIONAL
# ==========================================
elif menu == "✅ Form PJB Operasional":
    st.title("✅ Form PJB Operasional (Pertanggungjawaban)")
    st.markdown("Masukkan **Nomor Tiket** Anda untuk menarik data pengajuan sebelumnya secara otomatis.")
    
    # Kotak Pencarian Tiket
    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        cari_tiket = st.text_input("🔍 Masukkan Nomor Tiket SWFM (Sama seperti saat Request Dana):", placeholder="cth: BPS-2026-000000034391")
    with col_s2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        btn_cari = st.button("Cek Tiket", type="primary")
        
    if "pjb_data" not in st.session_state:
        st.session_state.pjb_data = None

    if btn_cari and cari_tiket:
        with st.spinner("Mencari data tiket di server..."):
            try:
                creds = get_credentials()
                data_ditemukan = get_data_request(cari_tiket, creds)
                
                if data_ditemukan:
                    st.session_state.pjb_data = data_ditemukan
                    st.success("🎉 Data ditemukan! Silakan lengkapi pertanggungjawaban di bawah ini.")
                else:
                    st.session_state.pjb_data = None
                    st.error(f"❌ Tiket '{cari_tiket}' tidak ditemukan di sheet '{SHEET_REQUEST}'. Pastikan nomor tiket sudah benar.")
            except Exception as e:
                st.error(f"Terjadi kesalahan koneksi: {e}")

    # Form PJB Muncul Jika Tiket Valid
    if st.session_state.pjb_data is not None:
        d = st.session_state.pjb_data
        
        st.info("💡 Data dari pengajuan awal (NOP, Cluster, Nama, Role, Site ID, dll) telah terisi otomatis dan dikunci.")
        
        with st.form("form_pjb_operasional"):
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.subheader("🔒 Data Terisi Otomatis")
                tanggal_pjb = st.date_input("Tanggal PJB")
                nop_pjb = st.text_input("NOP", value=d["NOP"], disabled=True)
                cluster_pjb = st.text_input("Cluster", value=d["Cluster"], disabled=True)
                nama_pjb = st.text_input("Nama", value=d["Nama"], disabled=True)
                role_pjb = st.text_input("Role", value=d["Role"], disabled=True)
                site_pjb = st.text_input("Site ID", value=d["Site ID"], disabled=True)
                keperluan_pjb = st.text_input("Keperluan Dana", value=d["Keperluan Dana"], disabled=True)
                jns_bbm_pjb = st.text_input("Jenis BBM", value=d["Jenis BBM"], disabled=True)
                deskripsi_pjb = st.text_area("Deskripsi Pekerjaan", value=d["Deskripsi"], disabled=True)
                plat_pjb = st.text_input("Plat Mobil/Motor", value=d["Plat"], disabled=True)
            
            with col_b:
                st.subheader("📝 Data Pertanggungjawaban Baru")
                km_akhir = st.text_input("Kolom K: KM Akhir (Tulis 0 jika tidak req bbm)", value="0")
                nominal_pjb = st.number_input("Kolom L: Total Nominal PJB", min_value=0, step=1000)
                tot_nilai_pjb = st.number_input("Kolom U: Total Nilai PJB (Sesuai total nota)", min_value=0, step=1000)
                no_tiket_pjb = st.text_input("Kolom V: Nomor Tiket", value=cari_tiket, disabled=True)
                tot_liter = st.text_input("Kolom W: Total Liter / Material", value="0")
                harga_satuan = st.number_input("Kolom X: Harga Satuan BBM / Material", min_value=0, step=500)
            
            st.markdown("---")
            st.subheader("📸 Upload Foto Evidence & Nota (Wajib Format Gambar)")
            st.caption("Pastikan mengunggah gambar yang sesuai pada masing-masing kolom agar laporan valid.")
            
            p1, p2, p3 = st.columns(3)
            with p1:
                f_pengisian = st.file_uploader("Kolom N: Foto Evidence Pengisian", type=["jpg","png","jpeg"])
                f_nota_bbm = st.file_uploader("Kolom O: Foto Nota BBM", type=["jpg","png","jpeg"])
                f_nota_km = st.file_uploader("Kolom P: Foto Nota Disanding KM", type=["jpg","png","jpeg"])
            with p2:
                f_material = st.file_uploader("Kolom Q: Foto Material", type=["jpg","png","jpeg"])
                f_nota_mat = st.file_uploader("Kolom R: Foto Nota Material Disanding", type=["jpg","png","jpeg"])
            with p3:
                f_penginapan = st.file_uploader("Kolom S: Foto Nota Penginapan", type=["jpg","png","jpeg"])
                f_pekerjaan = st.file_uploader("Kolom T: Foto Evidence Pekerjaan", type=["jpg","png","jpeg"])
            
            st.markdown("")
            submit_pjb = st.form_submit_button("🚀 Kirim Form PJB", type="primary")
            
            if submit_pjb:
                with st.spinner("Mengunggah foto ke cloud & merekam data PJB ke Spreadsheet..."):
                    try:
                        # Upload 7 foto ke ImgBB secara paralel/berurutan aman
                        url_pengisian = upload_to_imgbb(f_pengisian)
                        url_nota_bbm = upload_to_imgbb(f_nota_bbm)
                        url_nota_km = upload_to_imgbb(f_nota_km)
                        url_material = upload_to_imgbb(f_material)
                        url_nota_mat = upload_to_imgbb(f_nota_mat)
                        url_penginapan = upload_to_imgbb(f_penginapan)
                        url_pekerjaan = upload_to_imgbb(f_pekerjaan)
                        
                        creds = get_credentials()
                        waktu_pjb = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        tgl_pjb_str = tanggal_pjb.strftime("%d/%m/%Y")
                        
                        # Susunan Kolom A sampai X untuk Form PJB secara presisi
                        data_pjb = [
                            waktu_pjb,       # A: Timestamp
                            tgl_pjb_str,     # B: Tanggal
                            d["NOP"],        # C: NOP
                            d["Cluster"],    # D: Cluster
                            d["Nama"],       # E: Nama
                            d["Role"],       # F: Role
                            d["Site ID"],    # G: Site ID
                            d["Keperluan Dana"], # H: Keperluan Dana
                            d["Jenis BBM"],  # I: Jenis BBM
                            d["Deskripsi"],  # J: Deskripsi Pekerjaan
                            km_akhir,        # K: KM Akhir
                            nominal_pjb,     # L: Total Nominal PJB
                            d["Plat"],       # M: Plat Mobil/Motor
                            url_pengisian,   # N: Foto Evidence Pengisian
                            url_nota_bbm,    # O: Foto Nota BBM
                            url_nota_km,     # P: Foto Nota disanding KM
                            url_material,    # Q: Foto Material
                            url_nota_mat,    # R: Foto Nota material disanding
                            url_penginapan,  # S: Foto Nota Penginapan
                            url_pekerjaan,   # T: Foto Evidence Pekerjaan
                            tot_nilai_pjb,   # U: Total Nilai PJB
                            cari_tiket,      # V: Nomor tiket
                            tot_liter,       # W: Total Liter / Material
                            harga_satuan     # X: Harga Satuan BBM / material
                        ]
                        
                        append_data(SHEET_PJB, data_pjb, creds)
                        st.success(f"✅ Mantap! Pertanggungjawaban PJB untuk Tiket **{cari_tiket}** berhasil tersimpan ke sheet '{SHEET_PJB}'.")
                        
                        # Reset sesi PJB setelah sukses
                        st.session_state.pjb_data = None
                        time.sleep(2)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Terjadi kesalahan saat menyimpan PJB: {e}")
