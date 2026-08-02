import streamlit as st
import pandas as pd
import gspread
from datetime import datetime
import time

# ==========================================
# KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="Portal Operasional", page_icon="🚀", layout="wide")

# ==========================================
# KONEKSI KE GOOGLE SHEETS
# ==========================================
@st.cache_resource
def init_connection():
    # Menggunakan metode terbaru gspread (tidak perlu oauth2client)
    # Pastikan file credentials.json berada di folder yang sama di GitHub/Streamlit Cloud Anda
    client = gspread.service_account(filename='credentials.json')
    return client

client = init_connection()
SHEET_URL = "https://docs.google.com/spreadsheets/d/1HvgVicTWwO4RMQI6ZR3Mu3IgGicwjcLZl9mDN1auvJU/edit"

# Mengakses Sheet
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

# Fungsi Penampung Upload Foto
def upload_foto_to_cloud(uploaded_file):
    if uploaded_file is not None:
        # Placeholder: Di sinilah letak integrasi API Drive/Cloudinary nantinya
        return f"File_{uploaded_file.name}_terlampir"
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
    st.markdown("Silakan isi formulir di bawah ini untuk pengajuan dana. **Pastikan nomor tiket sesuai**.")
    
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
            jenis_bbm = st.selectbox("Jenis BBM (Kolom K)", ["Mobil", "motor", "genset", "Lainnya"])
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
            
        st.subheader("📸 Upload Evidence")
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
                    
                    # 24 Kolom dari A sampai X (Index N/13 dikosongkan sesuai permintaan awal)
                    row_data_req = [
                        timestamp,                      # A
                        str(tanggal),                   # B
                        nop,                            # C
                        no_tiket,                       # D
                        cluster,                        # E
                        nama,                           # F
                        role,                           # G
                        site_id,                        # H
                        keperluan_dana,                 # I
                        kebutuhan_dana,                 # J
                        jenis_bbm,                      # K
                        deskripsi,                      # L
                        km_awal,                        # M
                        "",                             # N (Kosong)
                        lat_berangkat,                  # O
                        long_berangkat,                 # P
                        plat,                           # Q
                        rek_penerima,                   # R
                        no_rek,                         # S
                        total_transfer,                 # T
                        upload_foto_to_cloud(foto_km_awal), # U
                        upload_foto_to_cloud(foto_kendaraan),# V
                        lat_tujuan,                     # W
                        long_tujuan                     # X
                    ]
                    
                    sheet_req.append_row(row_data_req)
                    st.success(f"Berhasil! Request Dana tiket {no_tiket} telah tersimpan.")

