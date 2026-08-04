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
# 0. KONFIGURASI HALAMAN & UI 3D PROFESIONAL
# ==========================================
st.set_page_config(page_title="Sistem ERP & Operasional", page_icon="🏦", layout="wide")

st.markdown("""
    <style>
        .main { background-color: #F4F7F6; font-family: 'Segoe UI', sans-serif; }
        
        .header-card {
            background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
            padding: 25px; border-radius: 15px; color: white; text-align: center;
            box-shadow: 0 10px 20px rgba(0,0,0,0.19), 0 6px 6px rgba(0,0,0,0.23);
            margin-bottom: 25px; animation: slideDown 0.8s ease-out;
        }
        
        .metric-3d {
            background: linear-gradient(145deg, #ffffff, #e6e6e6);
            padding: 20px; border-radius: 15px; text-align: center;
            box-shadow: 8px 8px 16px #d1d1d1, -8px -8px 16px #ffffff;
            transition: transform 0.3s ease; margin-bottom: 15px;
            border-left: 5px solid #2980b9;
        }
        .metric-3d:hover { transform: translateY(-5px); }
        .metric-title { font-size: 14px; color: #7f8c8d; font-weight: bold; text-transform: uppercase; }
        .metric-value { font-size: 24px; color: #2c3e50; font-weight: 900; }
        
        .sidebar-btn { width: 100%; border-radius: 8px; font-weight: bold; height: 45px; margin-bottom:10px; background-color: #ecf0f1; border: 1px solid #bdc3c7; color: #34495e; transition: 0.3s;}
        .sidebar-btn:hover { background-color: #3498db; color: white; border-color: #2980b9; }
        
        div.stAlert { border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .section-title { color: #2c3e50; font-size: 1.3rem; font-weight: 800; border-bottom: 3px solid #3498db; padding-bottom: 5px; margin-top: 25px; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 1px;}
        
        @keyframes slideDown { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. KONFIGURASI SERVER & ADMIN
# ==========================================
PASSWORD_KOORDINATOR = "Kamiyakin2027"
PASSWORD_LIVE = "liveaction"
ADMIN_PASSWORDS = {"Palangkaraya": "okkidah", "Pangkalanbun": "yurontur", "Tarakan": "donpablo", "Pontianak": "kingaloy"}

cloudinary.config(cloud_name="fxm61tjv", api_key="624877324969231", api_secret="LIFO6pfEg9fOM3nbsY8FBbVTpSI", secure=True)

MASTER_DATA = {
    "Palangkaraya": {"spreadsheet_id": "1HvgVicTWwO4RMQI6ZR3Mu3IgGicwjcLZl9mDN1auvJU", "clusters": ["Palangkaraya", "Barito Raya"], "names": ["ADI BOWO SANTOSO", "AHMAD", "AHMAD MUZAKIR", "AHMAD SETIAWAN", "ALFI SYAHRI", "ARMADI", "AULIA RAHMAN", "DARLI SUTANTO", "DIDI RIYADI", "FAHMI", "FRANS EJHA ADITYA", "GYLLBRHED ALFARY LOLOMSAIT", "HARUN NURASYID", "HORY YUSMANTO", "INDRA", "JAMES JIMBRIS TAMAILANG", "JUMADI", "KHILAL DAWAI KATIRI", "LEONARD HARA", "M. RIFANI", "MUHAMMAD MUKHLIS", "MUHAMMAD MUKTI", "MUNAWIR AHMAD", "MURJANI", "NURHAYAT", "OKY BANGKIT PAMUNGKAS", "PRADILA KANDI", "PUJIANTO", "PUTRA WARDANA", "REYNALDI RICARDO PUTRA", "RIKI HIDAYAT", "RIKO SETIADI", "SAILILLAH", "SARUL SAPUTRA", "SARWONO", "TAKLIM", "TIVIANSYAH", "TRISNO SUSANTO", "YAHYA MUHAMAD", "OKTA PRDIKA", "M KIKI FIRMANSYAH", "MAWARDAH", "HD"]},
    "Pangkalanbun": {"spreadsheet_id": "1bc0lDhR5iMtXZsKiKIdEwPY8JTaASeHFtaJSeXkywE4", "clusters": ["Ketapang", "Sampit", "Pangkalanbun"], "names": ["RIRIH HARIANTO", "MUKHAMAD ABDUL KHOLIP", "YAMA DEWANTA", "BAGUS SANTOSO", "IMRON SETIAWAN", "JOENDRIS HERDIAN KARA", "STEVEN HERDIAN KARA", "YUDIONO", "DADANG WAHYU SYAHPUTRA", "CAVIN ANDREAN EKA PUTRA", "RAHMAT RIYAN WAHYUDIN", "SUWITO", "DIDIK PRIYONO", "GUNTUR WAHYU PRADANA", "UTI MUHAMMAD KHAIRUL HUDA", "IDRUS MAULANA", "M. RIZKY", "TRIYONO", "ERIK SETIAWAN", "AGUS SUGANDA", "AJI SAPUTRA", "DIAN WAHYUDI", "HAFID BUDIANTO", "IWAN ZAINAL ABIDIN", "DANDI PUTRA", "PONIRAN", "PARYADI KUSUMA", "HERWANI", "DIAN WILDANI", "IPAN HARIONO", "FIRDAUS", "RONI YUDI ISYANTO", "AYU NUR ISLAMIAH", "ARDIANSYAH.", "DAYU SHANDY", "WAHYUDI", "TAJAM SAPUTRA", "MUJHAHID ALWI", "NANDA FIRMANSYAH", "WAHYU RAHMADANI", "TEGUH WICAKSONO", "FERI HARIADI", "NASUKI", "ANDARIANTO PUJI SURO", "BONDAN PRAMUDYA ANANTATUR", "SOLEKHAN", "RIZAL IHZAMAHENDRA", "MUHAMMAD ROIS FERDIANSYAH", "WIDI ARYANTO", "FHANNY AGUSTIAWAN"]},
    "Tarakan": {"spreadsheet_id": "1lRj1YdZGQwY5vHg8P4wudK9V1O_lJuEYjdyHkXoB-Wg", "clusters": ["Tarakan Inner", "Tarakan Outer"], "names": ["HENDRA WIRTASI SIMANULLANG", "ARIZONA ROSADI", "KUKUH BHASKARA", "NATAL SIMBOLON", "HERMAWAN", "IRVAN DINATA VANDITYAWAN", "ENDRAS SAPTA", "AHMADI", "EDI PANJI ERMAYANA", "HANS RISKY RONI TUAH GIRSANG", "IRMANSYAH B. SANGAJI", "REMO REMOLDUS MANALU", "MOHAMMAD RAFAI", "FIRMAN SYAHRUL", "AZMIR", "PETRUS RESI KELORE", "ANIR REZKY", "AHDAN", "PARJON SIMANULLANG", "RUSDI", "HASRIADI", "PURO SUGONDO", "ALIMUDIN M. SAER", "KORNELIUS USI KELORE", "RUSDIANSYAH", "JONTES YUSDA SIMANULLANG", "NANI SETIANINGSIH", "UNGGUL NUGRAHA", "YOGABITA INDOTENO", "JHON KENNEDI SIMANULLANG", "RAFI MUHAMAD SYARIF", "AGRIVA", "SEPTIAN ALVITO", "M. DEDI RIZALDI", "SAHARUDDIN.", "MUHAMMAD RASYID", "SUPRIADI", "JULIMAT SIHITE", "EFNI NURYADIN", "ERWIN SAPUTRA ARIANSYAH", "ALVEUS", "SUPRIADI BANDANGAN"]},
    "Pontianak": {"spreadsheet_id": "1VmoWPImNFMjnaIQpBXEVYdMiTEzsz3P4tpmzfA0EMDE", "clusters": ["Sintang", "Singkawang", "Pontianak"], "names": ["ALOYSIUS", "RUDI", "RONIYANTO", "SUKADI", "HAIRIL", "AZMI ASHADIQI", "SUYADI", "ARIEF DARUL IKHWAN", "MUHAMMAD AL FATAH", "YUDIANSYAH", "RAHMAD INDRA IRAWAN", "MATIUS MARTIN", "RYVAEEL DEWANGGA", "AMIRDA ANGGA SAPUTRA", "IZHARUDDIN", "VINSENSIUS YOGI", "GUSTI ARIZAL", "MUHAMMAD MIFTAHUDIN, A.MD", "BAYU ANGGARA PUTRA", "YONI IRAWAN", "SUGANDI", "IRVAN ANDRIYANA", "ALDIANSYAH", "ABANG HAMDANI", "ABANG KUSDIANSYAH", "SUMAN", "SANGGARA ISMARAWARI", "IBIN", "VALENTINUS PETRO", "DWI KURNIAWAN ISMANTO", "ARISAFRIADI", "DONATUS DONI", "NUR AHMAD KARDIYANTO", "AGRI PERDANA", "AKHSANUL FIKI", "ALI ALAMSYAH", "MUHAMMAD FIRZHA GIANNI HARSYA", "RICKY ARDILAY", "FAISAL", "WIJI SANTOSO", "HISYAM MUTHOYIB", "ARIF RAHMAN NUGROHO", "TOTOK SUGIARTO", "PURWANDI SETIAWAN", "JULIANTO BHAKTI PUTRO, SH", "ILHAMMUDIN", "AGUNG", "ROSIDI", "ABRAR ELZAH FATHALIF", "HENDRI YULIANSYAH", "JAMIL", "GORO SUKARTONO", "OKTAPIANUS JUMIN", "ONNIE SYAEFUDDIN", "BUDI", "ULUL AMRY", "RUHIAT, A.MD", "SUPIANDI", "WAHYUDI", "SUHENDRIK", "M. ARKAM", "SYAFRI APRIJAL", "ARIANTO SUMANTRI", "TUTU AGE ANDIKA", "VIRANDA SAPTA, A.MD", "TOTO HERMANSYAH", "KURNIAWAN", "ROBI ISKANDAR MASDIANSYAH", "MUTIIN CHANDRA", "MISJANI", "KHAIRUL FARISD", "ANDRA", "DODI RATMAYANTO", "WAWAN DARYANA", "MISWARDI", "JUPRILIAUS PICO", "DEDY PURNOMO", "EDI KURNIAWAN", "DEDE GUNAWAN", "WANDALA JAGOARDI PANDALO", "KARIYADI", "REZQI AL BARQAH", "FIRMANSYAH, SP"]}
}

LIST_KEPERLUAN = ["-- Pilih Keperluan --", "Tshoot", "Backup", "Support", "PM", "Program BCP", "Program Quikwin", "Program G348T", "Pengiriman Material SPMS", "Pembelian Material"]

# PERBAIKAN NAMA SHEET (d kecil)
SHEET_REQUEST = "Form Request dana"        
SHEET_PJB = "Form PJB"
SHEET_UM = "Data UM"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# ==========================================
# 3. FUNGSI INTI, KALKULASI MAPS & CACHING
# ==========================================
def clean_nominal(val):
    if pd.isna(val) or val == "": return 0
    v = str(val).replace('Rp', '').replace('.', '').replace(',', '').strip()
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
    if nama == "-- Pilih Nama --": return [], []
    req_tickets = {r[3].strip().upper(): r[1] for r in req_rows[1:] if len(r) > 5 and r[5].strip().upper() == nama.strip().upper()}
    pjb_tickets = {r[21].strip().upper() for r in pjb_rows[1:] if len(r) > 21 and r[4].strip().upper() == nama.strip().upper()}
    outstanding, history = [], []
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
        return cloudinary.uploader.upload(f"data:{file.type};base64,{encoded}", resource_type="auto").get("secure_url") 
    except Exception: return ""

def append_data(sheet_name, data, spreadsheet_id):
    gspread.authorize(get_credentials()).open_by_key(spreadsheet_id).worksheet(sheet_name).append_row(data)
    fetch_spreadsheet_data.clear()

# ==========================================
# 4. SIDEBAR (SLIDEBAR KHUSUS & NAVIGASI)
# ==========================================
if 'page' not in st.session_state: st.session_state.page = "📝 Form Request Dana"

st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2942/2942813.png", width=80)
st.sidebar.markdown("### 📋 MENU OPERASIONAL")
if st.sidebar.button("📝 Form Request Dana", use_container_width=True): st.session_state.page = "📝 Form Request Dana"
if st.sidebar.button("✅ Form PJB Operasional", use_container_width=True): st.session_state.page = "✅ Form PJB Operasional"

st.sidebar.markdown("### 📊 MENU ANALITIK (ADMIN)")
if st.sidebar.button("📊 Neraca / Buku Kas", use_container_width=True): st.session_state.page = "📊 Neraca / Buku Kas"
if st.sidebar.button("📈 Live Monitoring", use_container_width=True): st.session_state.page = "📈 Live Monitoring"

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 CEK STATUS TIKET")
cek_nop = st.sidebar.selectbox("📂 Area", ["-- Pilih Area --"] + list(MASTER_DATA.keys()))
if cek_nop != "-- Pilih Area --":
    cek_nama = st.sidebar.selectbox("👤 Petugas", ["-- Pilih Nama --"] + MASTER_DATA[cek_nop]["names"])
    if st.sidebar.button("Cari Histori"):
        if cek_nama != "-- Pilih Nama --":
            req_r, pjb_r, _, _ = fetch_spreadsheet_data(MASTER_DATA[cek_nop]["spreadsheet_id"])
            out_tkt, hist_tkt = get_user_tickets_status(cek_nama, req_r, pjb_r)
            if hist_tkt:
                st.sidebar.dataframe(pd.DataFrame(hist_tkt), hide_index=True)
                if out_tkt: st.sidebar.error(f"⚠️ {len(out_tkt)} tiket tertunggak (Belum PJB)!")
                else: st.sidebar.success("✅ Seluruh tiket aman!")
            else: st.sidebar.info("Tidak ada data.")

# ==========================================
# PAGE 1: FORM REQUEST DANA
# ==========================================
if st.session_state.page == "📝 Form Request Dana":
    st.markdown("<div class='header-card'><h2>📝 PORTAL PENGAJUAN DANA</h2><p>Rekam Jejak Keuangan & Kalkulasi Geospasial Secara Real-Time.</p></div>", unsafe_allow_html=True)
    
    col_l1, col_l2 = st.columns([4,1])
    with col_l2:
        if st.button("👉 Tuju ke Form PJB", type="secondary"): 
            st.session_state.page = "✅ Form PJB Operasional"
            st.rerun()

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
            
            if nama != "-- Pilih Nama --" and nama in tim_dict:
                auto_lat_brgkt = str(tim_dict[nama].get("Latitude", "0"))
                auto_long_brgkt = str(tim_dict[nama].get("Longtitude", "0"))
                
            outstanding_tkt, _ = get_user_tickets_status(nama, req_r, pjb_r)
            is_locked_user = len(outstanding_tkt) > 0
            
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
            jns_bbm = st.selectbox("Jenis Kendaraan / BBM", ["-- Pilih Kendaraan --", "Mobil", "motor", "genset"])
            km_awal = st.text_input("Indikator KM Awal (Tulis 0 jika tidak relevan)", value="0")
            plat = st.text_input("Plat Nomor Kendaraan")
            deskripsi = st.text_area("Deskripsi Pekerjaan / Justifikasi")

        is_vehicle = jns_bbm.lower() in ['mobil', 'motor']
        st.markdown("<div class='section-title'>📍 3. Rute Peta (Satelit) & Keuangan</div>", unsafe_allow_html=True)
        if not is_vehicle: st.info("ℹ️ Pengisian Koordinat dikunci (0) karena jenis BBM bukan Mobil/Motor.")
        
        col3, col4 = st.columns(2)
        with col3:
            lat_berangkat = st.text_input("Latitude Berangkat (Auto)", value=auto_lat_brgkt if is_vehicle else "0", disabled=not is_vehicle)
            long_berangkat = st.text_input("Longitude Berangkat (Auto)", value=auto_long_brgkt if is_vehicle else "0", disabled=not is_vehicle)
            rek_penerima = st.selectbox("Bank Penerima / E-Wallet", ["BNI", "BCA", "MANDIRI", "BRI"])
        with col4:
            lat_tujuan = st.text_input("Latitude Tujuan (Auto)", value=auto_lat_tujuan if is_vehicle else "0", disabled=not is_vehicle)
            long_tujuan = st.text_input("Longitude Tujuan (Auto)", value=auto_long_tujuan if is_vehicle else "0", disabled=not is_vehicle)
            no_rek = st.text_input("Nomor Rekening Tujuan")
            nominal_tf = st.number_input("Total Nominal Transfer (Rp)", min_value=0, step=1000)

        jarak_final_text = ""
        invalid_coords = False
        if is_vehicle:
            c_lat1, c_lon1 = clean_coord(lat_berangkat), clean_coord(long_berangkat)
            c_lat2, c_lon2 = clean_coord(lat_tujuan), clean_coord(long_tujuan)
            
            if c_lat1 != 0 and c_lon1 != 0 and c_lat2 != 0 and c_lon2 != 0:
                with st.spinner("Satelit sedang menarik data jalan raya..."):
                    jarak_km, poly_coords = get_route_and_distance(c_lon1, c_lat1, c_lon2, c_lat2)
                
                bbm_req = (jarak_km / 7) if jns_bbm.lower() == 'mobil' else (jarak_km / 15)
                jarak_final_text = f"{jarak_km:.1f} Km"
                
                st.markdown("#### 🗺️ Navigasi Jalan & Analisa BBM (3D Map)")
                m1, m2, m3 = st.columns(3)
                m1.markdown(f"<div class='metric-3d'><div class='metric-title'>Jarak Tempuh Jalan</div><div class='metric-value'>{jarak_final_text}</div></div>", unsafe_allow_html=True)
                m2.markdown(f"<div class='metric-3d'><div class='metric-title'>BBM Boros Maksimal</div><div class='metric-value'>{bbm_req:.1f} Liter</div></div>", unsafe_allow_html=True)
                m3.markdown(f"<div class='metric-3d'><div class='metric-title'>Tipe Kendaraan</div><div class='metric-value'>{jns_bbm.upper()}</div></div>", unsafe_allow_html=True)
                
                # PETA LEBIH KECIL (HEIGHT = 350, ZOOM DISESUAIKAN)
                layer_points = pdk.Layer("ScatterplotLayer", data=[{"pos": [c_lon1, c_lat1], "color": [255,50,50]}, {"pos": [c_lon2, c_lat2], "color": [50,255,50]}], get_position="pos", get_color="color", get_radius=300)
                layer_route = pdk.Layer("PathLayer", data=[{"path": poly_coords, "color": [52, 152, 219]}], get_path="path", get_width=5, get_color="color")
                view = pdk.ViewState(latitude=(c_lat1+c_lat2)/2, longitude=(c_lon1+c_lon2)/2, zoom=8, pitch=45)
                st.pydeck_chart(pdk.Deck(layers=[layer_route, layer_points], initial_view_state=view), use_container_width=True, height=350)
            else:
                invalid_coords = True
                st.warning("⚠️ Untuk kendaraan Mobil/Motor, Harap lengkapi Koordinat Keberangkatan & Tujuan.")

        st.markdown("<div class='section-title'>📸 4. Bukti Lampiran Fisik</div>", unsafe_allow_html=True)
        c_up1, c_up2 = st.columns(2)
        with c_up1: foto_km = st.file_uploader("Upload Foto KM Awal", type=["jpg", "png", "jpeg"])
        with c_up2: foto_evidance = st.file_uploader("Upload Foto Kendaraan/Pekerjaan", type=["jpg", "png", "jpeg"])
        
        st.markdown("<br>", unsafe_allow_html=True)
        form_invalid = (nama == "-- Pilih Nama --" or cluster == "-- Pilih Cluster --" or role == "-- Pilih Role --" or keperluan == "-- Pilih Keperluan --")

        if is_locked_user or is_duplicate:
            if is_locked_user: st.markdown(f"<div class='locked-box'>⛔ AKSES DITOLAK: Sdr. {nama} memiliki {len(outstanding_tkt)} tiket yang belum PJB!</div>", unsafe_allow_html=True)
            if is_duplicate: st.warning("⚠️ TIKET GANDA TERDETEKSI!")
            
            input_pass = st.text_input("🔑 Password Koordinator Khusus (Bypass):", type="password")
            if input_pass == PASSWORD_KOORDINATOR:
                if st.button("🚀 Paksakan Kirim Request Dana", type="primary"):
                    if form_invalid or not tiket.strip() or (nop == "Palangkaraya" and site_id == "-- Pilih Site ID --") or invalid_coords: st.error("Lengkapi form dengan benar!")
                    else:
                        with st.spinner("Memproses..."):
                            waktu = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                            data_req = [waktu, tanggal.strftime("%d/%m/%Y"), nop, tiket, cluster, nama, role, site_id, keperluan, kebutuhan, jns_bbm, deskripsi, km_awal, jarak_final_text, lat_berangkat, long_berangkat, plat, rek_penerima, no_rek, nominal_tf, upload_foto(foto_km), upload_foto(foto_evidance), lat_tujuan, long_tujuan]
                            append_data(SHEET_REQUEST, data_req, target_ss)
                            st.success(f"✅ Tiket {tiket} terekam!"); time.sleep(2); st.rerun()
        else:
            if st.button("🚀 Kirim Form Request Dana", type="primary"):
                if form_invalid or not tiket.strip() or (nop == "Palangkaraya" and site_id == "-- Pilih Site ID --") or invalid_coords: st.error("Lengkapi form dengan benar!")
                else:
                    with st.spinner("Memproses..."):
                        waktu = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        data_req = [waktu, tanggal.strftime("%d/%m/%Y"), nop, tiket, cluster, nama, role, site_id, keperluan, kebutuhan, jns_bbm, deskripsi, km_awal, jarak_final_text, lat_berangkat, long_berangkat, plat, rek_penerima, no_rek, nominal_tf, upload_foto(foto_km), upload_foto(foto_evidance), lat_tujuan, long_tujuan]
                        append_data(SHEET_REQUEST, data_req, target_ss)
                        st.success(f"✅ Tiket {tiket} sukses masuk!"); time.sleep(2); st.rerun()

# ==========================================
# PAGE 2: FORM PJB OPERASIONAL
# ==========================================
elif st.session_state.page == "✅ Form PJB Operasional":
    st.markdown("<div class='header-card' style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);'><h2>✅ PORTAL PJB (PENYELESAIAN)</h2><p>Lengkapi nota realisasi untuk menghapus status tunggakan.</p></div>", unsafe_allow_html=True)
    
    nop_cari = st.selectbox("📂 1. Pilih Database (NOP):", ["-- Pilih NOP --"] + list(MASTER_DATA.keys()))
    if nop_cari != "-- Pilih NOP --":
        target_ss = MASTER_DATA[nop_cari]["spreadsheet_id"]
        req_r, pjb_r, _, _ = fetch_spreadsheet_data(target_ss)
        
        pjb_tickets_all = {r[21].strip().upper() for r in pjb_r[1:] if len(r) > 21}
        pending_list = [{"Tanggal": r[1], "Nama": r[5], "No Tiket": r[3], "Keperluan": r[8] if len(r)>8 else ""} for r in req_r[1:] if len(r)>5 and r[3].strip().upper() not in pjb_tickets_all and r[3].strip() != ""]
        
        st.markdown("<div class='section-title'>📋 Tiket Belum Selesai (Outstanding)</div>", unsafe_allow_html=True)
        if pending_list: st.dataframe(pd.DataFrame(pending_list), hide_index=True, use_container_width=True)
        else: st.success("Seluruh tiket di area ini sudah clear!")
        
        st.markdown("<div class='section-title'>🔍 2. Tarik Data Tiket</div>", unsafe_allow_html=True)
        col_s2, col_s3 = st.columns([3, 1])
        with col_s2: cari_tiket = st.text_input("Masukkan Nomor Tiket SWFM:")
        with col_s3: 
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Cari Data", type="primary"):
                ditemukan = None
                for r in req_r[1:]:
                    if len(r) > 3 and r[3].strip().upper() == cari_tiket.strip().upper():
                        ditemukan = {"NOP": r[2], "Cluster": r[4], "Nama": r[5], "Role": r[6], "Site": r[7], "Keperluan": r[8], "BBM": r[10], "Desc": r[11], "Jarak": r[13] if len(r)>13 else "", "Plat": r[16] if len(r)>16 else ""}
                st.session_state.pjb_data = ditemukan
                if ditemukan: st.success("🎉 Histori ditarik otomatis!")
                else: st.error("❌ Tiket tidak ditemukan.")

        if st.session_state.get("pjb_data"):
            d = st.session_state.pjb_data
            st.markdown("<div class='section-title'>🔒 Rincian Sistem (Read-Only)</div>", unsafe_allow_html=True)
            col_a, col_b = st.columns(2)
            with col_a:
                tgl_pjb = st.date_input("Tanggal PJB")
                st.text_input("Nama Petugas", d["Nama"], disabled=True)
                st.text_input("Cluster & Role", f'{d["Cluster"]} - {d["Role"]}', disabled=True)
                st.text_input("Estimasi Jarak Tempuh (Sistem)", value=d["Jarak"], disabled=True)
            with col_b:
                st.text_input("Site ID Tujuan", d["Site"], disabled=True)
                st.text_input("Keperluan", d["Keperluan"], disabled=True)
                st.text_input("Kendaraan & Plat", f'{d["BBM"]} - {d["Plat"]}', disabled=True)
            
            st.markdown("<div class='section-title'>📝 Input Realisasi PJB</div>", unsafe_allow_html=True)
            col_c, col_d = st.columns(2)
            with col_c:
                km_akhir = st.text_input("KM Akhir Kendaraan", value="0")
                nominal_pjb = st.number_input("Nominal PJB Terpakai (Rp)", min_value=0, step=1000)
                tot_liter = st.text_input("Total Liter BBM/Material", value="0")
            with col_d:
                tot_nilai_nota = st.number_input("Total Sesuai Nota Fisik (Rp)", min_value=0, step=1000)
                harga_satuan = st.number_input("Harga Satuan (BBM/Material)", min_value=0, step=500)
            
            st.markdown("<div class='section-title'>📸 Lampiran Bukti (Foto)</div>", unsafe_allow_html=True)
            p1, p2, p3 = st.columns(3)
            with p1: f_isi = st.file_uploader("Evidance Pengisian", type=["jpg","png"]); f_nota_bbm = st.file_uploader("Nota BBM", type=["jpg","png"]); f_km = st.file_uploader("Foto KM / Disanding", type=["jpg","png"])
            with p2: f_mat = st.file_uploader("Foto Material", type=["jpg","png"]); f_notamat = st.file_uploader("Nota Material", type=["jpg","png"])
            with p3: f_inap = st.file_uploader("Nota Penginapan", type=["jpg","png"]); f_kerja = st.file_uploader("Evidance Pekerjaan", type=["jpg","png"])
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 Sahkan Pelaporan PJB", type="primary", use_container_width=True):
                with st.spinner("Mengunci data ke server..."):
                    waktu = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    data_pjb = [waktu, tgl_pjb.strftime("%d/%m/%Y"), d["NOP"], d["Cluster"], d["Nama"], d["Role"], d["Site"], d["Keperluan"], d["BBM"], d["Desc"], km_akhir, nominal_pjb, d["Plat"], upload_foto(f_isi), upload_foto(f_nota_bbm), upload_foto(f_km), upload_foto(f_mat), upload_foto(f_notamat), upload_foto(f_inap), upload_foto(f_kerja), tot_nilai_nota, cari_tiket, tot_liter, harga_satuan]
                    append_data(SHEET_PJB, [(r+[""]*24)[:24] for r in [data_pjb]][0], target_ss)
                    st.success("✅ PJB Sukses!"); st.session_state.pjb_data = None
                    time.sleep(2); st.rerun()

# ==========================================
# PAGE 3: NERACA / BUKU KAS (KONSEP STABIL)
# ==========================================
elif st.session_state.page == "📊 Neraca / Buku Kas":
    st.markdown("<div class='header-card header-admin'><h2>📊 BUKU KAS & NERACA</h2><p>Laporan Rekonsiliasi Saldo Keuangan Area</p></div>", unsafe_allow_html=True)
    col_adm1, col_adm2 = st.columns([1, 2])
    with col_adm1: nop_admin = st.selectbox("📂 Wilayah (NOP):", ["-- Pilih NOP --"] + list(MASTER_DATA.keys()))
    with col_adm2:
        if nop_admin != "-- Pilih NOP --": pass_admin = st.text_input("🔑 Password Admin:", type="password")
        
    if nop_admin != "-- Pilih NOP --" and pass_admin == ADMIN_PASSWORDS[nop_admin]:
        target_ss = MASTER_DATA[nop_admin]["spreadsheet_id"]
        
        st.markdown("<div class='section-title'>📥 1. Input Penambahan Uang Muka (UM)</div>", unsafe_allow_html=True)
        with st.form("form_tambah_um"):
            col_u1, col_u2, col_u3 = st.columns([1, 2, 1])
            with col_u1: tgl_um = st.date_input("Tanggal UM Masuk")
            with col_u2: um_nobis = st.text_input("Deskripsi / Dasar Dokumen UM")
            with col_u3: um_nominal = st.number_input("Nominal UM (Rp)", min_value=0, step=1000)
            
            if st.form_submit_button("💾 Rekam UM ke Buku Kas"):
                if um_nominal > 0 and um_nobis:
                    append_data(SHEET_UM, [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), tgl_um.strftime("%d/%m/%Y"), um_nobis, um_nominal], target_ss)
                    st.success("✅ UM Terekam!"); time.sleep(1); st.rerun()
                else: st.error("Isi form dengan benar!")
                
        st.markdown("<div class='section-title'>📅 2. Laporan Neraca & Kalkulasi Periode</div>", unsafe_allow_html=True)
        col_d1, col_d2 = st.columns(2)
        with col_d1: start_date = st.date_input("Dari Tanggal PJB/UM")
        with col_d2: end_date = st.date_input("Sampai Tanggal PJB/UM")
        
        if st.button("🔄 Kalkulasi Neraca", type="primary"):
            with st.spinner("Mensinkronisasi buku besar..."):
                _, pjb_r, um_r, _ = fetch_spreadsheet_data(target_ss)
                tot_um, tot_pjb = 0, 0
                
                if len(um_r) > 1:
                    df_um = pd.DataFrame(um_r[1:], columns=["Waktu", "Tanggal", "Deskripsi", "Nominal"])
                    df_um['Tanggal'] = pd.to_datetime(df_um['Tanggal'], format='%d/%m/%Y', errors='coerce')
                    df_um_filt = df_um[(df_um['Tanggal'].dt.date >= start_date) & (df_um['Tanggal'].dt.date <= end_date)].copy()
                    df_um_filt['Nominal'] = df_um_filt['Nominal'].apply(clean_nominal)
                    tot_um = df_um_filt['Nominal'].sum()
                    
                if len(pjb_r) > 1:
                    df_pjb = pd.DataFrame([(r + [""] * 24)[:24] for r in pjb_r[1:]], columns=["Waktu Input", "Tanggal PJB", "NOP", "Cluster", "Nama", "Role", "Site ID", "Keperluan", "Jenis BBM", "Deskripsi", "KM Akhir", "Nominal PJB", "Plat", "U1","U2","U3","U4","U5","U6","U7", "Nilai Nota", "Tiket", "Liter", "Harga Satuan"])
                    df_pjb['Tanggal PJB'] = pd.to_datetime(df_pjb['Tanggal PJB'], format='%d/%m/%Y', errors='coerce')
                    df_pjb_filt = df_pjb[(df_pjb['Tanggal PJB'].dt.date >= start_date) & (df_pjb['Tanggal PJB'].dt.date <= end_date)].copy()
                    df_pjb_filt['Nominal PJB'] = df_pjb_filt['Nominal PJB'].apply(clean_nominal)
                    tot_pjb = df_pjb_filt['Nominal PJB'].sum()
                
                m1, m2, m3 = st.columns(3)
                m1.markdown(f"<div class='metric-3d'><div class='metric-title'>Total UM Diterima</div><div class='metric-value'>Rp {tot_um:,.0f}</div></div>", unsafe_allow_html=True)
                m2.markdown(f"<div class='metric-3d'><div class='metric-title'>Total PJB Terserap</div><div class='metric-value'>Rp {tot_pjb:,.0f}</div></div>", unsafe_allow_html=True)
                m3.markdown(f"<div class='metric-3d'><div class='metric-title'>Sisa Kas Tercatat</div><div class='metric-value'>Rp {tot_um - tot_pjb:,.0f}</div></div>", unsafe_allow_html=True)
                
                st.markdown("---")
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    st.markdown("**📗 Rincian Pemasukan (UM)**")
                    if tot_um > 0:
                        df_u = df_um_filt[['Tanggal', 'Deskripsi', 'Nominal']].copy()
                        df_u['Tanggal'] = df_u['Tanggal'].dt.strftime('%d/%m/%Y')
                        st.dataframe(df_u, hide_index=True, use_container_width=True)
                with col_t2:
                    st.markdown("**📕 Rincian Pengeluaran (PJB)**")
                    if tot_pjb > 0:
                        df_p = df_pjb_filt[['Tanggal PJB', 'Tiket', 'Nama', 'Nominal PJB']].copy()
                        df_p['Tanggal PJB'] = df_p['Tanggal PJB'].dt.strftime('%d/%m/%Y')
                        st.dataframe(df_p, hide_index=True, use_container_width=True)

# ==========================================
# PAGE 4: LIVE MONITORING (DASHBOARD SAHAM)
# ==========================================
elif st.session_state.page == "📈 Live Monitoring":
    st.markdown("<div class='header-card' style='background: linear-gradient(135deg, #000000 0%, #434343 100%); color:#00ff00;'><h2>📈 LIVE FINANCIAL MONITORING</h2><p>Wall-Street Style Burn Rate Dashboard</p></div>", unsafe_allow_html=True)
    
    col_l1, col_l2 = st.columns([1, 2])
    with col_l1: nop_live = st.selectbox("🌐 Market (NOP):", ["-- Pilih NOP --"] + list(MASTER_DATA.keys()))
    with col_l2:
        if nop_live != "-- Pilih NOP --": pass_live = st.text_input("🔑 Live-Action Password:", type="password")
            
    if nop_live != "-- Pilih NOP --" and pass_live == PASSWORD_LIVE:
        st.markdown("<div class='section-title'>📅 Filter Periode Trading (Rekap)</div>", unsafe_allow_html=True)
        cd1, cd2 = st.columns(2)
        with cd1: start_live = st.date_input("Tarik Data Mulai")
        with cd2: end_live = st.date_input("Hingga")
        
        if st.button("📊 Tampilkan Analitik Live", type="primary", use_container_width=True):
            with st.spinner("Fetching Live Market Data..."):
                _, pjb_r, um_r, rekap_r = fetch_spreadsheet_data(MASTER_DATA[nop_live]["spreadsheet_id"])
                
                # Filter UM untuk Total Capital Periode Ini
                total_um = 0
                if len(um_r) > 1:
                    d_um = pd.DataFrame(um_r[1:], columns=["Waktu", "Tanggal", "Deskripsi", "Nominal"])
                    d_um['Tanggal'] = pd.to_datetime(d_um['Tanggal'], format='%d/%m/%Y', errors='coerce')
                    d_um = d_um[(d_um['Tanggal'].dt.date >= start_live) & (d_um['Tanggal'].dt.date <= end_live)]
                    total_um = d_um['Nominal'].apply(clean_nominal).sum()
                
                batas_harian = total_um / 7 if total_um > 0 else 0
                
                # Pengeluaran HARI INI mutlak
                today_str = datetime.now().strftime("%d/%m/%Y")
                pengeluaran_today = sum([clean_nominal(r[11]) for r in pjb_r[1:] if len(r)>11 and r[1].strip() == today_str])
                
                # Penyerapan di periode filter
                tot_serap_periode = 0
                df_trend = pd.DataFrame()
                if len(pjb_r) > 1:
                    df_p = pd.DataFrame([(r + [""] * 24)[:24] for r in pjb_r[1:]], columns=["W","Tanggal","N","C","Nm","R","S","K","B","D","K2","Nominal","P","u","u","u","u","u","u","u","N2","T","L","H"])
                    df_p['Tanggal'] = pd.to_datetime(df_p['Tanggal'], format='%d/%m/%Y', errors='coerce')
                    df_p = df_p[(df_p['Tanggal'].dt.date >= start_live) & (df_p['Tanggal'].dt.date <= end_live)].copy()
                    df_p['Nominal'] = df_p['Nominal'].apply(clean_nominal)
                    tot_serap_periode = df_p['Nominal'].sum()
                    df_trend = df_p.groupby(df_p['Tanggal'].dt.date)['Nominal'].sum().reset_index()
                    df_trend.set_index('Tanggal', inplace=True)
                
                # Sisa Kas dari REKAP PJB KOLOM P, Filter Kolom A
                sisa_kas_real = 0
                if len(rekap_r) > 1:
                    for r in rekap_r[1:]:
                        if len(r) > 15:
                            try:
                                t_tgl = pd.to_datetime(r[0].strip(), dayfirst=True).date()
                                if start_live <= t_tgl <= end_live: sisa_kas_real = clean_nominal(r[15])
                            except: pass
                
                avg_expense = df_trend['Nominal'].mean() if not df_trend.empty else 0
                sisa_hari = (sisa_kas_real / avg_expense) if avg_expense > 0 else 999
                
                st.markdown("---")
                m1, m2, m3, m4 = st.columns(4)
                m1.markdown(f"<div class='metric-3d' style='border-left:5px solid #2ecc71;'><div class='metric-title'>Total Capital (UM)</div><div class='metric-value'>Rp {total_um:,.0f}</div></div>", unsafe_allow_html=True)
                m2.markdown(f"<div class='metric-3d' style='border-left:5px solid #e74c3c;'><div class='metric-title'>Penyerapan</div><div class='metric-value'>Rp {tot_serap_periode:,.0f}</div></div>", unsafe_allow_html=True)
                m3.markdown(f"<div class='metric-3d' style='border-left:5px solid #f1c40f;'><div class='metric-title'>Maksimal 1 Hari</div><div class='metric-value'>Rp {batas_harian:,.0f}</div></div>", unsafe_allow_html=True)
                m4.markdown(f"<div class='metric-3d' style='border-left:5px solid #9b59b6;'><div class='metric-title'>Pengeluaran Hari Ini</div><div class='metric-value'>Rp {pengeluaran_today:,.0f}</div></div>", unsafe_allow_html=True)
                
                st.markdown(f"<div style='background-color:#1e1e1e; padding:30px; border-radius:15px; border:2px solid #333; text-align:center;'><h3 style='color:#7f8c8d; margin:0;'>SISA KAS (REKAP PJB)</h3><h1 style='color:#00ff00; font-size:50px; margin:0;'>Rp {sisa_kas_real:,.0f}</h1><p style='color:white; font-size:18px;'>Perkiraan dana akan habis dalam: <b style='color:#e74c3c;'>{sisa_hari:.1f} Hari Operasional</b></p></div>", unsafe_allow_html=True)
                
                if not df_trend.empty:
                    st.markdown("<br><h4 style='color:#2c3e50;'>📈 Grafik Burn Rate Periode Terpilih</h4>", unsafe_allow_html=True)
                    st.line_chart(df_trend, use_container_width=True)
