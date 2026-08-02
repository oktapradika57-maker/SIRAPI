import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import time

# ==========================================
# KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="Portal Operasional", page_icon="🚀", layout="wide")

# ==========================================
# KONEKSI KE GOOGLE SHEETS
# ==========================================
# CATATAN: Pastikan Anda menaruh file kredensial JSON dari Google Cloud API Anda
# dan membagikan akses edit spreadsheet ke email service account tersebut.
@st.cache_resource
def init_connection():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # Ganti 'credentials.json' dengan file JSON service account Anda
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    return client

client = init_connection()
SHEET_URL = "https://docs.google.com/spreadsheets/d/1HvgVicTWwO4RMQI6ZR3Mu3IgGicwjcLZl9mDN1auvJU/edit"

# Mengakses Sheet (Berdasarkan nama sheet. Ubah nama ini sesuai dengan nama Sheet di Spreadsheet Anda)
# Asumsi nama sheet: "Form Request Dana" dan "Form PJB"
try:
    sheet_req = client.open_by_url(SHEET_URL).worksheet("Form Request Dana")
    sheet_pjb = client.open_by_url(SHEET_URL).worksheet("Form PJB")
except Exception as e:
    st.error(f"Gagal menghubungkan ke spreadsheet: {e}")

# ==========================================
# DATA MASTER (DROPDOWNS)
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

# Fungsi Simulasi Upload Foto (Agar tidak error saat simpan text ke Sheet)
def upload_foto_to_cloud(uploaded_file):
    if uploaded_file is not None:
        # Di dunia nyata, gunakan Google Drive API / Cloudinary API disini
        # Lalu return URL publisnya.
        return f"https://link-foto-tersimpan.com/{uploaded_file.name}"
    return ""

# ==========================================
# SIDEBAR MENU
# ==========================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2942/2942813.png", width=100)
st.sidebar.title("Navigasi Menu")
menu = st.sidebar.radio("Pilih Form:", ["📝 Request Dana", "✅ PJB Operasional"])

