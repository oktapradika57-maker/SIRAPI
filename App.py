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
# 0. KONFIGURASI HALAMAN & UI PROFESIONAL
# ==========================================
st.set_page_config(page_title="SiRapi", page_icon="🏦", layout="wide")

st.markdown("""
    <style>
        .main { background-color: #F4F6F9; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .header-card {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            padding: 20px; border-radius: 10px; color: white; text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 25px;
        }
        .header-admin { background: linear-gradient(135deg, #f39c12 0%, #d35400 100%); }
        .stButton>button { 
            width: 100%; border-radius: 6px; font-weight: bold; height: 45px; 
            background-color: #2980b9; color: white; border: none; transition: 0.3s;
        }
        .stButton>button:hover { background-color: #1c5980; }
        div.stAlert { border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .locked-box { border-left: 5px solid #e74c3c; padding: 15px; background-color: #fceceb; border-radius: 5px; color: #c0392b; font-weight: bold; margin-bottom: 15px;}
        .section-title { color: #2c3e50; font-size: 1.2rem; font-weight: 600; border-bottom: 2px solid #bdc3c7; padding-bottom: 5px; margin-top: 20px; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. KONFIGURASI SERVER, KOORDINATOR & ADMIN
# ==========================================
PASSWORD_KOORDINATOR = "Kamiyakin2027"

ADMIN_PASSWORDS = {
    "Palangkaraya": "okkidah",
    "Pangkalanbun": "yurontur",
    "Tarakan": "donpablo",
    "Pontianak": "kingaloy"
}

cloudinary.config(
    cloud_name = "fxm61tjv", 
    api_key = "624877324969231", 
    api_secret = "LIFO6pfEg9fOM3nbsY8FBbVTpSI",
    secure = True
)

# ==========================================
# 2. MASTER DATA (DATABASE DINAMIS)
# ==========================================
MASTER_DATA = {
    "Palangkaraya": {
        "spreadsheet_id": "1HvgVicTWwO4RMQI6ZR3Mu3IgGicwjcLZl9mDN1auvJU",
        "clusters": ["Palangkaraya", "Barito Raya"],
        "names": ["ADI BOWO SANTOSO", "AHMAD", "AHMAD MUZAKIR", "AHMAD SETIAWAN", "ALFI SYAHRI", "ARMADI", "AULIA RAHMAN", "DARLI SUTANTO", "DIDI RIYADI", "FAHMI", "FRANS EJHA ADITYA", "GYLLBRHED ALFARY LOLOMSAIT", "HARUN NURASYID", "HORY YUSMANTO", "INDRA", "JAMES JIMBRIS TAMAILANG", "JUMADI", "KHILAL DAWAI KATIRI", "LEONARD HARA", "M. RIFANI", "MUHAMMAD MUKHLIS", "MUHAMMAD MUKTI", "MUNAWIR AHMAD", "MURJANI", "NURHAYAT", "OKY BANGKIT PAMUNGKAS", "PRADILA KANDI", "PUJIANTO", "PUTRA WARDANA", "REYNALDI RICARDO PUTRA", "RIKI HIDAYAT", "RIKO SETIADI", "SAILILLAH", "SARUL SAPUTRA", "SARWONO", "TAKLIM", "TIVIANSYAH", "TRISNO SUSANTO", "YAHYA MUHAMAD", "OKTA PRDIKA", "M KIKI FIRMANSYAH", "MAWARDAH", "HD"]
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

LIST_KEPERLUAN = ["Tshoot", "Backup", "Support", "PM", "Program BCP", "Program Quikwin", "Program G348T", "Pengiriman Material SPMS", "Pembelian Material"]
SHEET_REQUEST = "Form Request dana"        
SHEET_PJB = "Form PJB"                     
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# ==========================================
# 3. FUNGSI INTI & CACHING SUPER CEPAT
# ==========================================
@st.cache_resource
def get_credentials():
    with open("credentials.json", "w") as f:
        f.write(st.secrets["gcp_json"])
    return Credentials.from_service_account_file("credentials.json", scopes=SCOPES)

@st.cache_data(ttl=10)
def fetch_spreadsheet_data(spreadsheet_id):
    creds = get_credentials()
    client = gspread.authorize(creds)
    ss = client.open_by_key(spreadsheet_id)
    try: req_rows = ss.worksheet(SHEET_REQUEST).get_all_values()
    except: req_rows = []
    try: pjb_rows = ss.worksheet(SHEET_PJB).get_all_values()
    except: pjb_rows = []
    return req_rows, pjb_rows

@st.cache_data
def load_site_data():
    """Fungsi Membaca File Excel Site ID & Koordinat (Khusus Palangkaraya)"""
    try:
        df = pd.read_excel("Hasil_910_Site.xlsx")
        df = df.fillna(0) # Mencegah error jika ada kolom koordinat yang kosong
        site_dict = df.set_index('Site ID')[['Latitude Tujuan', 'Longtitude Tujuan']].to_dict('index')
        return site_dict, df['Site ID'].astype(str).tolist()
    except Exception as e:
        return {}, []

def get_user_tickets_status(nama, req_rows, pjb_rows):
    req_tickets = {}
    for r in req_rows[1:]:
        if len(r) > 5 and r[5].strip().upper() == nama.strip().upper():
            req_tickets[r[3].strip().upper()] = r[1]
    pjb_tickets = set()
    for r in pjb_rows[1:]:
        if len(r) > 21 and r[4].strip().upper() == nama.strip().upper():
            pjb_tickets.add(r[21].strip().upper())
            
    outstanding = []
    history = []
    for tkt, tgl in req_tickets.items():
        if tkt not in pjb_tickets:
            outstanding.append(tkt)
            history.append({"Tiket": tkt, "Tanggal": tgl, "Status": "🔴 Menunggu PJB"})
        else:
            history.append({"Tiket": tkt, "Tanggal": tgl, "Status": "🟢 Selesai"})
    return outstanding, sorted(history, key=lambda x: x["Status"], reverse=True)

def upload_foto(file):
    if file is None: return ""
    try:
        encoded = base64.b64encode(file.getvalue()).decode('utf-8')
        res = cloudinary.uploader.upload(f"data:{file.type};base64,{encoded}", resource_type="auto")
        return res.get("secure_url") 
    except Exception as e:
        st.error(f"Gagal Upload Foto: {e}")
        return ""

def append_data(sheet_name, data, spreadsheet_id):
    creds = get_credentials()
    client = gspread.authorize(creds)
    client.open_by_key(spreadsheet_id).worksheet(sheet_name).append_row(data)
    fetch_spreadsheet_data.clear()

# ==========================================
# 4. SIDEBAR MENU & VALIDASI TRACKING TIKET
# ==========================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2942/2942813.png", width=80)
st.sidebar.title("Navigasi Portal")
menu = st.sidebar.radio("📋 Pilih Transaksi:", ["📝 Form Request Dana", "✅ Form PJB Operasional", "📊 Neraca / Buku Kas (Admin)"])

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 Sistem Cek Status Tiket")
cek_nop = st.sidebar.selectbox("📂 NOP", list(MASTER_DATA.keys()), key="cek_nop")
cek_nama = st.sidebar.selectbox("👤 Nama Anda", MASTER_DATA[cek_nop]["names"], key="cek_nama")

if st.sidebar.button("Cari Histori Saya"):
    req_r, pjb_r = fetch_spreadsheet_data(MASTER_DATA[cek_nop]["spreadsheet_id"])
    out_tkt, hist_tkt = get_user_tickets_status(cek_nama, req_r, pjb_r)
    
    if hist_tkt:
        st.sidebar.dataframe(pd.DataFrame(hist_tkt), hide_index=True)
        if out_tkt: st.sidebar.error(f"⚠️ PERHATIAN: Anda memiliki {len(out_tkt)} tiket yang belum di-PJB-kan!")
        else: st.sidebar.success("✅ Hebat! Seluruh tiket Anda sudah selesai PJB.")
    else:
        st.sidebar.info("Belum ada data pengajuan untuk nama ini.")

# ==========================================
# MENU 1: FORM REQUEST DANA
# ==========================================
if menu == "📝 Form Request Dana":
    st.markdown("<div class='header-card'><h2>📝 Sistem Rekapitulasi Anggaran dan Pertanggungjawaban Informasi</h2><p>Pastikan data yang dimasukkan akurat dan akuntabel.</p></div>", unsafe_allow_html=True)
    nop = st.selectbox("📌 1. Pilih Database Regional (NOP)", list(MASTER_DATA.keys()))
    
    st.markdown("<div class='section-title'>📋 2. Informasi Petugas & Tiket</div>", unsafe_allow_html=True)
    target_ss = MASTER_DATA[nop]["spreadsheet_id"]
    req_r, pjb_r = fetch_spreadsheet_data(target_ss)
    all_requested_tickets = [r[3].strip().upper() for r in req_r[1:] if len(r) > 3]

    # Muat Data Excel Site ID & Koordinat ke Memori (Jika NOP Palangkaraya)
    site_dict, site_list = load_site_data()
    auto_lat = "0"
    auto_long = "0"

    col1, col2 = st.columns(2)
    with col1:
        tanggal = st.date_input("Tanggal Pengajuan")
        cluster = st.selectbox("Cluster Regional", MASTER_DATA[nop]["clusters"])
        nama = st.selectbox("Nama Petugas / Pemohon", MASTER_DATA[nop]["names"])
        outstanding_tkt, _ = get_user_tickets_status(nama, req_r, pjb_r)
        is_locked_user = len(outstanding_tkt) > 0
        tiket = st.text_input("Nomor Tiket SWFM (WAJIB)")
        is_duplicate_ticket = (tiket.strip().upper() in all_requested_tickets) and tiket.strip() != ""
        role = st.selectbox("Role Jabatan", ["PM", "TE", "MBP", "CME"])
        
        # LOGIKA KHUSUS SITE ID (PALANGKARAYA)
        if nop == "Palangkaraya" and len(site_list) > 0:
            site_id = st.selectbox("ID Site / Lokasi", ["-- Pilih Site ID --"] + site_list)
            if site_id != "-- Pilih Site ID --" and site_id in site_dict:
                auto_lat = str(site_dict[site_id].get("Latitude Tujuan", "0"))
                auto_long = str(site_dict[site_id].get("Longtitude Tujuan", "0"))
        else:
            site_id = st.text_input("ID Site / Lokasi")
        
    with col2:
        keperluan = st.selectbox("Klasifikasi Keperluan Dana", LIST_KEPERLUAN)
        kebutuhan = st.number_input("Estimasi Kebutuhan Dana (Rp)", min_value=0, step=1000)
        jns_bbm = st.selectbox("Jenis Kendaraan / BBM", ["Mobil", "motor", "genset"])
        km_awal = st.text_input("Indikator KM Awal (Tulis 0 jika tidak relevan)", value="0")
        plat = st.text_input("Plat Nomor Kendaraan")
        deskripsi = st.text_area("Deskripsi Pekerjaan / Justifikasi")

    st.markdown("<div class='section-title'>📍 3. Data Koordinat & Keuangan</div>", unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    with col3:
        lat_berangkat = st.text_input("Latitude Berangkat", value="0")
        long_berangkat = st.text_input("Longitude Berangkat", value="0")
        rek_penerima = st.selectbox("Bank Penerima / E-Wallet", ["BNI", "BCA", "MANDIRI", "BRI"])
    with col4:
        # OTOMATIS TERISI DARI PILIHAN DROPDOWN SITE ID DI ATAS
        lat_tujuan = st.text_input("Latitude Tujuan", value=auto_lat)
        long_tujuan = st.text_input("Longitude Tujuan", value=auto_long)
        no_rek = st.text_input("Nomor Rekening Tujuan")
        nominal_tf = st.number_input("Total Nominal Transfer (Rp)", min_value=0, step=1000)

    st.markdown("<div class='section-title'>📸 4. Bukti Lampiran Fisik (Evidance)</div>", unsafe_allow_html=True)
    c_up1, c_up2 = st.columns(2)
    with c_up1: foto_km = st.file_uploader("Upload Foto KM Awal", type=["jpg", "png", "jpeg"])
    with c_up2: foto_evidance = st.file_uploader("Upload Foto Kendaraan/Pekerjaan", type=["jpg", "png", "jpeg"])
    
    st.markdown("<br>", unsafe_allow_html=True)

    if is_locked_user or is_duplicate_ticket:
        if is_locked_user:
            st.markdown(f"<div class='locked-box'>⛔ AKSES DITOLAK: Sdr. {nama} memiliki {len(outstanding_tkt)} tiket yang belum dipertanggungjawabkan (PJB).<br>Tiket tertunggak: {', '.join(outstanding_tkt)}.<br>Harap selesaikan Form PJB terlebih dahulu!</div>", unsafe_allow_html=True)
        if is_duplicate_ticket:
            st.warning("⚠️ TIKET GANDA TERDETEKSI: Nomor tiket ini sudah pernah diajukan sebelumnya di dalam sistem!")
        st.info("💡 Hubungi Koordinator untuk mendapatkan izin bypass (membuka blokir).")
        
        input_pass = st.text_input("🔑 Masukkan Password Koordinator untuk Membuka Blokir Khusus:", type="password")
        if input_pass == PASSWORD_KOORDINATOR:
            st.success("✅ Akses Bypass Koordinator Diterima.")
            btn_submit = st.button("🚀 Paksakan Kirim Request Dana", type="primary")
            if btn_submit:
                if not tiket.strip(): st.error("Nomor Tiket SWFM wajib diisi!")
                elif nop == "Palangkaraya" and site_id == "-- Pilih Site ID --": st.error("Site ID wajib dipilih untuk NOP Palangkaraya!")
                else:
                    with st.spinner(f"Memproses pengajuan khusus ke Database {nop}..."):
                        url_km, url_evid = upload_foto(foto_km), upload_foto(foto_evidance)
                        waktu = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        data_req = [waktu, tanggal.strftime("%d/%m/%Y"), nop, tiket, cluster, nama, role, site_id, keperluan, kebutuhan, jns_bbm, deskripsi, km_awal, "", lat_berangkat, long_berangkat, plat, rek_penerima, no_rek, nominal_tf, url_km, url_evid, lat_tujuan, long_tujuan]
                        append_data(SHEET_REQUEST, data_req, target_ss)
                        st.success(f"✅ Transaksi Bypass Berhasil! Tiket {tiket} telah terekam.")
                        time.sleep(2)
                        st.rerun()
    else:
        btn_submit = st.button("🚀 Kirim Form Request Dana", type="primary")
        if btn_submit:
            if not tiket.strip(): st.error("Nomor Tiket SWFM wajib diisi!")
            elif nop == "Palangkaraya" and site_id == "-- Pilih Site ID --": st.error("Site ID wajib dipilih untuk NOP Palangkaraya!")
            else:
                with st.spinner(f"Mengenkripsi & mengirim data ke Database {nop}..."):
                    url_km, url_evid = upload_foto(foto_km), upload_foto(foto_evidance)
                    waktu = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    data_req = [waktu, tanggal.strftime("%d/%m/%Y"), nop, tiket, cluster, nama, role, site_id, keperluan, kebutuhan, jns_bbm, deskripsi, km_awal, "", lat_berangkat, long_berangkat, plat, rek_penerima, no_rek, nominal_tf, url_km, url_evid, lat_tujuan, long_tujuan]
                    append_data(SHEET_REQUEST, data_req, target_ss)
                    st.success(f"✅ Berhasil! Tiket {tiket} telah terekam aman di buku besar operasional.")
                    time.sleep(2)
                    st.rerun()

# ==========================================
# MENU 2: FORM PJB OPERASIONAL
# ==========================================
elif menu == "✅ Form PJB Operasional":
    st.markdown("<div class='header-card' style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);'><h2>✅ SiRAPI Pertanggungjawaban (PJB)</h2><p>Selesaikan pelaporan keuangan tepat waktu untuk membuka kembali akses pengajuan.</p></div>", unsafe_allow_html=True)
    
    col_s1, col_s2, col_s3 = st.columns([2, 3, 1])
    with col_s1: nop_cari = st.selectbox("📂 Pilih Database (NOP):", list(MASTER_DATA.keys()))
    with col_s2: cari_tiket = st.text_input("🔍 Masukkan Nomor Tiket SWFM:")
    with col_s3: 
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        btn_cari = st.button("Tarik Data Tiket", type="primary")
        
    if "pjb_data" not in st.session_state: st.session_state.pjb_data = None

    if btn_cari and cari_tiket:
        with st.spinner(f"Menarik histori tiket '{cari_tiket}' dari Ledger {nop_cari}..."):
            target_ss = MASTER_DATA[nop_cari]["spreadsheet_id"]
            req_r, _ = fetch_spreadsheet_data(target_ss)
            ditemukan = None
            for r in req_r[1:]:
                if len(r) > 3 and r[3].strip().upper() == cari_tiket.strip().upper():
                    ditemukan = {"NOP": r[2], "Cluster": r[4], "Nama": r[5], "Role": r[6], "Site ID": r[7], "Keperluan": r[8], "Jenis BBM": r[10], "Deskripsi": r[11], "Plat": r[16]}
            if ditemukan:
                st.session_state.pjb_data = ditemukan
                st.success("🎉 Histori ditemukan! Sistem akan melakukan *Auto-Fill*.")
            else:
                st.session_state.pjb_data = None
                st.error("❌ Tiket tidak ditemukan. Pastikan NOP dan Nomor Tiket benar.")

    if st.session_state.pjb_data is not None:
        d = st.session_state.pjb_data
        st.markdown("<div class='section-title'>🔒 Data Terenkripsi (Read-Only)</div>", unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        with col_a:
            tanggal_pjb = st.date_input("Tanggal Pelaporan PJB")
            nop_pjb = st.text_input("NOP", value=d["NOP"], disabled=True)
            cluster_pjb = st.text_input("Cluster", value=d["Cluster"], disabled=True)
            nama_pjb = st.text_input("Nama", value=d["Nama"], disabled=True)
            role_pjb = st.text_input("Role", value=d["Role"], disabled=True)
        with col_b:
            site_pjb = st.text_input("Site ID", value=d["Site ID"], disabled=True)
            keperluan_pjb = st.text_input("Keperluan", value=d["Keperluan"], disabled=True)
            jns_bbm_pjb = st.text_input("Jenis BBM", value=d["Jenis BBM"], disabled=True)
            plat_pjb = st.text_input("Plat Nomor", value=d["Plat"], disabled=True)
            deskripsi_pjb = st.text_input("Deskripsi Pekerjaan", value=d["Deskripsi"], disabled=True)
        
        st.markdown("<div class='section-title'>📝 Rincian Realisasi (PJB)</div>", unsafe_allow_html=True)
        col_c, col_d = st.columns(2)
        with col_c:
            km_akhir = st.text_input("Indikator KM Akhir", value="0")
            nominal_pjb = st.number_input("Total Nominal PJB Terpakai (Rp)", min_value=0, step=1000)
            tot_liter = st.text_input("Total Liter / Jumlah Material", value="0")
        with col_d:
            tot_nilai_pjb = st.number_input("Total Nilai Sesuai Nota Faktual (Rp)", min_value=0, step=1000)
            harga_satuan = st.number_input("Harga Satuan (BBM / Material)", min_value=0, step=500)
        
        st.markdown("<div class='section-title'>📸 Lampiran Validasi Nota & Fisik</div>", unsafe_allow_html=True)
        p1, p2, p3 = st.columns(3)
        with p1:
            f_pengisian = st.file_uploader("Evidance Pengisian", type=["jpg","png","jpeg"])
            f_nota_bbm = st.file_uploader("Nota BBM", type=["jpg","png","jpeg"])
            f_nota_km = st.file_uploader("Nota Disanding KM", type=["jpg","png","jpeg"])
        with p2:
            f_material = st.file_uploader("Foto Material", type=["jpg","png","jpeg"])
            f_nota_mat = st.file_uploader("Nota Material Disanding", type=["jpg","png","jpeg"])
        with p3:
            f_penginapan = st.file_uploader("Nota Penginapan", type=["jpg","png","jpeg"])
            f_pekerjaan = st.file_uploader("Evidance Pekerjaan", type=["jpg","png","jpeg"])
        
        st.markdown("<br>", unsafe_allow_html=True)
        submit_pjb = st.button("🚀 Sahkan Pelaporan PJB", type="primary", use_container_width=True)
        
        if submit_pjb:
            with st.spinner("Mengunggah faktur dan mengamankan pelaporan..."):
                target_ss = MASTER_DATA[d["NOP"]]["spreadsheet_id"]
                url_1, url_2, url_3 = upload_foto(f_pengisian), upload_foto(f_nota_bbm), upload_foto(f_nota_km)
                url_4, url_5 = upload_foto(f_material), upload_foto(f_nota_mat)
                url_6, url_7 = upload_foto(f_penginapan), upload_foto(f_pekerjaan)
                waktu_pjb = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                data_pjb = [waktu_pjb, tanggal_pjb.strftime("%d/%m/%Y"), d["NOP"], d["Cluster"], d["Nama"], d["Role"], d["Site ID"], d["Keperluan"], d["Jenis BBM"], d["Deskripsi"], km_akhir, nominal_pjb, d["Plat"], url_1, url_2, url_3, url_4, url_5, url_6, url_7, tot_nilai_pjb, cari_tiket, tot_liter, harga_satuan]
                append_data(SHEET_PJB, data_pjb, target_ss)
                st.success(f"✅ Pelaporan Akuntansi PJB Tiket {cari_tiket} berhasil ditutup!")
                st.session_state.pjb_data = None
                time.sleep(2)
                st.rerun()

# ==========================================
# MENU 3: NERACA / BUKU KAS (ADMIN)
# ==========================================
elif menu == "📊 Neraca / Buku Kas (Admin)":
    st.markdown("<div class='header-card header-admin'><h2>📊 Buku Kas & Neraca Operasional</h2><p>Laporan rekonsiliasi saldo keuangan untuk akses Administrator Khusus Wilayah.</p></div>", unsafe_allow_html=True)
    
    col_adm1, col_adm2 = st.columns([1, 2])
    with col_adm1:
        nop_admin = st.selectbox("📂 Wilayah (NOP):", list(MASTER_DATA.keys()))
    with col_adm2:
        pass_admin = st.text_input(f"🔑 Masukkan Password Admin {nop_admin}:", type="password")
        
    if pass_admin == ADMIN_PASSWORDS[nop_admin]:
        st.success(f"✅ Akses Sistem Keuangan **{nop_admin}** Terbuka!")
        
        st.markdown("<div class='section-title'>📅 1. Filter Periode Pembukuan</div>", unsafe_allow_html=True)
        col_d1, col_d2 = st.columns(2)
        with col_d1: start_date = st.date_input("Dari Tanggal")
        with col_d2: end_date = st.date_input("Sampai Tanggal")
        
        st.markdown("<div class='section-title'>💰 2. Input Dasar Uang Muka (UM)</div>", unsafe_allow_html=True)
        col_u1, col_u2 = st.columns([2, 1])
        with col_u1: um_nobis = st.text_input("Deskripsi / Dasar Dokumen UM (Cth: Nobis Agustus)")
        with col_u2: um_nominal = st.number_input("Nominal Uang Muka (Rp)", min_value=0, step=1000)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Tarik Laporan Neraca & Kalkulasi", type="primary"):
            with st.spinner("Mensinkronisasi buku besar..."):
                target_ss = MASTER_DATA[nop_admin]["spreadsheet_id"]
                _, pjb_rows = fetch_spreadsheet_data(target_ss)
                
                if len(pjb_rows) > 1:
                    cols = ["Waktu Input", "Tanggal PJB", "NOP", "Cluster", "Nama", "Role", "Site ID", "Keperluan", "Jenis BBM", "Deskripsi", "KM Akhir", "Nominal PJB", "Plat", "U1","U2","U3","U4","U5","U6","U7", "Nilai Nota", "Tiket", "Liter", "Harga Satuan"]
                    
                    clean_rows = []
                    for r in pjb_rows[1:]:
                        r_padded = r + [""] * (24 - len(r))
                        clean_rows.append(r_padded[:24])
                        
                    df = pd.DataFrame(clean_rows, columns=cols)
                    df['Tanggal PJB'] = pd.to_datetime(df['Tanggal PJB'], format='%d/%m/%Y', errors='coerce')
                    mask = (df['Tanggal PJB'].dt.date >= start_date) & (df['Tanggal PJB'].dt.date <= end_date)
                    df_filtered = df.loc[mask].copy()
                    
                    df_filtered['Nominal PJB'] = pd.to_numeric(df_filtered['Nominal PJB'], errors='coerce').fillna(0)
                    total_pengeluaran = df_filtered['Nominal PJB'].sum()
                    sisa_saldo = um_nominal - total_pengeluaran
                    
                    st.markdown(f"<div class='section-title'>📉 Ringkasan Saldo Operasional: {um_nobis}</div>", unsafe_allow_html=True)
                    m1, m2, m3 = st.columns(3)
                    m1.metric("💰 Total Uang Muka Masuk", f"Rp {um_nominal:,.0f}")
                    m2.metric("💸 Total PJB (Pengeluaran)", f"Rp {total_pengeluaran:,.0f}")
                    m3.metric("🧾 Sisa Saldo Tersedia", f"Rp {sisa_saldo:,.0f}", delta=sisa_saldo, delta_color="normal")
                    
                    st.markdown("<div class='section-title'>📄 Rincian Pengeluaran PJB</div>", unsafe_allow_html=True)
                    show_df = df_filtered[['Tanggal PJB', 'Tiket', 'Nama', 'Cluster', 'Keperluan', 'Nominal PJB', 'Deskripsi']].copy()
                    show_df['Tanggal PJB'] = show_df['Tanggal PJB'].dt.strftime('%d/%m/%Y')
                    show_df['Nominal PJB'] = show_df['Nominal PJB'].apply(lambda x: f"Rp {x:,.0f}")
                    st.dataframe(show_df, use_container_width=True, hide_index=True)
                else:
                    st.warning("Data PJB pada wilayah ini masih kosong.")
    elif pass_admin != "":
        st.error("❌ Akses Ditolak: Password yang Anda masukkan tidak sesuai untuk wilayah ini.")
