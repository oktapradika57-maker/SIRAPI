import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from datetime import datetime

st.set_page_config(page_title="Portal Keuangan & Operasional", layout="wide")

# ==========================================
# 1. KONFIGURASI (GANTI DENGAN DATA ANDA)
# ==========================================
CREDENTIALS_FILE = "kredensial_anda.json" 
DRIVE_FOLDER_ID = "ID_FOLDER_DRIVE_ANDA" 
SPREADSHEET_ID = "1HvgVicTWwO4RMQI6ZR3Mu3IgGicwjcLZl9mDN1auvJU" # ID dari URL
SHEET_REQUEST = "Form Responses 1" # Ganti jika nama tab Request Dana berbeda
SHEET_PJB = "Form Responses 2"     # Ganti jika nama tab PJB berbeda

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# DAFTAR DROPDOWN
LIST_NAMA = [
    "ADI BOWO SANTOSO", "AHMAD", "AHMAD MUZAKIR", "AHMAD SETIAWAN", "ALFI SYAHRI", 
    "ARMADI", "AULIA RAHMAN", "DARLI SUTANTO", "DIDI RIYADI", "FAHMI", "FRANS EJHA ADITYA", 
    "GYLLBRHED ALFARY LOLOMSAIT", "HARUN NURASYID", "HORY YUSMANTO", "INDRA", 
    "JAMES JIMBRIS TAMAILANG", "JUMADI", "KHILAL DAWAI KATIRI", "LEONARD HARA", 
    "M. RIFANI", "MUHAMMAD MUKHLIS", "MUHAMMAD MUKTI", "MUNAWIR AHMAD", "MURJANI", 
    "NURHAYAT", "OKY BANGKIT PAMUNGKAS", "PRADILA KANDI", "PUJIANTO", "PUTRA WARDANA", 
    "REYNALDI RICARDO PUTRA", "RIKI HIDAYAT", "RIKO SETIADI", "SAILILLAH", "SARUL SAPUTRA", 
    "SARWONO", "TAKLIM", "TIVIANSYAH", "TRISNO SUSANTO", "YAHYA MUHAMAD"
]
LIST_KEPERLUAN = ["Tshoot", "Backup", "Support", "PM", "Program BCP", "Program Quikwin", "Program G348T", "Pengiriman Material SPMS", "Pembelian Material"]

# ==========================================
# 2. FUNGSI UTILITAS
# ==========================================
@st.cache_resource
def get_credentials():
    return Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)

def upload_to_drive(file, credentials):
    if file is None: return ""
    try:
        drive_service = build('drive', 'v3', credentials=credentials)
        media = MediaIoBaseUpload(file, mimetype=file.type, resumable=True)
        uploaded = drive_service.files().create(
            body={'name': file.name, 'parents': [DRIVE_FOLDER_ID]}, 
            media_body=media, fields='webViewLink'
        ).execute()
        return uploaded.get('webViewLink')
    except Exception as e:
        st.error(f"Gagal upload {file.name}: {e}")
        return ""

def append_data(sheet_name, data, credentials):
    client = gspread.authorize(credentials)
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)
    sheet.append_row(data)

def get_data_request(tiket, credentials):
    client = gspread.authorize(credentials)
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_REQUEST)
    records = sheet.get_all_records()
    # Mencari baris yang kolom "Nomor Tiket SWFM" (Kolom D) nya cocok
    for row in records:
        if str(row.get("Nomor Tiket SWFM", "")) == str(tiket):
            return row
    return None

# ==========================================
# 3. ANTARMUKA APLIKASI
# ==========================================
st.title("Portal Operasional & Keuangan 💼")
menu = st.sidebar.radio("Pilih Menu:", ["📝 Request Dana", "✅ PJB Operasional"])