# ==========================================
# FORM: REQUEST DANA
# ==========================================
if menu == "📝 Request Dana":
    st.title("📝 Form Request Dana")
    st.markdown("Silakan isi formulir di bawah ini untuk melakukan pengajuan dana. Pastikan nomor tiket sesuai dengan SWFM.")
    
    with st.form("form_request"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Data Pekerjaan")
            tanggal = st.date_input("Tanggal (Kolom B)")
            nop = st.selectbox("NOP (Kolom C)", ["Palangkaraya"])
            no_tiket = st.text_input("Nomor Tiket SWFM (Kolom D)", placeholder="Contoh: BPS-2026-000000034391")
            cluster = st.selectbox("Cluster (Kolom E)", ["Palangkaraya", "Barito Raya"])
            nama = st.selectbox("Nama (Kolom F)", LIST_NAMA)
            role = st.selectbox("Role (Kolom G)", ["PM", "TE", "MBP", "CME"])
            site_id = st.text_input("Site ID (Kolom H)")
            keperluan_dana = st.selectbox("Keperluan Dana (Kolom I)", LIST_KEPERLUAN)
            deskripsi = st.text_area("Deskripsi Pekerjaan (Kolom L)")
            
        with col2:
            st.subheader("Detail Biaya & Lokasi")
            kebutuhan_dana = st.number_input("Kebutuhan Dana (Rp) (Kolom J)", min_value=0)
            jenis_bbm = st.selectbox("Jenis BBM (Kolom K)", ["Mobil", "motor", "genset"])
            km_awal = st.text_input("KM Awal (Kolom M)", placeholder="Tulis 0 jika tidak ada")
            plat = st.text_input("Plat Mobil/Motor (Kolom Q)")
            
            st.markdown("**Koordinat**")
            lat_berangkat = st.text_input("Lat Keberangkatan (Kolom O)", "0")
            long_berangkat = st.text_input("Long Keberangkatan (Kolom P)", "0")
            lat_tujuan = st.text_input("Lat Tujuan (Kolom W)", "0")
            long_tujuan = st.text_input("Long Tujuan (Kolom X)", "0")
            
            st.markdown("**Informasi Rekening**")
            rek_penerima = st.selectbox("Rekening Penerima (Kolom R)", ["BNI", "BCA", "MANDIRI", "BRI"])
            no_rek = st.text_input("Nomor Rekening/E-Walet (Kolom S)")
            total_transfer = st.number_input("Total Nominal Ditransfer (Kolom T)", min_value=0)
            
        st.subheader("📸 Upload Evidence (Dari Gallery/Camera)")
        c1, c2 = st.columns(2)
        with c1:
            foto_km_awal = st.file_uploader("Foto KM Awal (Kolom U)", type=["png", "jpg", "jpeg"])
        with c2:
            foto_kendaraan = st.file_uploader("Foto Kendaraan/Evidence (Kolom V)", type=["png", "jpg", "jpeg"])

        submit_req = st.form_submit_button("Kirim Request Dana", use_container_width=True)
        
        if submit_req:
            if not no_tiket:
                st.error("Nomor Tiket wajib diisi!")
            else:
                with st.spinner("Menyimpan data ke Spreadsheet..."):
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Susun Array tepat 24 elemen (A-X). Index 13 (N) dikosongkan karena tidak ada di prompt
                    row_data_req = [
                        timestamp,                      # A (0)
                        str(tanggal),                   # B (1)
                        nop,                            # C (2)
                        no_tiket,                       # D (3)
                        cluster,                        # E (4)
                        nama,                           # F (5)
                        role,                           # G (6)
                        site_id,                        # H (7)
                        keperluan_dana,                 # I (8)
                        kebutuhan_dana,                 # J (9)
                        jenis_bbm,                      # K (10)
                        deskripsi,                      # L (11)
                        km_awal,                        # M (12)
                        "",                             # N (13) -> Kosong
                        lat_berangkat,                  # O (14)
                        long_berangkat,                 # P (15)
                        plat,                           # Q (16)
                        rek_penerima,                   # R (17)
                        no_rek,                         # S (18)
                        total_transfer,                 # T (19)
                        upload_foto_to_cloud(foto_km_awal), # U (20)
                        upload_foto_to_cloud(foto_kendaraan),# V (21)
                        lat_tujuan,                     # W (22)
                        long_tujuan                     # X (23)
                    ]
                    
                    sheet_req.append_row(row_data_req)
                    st.success(f"Berhasil! Request Dana dengan tiket {no_tiket} telah tersimpan.")

# ==========================================
# FORM: PJB OPERASIONAL
# ==========================================
elif menu == "✅ PJB Operasional":
    st.title("✅ Form PJB Operasional")
    st.markdown("Masukkan Nomor Tiket yang sudah direquest sebelumnya. Sistem akan otomatis mengisi data yang ada.")
    
    # Pencarian Tiket
    search_col1, search_col2 = st.columns([3, 1])
    with search_col1:
        cari_tiket = st.text_input("Cari Nomor Tiket SWFM (Kolom V di PJB):")
    with search_col2:
        st.write("") # Spacer
        st.write("")
        btn_cari = st.button("Cari Data", type="primary", use_container_width=True)
        
    if "pjb_data" not in st.session_state:
        st.session_state.pjb_data = None

    if btn_cari and cari_tiket:
        with st.spinner("Mencari tiket di database..."):
            all_records = sheet_req.get_all_records()
            df_req = pd.DataFrame(all_records)
            
            # Cari baris yang nomor tiketnya sama (Kolom: Nomor Tiket SWFM)
            # Pastikan nama kolom header di Google Sheet sama dengan yang dicari
            matching_data = df_req[df_req['Nomor Tiket SWFM ( tulis cth BPS-2026-000000034391)'].astype(str) == cari_tiket]
            
            if not matching_data.empty:
                st.session_state.pjb_data = matching_data.iloc[0].to_dict()
                st.success("Data ditemukan! Silakan lengkapi form PJB di bawah.")
            else:
                st.session_state.pjb_data = None
                st.error("Nomor tiket tidak ditemukan. Pastikan sudah melakukan Request Dana.")

    # Menampilkan Form PJB Jika data ditemukan atau user ingin input manual
    if st.session_state.pjb_data is not None:
        data = st.session_state.pjb_data
        
        with st.form("form_pjb"):
            st.info("💡 Beberapa kolom telah diisi otomatis berdasarkan data Request Dana.")
            col1, col2 = st.columns(2)
            
            with col1:
                tanggal_pjb = st.date_input("Tanggal (Kolom B)")
                # AUTO FILL
                nop_pjb = st.text_input("NOP (Kolom C)", value=data.get('NOP (pilihan Palangkaraya)', ''), disabled=True)
                cluster_pjb = st.text_input("Cluster (Kolom D)", value=data.get('Cluster', ''), disabled=True)
                nama_pjb = st.text_input("Nama (Kolom E)", value=data.get('Nama', ''), disabled=True)
                role_pjb = st.text_input("Role (Kolom F)", value=data.get('Role', ''), disabled=True)
                site_id_pjb = st.text_input("Site ID (Kolom G)", value=data.get('Site ID', ''), disabled=True)
                keperluan_pjb = st.text_input("Keperluan Dana (Kolom H)", value=data.get('Keperluan Dana', ''), disabled=True)
                jenis_bbm_pjb = st.text_input("Jenis BBM (Kolom I)", value=data.get('Jenis BBM', ''), disabled=True)
                deskripsi_pjb = st.text_area("Deskripsi Pekerjaan (Kolom J)", value=data.get('Deskripsi Pekerjaan', ''))
                
            with col2:
                km_akhir = st.text_input("KM Akhir (Kolom K)", placeholder="Tulis 0 jika tidak ada req bbm")
                total_nominal_pjb = st.number_input("Total Nominal PJB (Kolom L)", min_value=0)
                plat_pjb = st.text_input("Plat Mobil/Motor (Kolom M)", value=data.get('Plat Mobil/Motor', ''))
                
                total_nilai_pjb = st.number_input("Total Nilai PJB (Sesuai nota) (Kolom U)", min_value=0)
                no_tiket_pjb = st.text_input("Nomor Tiket (Kolom V)", value=cari_tiket, disabled=True)
                total_liter = st.text_input("Total Liter / Material (Kolom W)")
                harga_satuan = st.text_input("Harga Satuan BBM/Material (Kolom X)")

            st.subheader("📸 Upload Evidence & Nota PJB (Dari Gallery/Camera)")
            st.caption("Unggah bukti foto sesuai keperluan. Kolom N sampai T.")
            
            f1, f2, f3 = st.columns(3)
            with f1:
                foto_ev_isi = st.file_uploader("Foto Evidence Pengisian (Kolom N)", type=["png", "jpg", "jpeg"])
                foto_nota_bbm = st.file_uploader("Foto Nota BBM (Kolom O)", type=["png", "jpg", "jpeg"])
                foto_nota_km = st.file_uploader("Foto Nota disanding KM (Kolom P)", type=["png", "jpg", "jpeg"])
            with f2:
                foto_material = st.file_uploader("Foto Material (Kolom Q)", type=["png", "jpg", "jpeg"])
                foto_nota_mat = st.file_uploader("Foto Nota Material disanding (Kolom R)", type=["png", "jpg", "jpeg"])
            with f3:
                foto_penginapan = st.file_uploader("Foto Nota Penginapan (Kolom S)", type=["png", "jpg", "jpeg"])
                foto_ev_kerja = st.file_uploader("Foto Evidence Pekerjaan (Kolom T)", type=["png", "jpg", "jpeg"])

            submit_pjb = st.form_submit_button("Kirim PJB", use_container_width=True)
            
            if submit_pjb:
                with st.spinner("Menyimpan PJB ke Spreadsheet..."):
                    timestamp_pjb = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Susun Array tepat 24 elemen (A-X)
                    row_data_pjb = [
                        timestamp_pjb,                  # A (0)
                        str(tanggal_pjb),               # B (1)
                        nop_pjb,                        # C (2)
                        cluster_pjb,                    # D (3)
                        nama_pjb,                       # E (4)
                        role_pjb,                       # F (5)
                        site_id_pjb,                    # G (6)
                        keperluan_pjb,                  # H (7)
                        jenis_bbm_pjb,                  # I (8)
                        deskripsi_pjb,                  # J (9)
                        km_akhir,                       # K (10)
                        total_nominal_pjb,              # L (11)
                        plat_pjb,                       # M (12)
                        upload_foto_to_cloud(foto_ev_isi), # N (13)
                        upload_foto_to_cloud(foto_nota_bbm), # O (14)
                        upload_foto_to_cloud(foto_nota_km), # P (15)
                        upload_foto_to_cloud(foto_material), # Q (16)
                        upload_foto_to_cloud(foto_nota_mat), # R (17)
                        upload_foto_to_cloud(foto_penginapan),# S (18)
                        upload_foto_to_cloud(foto_ev_kerja), # T (19)
                        total_nilai_pjb,                # U (20)
                        no_tiket_pjb,                   # V (21)
                        total_liter,                    # W (22)
                        harga_satuan                    # X (23)
                    ]
                    
                    sheet_pjb.append_row(row_data_pjb)
                    st.success("✅ Form PJB berhasil disubmit dan terekam di Spreadsheet!")
                    # Clear session
                    st.session_state.pjb_data = None
                    time.sleep(2)
                    st.rerun()
