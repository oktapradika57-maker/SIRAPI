import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from datetime import datetime
import time

# ==========================================
# 0. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="Portal Operasional & Keuangan", page_icon="💼", layout="wide")

# ==========================================
# 1. KONFIGURASI PENTING (ID DRIVE & SHEET)
# ==========================================
DRIVE_FOLDER_REQUEST = "1Hjgt0LaHBjKMnTyPNLYxRo2MdATlCz01ugu1eKgJ9Fyh-D3Mbye87MRwBbRpf4_qd_R0zvGX"
DRIVE_FOLDER_PJB = "1zPv_DLi4Knyl7FCYLmma1a1Jk8zAV3-Q37Nn2NMCR0pU79dGBPNXQcIK4edI_MefKWRvH7cI"

SPREADSHEET_ID = "1HvgVicTWwO4RMQI6ZR3Mu3IgGicwjcLZl9mDN1auvJU"
SHEET_REQUEST = "Form Request Dana"        
SHEET_PJB = "Form PJB"                     

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

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

def upload_to_drive(file, credentials, folder_id):
    if file is None: return ""
    try:
        drive_service = build('drive', 'v3', credentials=credentials)
        media = MediaIoBaseUpload(file, mimetype=file.type, resumable=True)
        uploaded = drive_service.files().create(
            body={'name': file.name, 'parents': [folder_id]}, 
            media_body=media, fields='webViewLink'
        ).execute()
        return uploaded.get('webViewLink')
    except Exception as e:
        st.error(f"Gagal upload foto {file.name}: {e}")
        return ""

def append_data(sheet_name, data, credentials):
    client = gspread.authorize(credentials)
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)
    sheet.append_row(data)

def get_data_request(tiket, credentials):
    client = gspread.authorize(credentials)
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_REQUEST)
    records = sheet.get_all_records()
    
    for row in records:
        tiket_di_sheet = str(row.get("Nomor Tiket SWFM ( tulis cth BPS-2026-000000034391)", row.get("Nomor Tiket SWFM", "")))
        if tiket_di_sheet == str(tiket):
            return row
    return None

# ==========================================
# 4. ANTARMUKA APLIKASI
# ==========================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2942/2942813.png", width=100)
st.sidebar.title("Navigasi Menu")
menu = st.sidebar.radio("Pilih Formulir:", ["📝 Request Dana", "✅ PJB Operasional"])

# ------------------------------------------
# MENU 1: REQUEST DANA
# ------------------------------------------
if menu == "📝 Request Dana":
    st.title("📝 Form Pengajuan Request Dana")
    st.markdown("Isi formulir di bawah ini dengan lengkap. Pastikan **Nomor Tiket** valid.")
    
    with st.form("form_req"):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Data Pekerjaan")
            tanggal = st.date_input("Tanggal")
            nop = st.selectbox("NOP", ["Palangkaraya"])
            tiket = st.text_input("Nomor Tiket SWFM (cth: BPS-2026-000000034391)")
            cluster = st.selectbox("Cluster", ["Palangkaraya", "Barito Raya"])
            nama = st.selectbox("Nama", LIST_NAMA)
            role = st.selectbox("Role", ["PM", "TE", "MBP", "CME"])
            site_id = st.text_input("Site ID")
            keperluan = st.selectbox("Keperluan Dana", LIST_KEPERLUAN)
            deskripsi = st.text_area("Deskripsi Pekerjaan (Jabarkan secara lengkap)")
            
        with col2:
            st.subheader("Detail Biaya & Lokasi")
            kebutuhan = st.number_input("Kebutuhan Dana (Rp)", min_value=0)
            jns_bbm = st.selectbox("Jenis BBM", ["Mobil", "motor", "genset", "Lainnya"])
            km_awal = st.text_input("KM Awal (Tulis 0 jika tidak req bbm)", value="0")
            plat = st.text_input("Plat Mobil/Motor")
            
            st.markdown("**Koordinat**")
            lat_berangkat = st.text_input("Lat Keberangkatan (-1.2654 / tulis 0 jika tidak ada)", value="0")
            long_berangkat = st.text_input("Long Keberangkatan (116.8253 / tulis 0 jika tidak ada)", value="0")
            lat_tujuan = st.text_input("Lat Tujuan (Tulis 0 jika tidak ada)", value="0")
            long_tujuan = st.text_input("Long Tujuan (Tulis 0 jika tidak ada)", value="0")
            
            st.markdown("**Informasi Transfer**")
            rek_penerima = st.selectbox("Rekening Penerima", ["BNI", "BCA", "MANDIRI", "BRI"])
            no_rek = st.text_input("Nomor Rekening/ E-Walet")
            nominal_tf = st.number_input("Total Nominal ditransfer", min_value=0)
            
        st.write("---")
        st.subheader("📸 Upload Bukti (Evidence)")
        c1, c2 = st.columns(2)
        with c1:
            foto_km = st.file_uploader("Foto KM Awal (Kolom U)", type=["jpg", "png", "jpeg"])
        with c2:
            foto_evidance = st.file_uploader("Foto Kendaraan/Evidence dll (Kolom V)", type=["jpg", "png", "jpeg"])
        
        submit_req = st.form_submit_button("Kirim Request Dana", use_container_width=True)
        
        if submit_req:
            if not tiket:
                st.error("Nomor Tiket SWFM wajib diisi!")
            else:
                with st.spinner("Mengunggah foto ke Drive Request Dana dan menyimpan ke Spreadsheet..."):
                    try:
                        creds = get_credentials()
                        url_km = upload_to_drive(foto_km, creds, DRIVE_FOLDER_REQUEST)
                        url_evid = upload_to_drive(foto_evidance, creds, DRIVE_FOLDER_REQUEST)
                        
                        waktu = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        tgl_str = tanggal.strftime("%d/%m/%Y")
                        
                        data_req = [
                            waktu, tgl_str, nop, tiket, cluster, nama, role, site_id, 
                            keperluan, kebutuhan, jns_bbm, deskripsi, km_awal, 
                            "", 
                            lat_berangkat, long_berangkat, plat, rek_penerima, no_rek, 
                            nominal_tf, url_km, url_evid, lat_tujuan, long_tujuan
                        ]
                        append_data(SHEET_REQUEST, data_req, creds)
                        st.success(f"✅ Berhasil! Request Dana dengan tiket {tiket} telah tersimpan.")
                    except Exception as e:
                        st.error(f"Terjadi kesalahan saat menyimpan: {e}")

