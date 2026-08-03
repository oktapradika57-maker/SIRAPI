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
        div.stAlert { border-radius: 6px; }
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
# 2. MASTER DATA (DINAMIS SESUAI NOP)
# ==========================================
MASTER_DATA = {
    "Palangkaraya": {
        "spreadsheet_id": "1HvgVicTWwO4RMQI6ZR3Mu3IgGicwjcLZl9mDN1auvJU",
        "clusters": ["Palangkaraya", "Barito Raya"],
        "names": ["ADI BOWO SANTOSO", "AHMAD", "AHMAD MUZAKIR", "AHMAD SETIAWAN", "ALFI SYAHRI", "ARMADI", "AULIA RAHMAN", "DARLI SUTANTO", "DIDI RIYADI", "FAHMI", "FRANS EJHA ADITYA", "GYLLBRHED ALFARY LOLOMSAIT", "HARUN NURASYID", "HORY YUSMANTO", "INDRA", "JAMES JIMBRIS TAMAILANG", "JUMADI", "KHILAL DAWAI KATIRI", "LEONARD HARA", "M. RIFANI", "MUHAMMAD MUKHLIS", "MUHAMMAD MUKTI", "MUNAWIR AHMAD", "MURJANI", "NURHAYAT", "OKY BANGKIT PAMUNGKAS", "PRADILA KANDI", "PUJIANTO", "PUTRA WARDANA", "REYNALDI RICARDO PUTRA", "RIKI HIDAYAT", "RIKO SETIADI", "SAILILLAH", "SARUL SAPUTRA", "SARWONO", "TAKLIM", "TIVIANSYAH", "TRISNO SUSANTO", "YAHYA MUHAMAD"]
    },
    "Pangkalanbun": {
        "spreadsheet_id": "1bc0lDhR5iMtXZsKiKIdEwPY8JTaASeHFtaJSeXkywE4",
        "clusters": ["Ketapang", "Sampit", "Pangkalanbun"],
        "names": ["RIRIH HARIANTO", "MUKHAMAD ABDUL KHOLIP", "YAMA DEWANTA", "BAGUS SANTOSO", "IMRON SETIAWAN", "JOENDRIS HERDIAN KARA", "STEVEN HERDIAN KARA", "YUDIONO", "DADANG WAHYU SYAHPUTRA", "CAVIN ANDREAN EKA PUTRA", "RAHMAT RIYAN WAHYUDIN", "SUWITO", "DIDIK PRIYONO", "GUNTUR WAHYU PRADANA", "UTI MUHAMMAD KHAIRUL HUDA", "IDRUS MAULANA", "M. RIZKY", "TRIYONO", "ERIK SETIAWAN", "AGUS SUGANDA", "AJI SAPUTRA", "DIAN WAHYUDI", "HAFID BUDIANTO", "IWAN ZAINAL ABIDIN", "DANDI PUTRA", "PONIRAN", "PARYADI KUSUMA", "HERWANI", "DIAN WILDANI", "IPAN HARIONO", "FIRDAUS", "RONI YUDI ISYANTO", "AYU NUR ISLAMIAH", "ARDIANSYAH.", "DAYU SHANDY", "WAHYUDI", "TAJAM SAPUTRA", "MUJHAHID ALWI", "NANDA FIRMANSYAH", "WAHYU RAHMADANI", "TEGUH WICAKSONO", "FERI HARIADI", "NASUKI", "ANDARIANTO PUJI SURO", "BONDAN PRAMUDYA ANANTATUR", "SOLEKHAN", "RIZAL IHZAMAHENDRA", "MUHAMMAD ROIS FERDIANSYAH", "WIDI ARYANTO", "FHANNY AGUSTIAWAN"]
    },
    "Tarakan": {
        "spreadsheet_id": "1lRj1YdZGQwY5vHg8P4wudK9V1O_lJuEYjdyHkXoB-Wg",
        "clusters": ["Tarakan Inner", "Tarakan Outer"],
        "names": ["HENDRA WIRTASI SIMANULLANG", "ARIZONA ROSADI", "KUKUH BHASKARA", "NATAL SIMBOLON", "HERMAWAN", "IRVAN DINATA VANDITYAWAN", "ENDRAS SAPTA", "AHMADI", "EDI PANJI ERMAYANA", "HANS RISKY RONI TUAH GIRSANG", "IRMANSYAH B. SANGAJI", "REMO REMOLDUS MANALU", "MOHAMMAD RAFAI", "FIRMAN SYAHRUL", "AZMIR", "PETRUS RESI KELORE", "ANIR REZKY", "AHDAN", "PARJON SIMANULLANG", "RUSDI", "HASRIADI", "PURO SUGONDO", "ALIMUDIN M. SAER", "KORNELIUS USI KELORE", "RUSDIANSYAH", "JONTES YUSDA SIMANULLANG", "NANI SETIANINGSIH", "UNGGUL NUGRAHA", "YOGABITA INDOTENO", "JHON KENNEDI SIMANULLANG", "RAFI MUHAMAD SYARIF", "AGRIVA", "SEPTIAN ALVITO", "M. DEDI RIZALDI", "SAHARUDDIN.", "MUHAMMAD RASYID", "SUPRIADI", "JULIMAT SIHITE", "EFNI NURYADIN", "ERWIN SAPUTRA ARIANSYAH", "ALVEUS", "SUPRIADI BANDANGAN"]
    },
    "Pontianak": {
        "spreadsheet_id": "1VmoWPImNFMjnaIQpBXEVYdMiTEzsz3P4tpmzfA0EMDE",
        "clusters": ["Sintang", "Singkawang", "Pontianak"],
        "names": ["ALOYSIUS", "RUDI", "RONIYANTO", "SUKADI", "HAIRIL", "AZMI ASHADIQI", "SUYADI", "ARIEF DARUL IKHWAN", "MUHAMMAD AL FATAH", "YUDIANSYAH", "RAHMAD INDRA IRAWAN", "MATIUS MARTIN", "RYVAEEL DEWANGGA", "AMIRDA ANGGA SAPUTRA", "IZHARUDDIN", "VINSENSIUS YOGI", "GUSTI ARIZAL", "MUHAMMAD MIFTAHUDIN, A.MD", "BAYU ANGGARA PUTRA", "YONI IRAWAN", "SUGANDI", "IRVAN ANDRIYANA", "ALDIANSYAH", "ABANG HAMDANI", "ABANG KUSDIANSYAH", "SUMAN", "SANGGARA ISMARAWARI", "IBIN", "VALENTINUS PETRO", "DWI KURNIAWAN ISMANTO", "ARISAFRIADI", "DONATUS DONI", "NUR AHMAD KARDIYANTO", "AGRI PERDANA", "AKHSANUL FIKI", "ALI ALAMSYAH", "MUHAMMAD FIRZHA GIANNI HARSYA", "RICKY ARDILAY", "FAISAL", "WIJI SANTOSO", "HISYAM MUTHOYIB", "ARIF RAHMAN NUGROHO", "TOTOK SUGIARTO", "PURWANDI SETIAWAN", "JULIANTO BHAKTI PUTRO, SH", "ILHAMMUDIN", "AGUNG", "ROSIDI", "ABRAR ELZAH FATHALIF", "HENDRI YULIANSYAH", "JAMIL", "GORO SUKARTONO", "OKTAPIANUS JUMIN", "ONNIE SYAEFUDDIN", "BUDI", "ULUL AMRY", "RUHIAT, A.MD", "SUPIANDI", "WAHYUDI", "SUHENDRIK", "M. ARKAM", "SYAFRI APRIJAL", "ARIANTO SUMANTRI", "TUTU AGE ANDIKA", "VIRANDA SAPTA, A.MD", "TOTO HERMANSYAH", "KURNIAWAN", "ROBI ISKANDAR MASDIANSYAH", "MUTIIN CHANDRA", "MISJANI", "KHAIRUL FARISD", "ANDRA", "DODI RATMAYANTO", "WAWAN DARYANA", "MISWARDI", "JUPRILIAUS PICO", "DEDY PURNOMO", "EDI KURNIAWAN", "DEDE GUNAWAN", "WANDALA JAGOARDI PANDALO", "KARIYADI", "REZQI AL BARQAH", "FIRMANSYAH, SP"]
    }
}

