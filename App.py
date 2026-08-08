import streamlit as st
import pandas as pd
import gspread
import base64
import cloudinary
import cloudinary.uploader
import requests
import math
import pydeck as pdk
from google.oauth2.service_account import Credentials
from datetime import datetime
import time

# ==========================================
# 0. KONFIGURASI HALAMAN & UI ELEGAN
# ==========================================
st.set_page_config(page_title="ERP Kinarya Utama Teknik", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
        .main { background-color: #F8FAFC; font-family: 'Inter', 'Segoe UI', sans-serif; }
        .header-card {
            background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
            padding: 30px; border-radius: 16px; color: white; text-align: center;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1); margin-bottom: 30px;
            border-bottom: 4px solid #3B82F6;
        }
        .hub-header { padding-top: 20px; padding-bottom: 30px; text-align: left; }
        .hub-title-main { font-size: 2.2rem; font-weight: 900; color: #1E293B; margin-bottom: 5px; }
        .hub-title-main span { color: #6366F1; }
        .hub-subtitle { font-size: 1rem; color: #64748B; margin-bottom: 20px; }
        
        .hub-card {
            background: #ffffff; border-radius: 20px; padding: 25px 20px; text-align: center;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); border: 1px solid #F1F5F9; 
            transition: all 0.3s ease; display: flex; flex-direction: column; align-items: center; margin-bottom: 15px;
        }
        .hub-card:hover { transform: translateY(-5px); box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); border-color: #E2E8F0; }
        .hub-icon {
            width: 70px; height: 70px; border-radius: 18px; display: flex;
            align-items: center; justify-content: center; font-size: 35px; margin-bottom: 18px;
        }
        .icon-green { background-color: #D1FAE5; color: #10B981; }
        .icon-blue { background-color: #E0F2FE; color: #0EA5E9; }
        .icon-orange { background-color: #FFEDD5; color: #F97316; }
        .icon-purple { background-color: #F3E8FF; color: #A855F7; }
        .hub-card-title { font-size: 1.15rem; font-weight: 800; color: #1E293B; margin-bottom: 8px; }
        .hub-card-desc { font-size: 0.85rem; color: #94A3B8; margin-bottom: 20px; font-weight: 500;}
        .metric-3d {
            background: #ffffff; padding: 25px; border-radius: 16px; text-align: center;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); border: 1px solid #E2E8F0; border-top: 5px solid #3B82F6; margin-bottom: 15px;
        }
        .metric-title { font-size: 0.875rem; color: #64748B; font-weight: 700; text-transform: uppercase; }
        .metric-value { font-size: 1.8rem; color: #0F172A; font-weight: 900; }
        .section-title { color: #1E293B; font-size: 1.25rem; font-weight: 800; border-bottom: 2px solid #E2E8F0; padding-bottom: 8px; margin-top: 30px; margin-bottom: 20px; text-transform: uppercase;}
        .footer-brand { width: 100%; text-align: center; font-size: 13px; color: #94A3B8; margin-top: 50px; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. KONFIGURASI SERVER & MASTER DATA
# ==========================================
AUTHORIZED_PASSWORDS = [
    "B09241925", "B09252588", "B09252589", "B09262648", "B09262667",
    "B09262771", "B09262669", "B09262799", "B09252583", "B0924649",
    "B09252500", "B09252501", "B0922270", "B0924599", "B09241097",
    "B09241113", "B09241115", "B09252576", "B09241146", "B09252184",
    "B09262613", "B09252531", "B09262666", "B09252577"
]
CUTOFF_DATE = datetime(2026, 8, 1).date()

cloudinary.config(cloud_name="fxm61tjv", api_key="624877324969231", api_secret="LIFO6pfEg9fOM3nbsY8FBbVTpSI", secure=True)

MASTER_DATA = {
    "Palangkaraya": {"spreadsheet_id": "1HvgVicTWwO4RMQI6ZR3Mu3IgGicwjcLZl9mDN1auvJU", "clusters": ["Palangkaraya", "Barito Raya"], "names": ["ADI BOWO SANTOSO", "AHMAD", "AHMAD MUZAKIR", "AHMAD SETIAWAN", "ALFI SYAHRI", "ARMADI", "AULIA RAHMAN", "DARLI SUTANTO", "DIDI RIYADI", "FAHMI", "FRANS EJHA ADITYA", "GYLLBRHED ALFARY LOLOMSAIT", "HARUN NURASYID", "HORY YUSMANTO", "INDRA", "JAMES JIMBRIS TAMAILANG", "JUMADI", "KHILAL DAWAI KATIRI", "LEONARD HARA", "M. RIFANI", "MUHAMMAD MUKHLIS", "MUHAMMAD MUKTI", "MUNAWIR AHMAD", "MURJANI", "NURHAYAT", "OKY BANGKIT PAMUNGKAS", "PRADILA KANDI", "PUJIANTO", "PUTRA WARDANA", "REYNALDI RICARDO PUTRA", "RIKI HIDAYAT", "RIKO SETIADI", "SAILILLAH", "SARUL SAPUTRA", "SARWONO", "TAKLIM", "TIVIANSYAH", "TRISNO SUSANTO", "YAHYA MUHAMAD", "OKTA PRDIKA", "M KIKI FIRMANSYAH", "MAWARDAH", "HD"]},
    "Pangkalanbun": {"spreadsheet_id": "1bc0lDhR5iMtXZsKiKIdEwPY8JTaASeHFtaJSeXkywE4", "clusters": ["Ketapang", "Sampit", "Pangkalanbun"], "names": ["RIRIH HARIANTO", "MUKHAMAD ABDUL KHOLIP", "YAMA DEWANTA", "BAGUS SANTOSO", "IMRON SETIAWAN", "JOENDRIS HERDIAN KARA", "STEVEN HERDIAN KARA", "YUDIONO", "DADANG WAHYU SYAHPUTRA", "CAVIN ANDREAN EKA PUTRA", "RAHMAT RIYAN WAHYUDIN", "SUWITO", "DIDIK PRIYONO", "GUNTUR WAHYU PRADANA", "UTI MUHAMMAD KHAIRUL HUDA", "IDRUS MAULANA", "M. RIZKY", "TRIYONO", "ERIK SETIAWAN", "AGUS SUGANDA", "AJI SAPUTRA", "DIAN WAHYUDI", "HAFID BUDIANTO", "IWAN ZAINAL ABIDIN", "DANDI PUTRA", "PONIRAN", "PARYADI KUSUMA", "HERWANI", "DIAN WILDANI", "IPAN HARIONO", "FIRDAUS", "RONI YUDI ISYANTO", "AYU NUR ISLAMIAH", "ARDIANSYAH.", "DAYU SHANDY", "WAHYUDI", "TAJAM SAPUTRA", "MUJHAHID ALWI", "NANDA FIRMANSYAH", "WAHYU RAHMADANI", "TEGUH WICAKSONO", "FERI HARIADI", "NASUKI", "ANDARIANTO PUJI SURO", "BONDAN PRAMUDYA ANANTATUR", "SOLEKHAN", "RIZAL IHZAMAHENDRA", "MUHAMMAD ROIS FERDIANSYAH", "WIDI ARYANTO", "FHANNY AGUSTIAWAN"]},
    "Tarakan": {"spreadsheet_id": "1lRj1YdZGQwY5vHg8P4wudK9V1O_lJuEYjdyHkXoB-Wg", "clusters": ["Tarakan Inner", "Tarakan Outer"], "names": ["HENDRA WIRTASI SIMANULLANG", "ARIZONA ROSADI", "KUKUH BHASKARA", "NATAL SIMBOLON", "HERMAWAN", "IRVAN DINATA VANDITYAWAN", "ENDRAS SAPTA", "AHMADI", "EDI PANJI ERMAYANA", "HANS RISKY RONI TUAH GIRSANG", "IRMANSYAH B. SANGAJI", "REMO REMOLDUS MANALU", "MOHAMMAD RAFAI", "FIRMAN SYAHRUL", "AZMIR", "PETRUS RESI KELORE", "ANIR REZKY", "AHDAN", "PARJON SIMANULLANG", "RUSDI", "HASRIADI", "PURO SUGONDO", "ALIMUDIN M. SAER", "KORNELIUS USI KELORE", "RUSDIANSYAH", "JONTES YUSDA SIMANULLANG", "NANI SETIANINGSIH", "UNGGUL NUGRAHA", "YOGABITA INDOTENO", "JHON KENNEDI SIMANULLANG", "RAFI MUHAMAD SYARIF", "AGRIVA", "SEPTIAN ALVITO", "M. DEDI RIZALDI", "SAHARUDDIN.", "MUHAMMAD RASYID", "SUPRIADI", "JULIMAT SIHITE", "EFNI NURYADIN", "ERWIN SAPUTRA ARIANSYAH", "ALVEUS", "SUPRIADI BANDANGAN"]},
    "Pontianak": {"spreadsheet_id": "1VmoWPImNFMjnaIQpBXEVYdMiTEzsz3P4tpmzfA0EMDE", "clusters": ["Sintang", "Singkawang", "Pontianak"], "names": ["ALOYSIUS", "RUDI", "RONIYANTO", "SUKADI", "HAIRIL", "AZMI ASHADIQI", "SUYADI", "ARIEF DARUL IKHWAN", "MUHAMMAD AL FATAH", "YUDIANSYAH", "RAHMAD INDRA IRAWAN", "MATIUS MARTIN", "RYVAEEL DEWANGGA", "AMIRDA ANGGA SAPUTRA", "IZHARUDDIN", "VINSENSIUS YOGI", "GUSTI ARIZAL", "MUHAMMAD MIFTAHUDIN, A.MD", "BAYU ANGGARA PUTRA", "YONI IRAWAN", "SUGANDI", "IRVAN ANDRIYANA", "ALDIANSYAH", "ABANG HAMDANI", "ABANG KUSDIANSYAH", "SUMAN", "SANGGARA ISMARAWARI", "IBIN", "VALENTINUS PETRO", "DWI KURNIAWAN ISMANTO", "ARISAFRIADI", "DONATUS DONI", "NUR AHMAD KARDIYANTO", "AGRI PERDANA", "AKHSANUL FIKI", "ALI ALAMSYAH", "MUHAMMAD FIRZHA GIANNI HARSYA", "RICKY ARDILAY", "FAISAL", "WIJI SANTOSO", "HISYAM MUTHOYIB", "ARIF RAHMAN NUGROHO", "TOTOK SUGIARTO", "PURWANDI SETIAWAN", "JULIANTO BHAKTI PUTRO, SH", "ILHAMMUDIN", "AGUNG", "ROSIDI", "ABRAR ELZAH FATHALIF", "HENDRI YULIANSYAH", "JAMIL", "GORO SUKARTONO", "OKTAPIANUS JUMIN", "ONNIE SYAEFUDDIN", "BUDI", "ULUL AMRY", "RUHIAT, A.MD", "SUPIANDI", "WAHYUDI", "SUHENDRIK", "M. ARKAM", "SYAFRI APRIJAL", "ARIANTO SUMANTRI", "TUTU AGE ANDIKA", "VIRANDA SAPTA, A.MD", "TOTO HERMANSYAH", "KURNIAWAN", "ROBI ISKANDAR MASDIANSYAH", "MUTIIN CHANDRA", "MISJANI", "KHAIRUL FARISD", "ANDRA", "DODI RATMAYANTO", "WAWAN DARYANA", "MISWARDI", "JUPRILIAUS PICO", "DEDY PURNOMO", "EDI KURNIAWAN", "DEDE GUNAWAN", "WANDALA JAGOARDI PANDALO", "KARIYADI", "REZQI AL BARQAH", "FIRMANSYAH, SP"]}
}

LIST_KEPERLUAN = ["-- Pilih Keperluan --", "Tshoot", "Backup", "Support", "PM", "Program BCP", "Program Quikwin", "Program G348T", "Pengiriman Material SPMS", "Pembelian Material"]
SHEET_REQUEST = "Form Request dana"        
SHEET_PJB = "Form PJB"
SHEET_UM = "Data UM"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# ==========================================
# 3. FUNGSI INTI & CACHING
# ==========================================
def parse_date(date_str):
    try: return datetime.strptime(date_str.strip(), "%d/%m/%Y").date()
    except: return datetime(1970, 1, 1).date()

def clean_nominal(val):
    if pd.isna(val) or val == "": return 0
    v = str(val).replace('Rp', '').replace(' ', '').strip()
    if v.endswith(',00'): v = v[:-3]
    if v.endswith('.00'): v = v[:-3]
    v = v.replace('.', '').replace(',', '')
    try: return int(v)
    except: return 0

def clean_coord(val):
    try:
        if pd.isna(val) or val == "": return 0.0
        return float(str(val).replace(',', '.').strip())
    except: return 0.0

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0 
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

def decode_polyline(polyline_str):
    index, lat, lng, coordinates = 0, 0, 0, []
    while index < len(polyline_str):
        changes = {'lat': 0, 'lng': 0}
        for unit in ['lat', 'lng']:
            shift, result = 0, 0
            while True:
                byte = ord(polyline_str[index]) - 63
                index += 1
                result |= (byte & 0x1f) << shift
                shift += 5
                if not byte >= 0x20: break
            changes[unit] = ~(result >> 1) if (result & 1) else (result >> 1)
        lat += changes['lat']; lng += changes['lng']
        coordinates.append([lng / 100000.0, lat / 100000.0])
    return coordinates

def get_route_and_distance(lon1, lat1, lon2, lat2):
    try:
        url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=simplified"
        res = requests.get(url, timeout=5).json()
        if res.get("code") == "Ok":
            dist_km = res["routes"][0]["distance"] / 1000
            poly = decode_polyline(res["routes"][0]["geometry"])
            return dist_km, poly
    except: pass
    dist_km = haversine(lat1, lon1, lat2, lon2) * 1.3 
    return dist_km, [[lon1, lat1], [lon2, lat2]]

@st.cache_resource
def get_credentials():
    with open("credentials.json", "w") as f: f.write(st.secrets["gcp_json"])
    return Credentials.from_service_account_file("credentials.json", scopes=SCOPES)

@st.cache_data(ttl=10)
def fetch_spreadsheet_data(spreadsheet_id):
    client = gspread.authorize(get_credentials()).open_by_key(spreadsheet_id)
    try: req = client.worksheet(SHEET_REQUEST).get_all_values()
    except: req = []
    try: pjb = client.worksheet(SHEET_PJB).get_all_values()
    except: pjb = []
    try: um = client.worksheet(SHEET_UM).get_all_values()
    except: um = []
    try: rekap = client.worksheet("Rekap PJB").get_all_values()
    except: rekap = []
    return req, pjb, um, rekap

@st.cache_data
def load_excel_data():
    try:
        df_site = pd.read_excel("Hasil_910_Site.xlsx").fillna(0)
        site_dict = df_site.set_index('Site ID')[['Latitude Tujuan', 'Longtitude Tujuan']].to_dict('index')
        site_list = df_site['Site ID'].astype(str).tolist()
    except: site_dict, site_list = {}, []
    try:
        df_tim = pd.read_excel("lonlat tim.xlsx").fillna(0)
        tim_dict = df_tim.set_index('Nama')[['Latitude', 'Longtitude']].to_dict('index')
    except: tim_dict = {}
    return site_dict, site_list, tim_dict

def get_user_tickets_status(nama, req_rows, pjb_rows):
    if nama == "-- Pilih Nama --": return [], [], []
    req_tickets = {}
    for r in req_rows[1:]:
        if len(r) > 5 and r[5].strip().upper() == nama.strip().upper():
            req_tickets[r[3].strip().upper()] = r[1]
                
    pjb_tickets = {r[21].strip().upper() for r in pjb_rows[1:] if len(r) > 21 and r[4].strip().upper() == nama.strip().upper()}
    
    outstanding_all = []    
    outstanding_lock = []   
    history = []
    
    for tkt, tgl in req_tickets.items():
        if tkt not in pjb_tickets:
            outstanding_all.append(tkt)
            if parse_date(tgl) >= CUTOFF_DATE:
                outstanding_lock.append(tkt)
            history.append({"Tiket": tkt, "Tanggal": tgl, "Status": "🔴 Menunggu PJB"})
        else:
            history.append({"Tiket": tkt, "Tanggal": tgl, "Status": "🟢 Selesai"})
            
    return outstanding_all, outstanding_lock, sorted(history, key=lambda x: x["Status"], reverse=True)

def upload_foto(file):
    if file is None: return ""
    try:
        encoded = base64.b64encode(file.getvalue()).decode('utf-8')
        return cloudinary.uploader.upload(f"data:{file.type};base64,{encoded}", resource_type="auto").get("secure_url") 
    except Exception: return ""

def append_data(sheet_name, data, spreadsheet_id):
    gspread.authorize(get_credentials()).open_by_key(spreadsheet_id).worksheet(sheet_name).append_row(data)
    fetch_spreadsheet_data.clear()

# ==========================================
# 4. SIDEBAR & NAVIGASI (RESPONSIVE)
# ==========================================
if 'page' not in st.session_state: st.session_state.page = "🏠 Hub Menu Utama"

try: st.sidebar.image("koperasi-jasa-konstruksi-tower-event-organizer-network-monitoring-telekomunikasi-kisel-group-logo-kut.webp", use_container_width=True)
except: st.sidebar.markdown("<h3 style='text-align:center;'>PT KUT</h3>", unsafe_allow_html=True)
st.sidebar.markdown("<hr>", unsafe_allow_html=True)

if st.sidebar.button("🏠 Home Dashboard", use_container_width=True): st.session_state.page = "🏠 Hub Menu Utama"
if st.sidebar.button("📝 Form Request Dana", use_container_width=True): st.session_state.page = "📝 Form Request Dana"
if st.sidebar.button("✅ Form PJB Operasional", use_container_width=True): st.session_state.page = "✅ Form PJB Operasional"

st.sidebar.markdown("### 📊 MENU ANALITIK (ADMIN)")
st.sidebar.text_input("🔑 Password Akses Analitik:", type="password", key="admin_password")
if st.session_state.get("admin_password") in AUTHORIZED_PASSWORDS:
    st.sidebar.success("✅ Akses Terbuka")
    if st.sidebar.button("📊 Neraca / Buku Kas", use_container_width=True): st.session_state.page = "📊 Neraca / Buku Kas"
    if st.sidebar.button("📈 Live Monitoring", use_container_width=True): st.session_state.page = "📈 Live Monitoring"

st.sidebar.markdown("<div class='footer-brand'>⚙️ Deploy by Okta Pradika</div>", unsafe_allow_html=True)

# ==========================================
# PAGE 0: HUB MENU UTAMA
# ==========================================
if st.session_state.page == "🏠 Hub Menu Utama":
    st.markdown("""
    <div class="hub-header">
        <div class="hub-title-main">Enterprise Analytics <span>Hub</span></div>
        <div class="hub-subtitle">Pilih modul di bawah ini untuk melihat detail dan mengeksekusi operasional departemen.</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="hub-card">
            <div class="hub-icon icon-green">💸</div>
            <div class="hub-card-title">Request Dana</div>
            <div class="hub-card-desc">Pengajuan dana & navigasi jarak</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Masuk Modul Request", use_container_width=True, type="primary"): 
            st.session_state.page = "📝 Form Request Dana"; st.rerun()
            
    with c2:
        st.markdown("""
        <div class="hub-card">
            <div class="hub-icon icon-blue">✅</div>
            <div class="hub-card-title">PJB Operasional</div>
            <div class="hub-card-desc">Realisasi nota & kalkulasi Total KM/RH</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Masuk Modul PJB", use_container_width=True, type="primary"): 
            st.session_state.page = "✅ Form PJB Operasional"; st.rerun()
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("""
        <div class="hub-card">
            <div class="hub-icon icon-orange">📊</div>
            <div class="hub-card-title">Buku Besar / Neraca</div>
            <div class="hub-card-desc">Evaluasi keuangan & histori PJB (Admin)</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Masuk Modul Neraca", use_container_width=True): 
            st.session_state.page = "📊 Neraca / Buku Kas"; st.rerun()
            
    with c4:
        st.markdown("""
        <div class="hub-card">
            <div class="hub-icon icon-purple">📈</div>
            <div class="hub-card-title">Live Monitoring</div>
            <div class="hub-card-desc">Laporan target & analisa SVA (Admin)</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Masuk Modul Live", use_container_width=True): 
            st.session_state.page = "📈 Live Monitoring"; st.rerun()

# ==========================================
# PAGE 1: FORM REQUEST DANA
# ==========================================
elif st.session_state.page == "📝 Form Request Dana":
    st.markdown("<div class='header-card'><h2>📝 PORTAL PENGAJUAN DANA</h2><p>PT Kinarya Utama Teknik - Operational System</p></div>", unsafe_allow_html=True)
    nop = st.selectbox("📌 1. Pilih Database Regional (NOP)", ["-- Pilih NOP --"] + list(MASTER_DATA.keys()))
    
    if nop != "-- Pilih NOP --":
        st.markdown("<div class='section-title'>📋 2. Informasi Petugas & Tiket</div>", unsafe_allow_html=True)
        target_ss = MASTER_DATA[nop]["spreadsheet_id"]
        req_r, pjb_r, _, _ = fetch_spreadsheet_data(target_ss)
        all_requested_tickets = [r[3].strip().upper() for r in req_r[1:] if len(r) > 3]

        site_dict, site_list, tim_dict = load_excel_data()
        auto_lat_tujuan, auto_long_tujuan = "0", "0"
        auto_lat_brgkt, auto_long_brgkt = "0", "0"

        col1, col2 = st.columns(2)
        with col1:
            tanggal = st.date_input("Tanggal Pengajuan")
            cluster = st.selectbox("Cluster Regional", ["-- Pilih Cluster --"] + MASTER_DATA[nop]["clusters"])
            nama = st.selectbox("Nama Petugas / Pemohon", ["-- Pilih Nama --"] + MASTER_DATA[nop]["names"])
            
            # --- AUTO FILL BANK & REKENING ---
            default_bank, default_no_rek = "BNI", ""
            if nama != "-- Pilih Nama --" and nama in tim_dict:
                auto_lat_brgkt = str(tim_dict[nama].get("Latitude", "0"))
                auto_long_brgkt = str(tim_dict[nama].get("Longtitude", "0"))
                for r in reversed(req_r[1:]): 
                    if len(r) > 18 and r[5].strip().upper() == nama.strip().upper():
                        if r[17].strip() in ["BNI", "BCA", "MANDIRI", "BRI"]:
                            default_bank = r[17].strip(); default_no_rek = r[18].strip(); break
                            
            out_all, out_lock, _ = get_user_tickets_status(nama, req_r, pjb_r)
            is_locked_user = len(out_lock) > 0
            tiket = st.text_input("Nomor Tiket SWFM (WAJIB)")
            is_duplicate = (tiket.strip().upper() in all_requested_tickets) and tiket.strip() != ""
            role = st.selectbox("Role Jabatan", ["-- Pilih Role --", "PM", "TE", "MBP", "CME"])
            
            if nop == "Palangkaraya" and len(site_list) > 0:
                site_id = st.selectbox("ID Site / Lokasi", ["-- Pilih Site ID --"] + site_list)
                if site_id != "-- Pilih Site ID --" and site_id in site_dict:
                    auto_lat_tujuan = str(site_dict[site_id].get("Latitude Tujuan", "0"))
                    auto_long_tujuan = str(site_dict[site_id].get("Longtitude Tujuan", "0"))
            else: site_id = st.text_input("ID Site / Lokasi")
            
        with col2:
            keperluan = st.selectbox("Klasifikasi Keperluan Dana", LIST_KEPERLUAN)
            kebutuhan = st.number_input("Estimasi Kebutuhan Dana (Rp)", min_value=0, step=1000)
            
            # --- MENU KENDARAAN, GENSET, DAN LAINNYA ---
            jns_kendaraan = st.selectbox("Jenis Kendaraan / Peralatan", ["-- Pilih Kategori --", "Mobil", "Motor", "Genset", "Lainnya"])
            jenis_bahan_bakar = ""
            if jns_kendaraan.lower() in ["mobil", "motor", "genset"]:
                jenis_bahan_bakar = st.selectbox("Pilih Jenis BBM (Wajib)", ["-- Pilih BBM --", "Pertalite", "Pertamax", "Dexlite", "Bio Solar", "Pertamina Dex"])
                
            final_bbm = f"{jns_kendaraan} - {jenis_bahan_bakar}" if jenis_bahan_bakar else jns_kendaraan
            
            # --- MEMORI RIWAYAT KM / RH GENSET ---
            last_indikator = 0
            if nama != "-- Pilih Nama --" and jns_kendaraan.lower() in ["mobil", "motor", "genset"]:
                for r in reversed(pjb_r[1:]): 
                    if len(r) > 10 and r[4].strip().upper() == nama.strip().upper():
                        if (jns_kendaraan.lower() == "genset" and "genset" in r[8].lower()) or (jns_kendaraan.lower() in ["mobil", "motor"] and any(v in r[8].lower() for v in ["mobil", "motor"])):
                            try:
                                last_indikator = int(clean_nominal(r[10]))
                                break
                            except: pass

            if jns_kendaraan.lower() == "genset":
                st.info(f"⏱️ Histori PJB: RH Genset terakhir Anda adalah **{last_indikator}**")
                label_indikator = "Input RH Genset Awal (Hour)"
            elif jns_kendaraan.lower() in ["mobil", "motor"]:
                st.info(f"🛣️ Histori PJB: KM Kendaraan terakhir Anda adalah **{last_indikator}**")
                label_indikator = "Input KM Awal Kendaraan"
            else:
                label_indikator = "Indikator Awal (Ketik 0 jika tidak relevan)"
                
            km_awal = st.number_input(label_indikator, min_value=0, value=last_indikator)
            plat = st.text_input("Plat Nomor Kendaraan / ID Genset")
            deskripsi = st.text_area("Deskripsi Pekerjaan / Justifikasi")

        is_vehicle = jns_kendaraan.lower() in ['mobil', 'motor']
        st.markdown("<div class='section-title'>📍 3. Rute Peta (Satelit) & Keuangan</div>", unsafe_allow_html=True)
        if not is_vehicle: st.info("ℹ️ Pengisian Koordinat Maps dikunci (0) karena kategori bukan Mobil/Motor.")
        
        col3, col4 = st.columns(2)
        with col3:
            lat_berangkat = st.text_input("Latitude Berangkat (Auto)", value=auto_lat_brgkt if is_vehicle else "0", disabled=not is_vehicle)
            long_berangkat = st.text_input("Longitude Berangkat (Auto)", value=auto_long_brgkt if is_vehicle else "0", disabled=not is_vehicle)
            bank_idx = ["BNI", "BCA", "MANDIRI", "BRI"].index(default_bank) if default_bank in ["BNI", "BCA", "MANDIRI", "BRI"] else 0
            rek_penerima = st.selectbox("Bank Penerima / E-Wallet", ["BNI", "BCA", "MANDIRI", "BRI"], index=bank_idx)
        with col4:
            lat_tujuan = st.text_input("Latitude Tujuan (Auto)", value=auto_lat_tujuan if is_vehicle else "0", disabled=not is_vehicle)
            long_tujuan = st.text_input("Longitude Tujuan (Auto)", value=auto_long_tujuan if is_vehicle else "0", disabled=not is_vehicle)
            no_rek = st.text_input("Nomor Rekening Tujuan", value=default_no_rek)
            nominal_tf = st.number_input("Total Nominal Transfer (Rp)", min_value=0, step=1000)

        jarak_final_text, invalid_coords = "", False
        if is_vehicle:
            c_lat1, c_lon1 = clean_coord(lat_berangkat), clean_coord(long_berangkat)
            c_lat2, c_lon2 = clean_coord(lat_tujuan), clean_coord(long_tujuan)
            if c_lat1 != 0 and c_lon1 != 0 and c_lat2 != 0 and c_lon2 != 0:
                with st.spinner("Satelit sedang menarik data jalan raya..."):
                    jarak_km_oneway, poly_coords = get_route_and_distance(c_lon1, c_lat1, c_lon2, c_lat2)
                jarak_km_pp = jarak_km_oneway * 2
                bbm_req = (jarak_km_pp / 7) if jns_kendaraan.lower() == 'mobil' else (jarak_km_pp / 15)
                jarak_final_text = f"{jarak_km_pp:.1f} Km (PP)"
                
                m1, m2, m3 = st.columns(3)
                m1.markdown(f"<div class='metric-3d'><div class='metric-title'>Jarak Tempuh (PP)</div><div class='metric-value'>{jarak_final_text}</div></div>", unsafe_allow_html=True)
                m2.markdown(f"<div class='metric-3d'><div class='metric-title'>BBM Estimasi (PP)</div><div class='metric-value'>{bbm_req:.1f} Liter</div></div>", unsafe_allow_html=True)
                m3.markdown(f"<div class='metric-3d'><div class='metric-title'>Tipe BBM</div><div class='metric-value'>{(jenis_bahan_bakar or '-').upper()}</div></div>", unsafe_allow_html=True)
            else: invalid_coords = True

        st.markdown("<div class='section-title'>📸 4. Bukti Lampiran Fisik</div>", unsafe_allow_html=True)
        c_up1, c_up2 = st.columns(2)
        with c_up1: foto_km = st.file_uploader("Upload Foto KM / RH Genset Awal", type=["jpg", "png", "jpeg"])
        with c_up2: foto_evidance = st.file_uploader("Upload Foto Kendaraan/Pekerjaan", type=["jpg", "png", "jpeg"])
        
        form_invalid = (nama == "-- Pilih Nama --" or cluster == "-- Pilih Cluster --" or role == "-- Pilih Role --" or keperluan == "-- Pilih Keperluan --" or jns_kendaraan == "-- Pilih Kategori --")
        izin_lanjut = True
        if is_duplicate:
            st.warning("⚠️ DATA DUPLIKAT: Sistem mendeteksi Tiket ini sudah diinput.")
            if not st.checkbox("✅ Ya, saya yakin data ini aman (Revisi/Baru)."): izin_lanjut = False

        if is_locked_user or (is_duplicate and not izin_lanjut):
            if is_locked_user: st.error(f"⛔ AKSES DITOLAK: Sdr. {nama} memiliki {len(out_lock)} tiket yang belum PJB!")
            if st.text_input("🔑 Password Khusus (Bypass):", type="password") in AUTHORIZED_PASSWORDS:
                if st.button("🚀 Paksakan Kirim Request Dana", type="primary"):
                    if form_invalid or not tiket.strip() or invalid_coords: st.error("Lengkapi form!")
                    else:
                        with st.spinner("Processing..."):
                            data_req = [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), tanggal.strftime("%d/%m/%Y"), nop, tiket, cluster, nama, role, site_id, keperluan, kebutuhan, final_bbm, deskripsi, str(km_awal), jarak_final_text, lat_berangkat, long_berangkat, plat, rek_penerima, no_rek, nominal_tf, upload_foto(foto_km), upload_foto(foto_evidance), lat_tujuan, long_tujuan]
                            append_data(SHEET_REQUEST, data_req, target_ss)
                            st.balloons(); st.success("🎉 Berhasil!"); time.sleep(2); st.rerun()
        else:
            if st.button("🚀 Kirim Form Request Dana", type="primary"):
                if form_invalid or not tiket.strip() or invalid_coords: st.error("Lengkapi form!")
                else:
                    with st.spinner("Memproses ke Database..."):
                        data_req = [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), tanggal.strftime("%d/%m/%Y"), nop, tiket, cluster, nama, role, site_id, keperluan, kebutuhan, final_bbm, deskripsi, str(km_awal), jarak_final_text, lat_berangkat, long_berangkat, plat, rek_penerima, no_rek, nominal_tf, upload_foto(foto_km), upload_foto(foto_evidance), lat_tujuan, long_tujuan]
                        append_data(SHEET_REQUEST, data_req, target_ss)
                        st.balloons(); st.success("🎉 Data Anda Berhasil Dikirim!"); time.sleep(2.5); st.rerun()

# ==========================================
# PAGE 2: FORM PJB OPERASIONAL
# ==========================================
elif st.session_state.page == "✅ Form PJB Operasional":
    st.markdown("<div class='header-card' style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); border-bottom: 4px solid #11998e;'><h2>✅ PORTAL PJB (PENYELESAIAN)</h2><p>Lengkapi nota realisasi untuk menghapus status tunggakan.</p></div>", unsafe_allow_html=True)
    nop_cari = st.selectbox("📂 1. Pilih Database (NOP):", ["-- Pilih NOP --"] + list(MASTER_DATA.keys()))
    
    if nop_cari != "-- Pilih NOP --":
        target_ss = MASTER_DATA[nop_cari]["spreadsheet_id"]
        req_r, pjb_r, _, _ = fetch_spreadsheet_data(target_ss)
        pjb_tickets_all = {r[21].strip().upper() for r in pjb_r[1:] if len(r) > 21}
        
        st.markdown("<div class='section-title'>🔍 2. Identifikasi Tim & Tarik Data</div>", unsafe_allow_html=True)
        col_id1, col_id2 = st.columns([2, 2])
        with col_id1: nama_pjb = st.selectbox("👤 Pilih Nama Anda (Otomatis Filter Tiket):", ["-- Pilih Nama --"] + MASTER_DATA[nop_cari]["names"])
        with col_id2: pass_nominal = st.text_input("🔑 Akses Nominal Request (Admin):", type="password")
            
        pending_list, pending_options = [], []
        for r in req_r[1:]:
            if len(r)>5 and r[3].strip() != "" and r[3].strip().upper() not in pjb_tickets_all:
                item = {"Tanggal": r[1], "Nama": r[5], "No Tiket": r[3], "Kategori": r[10] if len(r)>10 else "", "Keperluan": r[8] if len(r)>8 else ""}
                if pass_nominal == "B0924649": item["Nominal Request"] = f"Rp {clean_nominal(r[9]):,.0f}" if len(r)>9 else "Rp 0"
                if nama_pjb != "-- Pilih Nama --":
                    if item["Nama"].strip().upper() == nama_pjb.strip().upper(): pending_list.append(item); pending_options.append(r[3].strip().upper())
                else: pending_list.append(item)
        
        if pending_list: st.dataframe(pd.DataFrame(pending_list), hide_index=True, use_container_width=True)
        else: st.success("✅ Seluruh tiket clear!")
        
        col_s2, col_s3 = st.columns([3, 1])
        with col_s2: 
            pilihan_tiket = st.selectbox("🎫 Pilih Nomor Tiket Pending:", ["-- Pilih Tiket --"] + pending_options + ["-- Ketik Manual --"]) if pending_options else "-- Ketik Manual --"
            cari_tiket = st.text_input("Ketik Manual:") if pilihan_tiket == "-- Ketik Manual --" else ("" if pilihan_tiket == "-- Pilih Tiket --" else pilihan_tiket)
        with col_s3: 
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Tarik Data", type="primary", use_container_width=True) and cari_tiket:
                ditemukan = None
                for r in req_r[1:]:
                    if len(r) > 3 and r[3].strip().upper() == cari_tiket.strip().upper():
                        ditemukan = {"NOP": r[2], "Cluster": r[4], "Nama": r[5], "Role": r[6], "Site": r[7], "Keperluan": r[8], "BBM": r[10], "Desc": r[11], "KMAwal": clean_nominal(r[12]) if len(r)>12 else 0, "NominalReq": clean_nominal(r[9]) if len(r)>9 else 0, "Jarak": r[13] if len(r)>13 else "", "Plat": r[16] if len(r)>16 else ""}
                if ditemukan: st.session_state.pjb_data = ditemukan; st.success("🎉 Data Ditarik!")
                else: st.session_state.pjb_data = None; st.error("❌ Tidak ditemukan.")

        if st.session_state.get("pjb_data"):
            d = st.session_state.pjb_data
            st.markdown("<div class='section-title'>🔒 Rincian Terkunci (Sistem)</div>", unsafe_allow_html=True)
            c_a, c_b = st.columns(2)
            with c_a:
                tgl_pjb = st.date_input("Tanggal PJB")
                st.text_input("Nama Petugas", d["Nama"], disabled=True)
                st.text_input("Kategori & Plat", f'{d["BBM"]} - {d["Plat"]}', disabled=True)
            with c_b:
                st.text_input("Site ID Tujuan", d["Site"], disabled=True)
                st.text_input("Keperluan", d["Keperluan"], disabled=True)
                nominal_pjb = st.number_input("Nominal PJB Terpakai (Otomatis Dikunci)", value=int(d["NominalReq"]), disabled=True)

            st.markdown("<div class='section-title'>📝 Realisasi Lapangan & KM/RH</div>", unsafe_allow_html=True)
            c_c, c_d = st.columns(2)
            
            # --- PENENTUAN LABEL (GENSET ATAU KENDARAAN) ---
            is_genset = "genset" in str(d["BBM"]).lower()
            label_akhir = "RH Genset Akhir" if is_genset else "KM Akhir Kendaraan"
            info_text = "Total Jam Backup (RH)" if is_genset else "Total Perjalanan (KM)"
            icon_text = "⏱️" if is_genset else "🛣️"
            
            with c_c:
                km_akhir = st.number_input(f"{label_akhir} (Wajib Update)", min_value=int(d["KMAwal"]), value=int(d["KMAwal"]))
                total_km_tempuh = km_akhir - int(d["KMAwal"])
                st.info(f"{icon_text} Kalkulasi {info_text}: **{total_km_tempuh}**")
                
            with c_d:
                tot_liter = st.text_input("Total Liter BBM/Material", value="0")
                harga_satuan = st.number_input("Harga Satuan (BBM/Material)", min_value=0, step=500)
                tot_nilai_nota = st.number_input("Total Fisik Sesuai Nota (Rp)", min_value=0, step=1000)
            
            st.markdown("<div class='section-title'>📸 Lampiran Bukti (Foto)</div>", unsafe_allow_html=True)
            p1, p2, p3 = st.columns(3)
            with p1: f_isi = st.file_uploader("Evidance Pengisian", type=["jpg","png"]); f_nota_bbm = st.file_uploader("Nota BBM", type=["jpg","png"])
            with p2: f_mat = st.file_uploader("Foto Material", type=["jpg","png"]); f_notamat = st.file_uploader("Nota Material", type=["jpg","png"])
            with p3: f_inap = st.file_uploader("Nota Penginapan", type=["jpg","png"]); f_kerja = st.file_uploader("Evidance Pekerjaan", type=["jpg","png"]); f_km = st.file_uploader("Foto KM/RH Akhir (Disanding)", type=["jpg","png"])
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 Sahkan Pelaporan PJB", type="primary", use_container_width=True):
                if any(len(r)>21 and r[21].strip().upper() == cari_tiket.strip().upper() and clean_nominal(r[11]) == nominal_pjb for r in pjb_r[1:]):
                    st.error("⛔ Terindikasi Double Input (Tiket & Nominal Sama).")
                else:
                    with st.spinner("Memproses ke Database..."):
                        data_pjb = [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), tgl_pjb.strftime("%d/%m/%Y"), d["NOP"], d["Cluster"], d["Nama"], d["Role"], d["Site"], d["Keperluan"], d["BBM"], d["Desc"], str(km_akhir), nominal_pjb, d["Plat"], upload_foto(f_isi), upload_foto(f_nota_bbm), upload_foto(f_km), upload_foto(f_mat), upload_foto(f_notamat), upload_foto(f_inap), upload_foto(f_kerja), tot_nilai_nota, cari_tiket, tot_liter, harga_satuan, str(total_km_tempuh)]
                        append_data(SHEET_PJB, [(r+[""]*25)[:25] for r in [data_pjb]][0], target_ss)
                        st.balloons(); st.success("🎉 Laporan Berhasil Ditutup!"); st.session_state.pjb_data = None
                        time.sleep(2.5); st.rerun()

# ==========================================
# PAGE 3: NERACA / BUKU KAS
# ==========================================
elif st.session_state.page == "📊 Neraca / Buku Kas":
    st.markdown("<div class='header-card' style='background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); border-bottom: 4px solid #b45309;'><h2>📊 BUKU BESAR & LAPORAN KEUANGAN</h2></div>", unsafe_allow_html=True)
    if st.session_state.get("admin_password") not in AUTHORIZED_PASSWORDS: st.error("⛔ AKSES TERKUNCI: Halaman khusus Admin.")
    else:
        nop_admin = st.selectbox("📂 Wilayah (NOP):", ["-- Pilih NOP --"] + list(MASTER_DATA.keys()))
        if nop_admin != "-- Pilih NOP --":
            target_ss = MASTER_DATA[nop_admin]["spreadsheet_id"]
            st.markdown("<div class='section-title'>📥 1. Input Kas Masuk (Uang Muka)</div>", unsafe_allow_html=True)
            with st.form("form_tambah_um"):
                c_u1, c_u2, c_u3 = st.columns([1, 2, 1])
                with c_u1: tgl_um = st.date_input("Tanggal UM Masuk")
                with c_u2: um_nobis = st.text_input("Ref Dokumen UM")
                with c_u3: um_nominal = st.number_input("Nominal (Rp)", min_value=0, step=1000)
                if st.form_submit_button("💾 Rekam Kas Masuk"):
                    if um_nominal > 0 and um_nobis:
                        append_data(SHEET_UM, [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), tgl_um.strftime("%d/%m/%Y"), um_nobis, um_nominal], target_ss); st.success("✅ Terekam!"); time.sleep(1); st.rerun()
                    
            _, req_r, pjb_r, um_r, rekap_r = None, *fetch_spreadsheet_data(target_ss)
            unique_periode = list(set([r[16].strip() for r in rekap_r[1:] if len(r) > 16 and r[16].strip() != ""]))
            
            st.markdown("<div class='section-title'>📅 2. Filter Laporan Keuangan</div>", unsafe_allow_html=True)
            c_d1, c_d2, c_d3 = st.columns(3)
            with c_d1: start_date = st.date_input("Dari Tanggal")
            with c_d2: end_date = st.date_input("Sampai")
            with c_d3: filter_q_neraca = st.selectbox("📌 Filter Sinkronisasi Kolom Q", ["-- Semua Periode --"] + sorted(unique_periode))
            
            if st.button("🔄 Buat Laporan", type="primary", use_container_width=True):
                with st.spinner("Mengkompilasi Data..."):
                    tot_um = 0
                    if len(um_r) > 1:
                        df_um = pd.DataFrame(um_r[1:], columns=["Waktu", "Tanggal", "Deskripsi", "Nominal"])
                        df_um['Tanggal_Real'] = pd.to_datetime(df_um['Tanggal'], format='%d/%m/%Y', errors='coerce')
                        tot_um = df_um[(df_um['Tanggal_Real'].dt.date >= start_date) & (df_um['Tanggal_Real'].dt.date <= end_date)]['Nominal'].apply(clean_nominal).sum()
                    
                    tot_pjb = sum([clean_nominal(r[15]) for r in rekap_r[1:] if len(r) > 16 and (r[16].strip() == filter_q_neraca or filter_q_neraca == "-- Semua Periode --")]) if len(rekap_r)>1 else 0
                    
                    t1, t2 = st.tabs(["📊 Executive Summary", "📓 Buku Besar (PJB History)"])
                    with t1:
                        m1, m2, m3 = st.columns(3)
                        m1.markdown(f"<div class='metric-3d'><div class='metric-title'>Kas Masuk</div><div class='metric-value'>Rp {tot_um:,.0f}</div></div>", unsafe_allow_html=True)
                        m2.markdown(f"<div class='metric-3d'><div class='metric-title'>Penyerapan</div><div class='metric-value'>Rp {tot_pjb:,.0f}</div></div>", unsafe_allow_html=True)
                        m3.markdown(f"<div class='metric-3d'><div class='metric-title'>Sisa Kas</div><div class='metric-value'>Rp {tot_um - tot_pjb:,.0f}</div></div>", unsafe_allow_html=True)
                    with t2:
                        if len(pjb_r) > 1:
                            df_p = pd.DataFrame([(r + [""] * 25)[:25] for r in pjb_r[1:]], columns=["Waktu","Tanggal","N","C","Nama","R","S","Keperluan","B","D","K","Nominal","Pl","u1","u2","u3","u4","u5","u6","u7","NN","NoTiket","Lt","Hs","TKM_RH"])
                            df_p['Nominal'] = df_p['Nominal'].apply(clean_nominal)
                            st.dataframe(df_p[['Tanggal', 'NoTiket', 'Nama', 'Keperluan', 'TKM_RH', 'Nominal']], use_container_width=True)

# ==========================================
# PAGE 4: LIVE MONITORING
# ==========================================
elif st.session_state.page == "📈 Live Monitoring":
    st.markdown("<div class='header-card' style='background: linear-gradient(135deg, #020617 0%, #0F172A 100%); color:#10B981; border-bottom: 4px solid #10B981;'><h2>📈 LIVE FINANCIAL MONITORING</h2></div>", unsafe_allow_html=True)
    if st.session_state.get("admin_password") not in AUTHORIZED_PASSWORDS: st.error("⛔ AKSES TERKUNCI")
    else:
        nop_live = st.selectbox("🌐 Market (NOP):", ["-- Pilih NOP --"] + list(MASTER_DATA.keys()))
        if nop_live != "-- Pilih NOP --":
            _, req_r, pjb_r, um_r, rekap_r = None, *fetch_spreadsheet_data(MASTER_DATA[nop_live]["spreadsheet_id"])
            c1, c2 = st.columns(2)
            with c1: start_live = st.date_input("Mulai")
            with c2: end_live = st.date_input("Hingga")
            if st.button("📊 AKTIFKAN RADAR", type="primary", use_container_width=True):
                total_um = sum([clean_nominal(r[3]) for r in um_r[1:] if len(r)>3]) if len(um_r)>1 else 0
                tot_serap = sum([clean_nominal(r[15]) for r in rekap_r[1:] if len(r)>15]) if len(rekap_r)>1 else 0
                st.markdown(f"<div style='background-color:#0F172A; padding:40px; border-radius:16px; border:1px solid #334155; text-align:center;'><h3 style='color:#94A3B8;'>EQUITY / SISA KAS</h3><h1 style='color:#10B981; font-size:60px;'>Rp {total_um - tot_serap:,.0f}</h1></div>", unsafe_allow_html=True)
