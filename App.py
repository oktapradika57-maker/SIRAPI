import streamlit as st
import pandas as pd
import gspread
import base64
import cloudinary
import cloudinary.uploader
from google.oauth2.service_account import Credentials
from datetime import datetime
import time

# ==========================================
# 0. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="Portal Operasional", page_icon="💼", layout="wide")

st.markdown("""
    <style>
        .main { background-color: #f8f9fa; }
        .stButton>button { width: 100%; border-radius: 6px; font-weight: bold; height: 45px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. KONFIGURASI CLOUDINARY (SERVER FOTO)
# ==========================================
cloudinary.config(
    cloud_name = "fxm61tjv", 
    api_key = "624877324969231", 
    api_secret = "LIFO6pfEg9fOM3nbsY8FBbVTpSI",
    secure = True
)

# ==========================================
# 2. KONFIGURASI GOOGLE SHEETS
# ==========================================
SPREADSHEET_ID = "1HvgVicTWwO4RMQI6ZR3Mu3IgGicwjcLZl9mDN1auvJU"
SHEET_REQUEST = "Form Request dana"        
SHEET_PJB = "Form PJB"                     
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# ==========================================
# 3. DATA MASTER
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
# 4. FUNGSI UPLOAD & SPREADSHEET (ANTI GAGAL)
# ==========================================
@st.cache_resource
def get_credentials():
    creds_json = st.secrets["gcp_json"]
    with open("credentials.json", "w") as f:
        f.write(creds_json)
    return Credentials.from_service_account_file("credentials.json", scopes=SCOPES)

def upload_foto(file):
    """Fungsi super aman: ubah foto ke teks base64 lalu tembak ke Cloudinary"""
    if file is None: return ""
    try:
        # Konversi foto agar aman dikirim
        encoded = base64.b64encode(file.getvalue()).decode('utf-8')
        mime_type = file.type
        file_b64 = f"data:{mime_type};base64,{encoded}"
        
        # Upload ke server Cloudinary
        response = cloudinary.uploader.upload(file_b64, resource_type="auto")
        return response.get("secure_url") # Link gambar langsung bisa dibuka siapa saja
    except Exception as e:
        st.error(f"Gagal Upload Foto: {e}")
        return ""

def append_data(sheet_name, data, credentials):
    client = gspread.authorize(credentials)
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)
    sheet.append_row(data)

def get_data_request(tiket, credentials):
    client = gspread.authorize(credentials)
    rows = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_REQUEST).get_all_values()
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
# 5. SIDEBAR NAVIGASI
# ==========================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2942/2942813.png", width=80)
st.sidebar.title("Portal Operasional")
menu = st.sidebar.radio("📌 Pilih Menu Formulir:", ["📝 Form Request Dana", "✅ Form PJB Operasional"])

# ==========================================
# MENU 1: FORM REQUEST DANA
# ==========================================
if menu == "📝 Form Request Dana":
    st.title("📝 Pengajuan Form Request Dana")
    
    with st.form("form_request_dana"):
        col1, col2 = st.columns(2)
        with col1:
            tanggal = st.date_input("Tanggal Pengajuan")
            nop = st.selectbox("NOP", ["Palangkaraya"])
            tiket = st.text_input("Nomor Tiket SWFM (cth: BPS-2026-000000034391)")
            cluster = st.selectbox("Cluster", ["Palangkaraya", "Barito Raya"])
            nama = st.selectbox("Nama Petugas", LIST_NAMA)
            role = st.selectbox("Role", ["PM", "TE", "MBP", "CME"])
            site_id = st.text_input("Site ID")
            keperluan = st.selectbox("Keperluan Dana", LIST_KEPERLUAN)
            kebutuhan = st.number_input("Kebutuhan Dana (Rp)", min_value=0, step=1000)
            deskripsi = st.text_area("Deskripsi Pekerjaan")
            
        with col2:
            jns_bbm = st.selectbox("Jenis BBM", ["Mobil", "motor", "genset"])
            km_awal = st.text_input("KM Awal (Tulis 0 jika tidak req bbm)", value="0")
            plat = st.text_input("Plat Mobil/Motor")
            lat_berangkat = st.text_input("Lat Keberangkatan (-1.2654 / tulis 0)", value="0")
            long_berangkat = st.text_input("Long Keberangkatan (116.8253 / tulis 0)", value="0")
            lat_tujuan = st.text_input("Lat Tujuan (-1.2654 / tulis 0)", value="0")
            long_tujuan = st.text_input("Long Tujuan (116.8253 / tulis 0)", value="0")
            rek_penerima = st.selectbox("Rekening Penerima", ["BNI", "BCA", "MANDIRI", "BRI"])
            no_rek = st.text_input("Nomor Rekening / E-Wallet")
            nominal_tf = st.number_input("Total Nominal ditransfer (Rp)", min_value=0, step=1000)
            
        st.markdown("---")
        st.subheader("📸 Upload Bukti")
        c_up1, c_up2 = st.columns(2)
        with c_up1:
            foto_km = st.file_uploader("Foto KM Awal (Kolom U)", type=["jpg", "png", "jpeg"])
        with c_up2:
            foto_evidance = st.file_uploader("Foto Kendaraan/Evidence (Kolom V)", type=["jpg", "png", "jpeg"])
        
        submit_req = st.form_submit_button("🚀 Kirim Request Dana", type="primary")
        
        if submit_req:
            if not tiket.strip():
                st.error("Nomor Tiket SWFM wajib diisi!")
            else:
                with st.spinner("Mengunggah foto dan menyimpan data ke Spreadsheet..."):
                    # Proses Upload Foto
                    url_km = upload_foto(foto_km)
                    url_evid = upload_foto(foto_evidance)
                    
                    creds = get_credentials()
                    waktu = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    data_req = [
                        waktu, tanggal.strftime("%d/%m/%Y"), nop, tiket, cluster, nama, role, site_id, 
                        keperluan, kebutuhan, jns_bbm, deskripsi, km_awal, "", lat_berangkat, long_berangkat, 
                        plat, rek_penerima, no_rek, nominal_tf, url_km, url_evid, lat_tujuan, long_tujuan
                    ]
                    append_data(SHEET_REQUEST, data_req, creds)
                    st.success(f"✅ Data Teks & Foto Request Dana Tiket **{tiket}** BERHASIL tersimpan!")

# ==========================================
# MENU 2: FORM PJB OPERASIONAL
# ==========================================
elif menu == "✅ Form PJB Operasional":
    st.title("✅ Form PJB Operasional (Pertanggungjawaban)")
    
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
            creds = get_credentials()
            data_ditemukan = get_data_request(cari_tiket, creds)
            if data_ditemukan:
                st.session_state.pjb_data = data_ditemukan
                st.success("🎉 Data ditemukan! Silakan lengkapi form di bawah.")
            else:
                st.session_state.pjb_data = None
                st.error("❌ Tiket tidak ditemukan.")

    if st.session_state.pjb_data is not None:
        d = st.session_state.pjb_data
        
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
                keperluan_pjb = st.text_input("Keperluan", value=d["Keperluan Dana"], disabled=True)
                jns_bbm_pjb = st.text_input("Jenis BBM", value=d["Jenis BBM"], disabled=True)
                deskripsi_pjb = st.text_area("Deskripsi", value=d["Deskripsi"], disabled=True)
                plat_pjb = st.text_input("Plat", value=d["Plat"], disabled=True)
            
            with col_b:
                st.subheader("📝 Data Tambahan PJB")
                km_akhir = st.text_input("KM Akhir", value="0")
                nominal_pjb = st.number_input("Total Nominal PJB", min_value=0, step=1000)
                tot_nilai_pjb = st.number_input("Total Nilai PJB (Sesuai nota)", min_value=0, step=1000)
                tot_liter = st.text_input("Total Liter / Material", value="0")
                harga_satuan = st.number_input("Harga Satuan", min_value=0, step=500)
            
            st.markdown("---")
            st.subheader("📸 Upload Bukti")
            p1, p2, p3 = st.columns(3)
            with p1:
                f_pengisian = st.file_uploader("Foto Evidence Pengisian", type=["jpg","png","jpeg"])
                f_nota_bbm = st.file_uploader("Foto Nota BBM", type=["jpg","png","jpeg"])
                f_nota_km = st.file_uploader("Foto Nota Disanding KM", type=["jpg","png","jpeg"])
            with p2:
                f_material = st.file_uploader("Foto Material", type=["jpg","png","jpeg"])
                f_nota_mat = st.file_uploader("Foto Nota Material Disanding", type=["jpg","png","jpeg"])
            with p3:
                f_penginapan = st.file_uploader("Foto Nota Penginapan", type=["jpg","png","jpeg"])
                f_pekerjaan = st.file_uploader("Foto Evidence Pekerjaan", type=["jpg","png","jpeg"])
            
            submit_pjb = st.form_submit_button("🚀 Simpan Form PJB", type="primary")
            
        if submit_pjb:
            with st.spinner("Mengunggah foto dan merekam PJB ke Spreadsheet..."):
                # Upload Foto
                url_pengisian = upload_foto(f_pengisian)
                url_nota_bbm = upload_foto(f_nota_bbm)
                url_nota_km = upload_foto(f_nota_km)
                url_material = upload_foto(f_material)
                url_nota_mat = upload_foto(f_nota_mat)
                url_penginapan = upload_foto(f_penginapan)
                url_pekerjaan = upload_foto(f_pekerjaan)
                
                creds = get_credentials()
                waktu_pjb = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                data_pjb = [
                    waktu_pjb, tanggal_pjb.strftime("%d/%m/%Y"), d["NOP"], d["Cluster"], d["Nama"], d["Role"], 
                    d["Site ID"], d["Keperluan Dana"], d["Jenis BBM"], d["Deskripsi"], km_akhir, nominal_pjb, 
                    d["Plat"], url_pengisian, url_nota_bbm, url_nota_km, url_material, url_nota_mat, 
                    url_penginapan, url_pekerjaan, tot_nilai_pjb, cari_tiket, tot_liter, harga_satuan
                ]
                
                append_data(SHEET_PJB, data_pjb, creds)
                st.success(f"✅ Data Teks & Foto PJB Tiket **{cari_tiket}** BERHASIL tersimpan!")
                st.session_state.pjb_data = None
                time.sleep(2)
                st.rerun()