LIST_KEPERLUAN = [
    "Tshoot", "Backup", "Support", "PM", "Program BCP", "Program Quikwin", 
    "Program G348T", "Pengiriman Material SPMS", "Pembelian Material"
]

SHEET_REQUEST = "Form Request Dana"        
SHEET_PJB = "Form PJB"                     
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# ==========================================
# 3. FUNGSI UPLOAD & SPREADSHEET
# ==========================================
@st.cache_resource
def get_credentials():
    creds_json = st.secrets["gcp_json"]
    with open("credentials.json", "w") as f:
        f.write(creds_json)
    return Credentials.from_service_account_file("credentials.json", scopes=SCOPES)

def upload_foto(file):
    """Konversi foto ke base64 lalu tembak ke Cloudinary"""
    if file is None: return ""
    try:
        encoded = base64.b64encode(file.getvalue()).decode('utf-8')
        mime_type = file.type
        file_b64 = f"data:{mime_type};base64,{encoded}"
        response = cloudinary.uploader.upload(file_b64, resource_type="auto")
        return response.get("secure_url") 
    except Exception as e:
        st.error(f"Gagal Upload Foto: {e}")
        return ""

def append_data(sheet_name, data, credentials, spreadsheet_id):
    """Menyimpan data ke Spreadsheet yang dinamis sesuai NOP"""
    client = gspread.authorize(credentials)
    sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)
    sheet.append_row(data)

def get_data_request(tiket, credentials, spreadsheet_id):
    """Mengambil data tiket dari Spreadsheet yang dinamis sesuai NOP"""
    client = gspread.authorize(credentials)
    rows = client.open_by_key(spreadsheet_id).worksheet(SHEET_REQUEST).get_all_values()
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
menu = st.sidebar.radio("📌 Pilih Menu Formulir:", ["📝 Form Request Dana", "✅ Form PJB Operasional"])

