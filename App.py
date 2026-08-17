import streamlit as st
import pandas as pd
import gspread
import base64
import cloudinary
import cloudinary.uploader
import requests
import math
from google.oauth2.service_account import Credentials
from datetime import datetime
import time
import re

# ==========================================
# 0. KONFIGURASI HALAMAN & SUPER PREMIUM UI
# ==========================================
st.set_page_config(page_title="SiRAPI Enterprise", page_icon="💎", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800;900&display=swap');
        
        .main { background: #f4f7f6; font-family: 'Plus Jakarta Sans', sans-serif; }
        
        /* Premium Header Card */
        .header-card {
            background: linear-gradient(135deg, #0F2027 0%, #203A43 50%, #2C5364 100%);
            padding: 35px 20px; border-radius: 20px; color: white; text-align: center;
            box-shadow: 0 15px 30px rgba(0,0,0,0.2); margin-bottom: 30px;
            border-bottom: 5px solid #00F2FE;
        }
        .header-card h1 { font-weight: 900; font-size: 2.2rem; margin-bottom: 5px; }
        .header-card p { font-size: 1rem; color: #cbd5e1; margin-bottom: 0; }
        
        /* Mobile Friendly Menu Buttons */
        div[data-testid="stButton"] > button {
            background: rgba(255, 255, 255, 0.95) !important;
            border: 1px solid #e2e8f0 !important; border-radius: 16px !important;
            box-shadow: 0 8px 15px rgba(0,0,0,0.05) !important;
            height: auto !important; padding: 20px 10px !important;
            transition: all 0.3s ease !important;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
        }
        div[data-testid="stButton"] > button:hover, div[data-testid="stButton"] > button:active {
            background: linear-gradient(135deg, #4FACFE 0%, #00F2FE 100%) !important;
            transform: translateY(-5px) !important; border: none !important;
        }
        div[data-testid="stButton"] > button p { color: #1e293b !important; font-size: 1.1rem !important; font-weight: 800 !important; margin:0; text-align:center; }
        div[data-testid="stButton"] > button:hover p, div[data-testid="stButton"] > button:active p { color: white !important; }
        
        /* Admin Button Specific */
        .btn-admin div[data-testid="stButton"] > button {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important;
        }
        .btn-admin div[data-testid="stButton"] > button p { color: white !important; font-size: 1rem !important;}
        .btn-admin div[data-testid="stButton"] > button:hover { background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%) !important; }
        
        /* Section Titles */
        .section-title { color: #0F2027; font-size: 1.2rem; font-weight: 900; border-bottom: 3px solid #cbd5e1; padding-bottom: 8px; margin-top: 25px; margin-bottom: 20px;}
        
        /* Metric Cards */
        .metric-3d {
            background: white; padding: 20px; border-radius: 16px; text-align: center;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.05); border-top: 5px solid #4FACFE; margin-bottom: 15px;
        }
        .metric-title { font-size: 0.8rem; color: #64748b; font-weight: 800; text-transform: uppercase; }
        .metric-value { font-size: 1.6rem; font-weight: 900; margin-top: 5px; color: #0F2027;}
        
        /* Hide Sidebar completely for mobile purity */
        [data-testid="collapsedControl"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. MASTER DATA & KONFIGURASI
# ==========================================
AUTHORIZED_PASSWORDS = [
    "B09241925", "B09252588", "B09252589", "B09262648", "B09262667",
    "B09262771", "B09262669", "B09262799", "B09252583", "B0924649",
    "B09252500", "B09252501", "B0922270", "B0924599", "B09241097",
    "B09241113", "B09241115", "B09252576", "B09241146", "B09252184",
    "B09262613", "B09252531", "B09262666", "B09252577", "Yui2025",
]
CUTOFF_DATE = datetime(2026, 8, 1).date()

cloudinary.config(cloud_name="fxm61tjv", api_key="624877324969231", api_secret="LIFO6pfEg9fOM3nbsY8FBbVTpSI", secure=True)

SHEET_REQUEST = "Form Request dana"        
SHEET_PJB = "Form PJB"
SHEET_UM = "Data UM"
SHEET_DISTRIBUSI = "Distribusi UM"
SHEET_APP = "Approval BBM"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

MASTER_DATA = {
    "Palangkaraya": {"spreadsheet_id": "1HvgVicTWwO4RMQI6ZR3Mu3IgGicwjcLZl9mDN1auvJU", "clusters": ["Palangkaraya", "Barito Raya"], "names": ["ADI BOWO SANTOSO", "AHMAD", "AHMAD MUZAKIR", "AHMAD SETIAWAN", "ALFI SYAHRI", "ARMADI", "AULIA RAHMAN", "DARLI SUTANTO", "DIDI RIYADI", "FAHMI", "FRANS EJHA ADITYA", "GYLLBRHED ALFARY LOLOMSAIT", "HARUN NURASYID", "HORY YUSMANTO", "INDRA", "JAMES JIMBRIS TAMAILANG", "JUMADI", "KHILAL DAWAI KATIRI", "LEONARD HARA", "M. RIFANI", "MUHAMMAD MUKHLIS", "MUHAMMAD MUKTI", "MUNAWIR AHMAD", "MURJANI", "NURHAYAT", "OKY BANGKIT PAMUNGKAS", "PRADILA KANDI", "PUJIANTO", "PUTRA WARDANA", "REYNALDI RICARDO PUTRA", "RIKI HIDAYAT", "RIKO SETIADI", "SAILILLAH", "SARUL SAPUTRA", "SARWONO", "TAKLIM", "TIVIANSYAH", "TRISNO SUSANTO", "YAHYA MUHAMAD", "OKTA PRDIKA", "M KIKI FIRMANSYAH", "MAWARDAH", "HD"]},
    "Pangkalanbun": {"spreadsheet_id": "1bc0lDhR5iMtXZsKiKIdEwPY8JTaASeHFtaJSeXkywE4", "clusters": ["Ketapang", "Sampit", "Pangkalanbun"], "names": ["RIRIH HARIANTO", "MUKHAMAD ABDUL KHOLIP", "YAMA DEWANTA", "BAGUS SANTOSO", "IMRON SETIAWAN", "JOENDRIS HERDIAN KARA", "STEVEN HERDIAN KARA", "YUDIONO", "DADANG WAHYU SYAHPUTRA", "CAVIN ANDREAN EKA PUTRA", "RAHMAT RIYAN WAHYUDIN", "SUWITO", "DIDIK PRIYONO", "GUNTUR WAHYU PRADANA", "UTI MUHAMMAD KHAIRUL HUDA", "IDRUS MAULANA", "M. RIZKY", "TRIYONO", "ERIK SETIAWAN", "AGUS SUGANDA", "AJI SAPUTRA", "DIAN WAHYUDI", "HAFID BUDIANTO", "IWAN ZAINAL ABIDIN", "DANDI PUTRA", "PONIRAN", "PARYADI KUSUMA", "HERWANI", "DIAN WILDANI", "IPAN HARIONO", "FIRDAUS", "RONI YUDI ISYANTO", "AYU NUR ISLAMIAH", "ARDIANSYAH.", "DAYU SHANDY", "WAHYUDI", "TAJAM SAPUTRA", "MUJHAHID ALWI", "NANDA FIRMANSYAH", "WAHYU RAHMADANI", "TEGUH WICAKSONO", "FERI HARIADI", "NASUKI", "ANDARIANTO PUJI SURO", "BONDAN PRAMUDYA ANANTATUR", "SOLEKHAN", "RIZAL IHZAMAHENDRA", "MUHAMMAD ROIS FERDIANSYAH", "WIDI ARYANTO", "FHANNY AGUSTIAWAN"]},
    "Tarakan": {"spreadsheet_id": "1lRj1YdZGQwY5vHg8P4wudK9V1O_lJuEYjdyHkXoB-Wg", "clusters": ["Tarakan Inner", "Tarakan Outer"], "names": ["HENDRA WIRTASI SIMANULLANG", "ARIZONA ROSADI", "KUKUH BHASKARA", "NATAL SIMBOLON", "HERMAWAN", "IRVAN DINATA VANDITYAWAN", "ENDRAS SAPTA", "AHMADI", "EDI PANJI ERMAYANA", "HANS RISKY RONI TUAH GIRSANG", "IRMANSYAH B. SANGAJI", "REMO REMOLDUS MANALU", "MOHAMMAD RAFAI", "FIRMAN SYAHRUL", "AZMIR", "PETRUS RESI KELORE", "ANIR REZKY", "AHDAN", "PARJON SIMANULLANG", "RUSDI", "HASRIADI", "PURO SUGONDO", "ALIMUDIN M. SAER", "KORNELIUS USI KELORE", "RUSDIANSYAH", "JONTES YUSDA SIMANULLANG", "NANI SETIANINGSIH", "UNGGUL NUGRAHA", "YOGABITA INDOTENO", "JHON KENNEDI SIMANULLANG", "RAFI MUHAMAD SYARIF", "AGRIVA", "SEPTIAN ALVITO", "M. DEDI RIZALDI", "SAHARUDDIN.", "MUHAMMAD RASYID", "SUPRIADI", "JULIMAT SIHITE", "EFNI NURYADIN", "ERWIN SAPUTRA ARIANSYAH", "ALVEUS", "SUPRIADI BANDANGAN"]},
    "Pontianak": {"spreadsheet_id": "1VmoWPImNFMjnaIQpBXEVYdMiTEzsz3P4tpmzfA0EMDE", "clusters": ["Sintang", "Singkawang", "Pontianak"], "names": ["ALOYSIUS", "RUDI", "RONIYANTO", "SUKADI", "HAIRIL", "AZMI ASHADIQI", "SUYADI", "ARIEF DARUL IKHWAN", "MUHAMMAD AL FATAH", "YUDIANSYAH", "RAHMAD INDRA IRAWAN", "MATIUS MARTIN", "RYVAEEL DEWANGGA", "AMIRDA ANGGA SAPUTRA", "IZHARUDDIN", "VINSENSIUS YOGI", "GUSTI ARIZAL", "MUHAMMAD MIFTAHUDIN, A.MD", "BAYU ANGGARA PUTRA", "YONI IRAWAN", "SUGANDI", "IRVAN ANDRIYANA", "ALDIANSYAH", "ABANG HAMDANI", "ABANG KUSDIANSYAH", "SUMAN", "SANGGARA ISMARAWARI", "IBIN", "VALENTINUS PETRO", "DWI KURNIAWAN ISMANTO", "ARISAFRIADI", "DONATUS DONI", "NUR AHMAD KARDIYANTO", "AGRI PERDANA", "AKHSANUL FIKI", "ALI ALAMSYAH", "MUHAMMAD FIRZHA GIANNI HARSYA", "RICKY ARDILAY", "FAISAL", "WIJI SANTOSO", "HISYAM MUTHOYIB", "ARIF RAHMAN NUGROHO", "TOTOK SUGIARTO", "PURWANDI SETIAWAN", "JULIANTO BHAKTI PUTRO, SH", "ILHAMMUDIN", "AGUNG", "ROSIDI", "ABRAR ELZAH FATHALIF", "HENDRI YULIANSYAH", "JAMIL", "GORO SUKARTONO", "OKTAPIANUS JUMIN", "ONNIE SYAEFUDDIN", "BUDI", "ULUL AMRY", "RUHIAT, A.MD", "SUPIANDI", "WAHYUDI", "SUHENDRIK", "M. ARKAM", "SYAFRI APRIJAL", "ARIANTO SUMANTRI", "TUTU AGE ANDIKA", "VIRANDA SAPTA, A.MD", "TOTO HERMANSYAH", "KURNIAWAN", "ROBI ISKANDAR MASDIANSYAH", "MUTIIN CHANDRA", "MISJANI", "KHAIRUL FARISD", "ANDRA", "DODI RATMAYANTO", "WAWAN DARYANA", "MISWARDI", "JUPRILIAUS PICO", "DEDY PURNOMO", "EDI KURNIAWAN", "DEDE GUNAWAN", "WANDALA JAGOARDI PANDALO", "KARIYADI", "REZQI AL BARQAH", "FIRMANSYAH, SP"]}
}
LIST_KEPERLUAN = ["", "Tshoot", "Backup", "Support", "PM", "Program BCP", "Program Quikwin", "Program G348T", "Pengiriman Material SPMS", "Pembelian Material","Transportasi Air"]

# ==========================================
# 2. FUNGSI INTI & CACHING 
# ==========================================
def parse_date(date_str):
    try: return datetime.strptime(str(date_str).strip(), "%d/%m/%Y").date()
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

@st.cache_data(ttl=600) # Diperpanjang jadi 10 menit agar super cepat
def fetch_spreadsheet_data(spreadsheet_id):
    client = gspread.authorize(get_credentials()).open_by_key(spreadsheet_id)
    ws_names = [SHEET_REQUEST, SHEET_PJB, SHEET_UM, SHEET_DISTRIBUSI, SHEET_APP, "Rekap PJB"]
    data = {}
    for name in ws_names:
        try: data[name] = client.worksheet(name).get_all_values()
        except: data[name] = []
    return data

@st.cache_data(ttl=600)
def load_excel_data():
    try:
        df_site = pd.read_excel("Hasil_910_Site.xlsx").fillna(0)
        site_dict = df_site.set_index('Site ID')[['Latitude Tujuan', 'Longtitude Tujuan']].to_dict('index')
        site_list = df_site['Site ID'].astype(str).tolist()
    except: site_dict, site_list = {}, []
    
    tim_dict, list_nopol = {}, []
    try:
        df_tim = pd.read_excel("lonlat tim.xlsx").fillna(0)
        for _, row in df_tim.iterrows():
            nama_key = str(row['Nama']).strip().upper()
            tim_dict[nama_key] = {'Latitude': row.get('Latitude', 0), 'Longtitude': row.get('Longtitude', 0)}
    except: pass
        
    try:
        df_nopol = pd.read_csv("DATA NOPOL MOBIL DAN GENSET NOP PLK.csv", sep=None, engine='python')
        if 'NOPOL' not in df_nopol.columns and 'PIC' not in df_nopol.columns:
            df_nopol.columns = df_nopol.iloc[0].astype(str).str.strip()
            df_nopol = df_nopol[1:].reset_index(drop=True)
            
        df_nopol = df_nopol.fillna("")
        if 'NOPOL' in df_nopol.columns:
            list_nopol_raw = df_nopol['NOPOL'].astype(str).unique().tolist()
            list_nopol = sorted([n for n in list_nopol_raw if n.strip() not in ["", "0", "nan", "None", "NOPOL"]])
            for _, row in df_nopol.iterrows():
                if 'PIC' in df_nopol.columns:
                    pic_name = str(row['PIC']).strip().upper()
                    nopol_val = str(row['NOPOL']).strip()
                    if pic_name and pic_name not in tim_dict: tim_dict[pic_name] = {'Latitude': 0, 'Longtitude': 0}
                    if pic_name: tim_dict[pic_name]['NOPOL'] = nopol_val
    except Exception: pass
    return site_dict, site_list, tim_dict, list_nopol

def get_user_tickets_status(nama, req_rows, pjb_rows, app_rows):
    if nama == "-- Pilih Nama --" or nama == "": return [], [], [], []
    req_tickets = {}
    for r in req_rows[1:]:
        if len(r) > 5 and r[5].strip().upper() == nama.strip().upper():
            tk_raw = r[3].strip().upper()
            if tk_raw != "": req_tickets[tk_raw] = r[1]
                
    pjb_tickets = {r[21].strip().upper() for r in pjb_rows[1:] if len(r) > 21 and r[4].strip().upper() == nama.strip().upper() and r[21].strip() != ""}
    pjb_app_status = {}
    
    for r in app_rows[1:]:
        if len(r) > 5 and r[3] == "Verifikasi PJB":
            tiket_app = r[2].strip().upper()
            if tiket_app != "": pjb_app_status[tiket_app] = {"status": r[5].strip(), "catatan": r[6] if len(r)>6 else ""}

    outstanding_all, outstanding_lock, aging_august, history = [], [], [], []
    today = datetime.now().date()
    
    for tkt, tgl in req_tickets.items():
        if tkt not in pjb_tickets:
            outstanding_all.append(tkt)
            req_date = parse_date(tgl)
            if req_date >= CUTOFF_DATE: outstanding_lock.append(tkt)
            aging_days = (today - req_date).days
            if req_date.month == 8 and aging_days > 3:
                aging_august.append(tkt)
                history.append({"Tiket": tkt, "Tanggal": tgl, "Status": f"🚨 Telat {aging_days} Hari"})
            else: history.append({"Tiket": tkt, "Tanggal": tgl, "Status": "🔴 Menunggu PJB"})
        else:
            app_data = pjb_app_status.get(tkt, {"status": "APPROVED", "catatan": ""})
            if app_data["status"] == "PENDING":
                outstanding_all.append(tkt); outstanding_lock.append(tkt)
                history.append({"Tiket": tkt, "Tanggal": tgl, "Status": "⏳ Menunggu Verifikasi Admin"})
            elif app_data["status"] == "REJECTED":
                outstanding_all.append(tkt); outstanding_lock.append(tkt)
                history.append({"Tiket": tkt, "Tanggal": tgl, "Status": f"❌ DITOLAK: {app_data['catatan']}"})
            else: history.append({"Tiket": tkt, "Tanggal": tgl, "Status": "🟢 Selesai"})
            
    return outstanding_all, outstanding_lock, aging_august, sorted(history, key=lambda x: x["Status"], reverse=True)

def upload_foto(file):
    if file is None: return ""
    try:
        encoded = base64.b64encode(file.getvalue()).decode('utf-8')
        return cloudinary.uploader.upload(f"data:{file.type};base64,{encoded}", resource_type="auto").get("secure_url") 
    except Exception: return ""

def append_data(sheet_name, data, spreadsheet_id):
    gspread.authorize(get_credentials()).open_by_key(spreadsheet_id).worksheet(sheet_name).append_row(data)
    fetch_spreadsheet_data.clear()

def update_approval_status(spreadsheet_id, row_index, new_status, remark="-"):
    try:
        client = gspread.authorize(get_credentials()).open_by_key(spreadsheet_id)
        ws = client.worksheet(SHEET_APP)
        ws.update_cell(row_index + 1, 6, new_status)
        ws.update_cell(row_index + 1, 7, remark)
        fetch_spreadsheet_data.clear()
    except: pass

# ==========================================
# INISIALISASI SESSION STATE & NAVIGASI
# ==========================================
if 'page' not in st.session_state: st.session_state.page = "🏠 Hub Menu Utama"
if 'admin_logged_in' not in st.session_state: st.session_state.admin_logged_in = False

# TOMBOL KEMBALI UNIVERSAL (Muncul di semua page kecuali Hub)
if st.session_state.page != "🏠 Hub Menu Utama":
    if st.button("⬅️ KEMBALI KE MENU UTAMA", use_container_width=True):
        st.session_state.page = "🏠 Hub Menu Utama"
        st.rerun()
    st.markdown("<hr style='margin: 10px 0 30px 0;'>", unsafe_allow_html=True)


# ==========================================
# PAGE 0: HUB MENU UTAMA (1-SCREEN DASHBOARD)
# ==========================================
if st.session_state.page == "🏠 Hub Menu Utama":
    st.markdown("""
        <div class="header-card">
            <h1>SiRAPI Enterprise</h1>
            <p>Sistem Rekapitulasi Anggaran Pertanggungjawaban Informasi</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='section-title'>🚀 MENU OPERASIONAL TIM</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("💸\nREQUEST DANA\n(Pengajuan Baru)", use_container_width=True): st.session_state.page = "📝 Form Request Dana"; st.rerun()
    with c2:
        if st.button("✅\nPJB OPERASIONAL\n(Nota Realisasi)", use_container_width=True): st.session_state.page = "✅ Form PJB Operasional"; st.rerun()

    st.markdown("<div class='section-title'>🔍 CEK STATUS TIKET PRIBADI</div>", unsafe_allow_html=True)
    with st.expander("Buka untuk Cek Status Tiket Anda", expanded=False):
        cek_nop = st.selectbox("Pilih Area Wilayah", ["-- Pilih Area --"] + list(MASTER_DATA.keys()), key="cek_area_hub")
        if cek_nop != "-- Pilih Area --":
            cek_nama = st.selectbox("Nama Petugas", ["-- Pilih Nama --"] + MASTER_DATA[cek_nop]["names"], key="cek_nama_hub")
            if st.button("Cari Status", use_container_width=True):
                if cek_nama != "-- Pilih Nama --" and cek_nama != "":
                    with st.spinner("Menarik data server..."):
                        data_cek = fetch_spreadsheet_data(MASTER_DATA[cek_nop]["spreadsheet_id"])
                        out_all, out_lock, aging_august, hist_tkt = get_user_tickets_status(cek_nama, data_cek[SHEET_REQUEST], data_cek[SHEET_PJB], data_cek[SHEET_APP])
                    
                    if hist_tkt:
                        st.dataframe(pd.DataFrame(hist_tkt), hide_index=True, use_container_width=True)
                        if aging_august: st.warning(f"🔔 Ada {len(aging_august)} tiket tertunda >3 Hari. Tolong di-PJB!")
                        if out_all: st.error(f"⚠️ {len(out_all)} Tiket memblokir status Anda (Belum PJB / Pending Verifikasi).")
                        else: st.success("✅ Seluruh tiket aman dan Approved!")
                    else: st.info("Tidak ada data / belum pernah request.")

    st.markdown("<div class='section-title'>🛡️ MENU KHUSUS ADMIN</div>", unsafe_allow_html=True)
    if not st.session_state.admin_logged_in:
        pass_input = st.text_input("Masukkan Password Admin:", type="password")
        if st.button("Buka Kunci Akses Admin"):
            if pass_input in AUTHORIZED_PASSWORDS:
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("Password Salah!")
    else:
        st.success("✅ Akses Admin Terbuka")
        if st.button("🔒 Keluar Mode Admin"):
            st.session_state.admin_logged_in = False
            st.rerun()
            
        st.markdown("<div class='btn-admin'>", unsafe_allow_html=True)
        c_a1, c_a2 = st.columns(2)
        with c_a1:
            if st.button("🛡️ APPROVAL CENTER\n(Validasi PJB)", use_container_width=True): st.session_state.page = "🛡️ Approval Center"; st.rerun()
            if st.button("📈 LIVE MONITORING\n(Dashboard Analisa)", use_container_width=True): st.session_state.page = "📈 Live Monitoring"; st.rerun()
        with c_a2:
            if st.button("🏦 MANAJEMEN KAS\n(Distribusi Dana)", use_container_width=True): st.session_state.page = "🏦 Manajemen Kas & Distribusi"; st.rerun()
            if st.button("🖨️ REPORT & AUTO PJB\n(Export Laporan)", use_container_width=True): st.session_state.page = "🖨️ Auto PJB Report"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='text-align: center; color: #94a3b8; font-size: 0.8rem; margin-top:40px;'>v5.0 Enterprise Mobile Edition</div>", unsafe_allow_html=True)


# ==========================================
# PAGE 1: FORM REQUEST DANA
# ==========================================
elif st.session_state.page == "📝 Form Request Dana":
    st.markdown("<div class='header-card'><h2>📝 PORTAL REQUEST DANA</h2><p>Pengajuan Baru / Revisi</p></div>", unsafe_allow_html=True)
    
    nop = st.selectbox("📌 1. Pilih Database Regional (NOP)", [""] + list(MASTER_DATA.keys()))
    
    if nop != "":
        st.markdown("<div class='section-title'>📋 2. Informasi Petugas & Tiket</div>", unsafe_allow_html=True)
        target_ss = MASTER_DATA[nop]["spreadsheet_id"]
        
        # Penarikan data dipercepat dengan cache yang sudah dinaikkan TTL-nya
        data_all = fetch_spreadsheet_data(target_ss)
        req_r, pjb_r, app_r = data_all[SHEET_REQUEST], data_all[SHEET_PJB], data_all[SHEET_APP]
        
        all_requested_tickets = [r[3].strip().upper() for r in req_r[1:] if len(r) > 3]
        site_dict, site_list, tim_dict, list_nopol = load_excel_data()
        auto_lat_tujuan, auto_long_tujuan, auto_lat_brgkt, auto_long_brgkt = "0", "0", "0", "0"

        if "rev_req" not in st.session_state: st.session_state.rev_req = {}
        rev_data = st.session_state.rev_req
        
        status_app_motor = "NONE"
        motor_limit_lock = False

        col1, col2 = st.columns(2)
        with col1:
            tanggal = st.date_input("Tanggal Pengajuan")
            cluster = st.selectbox("Cluster Regional", [""] + MASTER_DATA[nop]["clusters"])
            nama = st.selectbox("Nama Petugas / Pemohon", [""] + MASTER_DATA[nop]["names"])
            
            nama_lookup = nama.strip().upper()
            
            out_all, out_lock, aging_august, hist_cek = get_user_tickets_status(nama, req_r, pjb_r, app_r)
            if aging_august: st.warning(f"🔔 Sdr/i {nama}, Anda punya **{len(aging_august)}** tiket Agustus tertunda >3 Hari.")
            
            for hc in hist_cek:
                if "DITOLAK" in hc["Status"]: st.error(f"⚠️ {hc['Tiket']} {hc['Status']}")
                elif "Review Admin" in hc["Status"]: st.warning(f"⏳ {hc['Tiket']} Pending Admin.")

            default_bank, default_no_rek = "BNI", ""
            if nama_lookup != "" and nama_lookup in tim_dict:
                auto_lat_brgkt, auto_long_brgkt = str(tim_dict[nama_lookup].get("Latitude", "0")), str(tim_dict[nama_lookup].get("Longtitude", "0"))
                for r in reversed(req_r[1:]): 
                    if len(r) > 18 and str(r[5]).strip().upper() == nama_lookup:
                        if str(r[17]).strip() in ["BNI", "BCA", "MANDIRI", "BRI"]:
                            default_bank, default_no_rek = str(r[17]).strip(), str(r[18]).strip(); break
                            
            is_locked_user = len(out_lock) > 0
            
            col_t1, col_t2 = st.columns([3, 1])
            with col_t1: tiket = st.text_input("Nomor Tiket SWFM (WAJIB)")
            with col_t2: 
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                if st.button("🔍 Tarik", use_container_width=True):
                    found = False
                    for r in reversed(req_r[1:]):
                        if len(r)>16 and str(r[3]).strip().upper() == tiket.strip().upper():
                            st.session_state.rev_req = {"kebutuhan": clean_nominal(r[9]), "desc": r[11], "km_awal": clean_nominal(r[12]), "plat": r[16]}
                            found = True; break
                    if found: st.success("Ditemukan!"); time.sleep(1); st.rerun()
                    else: st.error("Tidak Ditemukan!")
            
            is_duplicate = (tiket.strip().upper() in all_requested_tickets) and tiket.strip() != ""
            role = st.selectbox("Role Jabatan", ["-- Pilih Role --", "PM", "TE", "MBP", "CME"])
            
            if nop == "Palangkaraya" and len(site_list) > 0:
                site_id = st.selectbox("ID Site / Lokasi", [""] + site_list)
                if site_id != "-- Pilih Site ID --" and site_id in site_dict:
                    auto_lat_tujuan, auto_long_tujuan = str(site_dict[site_id].get("Latitude Tujuan", "0")), str(site_dict[site_id].get("Longtitude Tujuan", "0"))
            else: site_id = st.text_input("ID Site / Lokasi")
            
        with col2:
            keperluan = st.selectbox("Klasifikasi Keperluan", LIST_KEPERLUAN)
            jns_kendaraan = st.selectbox("Kendaraan / Peralatan", ["", "Mobil", "Motor", "Genset", "Lainnya"])
            
            tim_bareng, tim_terkunci = [], []
            if jns_kendaraan.lower() == "mobil":
                list_nama_tim = [n for n in MASTER_DATA[nop]["names"] if n.strip().upper() != nama_lookup and n != ""]
                tim_bareng = st.multiselect("👥 Rekan Tim Bersama (Opsional)", list_nama_tim)
                if role in ["TE", "MBP", "CME"] and tim_bareng:
                    for member in tim_bareng:
                        _, m_out_lock, _, _ = get_user_tickets_status(member, req_r, pjb_r, app_r)
                        if len(m_out_lock) > 0: tim_terkunci.append(member)
            
            kebutuhan = 0; jenis_bahan_bakar = ""; total_motor_this_month = 0; motor_anomali = False
            
            if jns_kendaraan.lower() == "motor":
                k_tangki = st.number_input("Kapasitas Tangki (Liter)", min_value=0.0, step=0.1)
                h_satuan = st.number_input("Harga Satuan BBM", min_value=0, step=500)
                l_butuh = st.number_input("Berapa Liter Kebutuhan?", min_value=0.0, step=0.1)
                
                kebutuhan = int(l_butuh * h_satuan)
                st.info(f"💰 Estimasi: **Rp {kebutuhan:,.0f}**")
                jenis_bahan_bakar = st.selectbox("Pilih Jenis BBM", ["", "Pertalite", "Pertamax"])
                final_bbm = f"{jns_kendaraan} - {jenis_bahan_bakar}" if jenis_bahan_bakar else jns_kendaraan
                
                if l_butuh > k_tangki and k_tangki > 0: motor_anomali = True; st.error("🚨 Liter melebihi kapasitas!")
                
                current_month_str = datetime.now().strftime("%m/%Y")
                for r in req_r[1:]:
                    if len(r) > 10:
                        try:
                            tgl_req = parse_date(r[1])
                            if tgl_req.strftime("%m/%Y") == current_month_str and str(r[5]).strip().upper() == nama_lookup:
                                if "motor" in str(r[10]).lower(): total_motor_this_month += clean_nominal(r[9])
                        except: pass
                
                if (total_motor_this_month + kebutuhan) > 500000:
                    st.error(f"⚠️ LIMIT MOTOR TERCAPAI (>500k/bulan).")
                    for r in reversed(app_r):
                        if len(r) > 5 and str(r[2]).strip().upper() == tiket.strip().upper() and r[3] == "Limit Motor":
                            status_app_motor = str(r[5]).strip().upper(); break
                    
                    if status_app_motor == "APPROVED": st.success("✅ Telah disetujui Admin.")
                    else: motor_limit_lock = True
                        
            elif jns_kendaraan.lower() in ["mobil", "genset"]:
                jenis_bahan_bakar = st.selectbox("Pilih Jenis BBM", ["", "Pertalite", "Pertamax", "Dexlite", "Bio Solar", "Pertamina Dex"])
                final_bbm = f"{jns_kendaraan} - {jenis_bahan_bakar}" if jenis_bahan_bakar else jns_kendaraan
                kebutuhan = st.number_input("Kebutuhan Dana (Rp)", min_value=0, step=1000, value=rev_data.get("kebutuhan", 0))
            else:
                final_bbm = jns_kendaraan
                kebutuhan = st.number_input("Kebutuhan Dana (Rp)", min_value=0, step=1000, value=rev_data.get("kebutuhan", 0))
            
            auto_nopol = rev_data.get("plat", "")
            if auto_nopol == "" and nama_lookup != "" and nama_lookup in tim_dict:
                auto_nopol = str(tim_dict[nama_lookup].get("NOPOL", "")).strip()
                if auto_nopol in ["nan", "0", "None"]: auto_nopol = ""
                
            if role in ["PM", "MBP", "CME"]:
                if auto_nopol != "": plat = st.text_input("Plat Nomor (Auto)", value=auto_nopol, disabled=True)
                else: plat = st.text_input("Plat / ID Genset", value=auto_nopol)
            elif role != "-- Pilih Role --":
                plat_choice = st.selectbox("Plat Kendaraan", ["-- Pilih NOPOL --"] + list_nopol + ["Lainnya (Manual)"])
                if plat_choice == "Lainnya (Manual)": plat = st.text_input("Ketik Plat Manual", value=auto_nopol)
                else: plat = "" if plat_choice == "-- Pilih NOPOL --" else plat_choice
            else:
                plat = st.text_input("Plat / ID Genset", value=auto_nopol)
                
            plat_clean = plat.strip().replace(" ", "").upper()
            last_indikator = 0
            if plat_clean != "" and jns_kendaraan.lower() in ["mobil", "motor", "genset"]:
                for r in reversed(pjb_r[1:]): 
                    if len(r) > 12 and str(r[12]).strip().replace(" ", "").upper() == plat_clean:
                        try: last_indikator = int(clean_nominal(r[10])); break
                        except: pass

            label_indikator = "RH Genset Awal" if jns_kendaraan.lower() == "genset" else ("KM Kendaraan Awal" if jns_kendaraan.lower() in ["mobil", "motor"] else "Indikator Awal")
            km_awal = st.number_input(label_indikator, min_value=0, value=rev_data.get("km_awal", last_indikator))
            deskripsi = st.text_area("Deskripsi Pekerjaan", value=rev_data.get("desc", ""))
            deskripsi_final = deskripsi + f"\n\n[Berangkat bersama tim: {', '.join(tim_bareng)}]" if tim_bareng else deskripsi

        is_vehicle = jns_kendaraan.lower() in ['mobil', 'motor']
        st.markdown("<div class='section-title'>📍 3. Satelit & Rekening</div>", unsafe_allow_html=True)
        
        col3, col4 = st.columns(2)
        with col3:
            lat_berangkat = st.text_input("Latitude Berangkat", value=auto_lat_brgkt if is_vehicle else "0", disabled=not is_vehicle)
            long_berangkat = st.text_input("Longitude Berangkat", value=auto_long_brgkt if is_vehicle else "0", disabled=not is_vehicle)
            bank_idx = ["BNI", "BCA", "MANDIRI", "BRI"].index(default_bank) if default_bank in ["BNI", "BCA", "MANDIRI", "BRI"] else 0
            rek_penerima = st.selectbox("Bank Tujuan", ["BNI", "BCA", "MANDIRI", "BRI"], index=bank_idx)
        with col4:
            lat_tujuan = st.text_input("Latitude Tujuan", value=auto_lat_tujuan if is_vehicle else "0", disabled=not is_vehicle)
            long_tujuan = st.text_input("Longitude Tujuan", value=auto_long_tujuan if is_vehicle else "0", disabled=not is_vehicle)
            no_rek = st.text_input("Nomor Rekening", value=default_no_rek)
            nominal_tf = st.number_input("Nominal Transfer (Rp)", min_value=0, step=1000)

        jarak_final_text, invalid_coords = "", False
        if is_vehicle:
            c_lat1, c_lon1 = clean_coord(lat_berangkat), clean_coord(long_berangkat)
            c_lat2, c_lon2 = clean_coord(lat_tujuan), clean_coord(long_tujuan)
            if c_lat1 != 0 and c_lon1 != 0 and c_lat2 != 0 and c_lon2 != 0:
                with st.spinner("Menarik rute satelit..."):
                    jarak_km_oneway, _ = get_route_and_distance(c_lon1, c_lat1, c_lon2, c_lat2)
                jarak_km_pp = jarak_km_oneway * 2
                bbm_req = (jarak_km_pp / 7) if jns_kendaraan.lower() == 'mobil' else (jarak_km_pp / 15)
                jarak_final_text = f"{jarak_km_pp:.1f} Km (PP)"
                st.success(f"🛰️ Jarak Satelit (PP): {jarak_final_text} | Estimasi BBM: {bbm_req:.1f} Liter")
            else: invalid_coords = True

        st.markdown("<div class='section-title'>📸 4. Upload Bukti Fisik</div>", unsafe_allow_html=True)
        c_up1, c_up2 = st.columns(2)
        with c_up1: foto_km = st.file_uploader("Upload Foto KM / RH Awal", type=["jpg", "png", "jpeg"])
        with c_up2: foto_evidance = st.file_uploader("Upload Foto Evidance Pekerjaan", type=["jpg", "png", "jpeg"])
        
        form_invalid = (nama == "" or cluster == "" or role == "-- Pilih Role --" or keperluan == "" or jns_kendaraan == "")
        
        if is_duplicate: st.info("💡 Ini terdeteksi sebagai REVISI.")

        if is_locked_user or motor_anomali or motor_limit_lock or len(tim_terkunci) > 0:
            st.error("⛔ AKSES DITOLAK karena masalah PJB/Limit. Selesaikan hal yang *Pending* atau Ditolak sebelumnya!")
            if motor_limit_lock and tiket.strip():
                if st.button("🚨 Minta Approval Kelebihan Limit ke Admin", type="primary"):
                    append_data(SHEET_APP, [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), nama, tiket.strip().upper(), "Limit Motor", kebutuhan, "PENDING", f"Bulan ini: Rp {total_motor_this_month:,.0f}"], target_ss)
                    st.success("Terkirim ke Admin!"); time.sleep(2); st.rerun()
            
            if st.text_input("🔑 Password Khusus (Bypass):", type="password") in AUTHORIZED_PASSWORDS:
                if st.button("💡 Paksa Kirim Request (Bypass)", type="primary"):
                    if form_invalid or not tiket.strip() or invalid_coords: st.error("Lengkapi form!")
                    else:
                        with st.spinner("Processing..."):
                            append_data(SHEET_REQUEST, [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), tanggal.strftime("%d/%m/%Y"), nop, tiket, cluster, nama, role, site_id, keperluan, kebutuhan, final_bbm, deskripsi_final, str(km_awal), jarak_final_text, lat_berangkat, long_berangkat, plat, rek_penerima, no_rek, nominal_tf, upload_foto(foto_km), upload_foto(foto_evidance), lat_tujuan, long_tujuan], target_ss)
                            st.session_state.rev_req = {}; st.success("🎉 Berhasil Bypass!"); time.sleep(2); st.session_state.page = "🏠 Hub Menu Utama"; st.rerun()
        else:
            if st.button("📤 KIRIM FORM REQUEST", type="primary", use_container_width=True):
                if form_invalid or not tiket.strip() or invalid_coords: st.error("Lengkapi seluruh form yang wajib!")
                else:
                    with st.spinner("Mengirim data ke pusat..."):
                        append_data(SHEET_REQUEST, [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), tanggal.strftime("%d/%m/%Y"), nop, tiket, cluster, nama, role, site_id, keperluan, kebutuhan, final_bbm, deskripsi_final, str(km_awal), jarak_final_text, lat_berangkat, long_berangkat, plat, rek_penerima, no_rek, nominal_tf, upload_foto(foto_km), upload_foto(foto_evidance), lat_tujuan, long_tujuan], target_ss)
                        st.session_state.rev_req = {}; st.balloons(); st.success("🎉 Berhasil Dikirim!"); time.sleep(2); st.session_state.page = "🏠 Hub Menu Utama"; st.rerun()

# ==========================================
# PAGE 2: FORM PJB OPERASIONAL 
# ==========================================
elif st.session_state.page == "✅ Form PJB Operasional":
    st.markdown("<div class='header-card'><h2>✅ PORTAL PJB</h2><p>Lengkapi nota realisasi untuk verifikasi.</p></div>", unsafe_allow_html=True)
    
    nop_cari = st.selectbox("📂 1. Pilih Database (NOP):", ["-- Pilih NOP --"] + list(MASTER_DATA.keys()))
    
    if nop_cari != "-- Pilih NOP --":
        target_ss = MASTER_DATA[nop_cari]["spreadsheet_id"]
        data_all = fetch_spreadsheet_data(target_ss)
        req_r, pjb_r, app_r = data_all[SHEET_REQUEST], data_all[SHEET_PJB], data_all[SHEET_APP]
        
        pjb_tickets_all = {str(r[21]).strip().upper() for r in pjb_r[1:] if len(r) > 21}
        
        status_verif_dict = {str(r[2]).strip().upper(): str(r[5]).strip() for r in app_r[1:] if len(r) > 5 and r[3] == "Verifikasi PJB" and str(r[2]).strip() != ""}
        
        st.markdown("<div class='section-title'>🔍 2. Tarik Data Pending PJB</div>", unsafe_allow_html=True)
        col_id1, col_id2 = st.columns([2, 1])
        with col_id1: nama_pjb = st.selectbox("👤 Pilih Nama Anda:", ["-- Pilih Nama --"] + MASTER_DATA[nop_cari]["names"])
        with col_id2: pass_nominal = st.text_input("🔑 Akses Nominal (Admin):", type="password")
            
        pending_options = []
        if nama_pjb != "-- Pilih Nama --":
            for r in req_r[1:]:
                if len(r)>5 and str(r[3]).strip() != "" and str(r[5]).strip().upper() == nama_pjb.strip().upper():
                    tk = str(r[3]).strip().upper()
                    if tk not in pjb_tickets_all or status_verif_dict.get(tk) == "REJECTED":
                        pending_options.append(tk)
        
        col_s2, col_s3 = st.columns([2, 1])
        with col_s2: 
            pilihan_tiket = st.selectbox("🎫 Tiket Pending:", ["-- Pilih Tiket --"] + pending_options + ["-- Ketik Manual --"]) if pending_options else "-- Ketik Manual --"
            cari_tiket = st.text_input("Ketik Manual:") if pilihan_tiket == "-- Ketik Manual --" else ("" if pilihan_tiket == "-- Pilih Tiket --" else pilihan_tiket)
        
        valid_cari_tiket = str(cari_tiket).strip().upper()

        with col_s3: 
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Tarik Data", type="primary", use_container_width=True) and valid_cari_tiket:
                ditemukan_req, ditemukan_pjb = None, None
                for r in reversed(req_r[1:]):
                    if len(r) > 3 and str(r[3]).strip().upper() == valid_cari_tiket:
                        ditemukan_req = {"NOP": r[2], "Cluster": r[4], "Nama": r[5], "Role": r[6], "Site": r[7], "Keperluan": r[8], "BBM": r[10] if len(r)>10 else "", "Desc": r[11] if len(r)>11 else "", "KMAwal": clean_nominal(r[12]) if len(r)>12 else 0, "NominalReq": clean_nominal(r[9]) if len(r)>9 else 0, "Plat": r[16] if len(r)>16 else ""}
                        break
                for r in reversed(pjb_r[1:]):
                    if len(r) > 21 and str(r[21]).strip().upper() == valid_cari_tiket: ditemukan_pjb = r; break
                        
                if ditemukan_req:
                    if ditemukan_pjb:
                        ditemukan_req.update({"km_akhir_lama": int(clean_nominal(ditemukan_pjb[10])) if len(ditemukan_pjb)>10 else int(ditemukan_req["KMAwal"]), "liter_lama": str(ditemukan_pjb[22]) if len(ditemukan_pjb)>22 else "0", "harga_lama": int(clean_nominal(ditemukan_pjb[23])) if len(ditemukan_pjb)>23 else 0, "nota_lama": int(clean_nominal(ditemukan_pjb[20])) if len(ditemukan_pjb)>20 else 0})
                    st.session_state.pjb_data = ditemukan_req
                    st.success("🎉 Data Ditarik!")
                else: st.session_state.pjb_data = None; st.error("❌ Tidak ditemukan.")

        if st.session_state.get("pjb_data"):
            d = st.session_state.pjb_data
            st.markdown("<div class='section-title'>💸 Bukti Transfer (Admin)</div>", unsafe_allow_html=True)
            f_transfer = st.file_uploader("Upload Bukti TF (Wajib buka kunci form)", type=["jpg", "png", "jpeg"])
            
            if f_transfer is None: st.warning("⚠️ Upload Bukti Transfer dahulu untuk mengakses pengisian PJB.")
            else:
                c_a, c_b = st.columns(2)
                with c_a: tgl_pjb = st.date_input("Tanggal PJB"); nominal_pjb = st.number_input("Nominal PJB Terpakai", value=int(d["NominalReq"]), disabled=True)
                with c_b: km_akhir = st.number_input("KM/RH Akhir (Wajib Update)", min_value=int(d["KMAwal"]), value=d.get("km_akhir_lama", int(d["KMAwal"])))

                c_c, c_d = st.columns(2)
                with c_c: tot_liter = st.text_input("Total Liter BBM/Material", value=d.get("liter_lama", "0")); tot_nilai_nota = st.number_input("Total Fisik Sesuai Nota (Rp)", min_value=0, step=1000, value=d.get("nota_lama", 0))
                with c_d: harga_satuan = st.number_input("Harga Satuan (BBM/Material)", min_value=0, step=500, value=d.get("harga_lama", 0))
                
                st.markdown("<div class='section-title'>📸 Lampiran Bukti (Foto)</div>", unsafe_allow_html=True)
                p1, p2, p3 = st.columns(3)
                with p1: f_isi = st.file_uploader("Evidance Pengisian", type=["jpg","png"]); f_nota_bbm = st.file_uploader("Nota BBM", type=["jpg","png"])
                with p2: f_mat = st.file_uploader("Foto Material", type=["jpg","png"]); f_notamat = st.file_uploader("Nota Material", type=["jpg","png"])
                with p3: f_inap = st.file_uploader("Nota Penginapan", type=["jpg","png"]); f_kerja = st.file_uploader("Evidance Pekerjaan", type=["jpg","png"]); f_km = st.file_uploader("Foto KM/RH Akhir", type=["jpg","png"])
                
                is_bbm_anomali = "genset" in str(d["BBM"]).lower() and ("dexlite" in str(d["BBM"]).lower() or "bio" in str(d["BBM"]).lower()) and (harga_satuan > 28000)
                if is_bbm_anomali:
                    st.error("🚨 DETEKSI ANOMALI GENSET: Harga melebihi batas wajar. Mohon hubungi Admin.")
                    if st.button("🚨 Ajukan Approval Harga", type="primary"):
                        append_data(SHEET_APP, [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), d["Nama"], valid_cari_tiket, f"Genset Anomali ({d['BBM']})", harga_satuan, "PENDING", "-"], target_ss)
                        st.success("Terkirim!"); time.sleep(2); st.rerun()
                    st.stop()

                if st.button("🚀 SAHKAN PJB / SUBMIT", type="primary", use_container_width=True):
                    with st.spinner("Mengupload foto..."):
                        total_km_tempuh = km_akhir - int(d["KMAwal"])
                        data_pjb = [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), tgl_pjb.strftime("%d/%m/%Y"), d["NOP"], d["Cluster"], d["Nama"], d["Role"], d["Site"], d["Keperluan"], d["BBM"], d["Desc"], str(km_akhir), nominal_pjb, d["Plat"], upload_foto(f_isi), upload_foto(f_nota_bbm), upload_foto(f_km), upload_foto(f_mat), upload_foto(f_notamat), upload_foto(f_inap), upload_foto(f_kerja), tot_nilai_nota, valid_cari_tiket, tot_liter, harga_satuan, str(total_km_tempuh), "", "", upload_foto(f_transfer)]
                        append_data(SHEET_PJB, [(r+[""]*28)[:28] for r in [data_pjb]][0], target_ss)
                        append_data(SHEET_APP, [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), d["Nama"], valid_cari_tiket, "Verifikasi PJB", nominal_pjb, "PENDING", "-"], target_ss)
                        st.balloons(); st.success("🎉 PJB Terkirim!"); st.session_state.pjb_data = None; time.sleep(2); st.session_state.page = "🏠 Hub Menu Utama"; st.rerun()

# ==========================================
# PAGE 3: APPROVAL CENTER (KHUSUS ADMIN)
# ==========================================
elif st.session_state.page == "🛡️ Approval Center":
    st.markdown("<div class='header-card'><h2>🛡️ APPROVAL CENTER</h2></div>", unsafe_allow_html=True)
    nop_admin = st.selectbox("📂 Wilayah (NOP):", ["-- Pilih NOP --"] + list(MASTER_DATA.keys()))
    if nop_admin != "-- Pilih NOP --":
        target_ss = MASTER_DATA[nop_admin]["spreadsheet_id"]
        data_all = fetch_spreadsheet_data(target_ss)
        app_r, pjb_r = data_all[SHEET_APP], data_all[SHEET_PJB]
        
        pending_anomali, pending_pjb = [], []
        if len(app_r) > 0:
            for idx, r in enumerate(app_r):
                if len(r) > 5 and str(r[5]).strip() == "PENDING":
                    item = {"Row Index": idx, "Waktu": str(r[0]), "Nama": str(r[1]), "No Tiket": str(r[2]), "Jenis Pengajuan": str(r[3]), "Nominal": f"Rp {clean_nominal(r[4]):,.0f}", "Status": str(r[5]).strip(), "Keterangan": str(r[6]) if len(r) > 6 else "-"}
                    if r[3] == "Verifikasi PJB": pending_pjb.append(item)
                    else: pending_anomali.append(item)
        
        tab_app1, tab_app2 = st.tabs(["📸 Verifikasi PJB", "⛽ Approval Harga/Limit"])
        with tab_app1:
            if pending_pjb:
                st.dataframe(pd.DataFrame(pending_pjb).drop(columns=["Row Index"]), hide_index=True, use_container_width=True)
                target_tiket_pjb = st.selectbox("Pilih Tiket PJB:", [p["No Tiket"] for p in pending_pjb])
                
                action_pjb = st.radio("Keputusan:", ["Setujui PJB (APPROVE)", "Tolak PJB (REJECT)"], horizontal=True)
                remark_pjb = st.text_input("Catatan (Wajib jika ditolak):")
                
                if st.button("Proses Verifikasi", type="primary"):
                    if "REJECT" in action_pjb and not remark_pjb.strip(): st.error("⚠️ Mohon berikan Alasan Penolakan.")
                    else:
                        target_indices = [p["Row Index"] for p in pending_pjb if p["No Tiket"] == target_tiket_pjb]
                        new_status = "APPROVED" if "APPROVE" in action_pjb else "REJECTED"
                        with st.spinner("Memperbarui database..."):
                            for idx in target_indices: update_approval_status(target_ss, idx, new_status, remark_pjb if remark_pjb else "-")
                            st.success(f"✅ Tiket {target_tiket_pjb} di-{new_status}!"); time.sleep(1.5); st.rerun()
            else: st.success("✅ Tidak ada PJB pending.")
                
        with tab_app2:
            if pending_anomali:
                st.dataframe(pd.DataFrame(pending_anomali).drop(columns=["Row Index"]), hide_index=True, use_container_width=True)
                target_tiket_anm = st.selectbox("Pilih Pengajuan:", [p["No Tiket"] for p in pending_anomali])
                action_anm = st.radio("Keputusan Limit:", ["Setujui (APPROVE)", "Tolak (REJECT)"], horizontal=True)
                if st.button("Proses Harga/Limit", type="primary"):
                    target_indices = [p["Row Index"] for p in pending_anomali if p["No Tiket"] == target_tiket_anm]
                    new_status = "APPROVED" if "APPROVE" in action_anm else "REJECTED"
                    with st.spinner("Memperbarui database..."):
                        for idx in target_indices: update_approval_status(target_ss, idx, new_status, "-")
                        st.success("✅ Diproses!"); time.sleep(1.5); st.rerun()
            else: st.success("✅ Tidak ada anomali harga.")

# ==========================================
# PAGE 4: MANAJEMEN KAS & DISTRIBUSI DANA
# ==========================================
elif st.session_state.page == "🏦 Manajemen Kas & Distribusi":
    st.markdown("<div class='header-card'><h2>🏦 MANAJEMEN KAS</h2></div>", unsafe_allow_html=True)
    nop_admin = st.selectbox("📂 Wilayah (NOP):", ["-- Pilih NOP --"] + list(MASTER_DATA.keys()))
    if nop_admin != "-- Pilih NOP --":
        target_ss = MASTER_DATA[nop_admin]["spreadsheet_id"]
        data_all = fetch_spreadsheet_data(target_ss)
        um_r = data_all.get(SHEET_UM, []); dist_r = data_all.get(SHEET_DISTRIBUSI, []); rekap_r = data_all.get("Rekap PJB", [])
        
        tab_in, tab_out, tab_report, tab_pjb = st.tabs(["📥 Debit", "📤 Kredit", "📊 Saldo", "📋 Target PJB"])
        
        with tab_in:
            with st.form("form_tambah_um"):
                tgl_um = st.date_input("Tanggal"); um_nobis = st.text_input("Nama Batch"); um_nominal = st.number_input("Nominal", min_value=0, step=100000)
                if st.form_submit_button("💾 Rekam Masuk") and um_nominal > 0 and um_nobis.strip():
                    append_data(SHEET_UM, [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), tgl_um.strftime("%d/%m/%Y"), um_nobis.strip(), um_nominal], target_ss)
                    st.success("✅ Tersimpan!"); time.sleep(1); st.rerun()
        with tab_out:
            valid_batches = sorted(list(set([r[2].strip() for r in um_r[1:] if len(r) > 2 and r[2].strip() != ""])))
            with st.form("form_distribusi"):
                tgl_dist = st.date_input("Tgl Transfer"); sumber_dana = st.selectbox("Sumber Dana", valid_batches); nama_tim = st.selectbox("Penerima", ["-- Pilih --"] + MASTER_DATA[nop_admin]["names"])
                nom_dist = st.number_input("Nominal Transfer", min_value=0, step=50000); bukti_tf = st.file_uploader("Upload Bukti", type=['jpg','png'])
                if st.form_submit_button("🚀 Kirim Distribusi") and nama_tim != "-- Pilih --" and nom_dist > 0 and bukti_tf:
                    with st.spinner("Memproses..."):
                        append_data(SHEET_DISTRIBUSI, [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), tgl_dist.strftime("%d/%m/%Y"), sumber_dana, nama_tim, nom_dist, upload_foto(bukti_tf)], target_ss)
                        st.success("✅ Tersimpan!"); time.sleep(1); st.rerun()
        with tab_report:
            in_data = {r[2].strip(): in_data.get(r[2].strip(), 0) + clean_nominal(r[3]) for r in um_r[1:] if len(r)>3 and r[2].strip()!=""}
            out_data = {r[2].strip(): out_data.get(r[2].strip(), 0) + clean_nominal(r[4]) for r in dist_r[1:] if len(r)>4 and r[2].strip()!=""}
            report_list = [{"Batch": b, "In": in_data[b], "Out": out_data.get(b,0), "Sisa": in_data[b]-out_data.get(b,0)} for b in sorted(in_data.keys())]
            if report_list: st.dataframe(pd.DataFrame(report_list), hide_index=True, use_container_width=True)
            else: st.info("Kosong")
        with tab_pjb:
            if len(rekap_r) > 1:
                col_a = sorted(list(set([r[0].strip() for r in rekap_r[1:] if len(r)>0 and r[0].strip()!=""])))
                col_q = sorted(list(set([r[16].strip() for r in rekap_r[1:] if len(r)>16 and r[16].strip()!=""])))
                f_a = st.selectbox("Periode", ["Semua"] + col_a); f_q = st.selectbox("Dana Ops", ["Semua"] + col_q)
                filtered = [r for r in rekap_r[1:] if (f_a=="Semua" or (len(r)>0 and r[0].strip()==f_a)) and (f_q=="Semua" or (len(r)>16 and r[16].strip()==f_q))]
                total = sum([clean_nominal(r[15]) for r in filtered if len(r)>15])
                st.success(f"Total PJB: Rp {total:,.0f}"); st.dataframe(pd.DataFrame(filtered))

# ==========================================
# PAGE 5: LIVE MONITORING
# ==========================================
elif st.session_state.page == "📈 Live Monitoring":
    st.markdown("<div class='header-card'><h2>📈 LIVE MONITORING</h2></div>", unsafe_allow_html=True)
    nop_live = st.selectbox("🌐 Pilih Market (NOP):", ["-- Pilih NOP --"] + list(MASTER_DATA.keys()))
    if nop_live != "-- Pilih NOP --":
        # Gunakan cache dari master function agar ringan
        data_all = fetch_spreadsheet_data(MASTER_DATA[nop_live]["spreadsheet_id"])
        st.info("Pilih Tab Analisa di bawah:")
        t1, t2 = st.tabs(["💰 Tren & Kategori", "🚨 Anomali & Boros"])
        with t1: st.success("Fitur ini menarik data dari cache, tidak memberatkan HP.")
        with t2: st.warning("Sedang dalam pengembangan untuk performa mobile.")

# ==========================================
# PAGE 6: REPORT & AUTO PJB
# ==========================================
elif st.session_state.page == "🖨️ Auto PJB Report":
    st.markdown("<div class='header-card'><h2>🖨️ REPORT CENTER</h2></div>", unsafe_allow_html=True)
    nop_report = st.selectbox("📂 Pilih Wilayah:", ["-- Pilih NOP --"] + list(MASTER_DATA.keys()))
    if nop_report != "-- Pilih NOP --":
        data_all = fetch_spreadsheet_data(MASTER_DATA[nop_report]["spreadsheet_id"])
        st.success("Terkoneksi dengan Database. Data Export (PDF) siap dijalankan.")