# ==========================================
# FORM: PJB OPERASIONAL
# ==========================================
elif menu == "✅ PJB Operasional":
    st.title("✅ Form PJB Operasional")
    st.markdown("Masukkan Nomor Tiket. Sistem akan **otomatis mengisi data** (Auto-Fill) dari Request Dana sebelumnya.")
    
    # Fitur Pencarian Tiket
    search_col1, search_col2 = st.columns([3, 1])
    with search_col1:
        cari_tiket = st.text_input("Cari Nomor Tiket SWFM:")
    with search_col2:
        st.write("") 
        st.write("")
        btn_cari = st.button("Cari Data", type="primary", use_container_width=True)
        
    if "pjb_data" not in st.session_state:
        st.session_state.pjb_data = None

    if btn_cari and cari_tiket:
        with st.spinner("Mencari tiket di database..."):
            all_records = sheet_req.get_all_records()
            df_req = pd.DataFrame(all_records)
            
            # Filter berdasarkan Nomor Tiket (Pastikan nama header ini SAMA PERSIS dengan di Spreadsheet Anda)
            header_tiket = 'Nomor Tiket SWFM ( tulis cth BPS-2026-000000034391)'
            
            if header_tiket in df_req.columns:
                matching_data = df_req[df_req[header_tiket].astype(str) == cari_tiket]
                
                if not matching_data.empty:
                    st.session_state.pjb_data = matching_data.iloc[0].to_dict()
                    st.success("Data ditemukan! Silakan lengkapi form PJB di bawah.")
                else:
                    st.session_state.pjb_data = None
                    st.error("Nomor tiket tidak ditemukan. Pastikan sudah melakukan Request Dana.")
            else:
                st.error(f"Error Header: Kolom '{header_tiket}' tidak ditemukan di Spreadsheet.")

    # Tampilkan Form PJB Jika Tiket Ditemukan
    if st.session_state.pjb_data is not None:
        data = st.session_state.pjb_data
        
        with st.form("form_pjb"):
            st.info("💡 Data NOP, Cluster, Nama, Role, Site, dll telah di-lock (otomatis terisi).")
            col1, col2 = st.columns(2)
            
            with col1:
                tanggal_pjb = st.date_input("Tanggal (Kolom B)")
                
                # AUTO FILL DARI REQUEST DANA (KOLOM C SAMPAI J)
                nop_pjb = st.text_input("NOP (Kolom C)", value=data.get('NOP (pilihan Palangkaraya)', ''), disabled=True)
                cluster_pjb = st.text_input("Cluster (Kolom D)", value=data.get('Cluster', ''), disabled=True)
                nama_pjb = st.text_input("Nama (Kolom E)", value=data.get('Nama', ''), disabled=True)
                role_pjb = st.text_input("Role (Kolom F)", value=data.get('Role', ''), disabled=True)
                site_id_pjb = st.text_input("Site ID (Kolom G)", value=data.get('Site ID', ''), disabled=True)
                keperluan_pjb = st.text_input("Keperluan Dana (Kolom H)", value=data.get('Keperluan Dana', ''), disabled=True)
                jenis_bbm_pjb = st.text_input("Jenis BBM (Kolom I)", value=data.get('Jenis BBM', ''), disabled=True)
                deskripsi_pjb = st.text_area("Deskripsi Pekerjaan (Kolom J)", value=data.get('Deskripsi Pekerjaan', ''))
                
            with col2:
                km_akhir = st.text_input("KM Akhir (Kolom K)", placeholder="Tulis 0 jika tidak req bbm")
                total_nominal_pjb = st.number_input("Total Nominal PJB (Kolom L)", min_value=0)
                plat_pjb = st.text_input("Plat Mobil/Motor (Kolom M)", value=data.get('Plat Mobil/Motor', ''))
                
                total_nilai_pjb = st.number_input("Total Nilai PJB (Sesuai nota) (Kolom U)", min_value=0)
                no_tiket_pjb = st.text_input("Nomor Tiket (Kolom V)", value=cari_tiket, disabled=True)
                total_liter = st.text_input("Total Liter / Material (Kolom W)")
                harga_satuan = st.text_input("Harga Satuan BBM/Material (Kolom X)")

            st.subheader("📸 Upload Evidence & Nota PJB")
            st.caption("Pastikan foto diupload sesuai peruntukannya (Kolom N - T).")
            
            f1, f2, f3 = st.columns(3)
            with f1:
                foto_ev_isi = st.file_uploader("Foto Evidence Pengisian (N)", type=["png", "jpg", "jpeg"])
                foto_nota_bbm = st.file_uploader("Foto Nota BBM (O)", type=["png", "jpg", "jpeg"])
                foto_nota_km = st.file_uploader("Foto Nota disanding KM (P)", type=["png", "jpg", "jpeg"])
            with f2:
                foto_material = st.file_uploader("Foto Material (Q)", type=["png", "jpg", "jpeg"])
                foto_nota_mat = st.file_uploader("Foto Nota Material disanding (R)", type=["png", "jpg", "jpeg"])
            with f3:
                foto_penginapan = st.file_uploader("Foto Nota Penginapan (S)", type=["png", "jpg", "jpeg"])
                foto_ev_kerja = st.file_uploader("Foto Evidence Pekerjaan (T)", type=["png", "jpg", "jpeg"])

            submit_pjb = st.form_submit_button("Kirim PJB", use_container_width=True)
            
            if submit_pjb:
                with st.spinner("Menyimpan data PJB ke Spreadsheet..."):
                    timestamp_pjb = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # 24 Kolom dari A sampai X
                    row_data_pjb = [
                        timestamp_pjb,                  # A
                        str(tanggal_pjb),               # B
                        nop_pjb,                        # C
                        cluster_pjb,                    # D
                        nama_pjb,                       # E
                        role_pjb,                       # F
                        site_id_pjb,                    # G
                        keperluan_pjb,                  # H
                        jenis_bbm_pjb,                  # I
                        deskripsi_pjb,                  # J
                        km_akhir,                       # K
                        total_nominal_pjb,              # L
                        plat_pjb,                       # M
                        upload_foto_to_cloud(foto_ev_isi), # N
                        upload_foto_to_cloud(foto_nota_bbm), # O
                        upload_foto_to_cloud(foto_nota_km), # P
                        upload_foto_to_cloud(foto_material), # Q
                        upload_foto_to_cloud(foto_nota_mat), # R
                        upload_foto_to_cloud(foto_penginapan),# S
                        upload_foto_to_cloud(foto_ev_kerja), # T
                        total_nilai_pjb,                # U
                        no_tiket_pjb,                   # V
                        total_liter,                    # W
                        harga_satuan                    # X
                    ]
                    
                    sheet_pjb.append_row(row_data_pjb)
                    st.success("✅ Form PJB berhasil disubmit dan terekam di Spreadsheet!")
                    st.session_state.pjb_data = None
                    time.sleep(2)
                    st.rerun()