# ------------------------------------------
# MENU 2: PJB OPERASIONAL
# ------------------------------------------
elif menu == "✅ PJB Operasional":
    st.title("✅ Form PJB Operasional")
    st.markdown("Cari Nomor Tiket Anda. Data akan **terisi otomatis** berdasarkan Request Dana sebelumnya.")
    
    search_col1, search_col2 = st.columns([3, 1])
    with search_col1:
        cari_tiket = st.text_input("🔍 Cari Nomor Tiket SWFM (Sama dengan pengajuan awal):")
    with search_col2:
        st.write("") 
        st.write("")
        btn_cari = st.button("Cari Data", type="primary", use_container_width=True)
        
    if "pjb_data" not in st.session_state:
        st.session_state.pjb_data = None

    if btn_cari and cari_tiket:
        with st.spinner("Mencari data tiket di server..."):
            try:
                creds = get_credentials()
                data_lama = get_data_request(cari_tiket, creds)
                
                if data_lama:
                    st.session_state.pjb_data = data_lama
                    st.success("✅ Data Ditemukan! Silakan lengkapi form PJB di bawah ini.")
                else:
                    st.session_state.pjb_data = None
                    st.error("❌ Nomor Tiket tidak ditemukan di data Request Dana.")
            except Exception as e:
                st.error(f"Terjadi kesalahan koneksi: {e}")

    if st.session_state.pjb_data is not None:
        d_lama = st.session_state.pjb_data
        
        with st.form("form_pjb"):
            st.info("💡 Kolom NOP, Cluster, Nama, Role, dll telah dikunci sesuai pengajuan awal.")
            col_a, col_b = st.columns(2)
            
            with col_a:
                tanggal_pjb = st.date_input("Tanggal PJB")
                nop_pjb = st.text_input("NOP", value=d_lama.get("NOP (pilihan Palangkaraya)", d_lama.get("NOP", "")), disabled=True)
                cluster_pjb = st.text_input("Cluster", value=d_lama.get("Cluster (Dropdown pilihan : Palangkaraya, Barito Raya)", d_lama.get("Cluster", "")), disabled=True)
                nama_pjb = st.text_input("Nama", value=d_lama.get("Nama Dibuat Dropdown dengan data berikut", d_lama.get("Nama", "")), disabled=True)
                role_pjb = st.text_input("Role", value=d_lama.get("Role (Dibuat dropdown : Pilihan PM,TE,MBP,CME)", d_lama.get("Role", "")), disabled=True)
                site_pjb = st.text_input("Site ID", value=d_lama.get("Site ID", ""), disabled=True)
                keperluan_pjb = st.text_input("Keperluan Dana", value=d_lama.get("Keperluan Dana", ""), disabled=True)
                jns_bbm_pjb = st.text_input("Jenis BBM", value=d_lama.get("Jenis BBM (Mobil,motor,genset)", d_lama.get("Jenis BBM", "")), disabled=True)
                deskripsi_pjb = st.text_area("Deskripsi Pekerjaan", value=d_lama.get("Deskripsi Pekerjaan (Jabarkan secara lengkap)", d_lama.get("Deskripsi Pekerjaan", "")))
            
            with col_b:
                km_akhir = st.text_input("KM Akhir (Tulis 0 jika tidak req bbm)", value="0")
                nominal_pjb = st.number_input("Total Nominal PJB", min_value=0)
                plat_pjb = st.text_input("Plat Mobil/Motor", value=d_lama.get("Plat Mobil/Motor", ""))
                
                tot_nilai_pjb = st.number_input("Total Nilai PJB (Sesuai nota upload)", min_value=0)
                no_tiket_pjb = st.text_input("Nomor Tiket", value=cari_tiket, disabled=True)
                tot_liter = st.text_input("Total Liter / Material", value="0")
                harga_satuan = st.number_input("Harga Satuan BBM / material", min_value=0)
            
            st.write("---")
            st.subheader("📸 Upload Foto Evidence & Nota (Langsung ke Drive PJB)")
            st.caption("Proses upload 7 foto ke Drive membutuhkan waktu, mohon tunggu hingga muncul notifikasi sukses.")
            
            f1, f2, f3 = st.columns(3)
            with f1:
                f_pengisian = st.file_uploader("Foto Evidance Pengisian (N)", type=["jpg","png","jpeg"])
                f_nota_bbm = st.file_uploader("Foto Nota BBM (O)", type=["jpg","png","jpeg"])
                f_nota_km = st.file_uploader("Foto Nota disanding KM (P)", type=["jpg","png","jpeg"])
            with f2:
                f_material = st.file_uploader("Foto Material (Q)", type=["jpg","png","jpeg"])
                f_nota_mat = st.file_uploader("Foto Nota material disanding (R)", type=["jpg","png","jpeg"])
            with f3:
                f_penginapan = st.file_uploader("Foto nota Penginapan (S)", type=["jpg","png","jpeg"])
                f_pekerjaan = st.file_uploader("Foto Evidance Pekerjaan (T)", type=["jpg","png","jpeg"])
            
            submit_pjb = st.form_submit_button("Kirim PJB", use_container_width=True)
            
            if submit_pjb:
                with st.spinner("Mulai mengunggah foto ke Google Drive PJB dan Menyimpan Data (Mohon Tunggu)..."):
                    try:
                        creds = get_credentials()
                        url_pengisian = upload_to_drive(f_pengisian, creds, DRIVE_FOLDER_PJB)
                        url_nota_bbm = upload_to_drive(f_nota_bbm, creds, DRIVE_FOLDER_PJB)
                        url_nota_km = upload_to_drive(f_nota_km, creds, DRIVE_FOLDER_PJB)
                        url_material = upload_to_drive(f_material, creds, DRIVE_FOLDER_PJB)
                        url_nota_mat = upload_to_drive(f_nota_mat, creds, DRIVE_FOLDER_PJB)
                        url_penginapan = upload_to_drive(f_penginapan, creds, DRIVE_FOLDER_PJB)
                        url_pekerjaan = upload_to_drive(f_pekerjaan, creds, DRIVE_FOLDER_PJB)
                        
                        waktu_pjb = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        tgl_pjb_str = tanggal_pjb.strftime("%d/%m/%Y")
                        
                        data_pjb = [
                            waktu_pjb, tgl_pjb_str, nop_pjb, cluster_pjb, nama_pjb, role_pjb, 
                            site_pjb, keperluan_pjb, jns_bbm_pjb, deskripsi_pjb, km_akhir, 
                            nominal_pjb, plat_pjb, 
                            url_pengisian, url_nota_bbm, url_nota_km, url_material, 
                            url_nota_mat, url_penginapan, url_pekerjaan, 
                            tot_nilai_pjb, cari_tiket, tot_liter, harga_satuan
                        ]
                        
                        append_data(SHEET_PJB, data_pjb, creds)
                        st.success(f"✅ Mantap! Form PJB untuk Tiket {cari_tiket} berhasil disubmit.")
                        
                        st.session_state.pjb_data = None
                        time.sleep(2)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Terjadi kesalahan saat menyimpan PJB: {e}")