if menu == "📝 Request Dana":
    st.header("Form Pengajuan Request Dana")
    
    with st.form("form_req"):
        col1, col2 = st.columns(2)
        with col1:
            tanggal = st.date_input("Tanggal")
            nop = st.selectbox("NOP", ["Palangkaraya"])
            tiket = st.text_input("Nomor Tiket SWFM (cth: BPS-2026-000000034391)")
            cluster = st.selectbox("Cluster", ["Palangkaraya", "Barito Raya"])
            nama = st.selectbox("Nama", LIST_NAMA)
            role = st.selectbox("Role", ["PM", "TE", "MBP", "CME"])
            site_id = st.text_input("Site ID")
            keperluan = st.selectbox("Keperluan Dana", LIST_KEPERLUAN)
            kebutuhan = st.text_input("Kebutuhan Dana (Rincian)")
            jns_bbm = st.selectbox("Jenis BBM", ["Mobil", "Motor", "Genset"])
        
        with col2:
            deskripsi = st.text_area("Deskripsi Pekerjaan (Jabarkan secara lengkap)")
            km_awal = st.text_input("KM Awal (Tulis 0 jika tidak req bbm)", value="0")
            lat_berangkat = st.text_input("Lat Keberangkatan (Format -1.2654 / tulis 0 jika tidak ada)", value="0")
            long_berangkat = st.text_input("Long Keberangkatan (Format 116.8253 / tulis 0 jika tidak ada)", value="0")
            plat = st.text_input("Plat Mobil/Motor")
            rek_penerima = st.selectbox("Rekening Penerima", ["BNI", "BCA", "MANDIRI", "BRI"])
            no_rek = st.text_input("Nomor Rekening/ E-Walet")
            nominal_tf = st.number_input("Total Nominal ditransfer", min_value=0)
            lat_tujuan = st.text_input("Lat Tujuan (Tulis 0 jika tidak ada)", value="0")
            long_tujuan = st.text_input("Long Tujuan (Tulis 0 jika tidak ada)", value="0")
            
        st.write("---")
        st.write("*Upload Bukti/Evidence*")
        foto_km = st.file_uploader("KM Awal (Format Foto)", type=["jpg", "png", "jpeg"])
        foto_evidance = st.file_uploader("Foto Kendaraan/Evidence dll", type=["jpg", "png", "jpeg"])
        
        submit_req = st.form_submit_button("Submit Request Dana")
        
        if submit_req:
            if not tiket:
                st.error("Nomor Tiket SWFM wajib diisi!")
            else:
                with st.spinner("Memproses data..."):
                    creds = get_credentials()
                    url_km = upload_to_drive(foto_km, creds)
                    url_evid = upload_to_drive(foto_evidance, creds)
                    
                    waktu = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    tgl_str = tanggal.strftime("%d/%m/%Y")
                    
                    # Mapping sesuai urutan Kolom A sampai X
                    data_req = [
                        waktu, tgl_str, nop, tiket, cluster, nama, role, site_id, 
                        keperluan, kebutuhan, jns_bbm, deskripsi, km_awal, 
                        "", # Kolom N kosong (sesuai request)
                        lat_berangkat, long_berangkat, plat, rek_penerima, no_rek, 
                        nominal_tf, url_km, url_evid, lat_tujuan, long_tujuan
                    ]
                    append_data(SHEET_REQUEST, data_req, creds)
                    st.success(f"Request Dana dengan Tiket {tiket} berhasil disubmit!")