# ==========================================
# MENU 1: FORM REQUEST DANA
# ==========================================
if menu == "📝 Form Request Dana":
    st.title("📝 Pengajuan Form Request Dana")
    st.markdown("---")
    
    # Layout sama persis seperti versi awal tanpa st.form
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📌 Informasi Pekerjaan")
        tanggal = st.date_input("Tanggal Pengajuan")
        nop = st.selectbox("NOP", list(MASTER_DATA.keys()))
        tiket = st.text_input("Nomor Tiket SWFM (cth: BPS-2026-000000034391)")
        # Dropdown Cluster & Nama seketika otomatis berubah berdasarkan NOP di atasnya!
        cluster = st.selectbox("Cluster", MASTER_DATA[nop]["clusters"])
        nama = st.selectbox("Nama Petugas", MASTER_DATA[nop]["names"])
        role = st.selectbox("Role", ["PM", "TE", "MBP", "CME"])
        site_id = st.text_input("Site ID")
        keperluan = st.selectbox("Keperluan Dana", LIST_KEPERLUAN)
        kebutuhan = st.number_input("Kebutuhan Dana (Rp)", min_value=0, step=1000)
        deskripsi = st.text_area("Deskripsi Pekerjaan")
        
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
    st.subheader("📸 Upload Bukti")
    c_up1, c_up2 = st.columns(2)
    with c_up1:
        foto_km = st.file_uploader("Foto KM Awal (Kolom U)", type=["jpg", "png", "jpeg"])
    with c_up2:
        foto_evidance = st.file_uploader("Foto Kendaraan/Evidence (Kolom V)", type=["jpg", "png", "jpeg"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    # Tombol submit reguler
    submit_req = st.button("🚀 Kirim Request Dana", type="primary", use_container_width=True)
    
    if submit_req:
        if not tiket.strip():
            st.error("Nomor Tiket SWFM wajib diisi!")
        else:
            with st.spinner(f"Menyimpan ke Database {nop} & Upload Foto..."):
                target_spreadsheet = MASTER_DATA[nop]["spreadsheet_id"]
                
                url_km = upload_foto(foto_km)
                url_evid = upload_foto(foto_evidance)
                
                creds = get_credentials()
                waktu = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                data_req = [
                    waktu, tanggal.strftime("%d/%m/%Y"), nop, tiket, cluster, nama, role, site_id, 
                    keperluan, kebutuhan, jns_bbm, deskripsi, km_awal, "", lat_berangkat, long_berangkat, 
                    plat, rek_penerima, no_rek, nominal_tf, url_km, url_evid, lat_tujuan, long_tujuan
                ]
                
                append_data(SHEET_REQUEST, data_req, creds, target_spreadsheet)
                st.success(f"✅ Data Tiket **{tiket}** BERHASIL tersimpan di Database **{nop}**!")

# ==========================================
# MENU 2: FORM PJB OPERASIONAL
# ==========================================
elif menu == "✅ Form PJB Operasional":
    st.title("✅ Form PJB Operasional")
    
    # Kolom pencarian sejajar
    col_s1, col_s2, col_s3 = st.columns([2, 3, 1])
    with col_s1:
        nop_cari = st.selectbox("📂 Pilih Database (NOP):", list(MASTER_DATA.keys()))
    with col_s2:
        cari_tiket = st.text_input("🔍 Masukkan Nomor Tiket SWFM:", placeholder="cth: BPS-2026-000000034391")
    with col_s3:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        btn_cari = st.button("Cek Tiket", type="primary")
        
    if "pjb_data" not in st.session_state:
        st.session_state.pjb_data = None

    if btn_cari and cari_tiket:
        with st.spinner(f"Mencari tiket '{cari_tiket}' di Database {nop_cari}..."):
            target_spreadsheet = MASTER_DATA[nop_cari]["spreadsheet_id"]
            creds = get_credentials()
            
            data_ditemukan = get_data_request(cari_tiket, creds, target_spreadsheet)
            if data_ditemukan:
                st.session_state.pjb_data = data_ditemukan
                st.success(f"🎉 Data ditemukan di {nop_cari}! Silakan lengkapi form PJB.")
            else:
                st.session_state.pjb_data = None
                st.error(f"❌ Tiket '{cari_tiket}' tidak ditemukan di Database {nop_cari}.")

    if st.session_state.pjb_data is not None:
        d = st.session_state.pjb_data
        
        st.markdown("---")
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
        
        st.markdown("<br>", unsafe_allow_html=True)
        submit_pjb = st.button("🚀 Simpan Form PJB", type="primary", use_container_width=True)
        
        if submit_pjb:
            with st.spinner("Mengunggah foto dan merekam PJB..."):
                target_spreadsheet = MASTER_DATA[d["NOP"]]["spreadsheet_id"]
                
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
                
                append_data(SHEET_PJB, data_pjb, creds, target_spreadsheet)
                st.success(f"✅ Data PJB Tiket **{cari_tiket}** BERHASIL tersimpan di Database {d['NOP']}!")
                st.session_state.pjb_data = None
                time.sleep(2)
                st.rerun()
