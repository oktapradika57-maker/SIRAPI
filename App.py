import streamlit as st
import pandas as pd
import gspread
import json
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

st.markdown("""
    <style>
        .main { background-color: #f8f9fa; }
        .stButton>button { width: 100%; border-radius: 6px; font-weight: bold; height: 45px; }
        .stTextInput>div>div>input, .stSelectbox>div>div>select, .stTextArea>div>div>textarea { border-radius: 6px; }
        div.stAlert { border-radius: 6px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. KONFIGURASI UTAMA
# ==========================================
SPREADSHEET_ID = "1HvgVicTWwO4RMQI6ZR3Mu3IgGicwjcLZl9mDN1auvJU"
SHEET_REQUEST = "Form Request dana"        
SHEET_PJB = "Form PJB"                     

# LINK GOOGLE FORM UNTUK UPLOAD FOTO (SESUAI REQUEST)
URL_FORM_FOTO_REQUEST = "https://docs.google.com/forms/d/e/1FAIpQLSdy9n-LQNePc36DYluD9XbNH07Gc2cOVy9CaU_Qj4kGJ9FTDg/viewform"
URL_FORM_FOTO_PJB = "https://docs.google.com/forms/d/e/1FAIpQLSdX4a8lC_fbKwGnOgkSkm1cyVoiJfTF1PR5Fy29as947vnFcA/viewform?usp=header"

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
# 3. FUNGSI KONEKSI SPREADSHEET
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

def append_data(sheet_name, data, credentials):
    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    try:
        sheet = spreadsheet.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        existing = [w.title for w in spreadsheet.worksheets()]
        raise Exception(f"Tab '{sheet_name}' tidak ditemukan! Tab tersedia: {existing}")
    sheet.append_row(data)

def get_data_request(tiket, credentials):
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
        if len(row) > 3 and str(row[3]).strip().upper() == str(tiket).strip().upper():
            return {
                "NOP": row[2] if len(row) > 2 else "",               
                "Cluster": row[4] if len(row) > 4 else "",           
                "Nama": row[5] if len(row) > 5 else "",              
                "Role": row[6] if len(row) > 6 else "",              
                "Site ID": row[7] if len(row) > 7 else "",           
                "Keperluan Dana": row[8] if len(row) > 8 else "",    
                "Jenis BBM": row[10] if len(row) > 10 else "",       
                "Deskripsi": row[11] if len(row) > 11 else "",       
                "Plat": row[16] if len(row) > 16 else ""             
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
    st.markdown("Isi data teks di bawah ini. Untuk upload bukti foto, Anda akan diarahkan ke Google Form setelah menekan tombol simpan.")
    
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
        st.info("📸 **PERHATIAN:** Setelah menekan tombol Simpan di bawah, Anda **WAJIB** membuka link Google Form yang muncul untuk mengupload **Foto KM Awal** dan **Foto Kendaraan/Evidence**.")
        submit_req = st.form_submit_button("🚀 Simpan Data & Lanjut Upload Foto", type="primary")
        
    if submit_req:
        if not tiket.strip():
            st.error("Nomor Tiket SWFM wajib diisi!")
        else:
            with st.spinner("Merekam data teks ke Spreadsheet..."):
                try:
                    creds = get_credentials()
                    waktu = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    tgl_str = tanggal.strftime("%d/%m/%Y")
                    
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
                        "Upload via Form", # U: Foto KM Awal (Keterangan)
                        "Upload via Form", # V: Foto Kendaraan/Evidence (Keterangan)
                        lat_tujuan,     # W: Lat Tujuan
                        long_tujuan     # X: Long Tujuan
                    ]
                    
                    append_data(SHEET_REQUEST, data_req, creds)
                    st.success(f"✅ Data Teks Request Dana Tiket **{tiket}** BERHASIL tersimpan!")
                    st.warning("👇 **LANGKAH TERAKHIR:** Klik tombol di bawah ini untuk mengupload Foto KM Awal & Kendaraan.")
                    
                    # TAMPILKAN TOMBOL MENUJU GOOGLE FORM REQUEST DANA
                    st.link_button("📸 BUKA GOOGLE FORM (UPLOAD FOTO REQUEST)", URL_FORM_FOTO_REQUEST)
                    
                except Exception as e:
                    st.error(f"Gagal menyimpan data: {e}")

# ==========================================
# MENU 2: FORM PJB OPERASIONAL
# ==========================================
elif menu == "✅ Form PJB Operasional":
    st.title("✅ Form PJB Operasional (Pertanggungjawaban)")
    st.markdown("Masukkan **Nomor Tiket** Anda untuk menarik data pengajuan sebelumnya secara otomatis.")
    
    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        cari_tiket = st.text_input("🔍 Masukkan Nomor Tiket SWFM:", placeholder="cth: BPS-2026-000000034391")
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
                    st.error(f"❌ Tiket '{cari_tiket}' tidak ditemukan di sheet '{SHEET_REQUEST}'.")
            except Exception as e:
                st.error(f"Terjadi kesalahan koneksi: {e}")

    if st.session_state.pjb_data is not None:
        d = st.session_state.pjb_data
        
        st.info("💡 Data pengajuan awal (NOP, Cluster, Nama, Role, Site ID, dll) terkunci otomatis.")
        
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
            st.info("""
            📸 **PERHATIAN:** Setelah menekan tombol Simpan, Anda **WAJIB** membuka link Google Form untuk mengupload 7 Foto berikut:
            1. Foto Evidence Pengisian
            2. Foto Nota BBM (Setelah isi)
            3. Foto Nota disanding dengan KM
            4. Foto Material
            5. Foto Nota material disanding
            6. Foto Nota Penginapan
            7. Foto Evidence Pekerjaan
            """)
            
            submit_pjb = st.form_submit_button("🚀 Simpan Data PJB & Lanjut Upload Foto", type="primary")
            
        if submit_pjb:
            with st.spinner("Merekam data teks PJB ke Spreadsheet..."):
                try:
                    creds = get_credentials()
                    waktu_pjb = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    tgl_pjb_str = tanggal_pjb.strftime("%d/%m/%Y")
                    
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
                        "Upload via Form", # N: Foto Evidence Pengisian
                        "Upload via Form", # O: Foto Nota BBM
                        "Upload via Form", # P: Foto Nota disanding KM
                        "Upload via Form", # Q: Foto Material
                        "Upload via Form", # R: Foto Nota material disanding
                        "Upload via Form", # S: Foto Nota Penginapan
                        "Upload via Form", # T: Foto Evidence Pekerjaan
                        tot_nilai_pjb,   # U: Total Nilai PJB
                        cari_tiket,      # V: Nomor tiket
                        tot_liter,       # W: Total Liter / Material
                        harga_satuan     # X: Harga Satuan BBM / material
                    ]
                    
                    append_data(SHEET_PJB, data_pjb, creds)
                    st.success(f"✅ Data Teks PJB untuk Tiket **{cari_tiket}** BERHASIL tersimpan.")
                    st.warning("👇 **LANGKAH TERAKHIR:** Klik tombol di bawah ini untuk mengupload 7 Foto Bukti PJB Anda.")
                    
                    # TAMPILKAN TOMBOL MENUJU GOOGLE FORM PJB
                    st.link_button("📸 BUKA GOOGLE FORM (UPLOAD FOTO PJB)", URL_FORM_FOTO_PJB)
                    
                    st.session_state.pjb_data = None
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat menyimpan PJB: {e}")