elif menu == "✅ PJB Operasional":
    st.header("Form PJB Operasional")
    
    cari_tiket = st.text_input("Masukkan Nomor Tiket SWFM (Sama dengan pengajuan):")
    
    if cari_tiket:
        try:
            creds = get_credentials()
            data_lama = get_data_request(cari_tiket, creds)
            
            if data_lama:
                st.success("✅ Data Tiket Ditemukan!")
                
                with st.form("form_pjb"):
                    st.subheader("Data Terisi Otomatis")
                    col_a, col_b = st.columns(2)
                    
                    # Menarik data lama ke input (bisa diedit jika ternyata ada perubahan, tapi sudah terisi)
                    with col_a:
                        tanggal_pjb = st.date_input("Tanggal PJB")
                        nop_pjb = st.text_input("NOP", value=data_lama.get("NOP", "Palangkaraya"))
                        cluster_pjb = st.text_input("Cluster", value=data_lama.get("Cluster", ""))
                        nama_pjb = st.text_input("Nama", value=data_lama.get("Nama", ""))
                        role_pjb = st.text_input("Role", value=data_lama.get("Role", ""))
                    with col_b:
                        site_pjb = st.text_input("Site ID", value=data_lama.get("Site ID", ""))
                        keperluan_pjb = st.text_input("Keperluan Dana", value=data_lama.get("Keperluan Dana", ""))
                        jns_bbm_pjb = st.text_input("Jenis BBM", value=data_lama.get("Jenis BBM", ""))
                        plat_pjb = st.text_input("Plat Mobil/Motor", value=data_lama.get("Plat Mobil/Motor", ""))
                        deskripsi_pjb = st.text_area("Deskripsi Pekerjaan", value=data_lama.get("Deskripsi Pekerjaan", ""))
                    
                    st.write("---")
                    st.subheader("Lengkapi Data PJB & Evidence")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        km_akhir = st.text_input("KM Akhir (Tulis 0 jika tidak req bbm)", value="0")
                        tot_liter = st.text_input("Total Liter / Material", value="0")
                        harga_satuan = st.number_input("Harga Satuan BBM / material", min_value=0)
                    with c2:
                        nominal_pjb = st.number_input("Total Nominal PJB", min_value=0)
                        tot_nilai_pjb = st.number_input("Total Nilai PJB (Sesuai nota upload)", min_value=0)
                    
                    st.write("*Upload Foto Evidence (Pilih dari Galeri)*")
                    f_pengisian = st.file_uploader("Foto Evidance Pengisian", type=["jpg","png","jpeg"])
                    f_nota_bbm = st.file_uploader("Foto Nota BBM (Setelah isi)", type=["jpg","png","jpeg"])
                    f_nota_km = st.file_uploader("Foto Nota disanding dengan KM", type=["jpg","png","jpeg"])
                    f_material = st.file_uploader("Foto Material", type=["jpg","png","jpeg"])
                    f_nota_mat = st.file_uploader("Foto Nota material disanding", type=["jpg","png","jpeg"])
                    f_penginapan = st.file_uploader("Foto nota Penginapan (wajib di kamar/depan losmen)", type=["jpg","png","jpeg"])
                    f_pekerjaan = st.file_uploader("Foto Evidance Pekerjaan", type=["jpg","png","jpeg"])
                    
                    submit_pjb = st.form_submit_button("Submit PJB")
                    
                    if submit_pjb:
                        with st.spinner("Mengunggah foto dan menyimpan PJB..."):
                            url_pengisian = upload_to_drive(f_pengisian, creds)
                            url_nota_bbm = upload_to_drive(f_nota_bbm, creds)
                            url_nota_km = upload_to_drive(f_nota_km, creds)
                            url_material = upload_to_drive(f_material, creds)
                            url_nota_mat = upload_to_drive(f_nota_mat, creds)
                            url_penginapan = upload_to_drive(f_penginapan, creds)
                            url_pekerjaan = upload_to_drive(f_pekerjaan, creds)
                            
                            waktu_pjb = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                            tgl_pjb_str = tanggal_pjb.strftime("%d/%m/%Y")
                            
                            # Mapping sesuai urutan Kolom A sampai X
                            data_pjb = [
                                waktu_pjb, tgl_pjb_str, nop_pjb, cluster_pjb, nama_pjb, role_pjb, 
                                site_pjb, keperluan_pjb, jns_bbm_pjb, deskripsi_pjb, km_akhir, 
                                nominal_pjb, plat_pjb, url_pengisian, url_nota_bbm, url_nota_km, 
                                url_material, url_nota_mat, url_penginapan, url_pekerjaan, 
                                tot_nilai_pjb, cari_tiket, tot_liter, harga_satuan
                            ]
                            append_data(SHEET_PJB, data_pjb, creds)
                            st.success(f"PJB untuk Tiket {cari_tiket} berhasil disubmit!")
            else:
                st.error("❌ Nomor Tiket tidak ditemukan di data Request Dana.")
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
