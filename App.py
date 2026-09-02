import streamlit as st
import pandas as pd
import gspread
import base64
import cloudinary
import cloudinary.uploader
import requests
import math
import os
import tempfile
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import time
import re
from collections import defaultdict

# ==========================================
# 0. KONFIGURASI HALAMAN & UI 3D MODERN
# ==========================================
st.set_page_config(page_title="SiRAPI Enterprise", page_icon="🔮", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800;900&display=swap');
        
        .main { background: #e0e5ec; font-family: 'Plus Jakarta Sans', sans-serif; }
        
        /* Premium Header Card 3D Neomorphism */
        .header-card {
            background: linear-gradient(135deg, #0F2027 0%, #203A43 50%, #2C5364 100%);
            padding: 40px 20px; border-radius: 24px; color: white; text-align: center;
            box-shadow: 10px 10px 20px rgba(15, 32, 39, 0.2), -10px -10px 20px rgba(255, 255, 255, 0.8);
            margin-bottom: 35px; margin-top: 15px; border-bottom: 5px solid #00F2FE;
            position: relative; overflow: hidden;
        }
        .header-card h1 { font-weight: 900; font-size: 2.5rem; margin-bottom: 5px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .header-card p { font-size: 1.1rem; color: #e2e8f0; margin-bottom: 0; font-weight: 300;}
        
        /* Menu Buttons - 3D Glass/Neomorphism */
        div[data-testid="stButton"] > button {
            background: rgba(255, 255, 255, 0.6) !important;
            backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(255, 255, 255, 0.8) !important; 
            border-radius: 20px !important;
            box-shadow: 8px 8px 16px rgba(163,177,198,0.6), -8px -8px 16px rgba(255,255,255, 0.8) !important;
            height: auto !important; padding: 25px 10px !important;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
        }
        div[data-testid="stButton"] > button:hover, div[data-testid="stButton"] > button:active {
            background: linear-gradient(135deg, #4FACFE 0%, #00F2FE 100%) !important;
            transform: translateY(-8px) scale(1.02) !important;
            box-shadow: 12px 12px 20px rgba(163,177,198,0.7), -12px -12px 20px rgba(255,255,255, 0.9) !important;
            border: none !important;
        }
        div[data-testid="stButton"] > button p { color: #334155 !important; font-size: 1.15rem !important; font-weight: 800 !important; margin:0; text-align:center; }
        div[data-testid="stButton"] > button:hover p, div[data-testid="stButton"] > button:active p { color: white !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.2); }
        
        /* Admin Button Specific 3D */
        .btn-admin div[data-testid="stButton"] > button {
            background: linear-gradient(145deg, #1e293b, #0f172a) !important;
            box-shadow: 8px 8px 16px rgba(163,177,198,0.6), -8px -8px 16px rgba(255,255,255, 0.8) !important;
        }
        .btn-admin div[data-testid="stButton"] > button p { color: white !important; font-size: 1.05rem !important; font-weight: 600 !important;}
        .btn-admin div[data-testid="stButton"] > button:hover { 
            background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%) !important; 
            box-shadow: inset 4px 4px 10px rgba(0,0,0,0.3) !important;
            transform: translateY(-5px) !important;
        }
        
        /* Section Titles Modern */
        .section-title { 
            color: #1e293b; font-size: 1.3rem; font-weight: 900; 
            background: linear-gradient(90deg, #e2e8f0 0%, transparent 100%);
            padding: 10px 15px; border-radius: 8px; border-left: 5px solid #4FACFE;
            margin-top: 30px; margin-bottom: 20px;
        }
        
        /* Metric Cards 3D Neomorphism */
        .metric-3d {
            background: #e0e5ec; padding: 25px 20px; border-radius: 20px; text-align: center;
            box-shadow: 9px 9px 16px rgb(163,177,198,0.6), -9px -9px 16px rgba(255,255,255, 0.5);
            border-top: 5px solid #00F2FE; margin-bottom: 20px; transition: transform 0.3s;
        }
        .metric-3d:hover { transform: translateY(-5px); }
        .metric-title { font-size: 0.85rem; color: #64748b; font-weight: 800; text-transform: uppercase; letter-spacing: 1px;}
        .metric-value { font-size: 1.8rem; font-weight: 900; margin-top: 8px; color: #0F2027; text-shadow: 1px 1px 1px rgba(255,255,255,0.8);}
        
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
SHEET_TIKET_PM = "PM Tiketing"
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

def clean_indicator(val):
    try:
        if pd.isna(val) or val == "": return 0.0
        v = str(val).replace(',', '.').replace(' ', '').strip()
        return float(v)
    except: return 0.0

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
            durasi_sec = res["routes"][0]["duration"]
            poly = decode_polyline(res["routes"][0]["geometry"])
            return dist_km, poly, durasi_sec
    except: pass
    dist_km = haversine(lat1, lon1, lat2, lon2) * 1.3 
    durasi_sec = (dist_km / 40.0) * 3600 # Estimasi kasar 40km/jam
    return dist_km, [[lon1, lat1], [lon2, lat2]], durasi_sec

def get_local_img_base64(filepath):
    try:
        if not os.path.exists(filepath): return ""
        with open(filepath, "rb") as f:
            encoded = base64.b64encode(f.read()).decode('utf-8')
        return f"data:image/png;base64,{encoded}"
    except: return ""

@st.cache_resource
def get_credentials():
    with open("credentials.json", "w") as f: f.write(st.secrets["gcp_json"])
    return Credentials.from_service_account_file("credentials.json", scopes=SCOPES)

@st.cache_data(ttl=600)
def fetch_spreadsheet_data(spreadsheet_id):
    client = gspread.authorize(get_credentials()).open_by_key(spreadsheet_id)
    ws_names = [SHEET_REQUEST, SHEET_PJB, SHEET_UM, SHEET_DISTRIBUSI, SHEET_APP, "Rekap PJB", SHEET_TIKET_PM]
    data = {}
    for name in ws_names:
        try: data[name] = client.worksheet(name).get_all_values()
        except: data[name] = []
    return data

def update_pm_ticket_status(spreadsheet_id, tickets_to_update, new_status):
    try:
        client = gspread.authorize(get_credentials()).open_by_key(spreadsheet_id)
        ws = client.worksheet(SHEET_TIKET_PM)
        rows = ws.get_all_values()
        t_list = [str(t).strip().upper() for t in tickets_to_update]
        for i, r in enumerate(rows):
            if len(r) > 3 and str(r[3]).strip().upper() in t_list:
                ws.update_cell(i + 1, 6, new_status)
        fetch_spreadsheet_data.clear()
    except Exception: pass

@st.cache_data(ttl=600)
def load_excel_data():
    try:
        df_site = pd.read_excel("Hasil_910_Site.xlsx").fillna(0)
        site_dict = df_site.set_index('Site ID')[['Latitude Tujuan', 'Longtitude Tujuan']].to_dict('index')
        site_list = df_site['Site ID'].astype(str).tolist()
    except: site_dict, site_list = {}, []
    
    tim_dict, list_nopol_csv = {}, []
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
            list_nopol_csv = sorted([n for n in list_nopol_raw if n.strip() not in ["", "0", "nan", "None", "NOPOL"]])
            for _, row in df_nopol.iterrows():
                if 'PIC' in df_nopol.columns:
                    pic_name = str(row['PIC']).strip().upper()
                    nopol_val = str(row['NOPOL']).strip()
                    if pic_name and pic_name not in tim_dict: tim_dict[pic_name] = {'Latitude': 0, 'Longtitude': 0}
                    if pic_name and nopol_val and nopol_val not in ["nan", "0", "None"]: 
                        tim_dict[pic_name]['NOPOL'] = nopol_val
    except Exception: pass
    
    nik_dict = {}
    try:
        for nik_file in ["NIK NOP PLK.xlsx", "Database_NIK.xlsx"]:
            if os.path.exists(nik_file):
                df_nik = pd.read_excel(nik_file).fillna("")
                col_nama = next((c for c in df_nik.columns if 'nama' in c.lower()), None)
                col_nik = next((c for c in df_nik.columns if 'nik' in c.lower() or 'nip' in c.lower()), None)
                if col_nama and col_nik:
                    for _, row in df_nik.iterrows():
                        nm_key = str(row[col_nama]).strip().upper()
                        nik_val = str(row[col_nik]).strip()
                        if nm_key and nik_val and nik_val not in ["nan", "0", "None"]:
                            nik_dict[nm_key] = nik_val
    except Exception: pass
        
    return site_dict, site_list, tim_dict, list_nopol_csv, nik_dict

def get_last_indicator(plat_clean, jns, pjb_r):
    if not plat_clean: return 0.0
    for r in reversed(pjb_r[1:]):
        if len(r) > 12:
            h_plat = str(r[12]).strip().replace(" ", "").upper()
            if h_plat == plat_clean and (jns.lower() in str(r[8]).lower()):
                return clean_indicator(r[10])
    return 0.0

def get_user_tickets_status(nama, req_rows, pjb_rows, app_rows):
    if nama == "-- Pilih Nama --" or nama == "": return [], [], [], []
    req_tickets = {}
    for r in req_rows[1:]:
        if len(r) > 5 and r[5].strip().upper() == nama.strip().upper():
            tk_raw = r[3].strip().upper()
            if tk_raw != "": req_tickets[tk_raw] = r[1]
                
    pjb_tickets_all_set = set()
    for r in pjb_rows[1:]:
        if len(r) > 21 and r[4].strip().upper() == nama.strip().upper() and r[21].strip() != "":
            tk_str = r[36].strip() if (len(r) > 36 and r[36].strip()) else r[21].strip()
            pjb_tickets_all_set.update([t.strip().upper() for t in tk_str.split(",")])
            
    pjb_app_status = {}
    req_app_status = {}
    for r in app_rows[1:]:
        if len(r) > 5:
            tiket_app = str(r[2]).strip().upper()
            if r[3] == "Verifikasi PJB":
                if tiket_app != "": pjb_app_status[tiket_app] = {"status": r[5].strip(), "catatan": r[6] if len(r)>6 else ""}
            elif r[3] == "Request Dana":
                if tiket_app != "": req_app_status[tiket_app] = str(r[5]).strip().upper()

    outstanding_all, outstanding_lock, aging_tickets, history = [], [], [], []
    today = datetime.now().date()
    
    for req_tk_raw, tgl in req_tickets.items():
        req_tk_list = [t.strip() for t in req_tk_raw.split(",") if t.strip()]
        req_set = set(req_tk_list)
        
        # LOGIKA BARU: Abaikan (Lepaskan Blokir) jika Request telah di-Reject Admin
        if req_app_status.get(req_tk_raw) == "REJECTED":
            history.append({"Tiket": req_tk_raw, "Tanggal": tgl, "Status": "❌ REQUEST DITOLAK Admin (Harap Ajukan Ulang)"})
            continue
            
        if not req_set.issubset(pjb_tickets_all_set):
            outstanding_all.append(req_tk_raw)
            req_date = parse_date(tgl)
            if req_date >= CUTOFF_DATE: outstanding_lock.append(req_tk_raw)
            aging_days = (today - req_date).days
            
            if req_date >= CUTOFF_DATE and aging_days > 3:
                aging_tickets.append(req_tk_raw)
                history.append({"Tiket": req_tk_raw, "Tanggal": tgl, "Status": f"🚨 Telat {aging_days} Hari"})
            else: history.append({"Tiket": req_tk_raw, "Tanggal": tgl, "Status": "🔴 Menunggu PJB (Belum Selesai)"})
        else:
            app_data = pjb_app_status.get(req_tk_raw, {"status": "APPROVED", "catatan": ""})
            if app_data["status"] == "PENDING":
                outstanding_all.append(req_tk_raw); outstanding_lock.append(req_tk_raw)
                history.append({"Tiket": req_tk_raw, "Tanggal": tgl, "Status": "⏳ PJB Menunggu Verifikasi Admin"})
            elif app_data["status"] == "REJECTED":
                outstanding_all.append(req_tk_raw); outstanding_lock.append(req_tk_raw)
                history.append({"Tiket": req_tk_raw, "Tanggal": tgl, "Status": f"❌ PJB DITOLAK: {app_data['catatan']}"})
            else: history.append({"Tiket": req_tk_raw, "Tanggal": tgl, "Status": "🟢 PJB Selesai & Approved"})
            
    return outstanding_all, outstanding_lock, aging_tickets, sorted(history, key=lambda x: x["Status"], reverse=True)

def upload_foto(file):
    if file is None: return ""
    try:
        encoded = base64.b64encode(file.getvalue()).decode('utf-8')
        return cloudinary.uploader.upload(f"data:{file.type};base64,{encoded}", resource_type="auto").get("secure_url") 
    except Exception: return ""

def append_data(sheet_name, data, spreadsheet_id):
    try:
        client = gspread.authorize(get_credentials()).open_by_key(spreadsheet_id)
        ws = client.worksheet(sheet_name)
        safe_data = [str(x) if x is not None else "" for x in data]
        ws.append_row(safe_data, value_input_option="USER_ENTERED", table_range="A1")
        fetch_spreadsheet_data.clear()
        return True
    except Exception as e:
        st.error(f"⚠️ Gagal menyimpan ke Spreadsheet ({sheet_name}). Error: {e}")
        return False

def update_approval_status(spreadsheet_id, row_index, new_status, remark="-"):
    try:
        client = gspread.authorize(get_credentials()).open_by_key(spreadsheet_id)
        ws = client.worksheet(SHEET_APP)
        ws.update_cell(row_index + 1, 6, new_status)
        ws.update_cell(row_index + 1, 7, remark)
        fetch_spreadsheet_data.clear()
    except Exception as e:
        st.error(f"Terjadi kendala saat update ke Google Sheets. (Code: {e})")

def save_new_nopol_to_csv(new_plat):
    try:
        file_name = "DATA NOPOL MOBIL DAN GENSET NOP PLK.csv"
        if os.path.exists(file_name):
            df = pd.read_csv(file_name, sep=None, engine='python')
            cols = df.columns.tolist()
            if 'NOPOL' in cols:
                new_row = pd.DataFrame([{'NOPOL': new_plat}])
                for c in cols:
                    if c not in new_row.columns: new_row[c] = ""
                new_row = new_row[cols]
                new_row.to_csv(file_name, mode='a', header=False, index=False)
            else:
                with open(file_name, "a") as f:
                    f.write(f"\n{new_plat}")
        else:
            with open(file_name, "w") as f:
                f.write(f"NOPOL,PIC\n{new_plat},")
    except Exception as e:
        pass 

# ==========================================
# INISIALISASI SESSION STATE & NAVIGASI
# ==========================================
if 'page' not in st.session_state: st.session_state.page = "🏠 Hub Menu Utama"
if 'admin_logged_in' not in st.session_state: st.session_state.admin_logged_in = False
if 'pdf_ready' not in st.session_state: st.session_state.pdf_ready = False

if st.session_state.page != "🏠 Hub Menu Utama":
    if st.button("⬅️ KEMBALI KE MENU UTAMA", use_container_width=True):
        st.session_state.page = "🏠 Hub Menu Utama"
        st.session_state.pdf_ready = False
        st.rerun()
    st.markdown("<hr style='margin: 10px 0 30px 0;'>", unsafe_allow_html=True)


# ==========================================
# PAGE 0: HUB MENU UTAMA (1-SCREEN DASHBOARD)
# ==========================================
if st.session_state.page == "🏠 Hub Menu Utama":
    
    c_logo1, c_logo2, c_logo3 = st.columns([1, 1, 1])
    with c_logo2:
        try: st.image("koperasi-jasa-konstruksi-tower-event-organizer-network-monitoring-telekomunikasi-kisel-group-logo-kut.webp", use_container_width=True)
        except: pass

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

    st.markdown("<div class='section-title'>🔍 CEK STATUS TIKET (PRIBADI & TIM)</div>", unsafe_allow_html=True)
    cek_nop = st.selectbox("Pilih Area Wilayah", ["-- Pilih Area --"] + list(MASTER_DATA.keys()), key="cek_area_hub")
    
    if cek_nop != "-- Pilih Area --":
        tab_pribadi, tab_tim_pending = st.tabs(["👤 Status Pribadi Anda", "🚨 Tim Belum PJB (Mulai Agustus)"])
        
        with tab_pribadi:
            cek_nama = st.selectbox("Nama Petugas", ["-- Pilih Nama --"] + MASTER_DATA[cek_nop]["names"], key="cek_nama_hub")
            if st.button("Cari Status Saya", use_container_width=True):
                if cek_nama != "-- Pilih Nama --" and cek_nama != "":
                    with st.spinner("Menarik data server..."):
                        data_cek = fetch_spreadsheet_data(MASTER_DATA[cek_nop]["spreadsheet_id"])
                        out_all, out_lock, aging_tickets, hist_tkt = get_user_tickets_status(cek_nama, data_cek[SHEET_REQUEST], data_cek[SHEET_PJB], data_cek[SHEET_APP])
                    
                    if hist_tkt:
                        st.dataframe(pd.DataFrame(hist_tkt), hide_index=True, use_container_width=True)
                        if aging_tickets: st.warning(f"🔔 Ada {len(aging_tickets)} request tertunda >3 Hari. Tolong segera di-PJB!")
                        if out_all: st.error(f"⚠️ {len(out_all)} Request memblokir status Anda (Belum PJB / Pending Verifikasi).")
                        else: st.success("✅ Seluruh tiket aman dan Approved!")
                    else: st.info("Tidak ada data / belum pernah request.")
                    
        with tab_tim_pending:
            st.info("Fitur ini menampilkan daftar tiket tim yang masih gantung (belum disubmit) mulai dari Agustus 2026 dan seterusnya ke depan.")
            if st.button("🔍 Tarik Data Tim Belum PJB", use_container_width=True, type="primary"):
                with st.spinner("Memindai seluruh data tim wilayah ini..."):
                    data_cek = fetch_spreadsheet_data(MASTER_DATA[cek_nop]["spreadsheet_id"])
                    req_r, pjb_r, app_r = data_cek[SHEET_REQUEST], data_cek[SHEET_PJB], data_cek[SHEET_APP]
                    
                    list_blm_pjb = []
                    for nm in MASTER_DATA[cek_nop]["names"]:
                        if not nm.strip(): continue
                        _, _, _, hist_tkt = get_user_tickets_status(nm, req_r, pjb_r, app_r)
                        
                        for h in hist_tkt:
                            tgl_req = parse_date(h["Tanggal"])
                            if tgl_req >= CUTOFF_DATE:
                                if "Menunggu PJB" in h["Status"] or "Telat" in h["Status"]:
                                    list_blm_pjb.append({
                                        "Nama Petugas": nm,
                                        "No Tiket / Request": h["Tiket"],
                                        "Tanggal Request": h["Tanggal"],
                                        "Status Terkini": h["Status"]
                                    })
                    
                    if list_blm_pjb:
                        st.error(f"⚠️ Ditemukan {len(list_blm_pjb)} tiket aktif yang belum dilaporkan!")
                        st.dataframe(pd.DataFrame(list_blm_pjb), hide_index=True, use_container_width=True)
                    else:
                        st.success("🎉 Luar biasa! Seluruh tim di wilayah ini sudah menyelesaikan PJB aktif.")

    st.markdown("<div class='section-title'>🛡️ MENU KHUSUS ADMIN</div>", unsafe_allow_html=True)
    if not st.session_state.admin_logged_in:
        pass_input = st.text_input("Masukkan Password Admin (Pusat):", type="password")
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
        
        if st.button("🎫 MASTER TIKET PM (Input Data PM Bulanan)", use_container_width=True): st.session_state.page = "🎫 Master Tiket PM"; st.rerun()
        
        c_a1, c_a2 = st.columns(2)
        with c_a1:
            if st.button("🛡️ APPROVAL CENTER\n(Validasi PJB & Revisi)", use_container_width=True): st.session_state.page = "🛡️ Approval Center"; st.rerun()
            if st.button("📈 LIVE MONITORING\n(Dashboard Analisa)", use_container_width=True): st.session_state.page = "📈 Live Monitoring"; st.rerun()
            if st.button("👀 REQ & PJB MONITORING\n(Pantau Tim & Warning)", use_container_width=True): st.session_state.page = "👀 Request & PJB Monitoring"; st.rerun()
        with c_a2:
            if st.button("🏦 MANAJEMEN KAS\n(Distribusi Dana)", use_container_width=True): st.session_state.page = "🏦 Manajemen Kas & Distribusi"; st.rerun()
            if st.button("🖨️ REPORT & AUTO PJB\n(Export Laporan)", use_container_width=True): st.session_state.page = "🖨️ Auto PJB Report"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='text-align: center; color: #94a3b8; font-size: 0.8rem; margin-top:50px;'>Created by Okta Pradika<br>KUT SYSTEM - v8.7 Enterprise Mobile Edition (3D)</div>", unsafe_allow_html=True)


# ==========================================
# PAGE ADMIN: MASTER TIKET PM
# ==========================================
elif st.session_state.page == "🎫 Master Tiket PM":
    st.markdown("<div class='header-card'><h2>🎫 MASTER DATA TIKET PM</h2><p>Push/Upload Daftar Tiket Preventative Maintenance Bulanan ke Database</p></div>", unsafe_allow_html=True)
    
    nop_pm = st.selectbox("📂 Pilih Database Regional (NOP):", ["-- Pilih NOP --"] + list(MASTER_DATA.keys()))
    if nop_pm != "-- Pilih NOP --":
        target_ss = MASTER_DATA[nop_pm]["spreadsheet_id"]
        data_all = fetch_spreadsheet_data(target_ss)
        pm_r = data_all.get(SHEET_TIKET_PM, [])
        
        c_pm1, c_pm2 = st.columns([1, 2])
        with c_pm1:
            st.markdown("### 📥 Input Tiket Baru")
            with st.form("form_tiket_pm"):
                bulan_pm = st.selectbox("Bulan / Periode", [f"{m} {datetime.now().year}" for m in ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]])
                site_pm = st.selectbox("Cluster / Site Target", MASTER_DATA[nop_pm]["clusters"])
                raw_tickets = st.text_area("Masukkan Nomor Tiket (Pisahkan dengan koma atau baris baru)", height=150)
                
                if st.form_submit_button("💾 Push ke Database (AVAILABLE)"):
                    if not raw_tickets.strip(): st.error("Daftar tiket kosong!")
                    else:
                        parsed = [t.strip().upper() for t in re.split(r'[,\n]+', raw_tickets) if t.strip()]
                        if parsed:
                            with st.spinner("Memasukkan tiket ke server..."):
                                client = gspread.authorize(get_credentials()).open_by_key(target_ss)
                                ws = client.worksheet(SHEET_TIKET_PM)
                                
                                new_rows = []
                                ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                                for t in parsed:
                                    new_rows.append([ts, nop_pm, bulan_pm, t, site_pm, "AVAILABLE"])
                                
                                ws.append_rows(new_rows)
                                fetch_spreadsheet_data.clear()
                                st.success(f"✅ Berhasil menambahkan {len(parsed)} Tiket PM Baru ke sistem!")
                                time.sleep(1.5); st.rerun()
        
        with c_pm2:
            st.markdown("### 📋 Daftar Tiket PM (Tersedia / AVAILABLE)")
            avail_pm_view = []
            for r in pm_r[1:]:
                try:
                    if len(r) >= 6 and str(r[1]).strip().upper() == nop_pm.strip().upper() and str(r[5]).strip().upper() == "AVAILABLE":
                        avail_pm_view.append({"Periode": r[2], "No Tiket": r[3], "Site/Cluster": r[4], "Status": r[5]})
                except: continue
            
            if avail_pm_view:
                st.dataframe(pd.DataFrame(avail_pm_view), hide_index=True, use_container_width=True)
            else:
                st.info("Tidak ada tiket PM yang tersedia di NOP ini. Silakan input di form sebelah kiri.")


# ==========================================
# PAGE 1: FORM REQUEST DANA
# ==========================================
elif st.session_state.page == "📝 Form Request Dana":
    st.markdown("<div class='header-card'><h2>📝 PORTAL PENGAJUAN DANA</h2><p>Operational System - Input Pengajuan Baru / Revisi (Multi-Split Engine)</p></div>", unsafe_allow_html=True)
    
    nop = st.selectbox("📌 1. Pilih Database Regional (NOP)", [""] + list(MASTER_DATA.keys()))
    
    if nop != "":
        st.markdown("<div class='section-title'>📋 2. Informasi Petugas & Tiket Pokok</div>", unsafe_allow_html=True)
        target_ss = MASTER_DATA[nop]["spreadsheet_id"]
        data_all = fetch_spreadsheet_data(target_ss)
        req_r, pjb_r, app_r = data_all[SHEET_REQUEST], data_all[SHEET_PJB], data_all[SHEET_APP]
        
        all_requested_tickets = [r[3].strip().upper() for r in req_r[1:] if len(r) > 3]
        site_dict, site_list, tim_dict, list_nopol_csv, nik_dict = load_excel_data()
        
        history_nopols = set()
        for r in req_r[1:]:
            if len(r) > 16 and r[16].strip(): history_nopols.add(r[16].strip().upper())
        for r in pjb_r[1:]:
            if len(r) > 12 and r[12].strip(): history_nopols.add(r[12].strip().upper())
            
        list_nopol = sorted(list(set([n.strip().upper() for n in list_nopol_csv if n.strip()] + list(history_nopols))))
        auto_lat_tujuan, auto_long_tujuan, auto_lat_brgkt, auto_long_brgkt = "0", "0", "0", "0"
        
        status_app_motor = "NONE"
        motor_limit_lock = False

        col1, col2 = st.columns(2)
        with col1:
            tanggal = st.date_input("Tanggal Pengajuan")
            cluster = st.selectbox("Cluster Regional", [""] + MASTER_DATA[nop]["clusters"])
            nama = st.selectbox("Nama Petugas / Pemohon (PIC Utama)", [""] + MASTER_DATA[nop]["names"])
            
            nama_lookup = nama.strip().upper()
            
            out_all, out_lock, aging_tickets, hist_cek = get_user_tickets_status(nama, req_r, pjb_r, app_r)
            if aging_tickets:
                st.warning(f"🔔 PENGINGAT: Sdr/i {nama}, Anda memiliki **{len(aging_tickets)}** pengajuan yang tertunda PJB >3 Hari!")
            
            for hc in hist_cek:
                if "DITOLAK" in hc["Status"]: st.error(f"⚠️ HARAP REVISI/RE-REQUEST: {hc['Tiket']} {hc['Status']}")
                elif "Review Admin" in hc["Status"]: st.warning(f"⏳ VERIFIKASI: {hc['Tiket']} Sedang Dalam Verifikasi Admin.")

            default_bank, default_no_rek = "BNI", ""
            if nama_lookup != "" and nama_lookup in tim_dict:
                auto_lat_brgkt, auto_long_brgkt = str(tim_dict[nama_lookup].get("Latitude", "0")), str(tim_dict[nama_lookup].get("Longtitude", "0"))
                for r in reversed(req_r[1:]): 
                    if len(r) > 18 and str(r[5]).strip().upper() == nama_lookup:
                        if str(r[17]).strip() in ["BNI", "BCA", "MANDIRI", "BRI"]:
                            default_bank, default_no_rek = str(r[17]).strip(), str(r[18]).strip(); break
                            
            is_locked_user = len(out_lock) > 0
            role = st.selectbox("Role Jabatan", ["-- Pilih Role --", "Admin", "Koordinator", "PM", "TE", "MBP", "CME"])
            
            if nop == "Palangkaraya" and len(site_list) > 0:
                site_id = st.selectbox("ID Site / Lokasi", [""] + site_list)
                if site_id != "-- Pilih Site ID --" and site_id in site_dict:
                    auto_lat_tujuan, auto_long_tujuan = str(site_dict[site_id].get("Latitude Tujuan", "0")), str(site_dict[site_id].get("Longtitude Tujuan", "0"))
            else: site_id = st.text_input("ID Site / Lokasi")

        with col2:
            keperluan = st.selectbox("Klasifikasi Keperluan Dana", LIST_KEPERLUAN)
            
            pm_selected_list = []
            if keperluan == "PM":
                st.markdown("<div style='background-color:#F0F9FF; padding:15px; border-radius:10px; border-left: 5px solid #0EA5E9; margin-bottom: 15px;'><b>🎫 Fitur Multi-Select Tiket PM</b><br><small>Silakan pilih sebanyak mungkin tiket yang akan dikerjakan dalam 1x pencairan dana ini.</small></div>", unsafe_allow_html=True)
                
                pm_r = data_all.get(SHEET_TIKET_PM, [])
                avail_pm = []
                for r in pm_r[1:]: 
                    try:
                        if len(r) >= 6:
                            cek_nop = str(r[1]).strip().replace(" ", "").upper()
                            target_nop = nop.strip().replace(" ", "").upper()
                            cek_status = str(r[5]).strip().upper()
                            cek_tiket = str(r[3]).strip().upper()
                            if cek_nop == target_nop and "AVAILABLE" in cek_status and cek_tiket != "":
                                avail_pm.append(cek_tiket)
                    except Exception:
                        continue
                        
                pm_selected_list = st.multiselect("Pilih Tiket PM yang akan digarap (Multi-Select):", avail_pm)
                tiket_string = ", ".join(pm_selected_list)
                
                if not tiket_string: tiket = st.text_input("Atau ketik Manual Tiket PM (Jika tidak ada di dropdown):")
                else: tiket = st.text_input("Tiket yang akan diajukan (Auto-Fill):", value=tiket_string, disabled=True)
            else:
                tiket = st.text_input("Nomor Tiket SWFM (WAJIB)")
                
            base_tiket_clean = tiket.strip().upper()
            
            is_duplicate = False
            is_rejected_request = False
            
            # Cek status "Request Dana" yang di reject di SHEET_APP
            for r in reversed(app_r[1:]):
                if len(r) > 5 and r[3] == "Request Dana" and str(r[2]).strip().upper() == base_tiket_clean:
                    if str(r[5]).strip().upper() == "REJECTED": is_rejected_request = True
                    break
            
            # Jika belum pernah ditolak Admin sepenuhnya, cek apakah duplikat
            if base_tiket_clean != "" and not is_rejected_request:
                for t in all_requested_tickets:
                    if base_tiket_clean in t: 
                        is_duplicate = True
                        break
                        
            status_izin = "NONE"
            if is_duplicate:
                safe_app_r = app_r[1:] if len(app_r) > 1 else []
                for r in reversed(safe_app_r):
                    if len(r) > 5 and r[3] == "Izin Revisi" and str(r[2]).strip().upper() == base_tiket_clean:
                        status_izin = str(r[5]).strip()
                        break
                        
                if status_izin != "APPROVED":
                    st.error(f"⛔ Akses Terkunci: Tiket Pokok **{base_tiket_clean}** sudah terdaftar di database. Untuk merevisi atau menambah item dana pada tiket ini, Anda **WAJIB** meminta Izin Revisi ke Admin.")
                    if status_izin == "PENDING":
                        st.warning("⏳ Status: Permintaan Izin Revisi Anda sedang MENUNGGU VERIFIKASI Admin di Approval Center.")
                    else:
                        if st.button("🚨 Minta Izin Revisi ke Admin Sekarang", type="primary", use_container_width=True):
                            append_data(SHEET_APP, [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), nama, base_tiket_clean, "Izin Revisi", 0, "PENDING", "-"], target_ss)
                            st.success("Permintaan Izin Revisi terkirim! Silakan hubungi Admin.")
                            time.sleep(2.5); st.rerun()
                    st.stop()
                else:
                    st.success("✅ Izin Revisi DIBERIKAN Admin. Silakan isi kembali data perbaikan Anda di bawah ini.")
                    
            if is_rejected_request:
                st.info(f"💡 Info: Request dengan tiket **{base_tiket_clean}** sebelumnya ditolak. Anda dapat menginput ulang (Re-Submit) di form ini.")

            deskripsi = st.text_area("Deskripsi Pekerjaan / Justifikasi (Harus Detail)", help="Contoh detail: PM membersihkan perangkat BTS dan area shelter dan recty")
            
            list_nama_tim = [n for n in MASTER_DATA[nop]["names"] if n.strip().upper() != nama_lookup and n != ""]
            tim_bareng = st.multiselect("👥 Pilih Rekan Tim yang Berangkat Bersama (Opsional)", list_nama_tim)
            
            tim_terkunci = []
            if role in ["TE", "MBP", "CME"] and tim_bareng:
                for member in tim_bareng:
                    _, m_out_lock, _, _ = get_user_tickets_status(member, req_r, pjb_r, app_r)
                    if len(m_out_lock) > 0: tim_terkunci.append(member)

        # --- CALCULATE MAPS FIRST SO UANG MAKAN & ESTIMASI BBM CAN USE THE DISTANCE ---
        st.markdown("<div class='section-title'>📍 3. Rute Peta (Satelit)</div>", unsafe_allow_html=True)
        c_lat1, c_lon1, c_lat2, c_lon2 = st.columns(4)
        with c_lat1: lat_berangkat = st.text_input("Lat Berangkat", value=auto_lat_brgkt)
        with c_lon1: long_berangkat = st.text_input("Long Berangkat", value=auto_long_brgkt)
        with c_lat2: lat_tujuan = st.text_input("Lat Tujuan", value=auto_lat_tujuan)
        with c_lon2: long_tujuan = st.text_input("Long Tujuan", value=auto_long_tujuan)

        jarak_km_oneway = 0.0
        jarak_km_pp = 0.0
        jarak_final_text = ""
        invalid_coords = False
        
        clat1, clon1 = clean_coord(lat_berangkat), clean_coord(long_berangkat)
        clat2, clon2 = clean_coord(lat_tujuan), clean_coord(long_tujuan)
        
        if clat1 != 0 and clon1 != 0 and clat2 != 0 and clon2 != 0:
            with st.spinner("Satelit menarik rute..."):
                jarak_km_oneway, poly, durasi_sec = get_route_and_distance(clon1, clat1, clon2, clat2)
            jarak_km_pp = jarak_km_oneway * 2
            
            dur_jam_pp = (durasi_sec * 2) / 3600.0
            jam_int = int(dur_jam_pp)
            mnt_int = int((dur_jam_pp - jam_int) * 60)
            
            jarak_final_text = f"{jarak_km_pp:.1f} Km (PP) | {jam_int} Jam {mnt_int} Mnt"
            st.info(f"🛣️ Jarak Tempuh Peta: **{jarak_km_pp:.1f} Km (PP)** (Titik HB ke Site: {jarak_km_oneway:.1f} Km)\n\n⏱️ Estimasi Waktu (PP): **{jam_int} Jam {mnt_int} Mnt**")
        else:
            invalid_coords = True
            st.warning("⚠️ Koordinat masih 0 / belum lengkap. Jika Anda memilih item kendaraan atau Uang Makan, sistem berpotensi menolak karena tidak bisa menghitung jarak.")

        # --- AUTO NOPOL BERDASARKAN NAMA TIM (DARI EXCEL/CSV) ---
        auto_nopol = ""
        if nama_lookup != "" and nama_lookup in tim_dict:
            auto_nopol = str(tim_dict[nama_lookup].get("NOPOL", "")).strip()
            if auto_nopol in ["nan", "0", "None"]: auto_nopol = ""

        # --- MULTI-SPLIT ENGINE FOR KEBUTUHAN DANA ---
        st.markdown("<div class='section-title'>🛒 4. Rincian Kebutuhan Dana (Pilih Bisa Lebih Dari 1)</div>", unsafe_allow_html=True)
        st.info("💡 **INFO SPLIT ENGINE:** Anda bisa memilih banyak kebutuhan sekaligus. Sistem akan otomatis **memecah form ini menjadi beberapa tiket PJB pending yang terpisah**.")
        
        kebutuhan_dana_list = st.multiselect("Silakan pilih seluruh jenis pengeluaran untuk tiket ini:", ["BBM", "Uang Makan", "Penginapan", "Material", "Fery Reguler/Carter", "Klotok/Kapal Carter"])
        
        sub_requests = []
        is_mobil = is_motor = is_genset = False
        total_motor_this_month = 0
        
        if "BBM" in kebutuhan_dana_list:
            st.markdown("<div style='background-color:#F8FAFC; padding:15px; border-radius:10px; border-left: 5px solid #3B82F6; margin-bottom: 15px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
            jns_bbm_list = st.multiselect("BBM untuk Kendaraan/Peralatan apa saja? (Bisa pilih lebih dari 1)", ["Mobil", "Motor", "Genset"])
            
            if "Mobil" in jns_bbm_list:
                is_mobil = True
                with st.expander("🚙 Input Nominal & Indikator BBM Mobil (Auto Nopol & Estimasi BBM)", expanded=True):
                    c_m1, c_m2 = st.columns(2)
                    with c_m1:
                        jb_mobil = st.selectbox("Jenis BBM Mobil", ["Pertalite", "Pertamax", "Dexlite", "Bio Solar", "Pertamina Dex"], key="b_mob")
                        
                        est_liter_mob = round(jarak_km_pp / 9.0, 1) if jarak_km_pp > 0 else 5.0
                        est_harga_mob = 10000 if "Pertalite" in jb_mobil else (12500 if "Pertamax" in jb_mobil else (14500 if "Dexlite" in jb_mobil else 6800))
                        default_est_dana_mob = int(est_liter_mob * est_harga_mob)
                        
                        keb_mobil = st.number_input("Estimasi Dana BBM Mobil (Rp)", min_value=0, step=1000, value=default_est_dana_mob, key="k_mob")
                        st.info(f"⛽ **Estimasi Otomatis:** Berdasarkan jarak PP {jarak_km_pp:.1f} KM (asumsi 9 KM/L), estimasi kebutuhan ± **{est_liter_mob} Liter**.")
                    with c_m2:
                        plat_mobil = st.text_input("Plat Mobil (Auto-Filled dari Nama Tim)", value=auto_nopol, key="p_mob").strip().upper()
                        last_km_mob = get_last_indicator(plat_mobil, "Mobil", pjb_r)
                        if plat_mobil: st.info(f"Histori KM terakhir (Auto-Track): **{last_km_mob}**")
                        km_awal_mob = st.number_input("Ketik KM Awal Mobil Aktual (Wajib)", min_value=0.0, step=0.1, value=float(last_km_mob), key="km_mob")
                        
                    sub_requests.append({
                        "tiket": f"{base_tiket_clean} [MOBIL]", "kategori": f"Mobil - {jb_mobil}",
                        "kebutuhan": keb_mobil, "plat": plat_mobil, "indikator": km_awal_mob, "last_ind": last_km_mob, "tipe": "Mobil"
                    })
                    
            if "Motor" in jns_bbm_list:
                is_motor = True
                with st.expander("🏍️ Input Nominal & Indikator BBM Motor (Auto Nopol & Estimasi BBM)", expanded=True):
                    c_mt1, c_mt2 = st.columns(2)
                    with c_mt1:
                        k_tangki = st.number_input("Kapasitas Tangki (Liter)", min_value=0.0, step=0.1, value=4.0, key="kt_mot")
                        h_satuan = st.number_input("Harga Satuan BBM (Rp/Liter)", min_value=0, step=500, value=10000, key="hs_mot")
                        
                        est_l_mot = round(jarak_km_pp / 35.0, 1) if jarak_km_pp > 0 else 2.0
                        l_butuh = st.number_input("Berapa Liter Kebutuhan?", min_value=0.0, step=0.1, value=est_l_mot, key="lb_mot")
                        keb_motor = int(l_butuh * h_satuan)
                        st.info(f"💰 Estimasi Dana: **Rp {keb_motor:,.0f}** (Estimasi ± {est_l_mot} Liter berdasarkan jarak PP)")
                        jb_motor = st.selectbox("Jenis BBM Motor", ["Pertalite", "Pertamax"], key="b_mot")
                    with c_mt2:
                        plat_motor = st.text_input("Plat Motor (Auto-Filled dari Nama Tim)", value=auto_nopol, key="p_mot").strip().upper()
                        last_km_mot = get_last_indicator(plat_motor, "Motor", pjb_r)
                        if plat_motor: st.info(f"Histori KM terakhir (Auto-Track): **{last_km_mot}**")
                        km_awal_mot = st.number_input("Ketik KM Awal Motor Aktual (Wajib)", min_value=0.0, step=0.1, value=float(last_km_mot), key="km_mot")
                    
                    if l_butuh > k_tangki and k_tangki > 0:
                        st.error("🚨 ANOMALI: Pengisian liter melebihi kapasitas tangki!")
                        motor_limit_lock = True
                        
                    sub_requests.append({
                        "tiket": f"{base_tiket_clean} [MOTOR]", "kategori": f"Motor - {jb_motor}",
                        "kebutuhan": keb_motor, "plat": plat_motor, "indikator": km_awal_mot, "last_ind": last_km_mot, "tipe": "Motor"
                    })
                    
                    current_month_str = datetime.now().strftime("%m/%Y")
                    for r in req_r[1:]:
                        if len(r) > 10:
                            try:
                                tgl_req = parse_date(r[1])
                                if tgl_req.strftime("%m/%Y") == current_month_str and str(r[5]).strip().upper() == nama_lookup:
                                    if "motor" in str(r[10]).lower(): total_motor_this_month += clean_nominal(r[9])
                            except: pass
                            
            if "Genset" in jns_bbm_list:
                is_genset = True
                with st.expander("⚡ Input Nominal & Indikator BBM Genset", expanded=True):
                    c_g1, c_g2 = st.columns(2)
                    with c_g1:
                        jb_genset = st.selectbox("Jenis BBM Genset", ["Dexlite", "Bio Solar", "Pertalite"], key="b_gen")
                        keb_genset = st.number_input("Estimasi Dana BBM Genset (Rp)", min_value=0, step=1000, value=150000, key="k_gen")
                    with c_g2:
                        plat_genset = st.text_input("ID / Kode / Plat Genset", key="p_gen").strip().upper()
                        last_rh_gen = get_last_indicator(plat_genset, "Genset", pjb_r)
                        if plat_genset: st.info(f"Histori RH terakhir: **{last_rh_gen}**")
                        rh_awal_gen = st.number_input("Ketik RH Awal Genset Aktual (Wajib)", min_value=0.0, step=0.1, value=float(last_rh_gen), key="rh_gen")
                        
                    sub_requests.append({
                        "tiket": f"{base_tiket_clean} [GENSET]", "kategori": f"Genset - {jb_genset}",
                        "kebutuhan": keb_genset, "plat": plat_genset, "indikator": rh_awal_gen, "last_ind": last_rh_gen, "tipe": "Genset"
                    })
            st.markdown("</div>", unsafe_allow_html=True)
            
        if "Uang Makan" in kebutuhan_dana_list or "Penginapan" in kebutuhan_dana_list:
            st.markdown("<div style='background-color:#E0F2FE; padding:15px; border-radius:10px; border-left: 5px solid #0284C7; margin-bottom: 15px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
            st.info("💡 **RULES AKOMODASI:** UM Maks Rp 60.000/hari (PP $\ge$ 80 KM). Penginapan Maks Rp 150.000/malam.")
            
            c_um1, c_um2 = st.columns(2)
            with c_um1:
                hari_req = st.number_input("Rencana Berapa Hari (Durasi Kerja)?", min_value=1, step=1, value=1)
                jml_org = 1 + len(tim_bareng)
                
            if "Uang Makan" in kebutuhan_dana_list:
                with c_um2:
                    max_um_nominal = 60000 * jml_org
                    nom_req_um = st.number_input(f"Nominal UM/Hari (Maks Rp 60.000 x {jml_org} org)", min_value=0, max_value=max_um_nominal, step=5000, value=max_um_nominal)
                    
                tot_um = hari_req * nom_req_um
                st.success(f"💰 Total Estimasi Uang Makan: **Rp {tot_um:,.0f}**")
                sub_requests.append({
                    "tiket": f"{base_tiket_clean} [UM]", "kategori": "Akomodasi",
                    "kebutuhan": tot_um, "plat": "", "indikator": 0.0, "last_ind": 0.0, "tipe": "UM",
                    "hari": hari_req, "nom_um": nom_req_um
                })
                
            if "Penginapan" in kebutuhan_dana_list:
                with c_um1:
                    malam_inap = st.number_input("Berapa Malam Menginap?", min_value=1, max_value=hari_req, step=1, value=hari_req if hari_req == 1 else hari_req - 1)
                with c_um2:
                    max_inap_nominal = 150000 * jml_org
                    nom_req_inap = st.number_input(f"Nominal Inap/Malam (Maks Rp 150.000 x {jml_org} org)", min_value=0, max_value=max_inap_nominal, step=10000, value=max_inap_nominal)
                    
                tot_inap = malam_inap * nom_req_inap
                st.success(f"🛏️ Total Estimasi Penginapan: **Rp {tot_inap:,.0f}**")
                sub_requests.append({
                    "tiket": f"{base_tiket_clean} [INAP]", "kategori": "Penginapan",
                    "kebutuhan": tot_inap, "plat": "", "indikator": 0.0, "last_ind": 0.0, "tipe": "Inap",
                    "hari": malam_inap, "nom_inap": nom_req_inap
                })
            st.markdown("</div>", unsafe_allow_html=True)
            
        if "Material" in kebutuhan_dana_list:
            with st.expander("📦 Detail Material", expanded=True):
                keb_mat = st.number_input("Estimasi Dana Material (Rp)", min_value=0, step=1000)
                sub_requests.append({"tiket": f"{base_tiket_clean} [MATERIAL]", "kategori": "Material", "kebutuhan": keb_mat, "plat": "", "indikator": 0.0, "last_ind": 0.0, "tipe": "Material"})
                
        if "Fery Reguler/Carter" in kebutuhan_dana_list:
            with st.expander("⛴️ Detail Fery Reguler/Carter", expanded=True):
                keb_fery = st.number_input("Estimasi Dana Fery (Rp)", min_value=0, step=1000)
                sub_requests.append({"tiket": f"{base_tiket_clean} [FERY]", "kategori": "Fery", "kebutuhan": keb_fery, "plat": "", "indikator": 0.0, "last_ind": 0.0, "tipe": "Fery"})
                
        if "Klotok/Kapal Carter" in kebutuhan_dana_list:
            with st.expander("🛥️ Detail Klotok/Kapal Carter", expanded=True):
                keb_klotok = st.number_input("Estimasi Dana Klotok (Rp)", min_value=0, step=1000)
                sub_requests.append({"tiket": f"{base_tiket_clean} [KLOTOK]", "kategori": "Klotok", "kebutuhan": keb_klotok, "plat": "", "indikator": 0.0, "last_ind": 0.0, "tipe": "Klotok"})

        total_kebutuhan_all = sum([r['kebutuhan'] for r in sub_requests])
        if sub_requests: st.markdown(f"<div class='metric-3d' style='border-top: 6px solid #10B981;'><div class='metric-title'>Total Kalkulasi Kebutuhan Dana Keseluruhan</div><div class='metric-value' style='background: -webkit-linear-gradient(45deg, #10B981, #059669); -webkit-background-clip: text;'>Rp {total_kebutuhan_all:,.0f}</div></div>", unsafe_allow_html=True)

        st.markdown("<div class='section-title'>🏦 5. Pembayaran & Lampiran</div>", unsafe_allow_html=True)
        col_pay1, col_pay2 = st.columns(2)
        with col_pay1:
            bank_idx = ["BNI", "BCA", "MANDIRI", "BRI"].index(default_bank) if default_bank in ["BNI", "BCA", "MANDIRI", "BRI"] else 0
            rek_penerima = st.selectbox("Bank Penerima / E-Wallet", ["BNI", "BCA", "MANDIRI", "BRI"], index=bank_idx)
            no_rek = st.text_input("Nomor Rekening Tujuan", value=default_no_rek)
        with col_pay2:
            st.info("Ketik nominal Total Transfer di bawah ini (Pastikan sesuai dengan total kalkulasi di atas).")
            nominal_tf_str = st.text_input("Total Nominal Transfer Final (TANPA TITIK/KOMA, Cth: 100000)", str(total_kebutuhan_all))
            if not nominal_tf_str.isdigit(): st.warning("⚠️ FORMAT SALAH: Nominal Transfer HANYA BOLEH ANGKA murni.")
            try: nominal_tf = int(nominal_tf_str.replace(".", "").replace(",", "").strip())
            except: nominal_tf = 0
            
        c_up1, c_up2 = st.columns(2)
        with c_up1: foto_km = st.file_uploader("Upload Foto KM / RH Genset Awal", type=["jpg", "png", "jpeg"])
        with c_up2: foto_evidance = st.file_uploader("Upload Foto Evidance Request", type=["jpg", "png", "jpeg"])
        
        form_invalid = (nama == "" or cluster == "" or role == "-- Pilih Role --" or keperluan == "" or not base_tiket_clean)

        if is_locked_user or len(tim_terkunci) > 0:
            if is_locked_user: st.error(f"⛔ AKSES DITOLAK: Sdr. {nama} dilarang Request Dana karena masih memiliki tiket PENDING Verifikasi, DITOLAK Admin, atau Belum di-PJB!")
            if len(tim_terkunci) > 0: st.error(f"⛔ AKSES DITOLAK: Rekan setim yang Anda bawa ({', '.join(tim_terkunci)}) memiliki PJB yang bermasalah/pending!")
        else:
            if is_motor:
                motor_kebutuhan = sum([r['kebutuhan'] for r in sub_requests if r['tipe'] == 'Motor'])
                if (total_motor_this_month + motor_kebutuhan) > 500000:
                    st.markdown("<div style='background-color:#FFE4E6; padding:20px; border-radius:10px; border-left: 5px solid #E11D48; margin-top:15px; margin-bottom: 25px;'>", unsafe_allow_html=True)
                    safe_app_r = app_r[1:] if len(app_r) > 1 else []
                    for r in reversed(safe_app_r):
                        if len(r) > 5 and str(r[2]).strip().upper() == base_tiket_clean and r[3] == "Limit Motor":
                            status_app_motor = str(r[5]).strip().upper()
                            break
                    if status_app_motor == "APPROVED": st.success("✅ Request kelebihan limit Motor telah disetujui Admin.")
                    elif status_app_motor == "PENDING":
                        st.warning("⏳ **STATUS APPROVAL:** Request kelebihan Limit Motor Anda sedang MENUNGGU VERIFIKASI Admin.")
                        motor_limit_lock = True
                    elif status_app_motor == "REJECTED":
                        st.error("❌ **STATUS APPROVAL:** DITOLAK Admin.")
                        motor_limit_lock = True
                    else:
                        st.error("🚨 **AKSES DITOLAK (LIMIT MOTOR):** Anda mencapai batas limit BBM Motor bulanan (>500k).")
                        if st.button("🚨 Minta Approval Kelebihan Limit ke Admin Sekarang", type="primary", use_container_width=True):
                            append_data(SHEET_APP, [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), nama, base_tiket_clean, "Limit Motor", motor_kebutuhan, "PENDING", f"Bulan ini: Rp {total_motor_this_month:,.0f}"], target_ss)
                            st.success("Berhasil diajukan ke Admin!"); time.sleep(2.5); st.rerun()
                        motor_limit_lock = True
                    st.markdown("</div>", unsafe_allow_html=True)
            
            if not motor_limit_lock:
                if st.button("📤 Submit Request Dana (Generate Tiket Split)", type="primary", use_container_width=True):
                    if form_invalid: 
                        st.error("❌ PENGIRIMAN DITOLAK: Pastikan semua form identitas dasar dan Tiket terisi lengkap!")
                        st.stop()
                    if not sub_requests:
                        st.error("❌ PENGIRIMAN DITOLAK: Anda belum memilih/mengisi satu pun Kebutuhan Dana!")
                        st.stop()
                    if nominal_tf <= 0:
                        st.error("❌ PENGIRIMAN DITOLAK: Total Nominal Transfer tidak boleh 0 / kosong!")
                        st.stop()
                        
                    for req in sub_requests:
                        if req['tipe'] in ['UM', 'Inap']:
                            if not (is_mobil or is_motor or is_genset) or invalid_coords:
                                st.error(f"❌ REQUEST {req['tipe']} DITOLAK: Koordinat Peta tidak valid. Syarat wajib adalah jarak tempuh aktual terdeteksi.")
                                st.stop()
                            if jarak_km_pp < 80:
                                st.error(f"❌ REQUEST {req['tipe']} DITOLAK: Jarak tempuh (Pulang-Pergi / PP) Anda hanya {jarak_km_pp:.1f} KM. Syarat wajib pencairan adalah jarak PP >= 80 KM.")
                                st.stop()
                            if len(deskripsi.strip().replace(" ", "")) <= 15:
                                st.error(f"❌ REQUEST {req['tipe']} DITOLAK: Deskripsi pekerjaan yang Anda ketik terlalu singkat.")
                                st.stop()
                        elif req['tipe'] in ['Mobil', 'Motor', 'Genset']:
                            if req['indikator'] <= 0:
                                st.error(f"❌ PENGIRIMAN DITOLAK: Angka KM/RH Awal pada {req['tipe']} bernilai 0!")
                                st.stop()
                            if req['indikator'] < req['last_ind']:
                                st.error(f"❌ PENGIRIMAN DITOLAK: Angka KM/RH pada {req['tipe']} ({req['indikator']}) tidak boleh lebih kecil dari histori terakhir ({req['last_ind']})!")
                                st.stop()
                    
                    with st.spinner(f"🚀 Memecah data menjadi {len(sub_requests)} tiket terpisah & Mengupload Server..."):
                        url_km = upload_foto(foto_km)
                        url_evidance = upload_foto(foto_evidance)
                        
                        ts_now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        tgl_str = tanggal.strftime("%d/%m/%Y")
                        
                        for req in sub_requests:
                            desc_final = deskripsi
                            if tim_bareng: desc_final += f"\n\n[Tim: {', '.join(tim_bareng)}]"
                            if req['tipe'] == 'UM': desc_final += f"\n\n[REQ AKOMODASI: {req['hari']} Hari @ Rp {req['nom_um']:,.0f}/hari = Rp {req['kebutuhan']:,.0f}]"
                            elif req['tipe'] == 'Inap': desc_final += f"\n\n[REQ PENGINAPAN: {req['hari']} Malam @ Rp {req['nom_inap']:,.0f}/malam = Rp {req['kebutuhan']:,.0f}]"
                            
                            data_req = [
                                ts_now, tgl_str, nop, req['tiket'], cluster, nama, role, site_id, keperluan, 
                                req['kebutuhan'], req['kategori'], desc_final, str(req['indikator']), 
                                jarak_final_text, lat_berangkat, long_berangkat, req['plat'], 
                                rek_penerima, no_rek, nominal_tf, url_km, url_evidance, lat_tujuan, long_tujuan
                            ]
                            append_data(SHEET_REQUEST, data_req, target_ss)
                            
                            if req['plat'] and req['plat'] not in list_nopol:
                                save_new_nopol_to_csv(req['plat'])
                                
                        if pm_selected_list:
                            update_pm_ticket_status(target_ss, pm_selected_list, "REQUESTED")
                            
                        st.balloons(); st.success(f"🎉 Berhasil memecah form ini menjadi {len(sub_requests)} pending PJB terpisah!"); time.sleep(3); st.session_state.page = "🏠 Hub Menu Utama"; st.rerun()


# ==========================================
# PAGE 2: FORM PJB OPERASIONAL 
# ==========================================
elif st.session_state.page == "✅ Form PJB Operasional":
    st.markdown("<div class='header-card'><h2>✅ PORTAL PJB (PENYELESAIAN)</h2><p>Pilih dan selesaikan sub-tiket Anda secara spesifik.</p></div>", unsafe_allow_html=True)
    
    nop_cari = st.selectbox("📂 1. Pilih Database (NOP):", ["-- Pilih NOP --"] + list(MASTER_DATA.keys()))
    
    if nop_cari != "-- Pilih NOP --":
        target_ss = MASTER_DATA[nop_cari]["spreadsheet_id"]
        data_all = fetch_spreadsheet_data(target_ss)
        req_r, pjb_r, app_r = data_all[SHEET_REQUEST], data_all[SHEET_PJB], data_all[SHEET_APP]
        
        site_dict, site_list, tim_dict, list_nopol_csv, nik_dict = load_excel_data()
        
        pjb_tickets_all_set = set()
        for r in pjb_r[1:]:
            if len(r) > 21 and r[21].strip() != "":
                tk_str = r[36].strip() if (len(r) > 36 and r[36].strip()) else r[21].strip()
                pjb_tickets_all_set.update([t.strip().upper() for t in tk_str.split(",")])
        
        status_verif_dict = {}
        for r in app_r[1:]:
            if len(r) > 5 and r[3] == "Verifikasi PJB":
                tiket_app = str(r[2]).strip().upper()
                if tiket_app != "": status_verif_dict[tiket_app] = str(r[5]).strip()
        
        st.markdown("<div class='section-title'>🔍 2. Identifikasi Tim & Tarik Sub-Tiket Data</div>", unsafe_allow_html=True)
        col_id1, col_id2 = st.columns([2, 2])
        with col_id1: nama_pjb = st.selectbox("👤 Pilih Nama Anda:", ["-- Pilih Nama --"] + MASTER_DATA[nop_cari]["names"])
        
        if nama_pjb != "-- Pilih Nama --":
            out_all, out_lock, aging_tickets, hist_cek = get_user_tickets_status(nama_pjb, req_r, pjb_r, app_r)
            if aging_tickets: st.warning(f"🔔 NOTIFIKASI: Anda memiliki **{len(aging_tickets)}** tiket tertunda >3 hari.")
            for hc in hist_cek:
                if "DITOLAK" in hc["Status"]: st.error(f"⚠️ HARAP REVISI/RE-REQUEST: {hc['Tiket']} {hc['Status']}")
                elif "Review Admin" in hc["Status"]: st.warning(f"⏳ PENDING VERIFIKASI: {hc['Tiket']}")

        with col_id2: pass_nominal = st.text_input("🔑 Akses Nominal (Admin):", type="password")
            
        pending_list, pending_options = [], []
        for r in req_r[1:]:
            if len(r)>5 and str(r[3]).strip() != "":
                req_tk_raw = str(r[3]).strip().upper()
                req_tk_list = [t.strip() for t in req_tk_raw.split(",") if t.strip()]
                nm = str(r[5]).strip().upper()
                
                req_set = set(req_tk_list)
                is_ready_to_pjb = False
                
                if not req_set.issubset(pjb_tickets_all_set):
                    is_ready_to_pjb = True
                elif status_verif_dict.get(req_tk_raw) == "REJECTED":
                    is_ready_to_pjb = True 
                    
                if is_ready_to_pjb:
                    item = {"Tanggal": r[1], "Nama": r[5], "No Request": req_tk_raw, "Kategori Item": r[10] if len(r)>10 else "", "Keperluan": r[8] if len(r)>8 else ""}
                    if pass_nominal == "B0924649": item["Nominal Request"] = f"Rp {clean_nominal(r[9]):,.0f}" if len(r)>9 else "Rp 0"
                    
                    if "PM" in (r[8] if len(r)>8 else ""):
                        rem = [t for t in req_tk_list if t not in pjb_tickets_all_set]
                        item["Sisa Tiket PM"] = ", ".join(rem) if rem else "Semua (Ditolak)"
                    
                    if nama_pjb != "-- Pilih Nama --":
                        if nm == nama_pjb.strip().upper(): pending_list.append(item); pending_options.append(req_tk_raw)
                    else: pending_list.append(item)
        
        if pending_list: st.dataframe(pd.DataFrame(pending_list), hide_index=True, use_container_width=True)
        else: st.success("💎 Seluruh sub-tiket sudah di-PJB!")
        
        st.info("💡 Jika Anda sedang **merevisi PJB (Izin Revisi Approved)** namun tidak muncul di dropdown, silakan gunakan opsi **-- Ketik Manual --** dan masukkan nomor tiketnya secara spesifik.")
        col_s2, col_s3 = st.columns([3, 1])
        with col_s2: 
            pilihan_tiket = st.selectbox("🎫 Pilih Sub-Tiket Pending yang ingin di-PJB-kan:", ["-- Pilih Tiket --"] + pending_options + ["-- Ketik Manual --"]) if pending_options else "-- Ketik Manual --"
            cari_tiket = st.text_input("Ketik Manual (Termasuk Request Baru Hasil Izin Revisi):") if pilihan_tiket == "-- Ketik Manual --" else ("" if pilihan_tiket == "-- Pilih Tiket --" else pilihan_tiket)
        
        valid_cari_tiket = str(cari_tiket).strip().upper()

        with col_s3: 
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Tarik Data PJB", type="primary", use_container_width=True) and valid_cari_tiket:
                ditemukan_req = None
                ditemukan_pjb = None
                
                for r in reversed(req_r[1:]):
                    if len(r) > 3 and str(r[3]).strip().upper() == valid_cari_tiket:
                        ditemukan_req = {
                            "NOP": r[2], "Cluster": r[4], "Nama": r[5], "Role": r[6], "Site": r[7], "Keperluan": r[8], 
                            "BBM": r[10] if len(r)>10 else "", "Desc": r[11] if len(r)>11 else "", 
                            "KMAwal": clean_indicator(r[12]) if len(r)>12 else 0.0, 
                            "NominalReq": clean_nominal(r[9]) if len(r)>9 else 0, 
                            "Jarak": r[13] if len(r)>13 else "", "Plat": r[16] if len(r)>16 else "",
                            "LatBerangkat": r[14] if len(r)>14 else "0",
                            "LongBerangkat": r[15] if len(r)>15 else "0",
                            "LatTujuan": r[22] if len(r)>22 else "0",
                            "LongTujuan": r[23] if len(r)>23 else "0",
                        }
                        break
                        
                for r in reversed(pjb_r[1:]):
                    if len(r) > 21 and str(r[21]).strip().upper() == valid_cari_tiket:
                        ditemukan_pjb = r
                        break
                        
                if ditemukan_req:
                    if ditemukan_pjb:
                        ditemukan_req["km_akhir_lama"] = float(clean_indicator(ditemukan_pjb[10])) if len(ditemukan_pjb)>10 else 0.0
                        ditemukan_req["liter_lama"] = str(ditemukan_pjb[22]) if len(ditemukan_pjb)>22 else "0"
                        ditemukan_req["harga_lama"] = int(clean_nominal(ditemukan_pjb[23])) if len(ditemukan_pjb)>23 else 0
                        ditemukan_req["nota_lama"] = int(clean_nominal(ditemukan_pjb[20])) if len(ditemukan_pjb)>20 else 0
                        
                    st.session_state.pjb_data = ditemukan_req
                    st.success("🎉 Data Ditarik!")
                else:
                    st.session_state.pjb_data = None
                    st.error("❌ Data Pengajuan (Request) Tidak ditemukan di Database.")

        if st.session_state.get("pjb_data"):
            d = st.session_state.pjb_data
            
            is_pm = ("PM" in str(d["Keperluan"]).upper())
            specific_pm_tickets = valid_cari_tiket
            
            if is_pm:
                st.markdown("<div style='background-color:#F0F9FF; padding:15px; border-radius:10px; border-left: 5px solid #0EA5E9; margin-bottom: 15px;'><b>🎫 PJB Parsial (Khusus PM Multi-Select)</b></div>", unsafe_allow_html=True)
                req_tk_list = [t.strip() for t in valid_cari_tiket.split(",") if t.strip()]
                remaining = [t for t in req_tk_list if t not in pjb_tickets_all_set]
                if not remaining: remaining = req_tk_list
                selected_pm = st.multiselect("Pilih Tiket PM yang ingin dilaporkan:", remaining, default=remaining)
                specific_pm_tickets = ", ".join(selected_pm)

            st.markdown("<div class='section-title'>⚙️ Kategori Pelaporan (Auto-Locked)</div>", unsafe_allow_html=True)
            if "akomodasi" in str(d["BBM"]).lower():
                jns_pjb = "🍽️ Biaya Akomodasi"
                st.info("📌 **Kategori Sub-Tiket:** BIAYA AKOMODASI")
            else:
                jns_pjb = "🛠️ Operational Umum"
                st.info(f"📌 **Kategori Sub-Tiket:** {str(d['BBM']).upper()}")
            
            st.markdown("<div class='section-title'>💸 Validasi Budget & Bukti Transfer</div>", unsafe_allow_html=True)
            f_transfer = st.file_uploader("Upload Foto Bukti Transfer Dana (WAJIB)", type=["jpg", "png", "jpeg"])
            
            if f_transfer is None:
                st.warning("⚠️ **AKSES TERKUNCI:** Silakan upload Bukti Transfer dari Admin terlebih dahulu.")
            else:
                st.success("✅ Bukti Transfer terlampir.")
                
                st.markdown("<div class='section-title'>🔒 Rincian Terkunci (Sistem)</div>", unsafe_allow_html=True)
                c_a, c_b, c_c = st.columns([2, 1, 2])
                with c_a:
                    tgl_pjb = st.date_input("Tanggal PJB")
                    st.text_input("Nama Petugas", d["Nama"], disabled=True)
                    st.text_input("Kategori Sub-Tiket & Plat", f'{d["BBM"]} - {d["Plat"]}', disabled=True)
                with c_b:
                    nik_petugas = nik_dict.get(d["Nama"].strip().upper(), "-")
                    st.text_input("NIK Karyawan (Dari Excel)", nik_petugas, disabled=True)
                with c_c:
                    st.text_input("Site ID Tujuan", d["Site"], disabled=True)
                    st.text_input("Keperluan", d["Keperluan"], disabled=True)
                    
                    if "Operational" in jns_pjb: nominal_pjb = st.number_input("Nominal PJB Terpakai pada sub-tiket ini", value=int(d["NominalReq"]))
                    else: st.info("Nominal PJB disesuaikan dengan Kalkulator UM di bawah.")

                d_km_awal = float(d["KMAwal"])
                km_akhir = d_km_awal
                total_km_tempuh = 0.0
                tot_liter = "0"
                harga_satuan = 0
                tot_nilai_nota = 0
                f_isi, f_nota_bbm, f_mat, f_notamat, f_inap, f_kerja, f_km = None, None, None, None, None, None, None
                f_um1, f_um2, f_um3, f_um4 = None, None, None, None
                
                is_genset = "genset" in str(d["BBM"]).lower()
                is_vehicle = "mobil" in str(d["BBM"]).lower() or "motor" in str(d["BBM"]).lower() or is_genset
                
                label_akhir = "RH Genset Akhir" if is_genset else "KM Akhir Kendaraan"
                info_text = "Total Jam Backup (RH)" if is_genset else "Total Perjalanan (KM)"
                icon_text = "⏱️" if is_genset else "🛣️"
                
                # Fetch actual last KM from PJB history to enforce continuity
                jenis_kendaraan = "Mobil" if "mobil" in str(d["BBM"]).lower() else ("Motor" if "motor" in str(d["BBM"]).lower() else "Genset")
                real_km_awal = get_last_indicator(d["Plat"].strip().upper(), jenis_kendaraan, pjb_r) if is_vehicle else 0.0
                
                if "Operational" in jns_pjb:
                    st.markdown("<div class='section-title'>📝 Realisasi Lapangan & Nominal (Fisik)</div>", unsafe_allow_html=True)
                    if is_vehicle:
                        c_c1, c_d1 = st.columns(2)
                        with c_c1:
                            st.info(f"📍 {label_akhir.split(' ')[0]} Terakhir di Sistem (Histori PJB Sebelumnya): **{real_km_awal}**")
                            st.caption(f"*(Mengabaikan input saat request ({d_km_awal}) agar perhitungan valid dari PJB ke PJB)*")
                            
                            default_km_akhir = float(d.get("km_akhir_lama", real_km_awal))
                            km_akhir = st.number_input(f"Ketik Angka {label_akhir} AKTUAL SAAT INI (Wajib)", min_value=0.0, value=default_km_akhir, step=0.1)
                            
                            total_km_tempuh = km_akhir - real_km_awal
                            
                            if km_akhir > 0 and total_km_tempuh >= 0: st.info(f"{icon_text} Kalkulasi {info_text} (Trip): **{total_km_tempuh:.2f}**")
                            elif km_akhir > 0 and total_km_tempuh < 0: st.error(f"⚠️ PERINGATAN: Angka yang diketik lebih kecil dari KM/RH Awal histori ({real_km_awal})!")
                        
                        with c_d1:
                            tot_liter = st.text_input("Total Liter BBM", value=d.get("liter_lama", "0"))
                            harga_satuan = st.number_input("Harga Satuan (BBM)", min_value=0, step=500, value=d.get("harga_lama", 0))
                            tot_nilai_nota = st.number_input("Total Fisik Sesuai Nota (Rp)", min_value=0, step=1000, value=d.get("nota_lama", 0))
                            
                        st.markdown("<div class='section-title'>📸 Lampiran Bukti Utama</div>", unsafe_allow_html=True)
                        p1, p2, p3 = st.columns(3)
                        with p1: f_isi = st.file_uploader("1. Foto Evidance Pengisian", type=["jpg","png"])
                        with p2: f_km = st.file_uploader("2. Foto Nota disanding KM/RH", type=["jpg","png"])
                        with p3: f_kerja = st.file_uploader("3. Foto Evidance Pekerjaan", type=["jpg","png"])
                    else:
                        c_m1, c_m2 = st.columns(2)
                        with c_m1:
                            tot_nilai_nota = st.number_input("Total Fisik Sesuai Kwitansi/Nota (Rp)", min_value=0, step=1000, value=d.get("nota_lama", 0))
                        with c_m2:
                            km_akhir = d_km_awal
                            total_km_tempuh = 0.0
                            tot_liter = "0"
                            harga_satuan = 0
                            
                        st.markdown("<div class='section-title'>📸 Lampiran Bukti Utama</div>", unsafe_allow_html=True)
                        p1, p2, p3 = st.columns(3)
                        with p1: f_nota_bbm = st.file_uploader("1. Kwitansi Support", type=["jpg","png"])
                        
                        if "penginapan" in str(d["BBM"]).lower():
                            with p2: f_inap = st.file_uploader("2. Foto Nota/Kwitansi Hotel", type=["jpg","png"])
                        else:
                            with p2: f_notamat = st.file_uploader("2. Foto Nota Material Disanding", type=["jpg","png"])
                            
                        with p3: f_kerja = st.file_uploader("3. Foto Evidance Pekerjaan", type=["jpg","png"])
                else:
                    st.markdown("<div class='section-title'>🗓️ Rincian Keberangkatan & Nominal Uang Makan</div>", unsafe_allow_html=True)
                    c_um_a, c_um_b, c_um_c = st.columns(3)
                    with c_um_a: tgl_berangkat = st.date_input("Tanggal Keberangkatan", value=tgl_pjb)
                    with c_um_b: lama_hari = st.number_input("Lama Hari (Durasi Kerja)", min_value=1, step=1, value=1)
                    with c_um_c: nom_um_harian = st.number_input("Nominal Uang Makan Harian", min_value=0, step=5000, value=60000)
                    
                    tgl_kembali = tgl_berangkat + timedelta(days=lama_hari)
                    total_um_calc = lama_hari * nom_um_harian
                    st.success(f"📅 Tanggal Kembali: **{tgl_kembali.strftime('%d/%m/%Y')}** | 💰 Total Uang Makan: **Rp {total_um_calc:,.0f}**")
                    
                    st.markdown("<div class='section-title'>📸 Lampiran Eviden Aktivitas Uang Makan (WAJIB 4 FOTO)</div>", unsafe_allow_html=True)
                    c_um1, c_um2, c_um3, c_um4 = st.columns(4)
                    with c_um1: f_um1 = st.file_uploader("Foto Aktivitas 1", type=["jpg","png","jpeg"], key="um1")
                    with c_um2: f_um2 = st.file_uploader("Foto Aktivitas 2", type=["jpg","png","jpeg"], key="um2")
                    with c_um3: f_um3 = st.file_uploader("Foto Aktivitas 3", type=["jpg","png","jpeg"], key="um3")
                    with c_um4: f_um4 = st.file_uploader("Foto Aktivitas 4", type=["jpg","png","jpeg"], key="um4")

                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🚀 Sahkan Pelaporan PJB / Submit Revisi", type="primary", use_container_width=True):
                    if "Operational" in jns_pjb:
                        if is_vehicle and (km_akhir <= 0):
                            st.error(f"❌ PENGIRIMAN DITOLAK: {label_akhir} aktual belum diisi!")
                            st.stop()
                        elif is_vehicle and (km_akhir < real_km_awal):
                            st.error(f"❌ PENGIRIMAN DITOLAK: Angka yang dimasukkan ({km_akhir}) lebih kecil dari KM/RH Awal histori ({real_km_awal})!")
                            st.stop()
                    else:
                        if not (f_um1 and f_um2 and f_um3 and f_um4):
                            st.error("❌ PENGIRIMAN DITOLAK: Anda WAJIB mengunggah 4 Foto Eviden Aktivitas!")
                            st.stop()
                            
                    with st.spinner("Mengupload foto dan men-generate laporan ke sistem..."):
                        if "Akomodasi" in jns_pjb: nominal_pjb = total_um_calc 
                            
                        url_um1 = upload_foto(f_um1) if f_um1 else ""
                        url_um2 = upload_foto(f_um2) if f_um2 else ""
                        url_um3 = upload_foto(f_um3) if f_um3 else ""
                        url_um4 = upload_foto(f_um4) if f_um4 else ""
                        
                        url_isi = upload_foto(f_isi) if f_isi else ""                  
                        url_notabbm = upload_foto(f_nota_bbm) if f_nota_bbm else ""    
                        url_km = upload_foto(f_km) if f_km else ""                     
                        url_mat = upload_foto(f_mat) if f_mat else ""                  
                        url_notamat = upload_foto(f_notamat) if f_notamat else ""      
                        url_inap = upload_foto(f_inap) if f_inap else ""               
                        url_kerja = upload_foto(f_kerja) if f_kerja else ""            
                        
                        tgl_berangkat_str = tgl_berangkat.strftime("%d/%m/%Y") if "Akomodasi" in jns_pjb else ""
                        lama_hari_str = str(lama_hari) if "Akomodasi" in jns_pjb else ""
                        nom_um_harian_str = str(nom_um_harian) if "Akomodasi" in jns_pjb else ""
                        
                        pdf_link_cloud = ""
                        b64_html = ""
                        
                        if "Akomodasi" in jns_pjb:
                            bulan_romawi = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]
                            romawi = bulan_romawi[tgl_pjb.month] if 1 <= tgl_pjb.month <= 12 else "VIII"
                            logo_base64 = get_local_img_base64("koperasi-jasa-konstruksi-tower-event-organizer-network-monitoring-telekomunikasi-kisel-group-logo-kut.webp")

                            html_um = f"""
                            <!DOCTYPE html>
                            <html>
                            <head>
                                <meta charset="UTF-8">
                                <title>Surat Tugas & PJB - {valid_cari_tiket}</title>
                                <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
                                <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
                                <style>
                                    body {{ font-family: 'Times New Roman', Times, serif; font-size: 11pt; line-height: 1.5; margin: 0; background: #525659; }}
                                    @page {{ size: A4; margin: 0; }}
                                    .page {{ 
                                        width: 210mm; min-height: 297mm; background: white; margin: 10mm auto; 
                                        padding: 15mm 20mm; box-sizing: border-box; box-shadow: 0 0 10px rgba(0,0,0,0.5);
                                        page-break-after: always; position: relative;
                                    }}
                                    h3 {{ text-align: center; font-size: 14pt; margin-bottom: 15px; font-weight: bold; }}
                                    table {{ width: 100%; border-collapse: collapse; margin-bottom: 10px; font-size: 11pt; }}
                                    .tbl-info td {{ padding: 3px 5px; vertical-align: top; }}
                                    .tbl-data th, .tbl-data td {{ border: 1px solid black; padding: 6px; text-align: center; }}
                                    .tbl-uang td, .tbl-uang th {{ border: 1px solid black; padding: 6px; }}
                                    .signature {{ display: flex; justify-content: space-between; margin-top: 30px; text-align: center; }}
                                    .signature div {{ width: 45%; }}
                                    .photo-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 20px; }}
                                    .photo-item {{ text-align: center; border: 1px solid #ddd; padding: 10px; border-radius: 5px; }}
                                    .photo-item img {{ width: 100%; max-height: 250px; object-fit: contain; }}
                                    .logo-header {{ text-align: right; margin-bottom: 10px; padding-right: 5px; }}
                                    .logo-header img {{ width: 220px; height: auto; object-fit: contain; }}
                                </style>
                            </head>
                            <body>
                                <div class="page">
                                    <div class="logo-header"><img src="{logo_base64}" alt="Logo KUT"></div>
                                    <div class="content">
                                        <h3 style="letter-spacing: 5px;"><u>SURAT TUGAS</u></h3>
                                        <table class="tbl-info" style="width: 70%;">
                                            <tr><td width="150">Nama</td><td width="10">:</td><td>Okta Pradika</td></tr>
                                            <tr><td>NIK</td><td>:</td><td>B0924649</td></tr>
                                            <tr><td>Jabatan</td><td>:</td><td>Koordinator NOP Palangka Raya</td></tr>
                                        </table>
                                        <table class="tbl-data">
                                            <tr><th>No.</th><th>Nama</th><th>NIK</th><th>Jabatan</th><th>Lokasi Kerja</th></tr>
                                            <tr><td>1</td><td>{d['Nama']}</td><td>{nik_petugas}</td><td>{d['Role']}</td><td>{d['Site']}</td></tr>
                                        </table>
                                        <table class="tbl-info">
                                            <tr><td width="150">No Ticket</td><td width="10">:</td><td>{specific_pm_tickets}</td></tr>
                                            <tr><td>Tujuan</td><td>:</td><td>{d['Site']}</td></tr>
                                            <tr><td>Estimasi Jarak (Peta)</td><td>:</td><td><b>{d.get('Jarak', '-')}</b></td></tr>
                                            <tr><td>Lama tugas dinas</td><td>:</td><td>{lama_hari} Hari</td></tr>
                                            <tr><td>Tgl. Berangkat</td><td>:</td><td>{tgl_berangkat.strftime("%d/%m/%Y")}</td></tr>
                                            <tr><td>Tgl. Kembali</td><td>:</td><td>{tgl_kembali.strftime("%d/%m/%Y")}</td></tr>
                                            <tr><td>Keperluan</td><td>:</td><td>{d['Keperluan']}</td></tr>
                                        </table>
                                        <div style="text-align: right; margin-top: 30px;">Palangka Raya, {tgl_pjb.strftime("%d/%m/%Y")}</div>
                                        <div class="signature">
                                            <div><p>Koordinator NOP Palangka Raya,</p><br><br><br><p><b><u>Okta Pradika</u></b><br>NIK. B0924649</p></div>
                                            <div><p>POH. SPV Operation,</p><br><br><br><p><b><u>Rian Sharon</u></b><br>NIK. 79058</p></div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="page">
                                    <div class="logo-header"><img src="{logo_base64}" alt="Logo KUT"></div>
                                    <div class="content">
                                        <h3><u>SURAT PENGAJUAN UANG MAKAN</u></h3>
                                        <div style="text-align: center; margin-top: -15px; margin-bottom: 20px;">Nomor : &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; /KUT/{romawi}/{tgl_pjb.year}</div>
                                        <table class="tbl-info" style="width: 70%;">
                                            <tr><td width="150">Nama</td><td width="10">:</td><td>{d['Nama']}</td></tr>
                                            <tr><td>NIK</td><td>:</td><td>{nik_petugas}</td></tr>
                                            <tr><td>Jabatan</td><td>:</td><td>{d['Role']}</td></tr>
                                        </table>
                                        <table class="tbl-data">
                                            <tr><th>No.</th><th>Tujuan Tugas</th><th>Berangkat</th><th>Kembali</th><th>Uraian Penugasan</th></tr>
                                            <tr><td>1</td><td>{d['Site']}</td><td>{tgl_berangkat.strftime("%d/%m/%Y")}</td><td>{tgl_kembali.strftime("%d/%m/%Y")}</td><td>{d.get('Desc', '-')}</td></tr>
                                        </table>
                                        <div style="margin-top: 15px;"><b>Peta Satelit Rute Perjalanan:</b><div id="map" style="height: 250px; width: 100%; border: 1px solid #475569; border-radius: 8px; margin-top: 5px;"></div></div>
                                        <table class="tbl-uang" style="margin-top:15px;">
                                            <tr style="background: #f0f0f0;"><th colspan="3">Bantuan Perjalanan Dinas</th><th colspan="2">Perhitungan</th><th>Jumlah</th></tr>
                                            <tr><td colspan="3">Uang Makan ({d['Nama']})</td><td align="center">{lama_hari} Hari x Rp. {nom_um_harian:,.0f}</td><td width="30">Rp.</td><td align="right">{total_um_calc:,.0f}</td></tr>
                                            <tr><th colspan="5" align="right">Jumlah Total</th><th align="right">Rp. {total_um_calc:,.0f}</th></tr>
                                        </table>
                                        <div class="signature">
                                            <div><p>Koordinator NOP Palangka Raya,</p><br><br><br><p><b><u>Okta Pradika</u></b><br>NIK. B0924649</p></div>
                                            <div><p>POH. SPV Operation,</p><br><br><br><p><b><u>Rian Sharon</u></b><br>NIK. 79058</p></div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="page">
                                    <div class="logo-header"><img src="{logo_base64}" alt="Logo KUT"></div>
                                    <div class="content">
                                        <h3><u>LAMPIRAN FOTO AKTIVITAS LAPANGAN</u></h3>
                                        <div class="photo-grid">
                                            <div class="photo-item"><img src="{url_um1}"><br><b>Foto Aktivitas 1</b></div>
                                            <div class="photo-item"><img src="{url_um2}"><br><b>Foto Aktivitas 2</b></div>
                                            <div class="photo-item"><img src="{url_um3}"><br><b>Foto Aktivitas 3</b></div>
                                            <div class="photo-item"><img src="{url_um4}"><br><b>Foto Aktivitas 4</b></div>
                                        </div>
                                    </div>
                                </div>
                                <script>
                                    window.onload = function() {{
                                        var lat1 = parseFloat("{d.get('LatBerangkat', '0')}");
                                        var lon1 = parseFloat("{d.get('LongBerangkat', '0')}");
                                        var lat2 = parseFloat("{d.get('LatTujuan', '0')}");
                                        var lon2 = parseFloat("{d.get('LongTujuan', '0')}");
                                        if (lat1 !== 0 && lat2 !== 0) {{
                                            var map = L.map('map');
                                            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png').addTo(map);
                                            var latlngs = [ [lat1, lon1], [lat2, lon2] ];
                                            var polyline = L.polyline(latlngs, {{color: 'red', weight: 4}}).addTo(map);
                                            L.marker([lat1, lon1]).addTo(map); L.marker([lat2, lon2]).addTo(map);
                                            map.fitBounds(polyline.getBounds(), {{padding: [30,30]}});
                                            setTimeout(function(){{ window.print(); }}, 1500);
                                        }}
                                    }};
                                </script>
                            </body>
                            </html>
                            """
                            b64_html = base64.b64encode(html_um.encode("utf-8")).decode()
                            try:
                                with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
                                    tmp.write(html_um.encode('utf-8'))
                                    tmp_path = tmp.name
                                res_cloud = cloudinary.uploader.upload(tmp_path, resource_type="raw")
                                pdf_link_cloud = res_cloud.get("secure_url", "")
                                os.remove(tmp_path)
                            except Exception: pass
                            
                            st.session_state.pdf_ready = True
                            st.session_state.pdf_html = b64_html
                            st.session_state.pdf_filename = f"Surat_PJB_{valid_cari_tiket[:10]}.html"
                            
                        data_pjb = [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), tgl_pjb.strftime("%d/%m/%Y"), d["NOP"], d["Cluster"], d["Nama"], d["Role"], d["Site"], d["Keperluan"], d["BBM"], d["Desc"], str(km_akhir), nominal_pjb, d["Plat"], url_isi, url_notabbm, url_km, url_mat, url_notamat, url_inap, url_kerja, tot_nilai_nota, valid_cari_tiket, tot_liter, harga_satuan, str(round(total_km_tempuh, 2)), "", "", upload_foto(f_transfer), url_um1, url_um2, url_um3, url_um4, tgl_berangkat_str, lama_hari_str, nom_um_harian_str, pdf_link_cloud, specific_pm_tickets]
                        
                        data_pjb_padded = (data_pjb + [""] * 37)[:37]
                        sukses_pjb = append_data(SHEET_PJB, data_pjb_padded, target_ss)
                        
                        if sukses_pjb: 
                            append_data(SHEET_APP, [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), d["Nama"], valid_cari_tiket, "Verifikasi PJB", nominal_pjb, "PENDING", "-"], target_ss)
                            st.balloons()
                            st.success(f"🎉 PJB Berhasil Dikirim untuk Verifikasi Admin!")
                            st.session_state.pjb_data = None
                            if "Operational" in jns_pjb:
                                time.sleep(2.5)
                                st.session_state.page = "🏠 Hub Menu Utama"
                                st.rerun()
                        else: st.error("🚨 Gagal mengirim ke Google Sheet.")

        if st.session_state.get("pdf_ready"):
            st.markdown(f"""
                <div style="background-color: #ecfdf5; padding: 25px; border-radius: 12px; text-align: center; margin-top: 25px; border: 2px dashed #10B981;">
                    <h3 style="color: #065f46; margin-top: 0;">📄 Surat Tugas & PJB (Auto PDF) Siap!</h3>
                    <a href="data:text/html;base64,{st.session_state.pdf_html}" download="{st.session_state.pdf_filename}" target="_blank"
                       style="display: inline-block; background-color: #10B981; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 1.1em; margin: 15px 0;">
                       📥 Download & Print Dokumen Resmi (Format A4 + Maps)
                    </a>
                </div>
            """, unsafe_allow_html=True)
            if st.button("⬅️ Selesai & Kembali ke Menu Utama", use_container_width=True):
                st.session_state.pdf_ready = False
                st.session_state.page = "🏠 Hub Menu Utama"
                st.rerun()


# ==========================================
# PAGE 3: APPROVAL CENTER (KHUSUS ADMIN)
# ==========================================
elif st.session_state.page == "🛡️ Approval Center":
    st.markdown("<div class='header-card'><h2>🛡️ APPROVAL CENTER</h2><p>Pusat Verifikasi PJB, Izin Revisi, & Harga BBM Anomali</p></div>", unsafe_allow_html=True)
    
    nop_admin = st.selectbox("📂 Wilayah (NOP):", ["-- Pilih NOP --"] + list(MASTER_DATA.keys()))
    if nop_admin != "-- Pilih NOP --":
        target_ss = MASTER_DATA[nop_admin]["spreadsheet_id"]
        data_all = fetch_spreadsheet_data(target_ss)
        app_r, pjb_r = data_all[SHEET_APP], data_all[SHEET_PJB]
        
        pending_anomali, pending_pjb = [], []
        if len(app_r) > 0:
            for idx, r in enumerate(app_r):
                if len(r) > 5 and str(r[5]).strip() == "PENDING":
                    item = {
                        "Row Index": idx, "Waktu": str(r[0]), "Nama": str(r[1]), "Request Ref / Tiket": str(r[2]), 
                        "Jenis Pengajuan": str(r[3]), "Nominal": f"Rp {clean_nominal(r[4]):,.0f}", 
                        "Status": str(r[5]).strip(), "Keterangan": str(r[6]) if len(r) > 6 else "-"
                    }
                    if r[3] == "Verifikasi PJB": pending_pjb.append(item)
                    else: pending_anomali.append(item)
        
        tab_app1, tab_app2 = st.tabs(["📸 Verifikasi Foto PJB", "⛽ Approval Revisi & Limit/Harga BBM"])
        with tab_app1:
            st.markdown("### 🔍 Daftar Tunggu Verifikasi PJB")
            if pending_pjb:
                st.dataframe(pd.DataFrame(pending_pjb).drop(columns=["Row Index"]), hide_index=True, use_container_width=True)
                target_tiket_pjb = st.selectbox("Pilih Request/Sub-Tiket PJB untuk divalidasi:", [p["Request Ref / Tiket"] for p in pending_pjb], key="sel_pjb")
                
                pjb_target = None
                for r in reversed(pjb_r[1:]):
                    if len(r) > 21 and str(r[21]).strip().upper() == target_tiket_pjb.strip().upper(): pjb_target = r; break
                        
                if pjb_target:
                    cf1, cf2, cf3 = st.columns(3)
                    with cf1:
                        if len(pjb_target) > 13 and pjb_target[13]: st.image(pjb_target[13], caption="Evidance Pengisian", use_container_width=True)
                    with cf2:
                        if len(pjb_target) > 15 and pjb_target[15]: st.image(pjb_target[15], caption="Nota KM/RH", use_container_width=True)
                    with cf3:
                        if len(pjb_target) > 19 and pjb_target[19]: st.image(pjb_target[19], caption="Evidance Pekerjaan", use_container_width=True)
                
                ca1, ca2 = st.columns(2)
                with ca1: action_pjb = st.radio("Keputusan Admin:", ["Setujui PJB (APPROVE)", "Tolak PJB (REJECT)"], key="rad_pjb")
                with ca2: remark_pjb = st.text_input("Catatan / Remark:", key="rem_pjb")
                
                if st.button("Proses Verifikasi PJB", type="primary"):
                    target_indices = [p["Row Index"] for p in pending_pjb if p["Request Ref / Tiket"] == target_tiket_pjb]
                    new_status = "APPROVED" if "APPROVE" in action_pjb else "REJECTED"
                    with st.spinner("Memperbarui database..."):
                        for idx in target_indices:
                            update_approval_status(target_ss, idx, new_status, remark_pjb if remark_pjb else "-")
                        st.success(f"✅ Tiket {target_tiket_pjb} berhasil di-{new_status}!")
                        time.sleep(2); st.rerun()
            else: st.success("✅ Tidak ada PJB yang menunggu verifikasi.")
                
        with tab_app2:
            st.markdown("### 🚨 Daftar Tunggu Izin Revisi & Limit/Harga BBM")
            if pending_anomali:
                st.dataframe(pd.DataFrame(pending_anomali).drop(columns=["Row Index"]), hide_index=True, use_container_width=True)
                ce1, ce2 = st.columns(2)
                with ce1: target_tiket_anm = st.selectbox("Pilih Tiket:", [p["Request Ref / Tiket"] for p in pending_anomali], key="sel_anm")
                with ce2: action_anm = st.radio("Keputusan Admin:", ["Setujui (APPROVE)", "Tolak (REJECT)"], key="rad_anm")
                
                if st.button("Proses Keputusan", type="primary"):
                    target_indices = [p["Row Index"] for p in pending_anomali if p["Request Ref / Tiket"] == target_tiket_anm]
                    new_status = "APPROVED" if "APPROVE" in action_anm else "REJECTED"
                    with st.spinner("Memperbarui database..."):
                        for idx in target_indices:
                            update_approval_status(target_ss, idx, new_status, "-")
                        st.success(f"✅ Berhasil di-{new_status}!")
                        time.sleep(2); st.rerun()
            else: st.success("✅ Tidak ada request revisi atau anomali yang menggantung.")


# ==========================================
# PAGE 4: MANAJEMEN KAS & DISTRIBUSI DANA
# ==========================================
elif st.session_state.page == "🏦 Manajemen Kas & Distribusi":
    st.markdown("<div class='header-card'><h2>🏦 MANAJEMEN KAS & DISTRIBUSI TIM</h2><p>Sistem Pencatatan Uang Masuk & Rekap Distribusi ke Petugas Lapangan</p></div>", unsafe_allow_html=True)
    
    nop_admin = st.selectbox("📂 Wilayah (NOP):", ["-- Pilih NOP --"] + list(MASTER_DATA.keys()))
    if nop_admin != "-- Pilih NOP --":
        target_ss = MASTER_DATA[nop_admin]["spreadsheet_id"]
        data_all = fetch_spreadsheet_data(target_ss)
        um_r = data_all.get(SHEET_UM, [])
        dist_r = data_all.get(SHEET_DISTRIBUSI, [])
        rekap_r = data_all.get("Rekap PJB", [])
        
        tab_in, tab_out, tab_report, tab_pjb = st.tabs(["📥 1. Dana Masuk", "📤 2. Distribusi Tim", "📊 3. Buku Besar", "📋 4. List PJB"])
        
        with tab_in:
            with st.form("form_tambah_um"):
                c_u1, c_u2, c_u3 = st.columns([1, 2, 1])
                with c_u1: tgl_um = st.date_input("Tanggal Turun")
                with c_u2: um_nobis = st.text_input("Nama Batch / Sumber Dana")
                with c_u3: um_nominal = st.number_input("Nominal (Rp)", min_value=0, step=100000)
                
                if st.form_submit_button("💾 Rekam Kas Masuk"):
                    if um_nominal > 0 and um_nobis.strip():
                        append_data(SHEET_UM, [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), tgl_um.strftime("%d/%m/%Y"), um_nobis.strip(), um_nominal], target_ss)
                        st.success("✅ Berhasil direkam!"); time.sleep(1.5); st.rerun()
            
            if len(um_r) > 1:
                padded_um = [(r + [""] * 4)[:4] for r in um_r[1:]]
                df_um_view = pd.DataFrame(padded_um, columns=["Waktu", "Tanggal", "Nama Batch Dana", "Nominal"])
                df_um_view["Nominal"] = df_um_view["Nominal"].apply(lambda x: f"Rp {clean_nominal(x):,.0f}")
                st.dataframe(df_um_view, hide_index=True, use_container_width=True)

        with tab_out:
            valid_batches = sorted(list(set([r[2].strip() for r in um_r[1:] if len(r) > 2 and r[2].strip() != ""])))
            if valid_batches:
                with st.form("form_distribusi"):
                    c_d1, c_d2 = st.columns(2)
                    with c_d1:
                        tgl_dist = st.date_input("Tanggal Transfer")
                        sumber_dana = st.selectbox("Sumber Dana", valid_batches)
                        nama_tim = st.selectbox("Penerima", ["-- Pilih --"] + MASTER_DATA[nop_admin]["names"])
                    with c_d2:
                        nom_dist = st.number_input("Nominal (Rp)", min_value=0, step=50000)
                        bukti_tf = st.file_uploader("Bukti Transfer", type=['jpg','png','jpeg'])
                        
                    if st.form_submit_button("🚀 Kirim"):
                        if nama_tim != "-- Pilih --" and nom_dist > 0 and bukti_tf is not None:
                            url_bukti = upload_foto(bukti_tf)
                            append_data(SHEET_DISTRIBUSI, [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), tgl_dist.strftime("%d/%m/%Y"), sumber_dana, nama_tim, nom_dist, url_bukti], target_ss)
                            st.success("✅ Dicatat!"); time.sleep(2); st.rerun()
            
            if len(dist_r) > 1:
                padded_dist = [(r + [""] * 6)[:6] for r in reversed(dist_r[1:])]
                df_dist_view = pd.DataFrame(padded_dist, columns=["Timestamp", "Tgl Transfer", "Sumber Dana", "Nama Penerima", "Nominal", "Link Bukti"])
                df_dist_view["Nominal"] = df_dist_view["Nominal"].apply(lambda x: f"Rp {clean_nominal(x):,.0f}")
                st.dataframe(df_dist_view.drop(columns=["Timestamp", "Link Bukti"]), hide_index=True, use_container_width=True)

        with tab_report:
            in_data = {}
            for r in um_r[1:]:
                if len(r) > 3 and r[2].strip() != "":
                    batch = r[2].strip()
                    in_data[batch] = in_data.get(batch, 0) + clean_nominal(r[3])
            
            out_data = {}
            for r in dist_r[1:]:
                if len(r) > 4 and r[2].strip() != "":
                    batch = r[2].strip()
                    out_data[batch] = out_data.get(batch, 0) + clean_nominal(r[4])
            
            report_list = []
            total_in_global = 0
            total_out_global = 0
            
            for batch in sorted(in_data.keys()):
                tot_in = in_data[batch]
                tot_out = out_data.get(batch, 0)
                saldo_sisa = tot_in - tot_out
                total_in_global += tot_in
                total_out_global += tot_out
                report_list.append({
                    "Nama Batch / Sumber Dana": batch,
                    "Total Dana Turun": tot_in,
                    "Total Distribusi ke Tim": tot_out,
                    "Sisa Saldo Tersedia": saldo_sisa
                })
            
            if report_list:
                m1, m2, m3 = st.columns(3)
                m1.markdown(f"<div class='metric-3d'><div class='metric-title'>Grand Total Kas Masuk</div><div class='metric-value'>Rp {total_in_global:,.0f}</div></div>", unsafe_allow_html=True)
                m2.markdown(f"<div class='metric-3d'><div class='metric-title'>Grand Total Distribusi</div><div class='metric-value'>Rp {total_out_global:,.0f}</div></div>", unsafe_allow_html=True)
                m3.markdown(f"<div class='metric-3d'><div class='metric-title'>Sisa Kas Keseluruhan</div><div class='metric-value'>Rp {(total_in_global - total_out_global):,.0f}</div></div>", unsafe_allow_html=True)
                
                df_report = pd.DataFrame(report_list)
                df_view_report = df_report.copy()
                df_view_report["Total Dana Turun"] = df_view_report["Total Dana Turun"].apply(lambda x: f"Rp {x:,.0f}")
                df_view_report["Total Distribusi ke Tim"] = df_view_report["Total Distribusi ke Tim"].apply(lambda x: f"Rp {x:,.0f}")
                df_view_report["Sisa Saldo Tersedia"] = df_view_report["Sisa Saldo Tersedia"].apply(lambda x: f"Rp {x:,.0f}")
                st.dataframe(df_view_report, hide_index=True, use_container_width=True)

        with tab_pjb:
            if len(rekap_r) > 1:
                list_col_a = sorted(list(set([r[0].strip() for r in rekap_r[1:] if len(r) > 0 and r[0].strip() != ""])))
                list_col_q = sorted(list(set([r[16].strip() for r in rekap_r[1:] if len(r) > 16 and r[16].strip() != ""])))
                
                c_f1, c_f2 = st.columns(2)
                with c_f1: filter_col_a = st.selectbox("📅 Filter Kolom A (Periode/Waktu):", ["-- Semua Periode --"] + list_col_a)
                with c_f2: filter_col_q = st.selectbox("💰 Filter Kolom Q (Nama Dana Ops):", ["-- Semua Dana Ops --"] + list_col_q)
                
                filtered_pjb = []
                total_nominal_pjb = 0
                
                for r in rekap_r[1:]:
                    val_a = r[0].strip() if len(r) > 0 else ""
                    val_q = r[16].strip() if len(r) > 16 else ""
                    pass_a = (filter_col_a == "-- Semua Periode --") or (val_a == filter_col_a)
                    pass_q = (filter_col_q == "-- Semua Dana Ops --") or (val_q == filter_col_q)
                    
                    if pass_a and pass_q:
                        nom = clean_nominal(r[15]) if len(r) > 15 else 0
                        total_nominal_pjb += nom
                        filtered_pjb.append({
                            "Kolom A (Periode)": val_a, "Tanggal": r[1] if len(r) > 1 else "-",
                            "Nama Tim": r[4] if len(r) > 4 else "-", "Role": r[6] if len(r) > 6 else "-",
                            "Keperluan": r[8] if len(r) > 8 else "-", "No Tiket / Deskripsi": r[9] if len(r) > 9 else "-",
                            "Kolom Q (Dana Ops)": val_q, "Nominal PJB": nom
                        })
                        
                st.markdown(f"<div class='metric-3d'><div class='metric-title'>Total Nominal PJB (Filtered)</div><div class='metric-value'>Rp {total_nominal_pjb:,.0f}</div></div>", unsafe_allow_html=True)
                if filtered_pjb:
                    df_pjb_ops = pd.DataFrame(filtered_pjb)
                    df_pjb_ops["Nominal PJB"] = df_pjb_ops["Nominal PJB"].apply(lambda x: f"Rp {x:,.0f}")
                    st.dataframe(df_pjb_ops, hide_index=True, use_container_width=True)


# ==========================================
# PAGE 5: LIVE MONITORING
# ==========================================
elif st.session_state.page == "📈 Live Monitoring":
    st.markdown("<div class='header-card'><h2>📈 LIVE MONITORING DASHBOARD</h2><p>Analisa Kas, Daily Pengeluaran, Tracker Satelit, & Analisa Performa Mobil (NOPOL)</p></div>", unsafe_allow_html=True)
    
    nop_live = st.selectbox("🌐 Pilih Market (NOP):", ["-- Pilih NOP --"] + list(MASTER_DATA.keys()))
    if nop_live != "-- Pilih NOP --":
        data_all = fetch_spreadsheet_data(MASTER_DATA[nop_live]["spreadsheet_id"])
        um_r, rekap_r, pjb_r, req_r, app_r = data_all[SHEET_UM], data_all["Rekap PJB"], data_all[SHEET_PJB], data_all[SHEET_REQUEST], data_all[SHEET_APP]
        
        t1, t2, t3, t4 = st.tabs(["💰 1. Sisa Kas", "🚨 2. Anomali", "🕵️ 3. Evaluasi Satelit", "🚗 4. Performa Mobil (NOPOL)"])
        
        with t1:
            total_um = sum([clean_nominal(r[3]) for r in um_r[1:] if len(r)>3]) if len(um_r)>1 else 0
            tot_serap = sum([clean_nominal(r[15]) for r in rekap_r[1:] if len(r)>15]) if len(rekap_r)>1 else 0
            sisa_kas = total_um - tot_serap
            m1, m2, m3 = st.columns(3)
            m1.markdown(f"<div class='metric-3d'><div class='metric-title'>Total Kas Masuk</div><div class='metric-value'>Rp {total_um:,.0f}</div></div>", unsafe_allow_html=True)
            m2.markdown(f"<div class='metric-3d'><div class='metric-title'>Total Penyerapan</div><div class='metric-value'>Rp {tot_serap:,.0f}</div></div>", unsafe_allow_html=True)
            m3.markdown(f"<div class='metric-3d'><div class='metric-title'>Sisa Kas</div><div class='metric-value'>Rp {sisa_kas:,.0f}</div></div>", unsafe_allow_html=True)
            
            if len(pjb_r) > 1:
                df_pjb_all = pd.DataFrame([(r + [""] * 37)[:37] for r in pjb_r[1:]], columns=["Waktu","Tanggal","N","C","Nama","R","S","Keperluan","BBM","D","KMAkhir","Nominal","Pl","u1","u2","u3","u4","u5","u6","u7","NN","NoTiket","Lt","Hs","TKM_RH","u8","u9","BuktiTF","UM1","UM2","UM3","UM4", "TglB", "LmHr", "NomH", "PDFLink", "PMMulti"])
                df_pjb_all['Nominal_Clean'] = df_pjb_all['Nominal'].apply(clean_nominal)
                df_pjb_all['Tanggal_PJB'] = pd.to_datetime(df_pjb_all['Tanggal'], format='%d/%m/%Y', errors='coerce')
                df_daily = df_pjb_all.dropna(subset=['Tanggal_PJB']).groupby('Tanggal_PJB')['Nominal_Clean'].sum().reset_index().sort_values('Tanggal_PJB')
                
                if not df_daily.empty:
                    df_daily.columns = ['Tanggal PJB', 'Total Pengeluaran (Rp)_num']
                    st.area_chart(df_daily.set_index('Tanggal PJB')['Total Pengeluaran (Rp)_num'], use_container_width=True)
        
        with t2:
            warning_list = []
            for pjb in pjb_r[1:]:
                if len(pjb) > 24:
                    no_tiket = pjb[21]
                    req_match = next((x for x in req_r[1:] if len(x) > 13 and x[3] == no_tiket), None)
                    if req_match:
                        nama_petugas, kategori_bbm = req_match[5], req_match[10]
                        km_awal, km_akhir = float(clean_indicator(req_match[12])), float(clean_indicator(pjb[10]))
                        total_km = km_akhir - km_awal
                        nominal_pjb_val = clean_nominal(pjb[11]) if len(pjb)>11 else clean_nominal(req_match[9])
                        
                        try: liter_val = float(str(pjb[22]).replace(',', '.'))
                        except: liter_val = 0.0
                        
                        is_mobil, is_motor, is_genset = "mobil" in str(kategori_bbm).lower(), "motor" in str(kategori_bbm).lower(), "genset" in str(kategori_bbm).lower()
                        is_boros, ket_status = False, "Normal"
                        if liter_val > 0:
                            ratio = total_km / liter_val
                            if is_mobil and ratio < 7: is_boros, ket_status = True, f"🔴 Mobil Boros ({ratio:.1f} KM/L < 7)"
                            elif is_motor and ratio < 15: is_boros, ket_status = True, f"🔴 Motor Boros ({ratio:.1f} KM/L < 15)"
                        
                        harga_satuan_val = clean_nominal(pjb[23]) if len(pjb)>23 else 0
                        if is_genset and ("dexlite" in str(kategori_bbm).lower() or "bio solar" in str(kategori_bbm).lower()) and harga_satuan_val > 28000:
                            is_boros, ket_status = True, f"🚨 Anomali Harga Genset (Rp {harga_satuan_val:,})"
                            
                        if is_boros: warning_list.append({"Nama Tim": nama_petugas, "Tiket Spesifik": no_tiket, "Nominal PJB": f"Rp {nominal_pjb_val:,.0f}", "Kategori": kategori_bbm, "Total Jarak/RH": f"{total_km:.2f}", "Liter": liter_val, "Status Warning": ket_status})
                        
            if warning_list: st.dataframe(pd.DataFrame(warning_list), hide_index=True, use_container_width=True)
            else: st.success("✨ Sempurna! Tidak ada anomali atau pemborosan pada tim wilayah ini.")

        with t3:
            eval_list = []
            for pjb in pjb_r[1:]:
                if len(pjb) > 24:
                    no_tiket = str(pjb[21]).strip().upper()
                    req_match = next((x for x in req_r[1:] if len(x) > 13 and str(x[3]).strip().upper() == no_tiket), None)
                    if req_match:
                        kategori, jarak_satelit = req_match[10], req_match[13]
                        angka_satelit = 0
                        try:
                            match = re.search(r"([\d\.]+)", str(jarak_satelit))
                            if match: angka_satelit = float(match.group(1))
                        except: pass

                        km_awal, km_akhir = float(clean_indicator(req_match[12])), float(clean_indicator(pjb[10]))
                        total_input_tim = km_akhir - km_awal
                        nominal_pjb_val = clean_nominal(pjb[11]) if len(pjb)>11 else clean_nominal(req_match[9])
                        
                        is_genset, is_mobil, is_motor = "genset" in str(kategori).lower(), "mobil" in str(kategori).lower(), "motor" in str(kategori).lower()
                        liter_val = 0.0
                        if len(pjb) > 22:
                            try: liter_val = float(str(pjb[22]).replace(',', '.'))
                            except: pass
                            
                        status_bbm, analisa_bbm, status_jarak = "-", "-", "🟢 Aman"
                        if liter_val > 0:
                            val_per_liter = total_input_tim / liter_val
                            analisa_bbm = f"{val_per_liter:.1f} {'KM/L' if not is_genset else 'RH/L'}"
                            if is_mobil: status_bbm = "🔴 Boros (< 7 KM/L)" if val_per_liter < 7 else "🟢 Normal"
                            elif is_motor: status_bbm = "🔴 Boros (< 15 KM/L)" if val_per_liter < 15 else "🟢 Normal"
                            else: status_bbm = "⚪ N/A"

                        if is_mobil or is_motor:
                            if angka_satelit > 0: status_jarak = "🟢 Aman & Wajar" if total_input_tim > angka_satelit else "🟢 Aman"
                            else: status_jarak = "⚪ Data Satelit Kosong"
                        else: status_jarak = "⏱️ (RH Genset / Item Lain)"

                        eval_list.append({"Nama Tim": req_match[5], "Tiket Spesifik": no_tiket, "Nominal PJB": f"Rp {nominal_pjb_val:,.0f}", "Kategori": kategori, "KM/RH Awal": km_awal, "KM/RH Akhir": km_akhir, "Total Jarak": f"{total_input_tim:.2f}", "Jarak Satelit": f"{angka_satelit}" if (is_mobil or is_motor) and angka_satelit > 0 else "-", "Status Jarak": status_jarak, "Rasio Aktual": analisa_bbm, "Status Konsumsi": status_bbm})
            
            if eval_list:
                def highlight_markup(s): return ['background-color: #FEE2E2; color: #DC2626; font-weight: bold' if '🔴' in str(v) else '' for v in s]
                st.dataframe(pd.DataFrame(eval_list).style.apply(highlight_markup, subset=['Status Jarak', 'Status Konsumsi']), hide_index=True, use_container_width=True)

        with t4:
            st.markdown("### 🚙 Analisa Performa & Efisiensi Mobil (Berdasarkan NOPOL)")
            st.info("💡 **ANALISA KENDARAAN (FIXED):** Tabel ini menghitung jarak tempuh **TOTAL (Akumulasi)** dari selisih `KM Akhir - KM Awal` untuk setiap perjalanan yang dilakukan mobil bersangkutan. Menjadikan rasio Konsumsi Mesin (KM/L) sangat valid.")
            
            car_stats = {}
            for pjb in pjb_r[1:]:
                if len(pjb) > 24:
                    kategori = str(pjb[8]).lower()
                    plat = str(pjb[12]).strip().upper()
                    no_tiket = str(pjb[21]).strip().upper()
                    if "mobil" in kategori and plat and plat not in ["", "0", "NONE", "NAN"]:
                        if plat not in car_stats:
                            car_stats[plat] = {"Total Jarak Trip (KM)": 0.0, "Total Liter": 0.0, "Total Dana (Rp)": 0}
                        
                        km_awal = 0.0
                        req_match = next((x for x in req_r[1:] if len(x) > 13 and str(x[3]).strip().upper() == no_tiket), None)
                        if req_match: km_awal = float(clean_indicator(req_match[12]))
                        
                        km_akhir = float(clean_indicator(pjb[10]))
                        jarak_trip = km_akhir - km_awal if km_akhir > km_awal else 0.0
                        
                        try: liter = float(str(pjb[22]).replace(',', '.'))
                        except: liter = 0.0
                        try: nominal = clean_nominal(pjb[11])
                        except: nominal = 0
                        
                        car_stats[plat]["Total Jarak Trip (KM)"] += jarak_trip
                        car_stats[plat]["Total Liter"] += liter
                        car_stats[plat]["Total Dana (Rp)"] += nominal
            
            car_list = []
            for plat, data in car_stats.items():
                eff = data["Total Jarak Trip (KM)"] / data["Total Liter"] if data["Total Liter"] > 0 else 0.0
                car_list.append({
                    "NOPOL Kendaraan": plat,
                    "Total Akumulasi Jarak (KM)": round(data["Total Jarak Trip (KM)"], 2),
                    "Total Pengisian BBM (Liter)": round(data["Total Liter"], 2),
                    "Total Dana Dikeluarkan": f"Rp {data['Total Dana (Rp)']:,.0f}",
                    "Konstanta Mesin / Efisiensi": f"{eff:.2f} KM / Liter"
                })
                
            if car_list:
                df_cars = pd.DataFrame(car_list).sort_values("Total Akumulasi Jarak (KM)", ascending=False)
                st.dataframe(df_cars, hide_index=True, use_container_width=True)
            else:
                st.info("Belum ada data PJB Mobil ber-NOPOL yang tercatat di database untuk dianalisa.")


# ==========================================
# PAGE 6: REPORT & AUTO PJB
# ==========================================
elif st.session_state.page == "🖨️ Auto PJB Report":
    st.markdown("<div class='header-card'><h2>🖨️ REPORT & EXPORT CENTER</h2><p>Generator Laporan PDF Otomatis & Analisa Tabel Tiket Menyeluruh</p></div>", unsafe_allow_html=True)
    
    nop_report = st.selectbox("📂 Pilih Wilayah Database (NOP):", ["-- Pilih NOP --"] + list(MASTER_DATA.keys()))
    if nop_report != "-- Pilih NOP --":
        with st.spinner("Membaca seluruh database laporan..."):
            target_ss = MASTER_DATA[nop_report]["spreadsheet_id"]
            data_all = fetch_spreadsheet_data(target_ss)
            req_r = data_all.get(SHEET_REQUEST, [])
            pjb_r = data_all.get(SHEET_PJB, [])
            rekap_r = data_all.get("Rekap PJB", [])
            _, _, _, _, nik_dict = load_excel_data()
        
        tab_report1, tab_report2, tab_report3 = st.tabs(["📑 1. Auto PJB Biasa (List Foto)", "📊 2. Rekap Request vs PJB", "🖨️ 3. Cetak Surat Tugas & UM"])
        
        with tab_report1:
            if len(rekap_r) > 1 and len(pjb_r) > 1:
                dict_photos = defaultdict(list)
                for r in pjb_r[1:]:
                    if len(r) > 21:
                        tk = str(r[21]).strip().upper()
                        if tk:
                            photo_data = {
                                "N (Evidance Pengisian)": r[13] if len(r)>13 else "",
                                "O (Kwitansi Support / Non-BBM)": r[14] if len(r)>14 else "",
                                "P (Foto Nota Disanding KM/RH)": r[15] if len(r)>15 else "",
                                "R (Foto Nota Material Disanding)": r[17] if len(r)>17 else "",
                                "T (Evidance Pekerjaan)": r[19] if len(r)>19 else "",
                                "U (Foto Aktivitas UM 1)": r[28] if len(r)>28 else "",
                                "V (Foto Aktivitas UM 2)": r[29] if len(r)>29 else "",
                                "W (Foto Aktivitas UM 3)": r[30] if len(r)>30 else "",
                                "X (Foto Aktivitas UM 4)": r[31] if len(r)>31 else "",
                                "Y (Link PDF Akomodasi)": r[35] if len(r)>35 else ""
                            }
                            dict_photos[tk].append(photo_data)
                
                list_periode = sorted(list(set([r[16].strip() for r in rekap_r[1:] if len(r) > 16 and r[16].strip() != ""])))
                list_role = sorted(list(set([r[6].strip() for r in rekap_r[1:] if len(r) > 6 and r[6].strip() != ""])))
                
                st.markdown("<div class='section-title'>🔍 Parameter Filter Laporan</div>", unsafe_allow_html=True)
                col_f1, col_f2 = st.columns(2)
                with col_f1: filter_periode = st.selectbox("📅 Periode Dana Ops (Dari Kolom Q Rekap):", ["Semua Periode"] + list_periode)
                with col_f2: filter_role = st.multiselect("💼 Role Pekerjaan (Pilih Banyak):", list_role, default=list_role)

                st.markdown("<div class='section-title'>📸 Pilih Lampiran Foto (Multi-Select)</div>", unsafe_allow_html=True)
                pilihan_foto = st.multiselect(
                    "Pilih kolom foto yang ingin ditarik dari Form PJB:",
                    [
                        "N (Evidance Pengisian)", "O (Kwitansi Support / Non-BBM)", "P (Foto Nota Disanding KM/RH)", 
                        "R (Foto Nota Material Disanding)", "T (Evidance Pekerjaan)", "U (Foto Aktivitas UM 1)", 
                        "V (Foto Aktivitas UM 2)", "W (Foto Aktivitas UM 3)", "X (Foto Aktivitas UM 4)", "Y (Link PDF Akomodasi)"
                    ],
                    default=[
                        "N (Evidance Pengisian)", "O (Kwitansi Support / Non-BBM)", "P (Foto Nota Disanding KM/RH)",
                        "R (Foto Nota Material Disanding)", "T (Evidance Pekerjaan)", "Y (Link PDF Akomodasi)"
                    ]
                )
                
                if st.button("🚀 Generate Laporan Lumpsum", type="primary", use_container_width=True):
                    html_content = ""
                    count_match = 0
                    ticket_counts = defaultdict(int)
                    
                    for idx, row in enumerate(rekap_r[1:]):
                        row_periode = row[16].strip() if len(row) > 16 else ""
                        row_role = row[6].strip() if len(row) > 6 else ""
                        pass_periode = (filter_periode == "Semua Periode") or (row_periode == filter_periode)
                        pass_role = (len(filter_role) == 0) or (row_role in filter_role)
                        
                        if pass_periode and pass_role:
                            found_tiket = None
                            for cell in row:
                                if str(cell).strip().upper() in dict_photos:
                                    found_tiket = str(cell).strip().upper()
                                    break
                            
                            if found_tiket:
                                count_match += 1
                                idx_for_tk = ticket_counts[found_tiket]
                                if idx_for_tk < len(dict_photos[found_tiket]): current_photo_data = dict_photos[found_tiket][idx_for_tk]
                                else: current_photo_data = dict_photos[found_tiket][-1]
                                ticket_counts[found_tiket] += 1
                                
                                html_content += f"""
                                <div class='ticket-card'>
                                    <div class='ticket-header'>🎫 SUB-TIKET: {found_tiket}</div>
                                    <table>
                                        <tr><td width='15%'><b>Tanggal</b></td><td width='35%'>: {row[0] if len(row)>0 else '-'}</td><td width='15%'><b>Periode</b></td><td>: {row_periode}</td></tr>
                                        <tr><td><b>Nama</b></td><td>: {row[4] if len(row)>4 else '-'}</td><td><b>Nominal</b></td><td>: <span style='color:green; font-weight:bold;'>Rp {row[15] if len(row)>15 else '0'}</span></td></tr>
                                        <tr><td><b>Role/Jabatan</b></td><td>: {row_role}</td><td><b>Keperluan</b></td><td>: {row[8] if len(row)>8 else '-'}</td></tr>
                                        <tr><td valign='top'><b>Deskripsi</b></td><td colspan='3'>: {row[9] if len(row)>9 else '-'}</td></tr>
                                    </table>
                                    <div class='photo-container'>
                                """
                                if pilihan_foto:
                                    for p_name in pilihan_foto:
                                        url_foto = current_photo_data.get(p_name, "")
                                        if p_name == "Y (Link PDF Akomodasi)":
                                            if url_foto and url_foto.startswith("http"):
                                                html_content += f"<div class='photo-box' style='padding:20px;'><br><a href='{url_foto}' target='_blank' style='background:#0ea5e9; color:white; padding:8px 15px; text-decoration:none; border-radius:5px;'>📥 Download PDF Surat Tugas</a><br><br></div>"
                                        else:
                                            if url_foto and url_foto.startswith("http"): html_content += f"<div class='photo-box'><img src='{url_foto}'><br>{p_name}</div>"
                                            else: html_content += f"<div class='photo-box'><br><br>🚫 Tidak Ada<br>{p_name}</div>"
                                html_content += "</div></div>"
                    
                    if count_match > 0:
                        full_html = f"""
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <meta charset="UTF-8">
                            <title>Laporan Auto PJB - {nop_report}</title>
                            <style>
                                @page {{ size: A4 portrait; margin: 15mm; }}
                                body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #333; margin: 0; padding: 0; background: #fff; }}
                                h1 {{ text-align: center; color: #0F2027; border-bottom: 2px solid #00F2FE; padding-bottom: 10px; margin-top: 10px; }}
                                .ticket-card {{ width: 100%; border: 2px solid #000; padding: 15mm; box-sizing: border-box; margin-bottom: 20px; border-radius: 8px; page-break-inside: avoid; }}
                                .ticket-header {{ background-color: #f1f5f9; padding: 10px; font-weight: bold; font-size: 1.2em; border-bottom: 2px solid #0ea5e9; margin-bottom: 15px; }}
                                table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 1em; }}
                                td {{ padding: 8px; border-bottom: 1px solid #e2e8f0; }}
                                .photo-container {{ display: flex; flex-wrap: wrap; gap: 2%; justify-content: flex-start; }}
                                .photo-box {{ width: 49%; text-align: center; font-size: 0.9em; font-weight: bold; border: 1px solid #ccc; margin-bottom: 15px; padding: 10px; box-sizing: border-box; background: #fafafa;}}
                                .photo-box img {{ width: 100%; height: auto; max-height: 400px; object-fit: contain; border-radius: 4px; margin-bottom: 10px; display:block; margin-left:auto; margin-right:auto; }}
                                @media print {{ body {{ padding: 0; }} .ticket-card {{ margin-bottom: 20mm; box-shadow: none; }} }}
                            </style>
                        </head>
                        <body>
                            <h1>Laporan Lumpsum & PJB - {nop_report}</h1>
                            <p style="text-align:center; color:#64748b; font-size:0.9em; margin-bottom:30px;">Filter Periode: {filter_periode} | Total: {count_match} Sub-Tiket</p>
                            {html_content}
                        </body>
                        </html>
                        """
                        
                        st.success(f"✅ Berhasil merangkum **{count_match}** sub-tiket (Mengakomodir duplikat tiket di baris berbeda secara urut).")
                        b64_html = base64.b64encode(full_html.encode("utf-8")).decode()
                        st.markdown(f"""
                            <a href="data:text/html;base64,{b64_html}" download="Laporan_PJB_{nop_report}.html" 
                            style="display: block; text-align: center; background-color: #0ea5e9; color: white; padding: 15px 20px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 1.1em;">
                            📥 Download Laporan (Buka file lalu CTRL+P dan Save as PDF)
                            </a>
                        """, unsafe_allow_html=True)
                        st.markdown("<hr>", unsafe_allow_html=True)
                        st.components.v1.html(full_html, height=800, scrolling=True)
                    else: st.warning("⚠️ Tidak ada data yang cocok dengan filter yang dipilih.")
            else: st.info("⚠️ Data Sheet 'Rekap PJB' atau 'Form PJB' belum tersedia/masih kosong.")
        
        with tab_report2:
            st.markdown("### 📊 Status Tracking All Data (Request Dana vs Penyelesaian PJB)")
            if len(req_r) > 1:
                pjb_map = {}
                for r in reversed(pjb_r[1:]):  
                    if len(r) > 21 and str(r[21]).strip() != "":
                        tk = str(r[21]).strip().upper()
                        if tk not in pjb_map: pjb_map[tk] = {"Tgl PJB": r[1] if len(r)>1 else "", "Nominal PJB": 0, "Specific PM": ""}
                        pjb_map[tk]["Nominal PJB"] += clean_nominal(r[11]) if len(r)>11 else 0
                        if len(r)>36 and r[36].strip(): pjb_map[tk]["Specific PM"] += f", {r[36].strip()}" if pjb_map[tk]["Specific PM"] else r[36].strip()
                
                rekap_all = []
                for r in req_r[1:]:
                    if len(r) > 5 and str(r[3]).strip() != "":
                        tk = str(r[3]).strip().upper()
                        nom_req = clean_nominal(r[9]) if len(r)>9 else 0
                        has_pjb = tk in pjb_map
                        nom_pjb = pjb_map[tk]["Nominal PJB"] if has_pjb else 0
                        selisih = nom_req - nom_pjb
                        
                        status_lap = "✅ Selesai PJB" if has_pjb else "⏳ Menunggu PJB"
                        if has_pjb and selisih > 0 and "PM" in (r[8] if len(r)>8 else ""):
                            status_lap = "🔄 PJB Sebagian / Sisa"
                            
                        rekap_all.append({
                            "Sub-Tiket Split": tk, "Tgl Request": r[1] if len(r)>1 else "",
                            "Nama": r[5] if len(r)>5 else "", "Kategori Item": r[10] if len(r)>10 else "",
                            "Keperluan": r[8] if len(r)>8 else "", "Nominal Request": nom_req,
                            "Status Laporan": status_lap, "Tgl PJB": pjb_map[tk]["Tgl PJB"] if has_pjb else "-",
                            "Tiket PM Spesifik Ter-PJB": pjb_map[tk]["Specific PM"] if has_pjb else "-",
                            "Nominal PJB Total": nom_pjb, "Sisa / Selisih Dana": selisih
                        })
                
                if rekap_all:
                    df_rekap_all = pd.DataFrame(rekap_all)
                    df_view = df_rekap_all.copy()
                    df_view['Nominal Request'] = df_view['Nominal Request'].apply(lambda x: f"Rp {x:,.0f}")
                    df_view['Nominal PJB Total'] = df_view['Nominal PJB Total'].apply(lambda x: f"Rp {x:,.0f}" if x > 0 else "-")
                    df_view['Sisa / Selisih Dana'] = df_view['Sisa / Selisih Dana'].apply(lambda x: f"Rp {x:,.0f}")
                    
                    def highlight_status(val):
                        if '✅' in str(val): color = '#10B981'
                        elif '🔄' in str(val): color = '#3B82F6'
                        else: color = '#F59E0B'
                        return f'color: {color}; font-weight: bold;'
                        
                    st.dataframe(df_view.style.map(highlight_status, subset=['Status Laporan']), hide_index=True, use_container_width=True)
                    csv_rekap = df_rekap_all.to_csv(index=False).encode('utf-8')
                    st.download_button(label="📥 Export Tabel Rekap ke CSV/Excel", data=csv_rekap, file_name=f"Rekap_All_Data_{nop_report}.csv", mime='text/csv', use_container_width=True)
                else: st.info("Tidak ada data Request Dana.")
            else: st.info("⚠️ Data Sheet 'Request Dana' masih kosong.")

        with tab_report3:
            st.markdown("<div class='section-title'>🖨️ Cetak Ulang Dokumen Surat Tugas & Uang Makan</div>", unsafe_allow_html=True)
            st.info("Fitur khusus untuk Admin menarik dan mencetak ulang dokumen resmi PDF Surat Tugas & Uang Makan (3 Halaman) yang disubmit oleh Tim secara Real-time.")
            
            tiket_um_list = []
            pjb_um_dict = {}
            for r in reversed(pjb_r[1:]):
                if len(r) > 31 and str(r[21]).strip() != "":
                    tk = str(r[21]).strip().upper()
                    if str(r[28]).startswith("http"):
                        tiket_um_list.append(tk)
                        pjb_um_dict[tk] = r
            
            tiket_um_list = sorted(list(set(tiket_um_list)))
            
            if not tiket_um_list:
                st.warning("Belum ada request PJB kategori Biaya Akomodasi / Uang Makan di database NOP ini.")
            else:
                c_p1, c_p2 = st.columns([3, 1])
                with c_p1:
                    pilih_tk_cetak = st.selectbox("🎫 Pilih Nomor Sub-Tiket PJB (Akomodasi):", ["-- Pilih Tiket --"] + tiket_um_list)
                
                if pilih_tk_cetak != "-- Pilih Tiket --":
                    req_match = next((x for x in reversed(req_r[1:]) if len(x) > 3 and str(x[3]).strip().upper() == pilih_tk_cetak), None)
                    pjb_match = pjb_um_dict[pilih_tk_cetak]
                    
                    if req_match:
                        nama_petugas_cetak = str(req_match[5]).strip()
                        role_cetak = str(req_match[6]).strip()
                        site_cetak = str(req_match[7]).strip()
                        kep_cetak = str(req_match[8]).strip()
                        desc_cetak = str(req_match[11]).strip() if len(req_match) > 11 else "-"
                        jarak_cetak = str(req_match[13]).strip() if len(req_match) > 13 else "-"
                        
                        lat1_cetak = str(req_match[14]).strip() if len(req_match) > 14 else "0"
                        lon1_cetak = str(req_match[15]).strip() if len(req_match) > 15 else "0"
                        lat2_cetak = str(req_match[22]).strip() if len(req_match) > 22 else "0"
                        lon2_cetak = str(req_match[23]).strip() if len(req_match) > 23 else "0"
                        
                        nik_cetak = nik_dict.get(nama_petugas_cetak.upper(), "-")
                        
                        tgl_pjb_cetak = parse_date(pjb_match[1]) if len(pjb_match) > 1 else datetime.now().date()
                        nom_pjb_cetak = clean_nominal(pjb_match[11]) if len(pjb_match) > 11 else 0
                        
                        tgl_berangkat_cetak_str = pjb_match[32] if len(pjb_match) > 32 and pjb_match[32] else tgl_pjb_cetak.strftime("%d/%m/%Y")
                        
                        try: lama_hari_cetak = int(pjb_match[33]) if len(pjb_match) > 33 and pjb_match[33] else 1
                        except: lama_hari_cetak = 1
                            
                        try: nom_um_harian_cetak = int(pjb_match[34]) if len(pjb_match) > 34 and pjb_match[34] else nom_pjb_cetak
                        except: nom_um_harian_cetak = nom_pjb_cetak
                        
                        specific_pm_cetak = pjb_match[36] if len(pjb_match) > 36 and pjb_match[36].strip() else pilih_tk_cetak
                        
                        tgl_berangkat_cetak_date = parse_date(tgl_berangkat_cetak_str)
                        tgl_kembali_cetak_date = tgl_berangkat_cetak_date + timedelta(days=lama_hari_cetak)
                        
                        url_um1 = pjb_match[28] if len(pjb_match) > 28 else ""
                        url_um2 = pjb_match[29] if len(pjb_match) > 29 else ""
                        url_um3 = pjb_match[30] if len(pjb_match) > 30 else ""
                        url_um4 = pjb_match[31] if len(pjb_match) > 31 else ""
                        
                        with c_p2:
                            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                            if st.button("🖨️ Tarik & Generate PDF A4", type="primary", use_container_width=True):
                                bulan_romawi = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]
                                romawi = bulan_romawi[tgl_pjb_cetak.month] if 1 <= tgl_pjb_cetak.month <= 12 else "VIII"
                                logo_base64 = get_local_img_base64("koperasi-jasa-konstruksi-tower-event-organizer-network-monitoring-telekomunikasi-kisel-group-logo-kut.webp")
                                
                                html_admin_um = f"""
                                <!DOCTYPE html>
                                <html>
                                <head>
                                    <meta charset="UTF-8">
                                    <title>Surat Tugas & PJB - {pilih_tk_cetak}</title>
                                    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
                                    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
                                    <style>
                                        body {{ font-family: 'Times New Roman', Times, serif; font-size: 11pt; line-height: 1.5; margin: 0; background: #525659; }}
                                        @page {{ size: A4; margin: 0; }}
                                        .page {{ width: 210mm; min-height: 297mm; background: white; margin: 10mm auto; position: relative; padding: 15mm 20mm; box-sizing: border-box; box-shadow: 0 0 10px rgba(0,0,0,0.5); page-break-after: always; }}
                                        h3 {{ text-align: center; font-size: 14pt; margin-bottom: 15px; font-weight: bold; }}
                                        table {{ width: 100%; border-collapse: collapse; margin-bottom: 10px; font-size: 11pt; }}
                                        .tbl-info td {{ padding: 3px 5px; vertical-align: top; }}
                                        .tbl-data th, .tbl-data td {{ border: 1px solid black; padding: 6px; text-align: center; }}
                                        .tbl-uang td, .tbl-uang th {{ border: 1px solid black; padding: 6px; }}
                                        .signature {{ display: flex; justify-content: space-between; margin-top: 30px; text-align: center; }}
                                        .signature div {{ width: 45%; }}
                                        .photo-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 20px; }}
                                        .photo-item {{ text-align: center; border: 1px solid #ddd; padding: 10px; border-radius: 5px; }}
                                        .photo-item img {{ width: 100%; max-height: 250px; object-fit: contain; }}
                                        .logo-header {{ text-align: right; margin-bottom: 10px; padding-right: 5px; }}
                                        .logo-header img {{ width: 220px; height: auto; object-fit: contain; }}
                                        @media print {{ body {{ background: white; margin: 0; }} .page {{ margin: 0; box-shadow: none; width: 100%; height: 100%; padding: 15mm 20mm; page-break-after: always; }} }}
                                    </style>
                                </head>
                                <body>
                                    <!-- PAGE 1: SURAT TUGAS -->
                                    <div class="page">
                                        <div class="logo-header">
                                            <img src="{logo_base64}" alt="Logo KUT">
                                        </div>
                                        <div class="content">
                                            <h3 style="letter-spacing: 5px;"><u>SURAT TUGAS</u></h3>
                                            <p>Saya yang bertanda tangan di bawah ini:</p>
                                            <table class="tbl-info" style="width: 70%;">
                                                <tr><td width="150">Nama</td><td width="10">:</td><td>Okta Pradika</td></tr>
                                                <tr><td>NIK</td><td>:</td><td>B0924649</td></tr>
                                                <tr><td>Jabatan</td><td>:</td><td>Koordinator NOP Palangka Raya</td></tr>
                                            </table>
                                            <p>Dengan ini menugaskan sebagai berikut :</p>
                                            <table class="tbl-data">
                                                <tr><th>No.</th><th>Nama</th><th>NIK</th><th>Jabatan</th><th>Lokasi Kerja</th></tr>
                                                <tr><td>1</td><td>{nama_petugas_cetak}</td><td>{nik_cetak}</td><td>{role_cetak}</td><td>{site_cetak}</td></tr>
                                            </table>
                                            <table class="tbl-info">
                                                <tr><td width="150">No Ticket</td><td width="10">:</td><td>{specific_pm_cetak}</td></tr>
                                                <tr><td>Tujuan</td><td>:</td><td>{site_cetak}</td></tr>
                                                <tr><td>Estimasi Jarak (Peta)</td><td>:</td><td><b>{jarak_cetak}</b> (Titik HB ke Site)</td></tr>
                                                <tr><td>Lama tugas dinas</td><td>:</td><td>{lama_hari_cetak} Hari</td></tr>
                                                <tr><td>Tgl. Berangkat</td><td>:</td><td>{tgl_berangkat_cetak_date.strftime("%d/%m/%Y")}</td></tr>
                                                <tr><td>Tgl. Kembali</td><td>:</td><td>{tgl_kembali_cetak_date.strftime("%d/%m/%Y")}</td></tr>
                                                <tr><td>Keperluan</td><td>:</td><td>{kep_cetak}</td></tr>
                                            </table>
                                            <p>Demikianlah Surat Penugasan ini dibuat agar dapat dilaksanakan dengan sebaik-baiknya dan melaporkan hasilnya setelah selesai pelaksanaan tugas.</p>
                                            <div style="text-align: right; margin-top: 30px; margin-bottom: 30px;">Palangka Raya, {tgl_pjb_cetak.strftime("%d/%m/%Y")}</div>
                                            <div class="signature">
                                                <div><p>Koordinator NOP Palangka Raya,</p><br><br><br><p><b><u>Okta Pradika</u></b><br>NIK. B0924649</p></div>
                                                <div><p>POH. SPV Operation,</p><br><br><br><p><b><u>Rian Sharon</u></b><br>NIK. 79058</p></div>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <!-- PAGE 2: PENGAJUAN UANG MAKAN & PETA -->
                                    <div class="page">
                                        <div class="logo-header">
                                            <img src="{logo_base64}" alt="Logo KUT">
                                        </div>
                                        <div class="content">
                                            <h3><u>SURAT PENGAJUAN UANG MAKAN</u></h3>
                                            <div style="text-align: center; margin-top: -15px; margin-bottom: 20px;">
                                                Nomor : &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; /KUT/{romawi}/{tgl_pjb_cetak.year}
                                            </div>
                                            <p>Koordinator ENOM NOP Palangka Raya PT. Kinarya Utama Teknik, dengan ini menugaskan kepada :</p>
                                            <table class="tbl-info" style="width: 70%;">
                                                <tr><td width="150">Nama</td><td width="10">:</td><td>{nama_petugas_cetak}</td></tr>
                                                <tr><td>NIK</td><td>:</td><td>{nik_cetak}</td></tr>
                                                <tr><td>Jabatan</td><td>:</td><td>{role_cetak}</td></tr>
                                            </table>
                                            <br>
                                            <table class="tbl-data">
                                                <tr><th>No.</th><th>Tujuan Tugas</th><th>Berangkat</th><th>Kembali</th><th>Uraian Penugasan</th></tr>
                                                <tr><td>1</td><td>{site_cetak}</td><td>{tgl_berangkat_cetak_date.strftime("%d/%m/%Y")}</td><td>{tgl_kembali_cetak_date.strftime("%d/%m/%Y")}</td><td>{desc_cetak}</td></tr>
                                            </table>
                                            
                                            <div style="margin-top: 15px; page-break-inside: avoid;">
                                                <b>Peta Satelit Rute Perjalanan:</b>
                                                <div id="map" style="height: 250px; width: 100%; border: 1px solid #475569; border-radius: 8px; margin-top: 5px;"></div>
                                            </div>
                                            
                                            <table class="tbl-uang" style="margin-top:15px;">
                                                <tr style="background: #f0f0f0;"><th colspan="3">Bantuan Perjalanan Dinas</th><th colspan="2">Perhitungan</th><th>Jumlah</th></tr>
                                                <tr><td colspan="3">Uang Makan ({nama_petugas_cetak})</td><td align="center">{lama_hari_cetak} Hari x Rp. {nom_um_harian_cetak:,.0f}</td><td width="30" style="border-right: none;">Rp.</td><td align="right" style="border-left: none;">{nom_pjb_cetak:,.0f}</td></tr>
                                                <tr><td colspan="3">Bantuan Penginapan</td><td align="center">0 Malam x Rp. 0</td><td width="30" style="border-right: none;">Rp.</td><td align="right" style="border-left: none;">0</td></tr>
                                                <tr><th colspan="5" align="right">Jumlah Total</th><th align="right">Rp. {nom_pjb_cetak:,.0f}</th></tr>
                                            </table>
                                            <table class="tbl-info" style="width: 300px; float: right; margin-top: 20px;">
                                                <tr><td width="120">Dikeluarkan di</td><td>: Palangka Raya</td></tr>
                                                <tr><td>Pada Tanggal</td><td>: {tgl_pjb_cetak.strftime("%d/%m/%Y")}</td></tr>
                                            </table>
                                            <div style="clear: both;"></div>
                                            <div class="signature">
                                                <div><p>Koordinator NOP Palangka Raya,</p><br><br><br><p><b><u>Okta Pradika</u></b><br>NIK. B0924649</p></div>
                                                <div><p>POH. SPV Operation,</p><br><br><br><p><b><u>Rian Sharon</u></b><br>NIK. 79058</p></div>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <!-- PAGE 3: LAMPIRAN FOTO EVIDEN -->
                                    <div class="page">
                                        <div class="logo-header">
                                            <img src="{logo_base64}" alt="Logo KUT">
                                        </div>
                                        <div class="content">
                                            <h3><u>LAMPIRAN FOTO AKTIVITAS LAPANGAN</u></h3>
                                            <div class="photo-grid">
                                                <div class="photo-item"><img src="{url_um1}"><br><b>Foto Aktivitas 1</b></div>
                                                <div class="photo-item"><img src="{url_um2}"><br><b>Foto Aktivitas 2</b></div>
                                                <div class="photo-item"><img src="{url_um3}"><br><b>Foto Aktivitas 3</b></div>
                                                <div class="photo-item"><img src="{url_um4}"><br><b>Foto Aktivitas 4</b></div>
                                            </div>
                                        </div>
                                    </div>
                                    <script> 
                                        window.onload = function() {{
                                            var lat1 = parseFloat("{lat1_cetak}");
                                            var lon1 = parseFloat("{lon1_cetak}");
                                            var lat2 = parseFloat("{lat2_cetak}");
                                            var lon2 = parseFloat("{lon2_cetak}");
                                            
                                            if (lat1 !== 0 && lat2 !== 0 && !isNaN(lat1) && !isNaN(lat2)) {{
                                                var map = L.map('map');
                                                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                                                    attribution: '© OpenStreetMap'
                                                }}).addTo(map);
                                                
                                                var latlngs = [ [lat1, lon1], [lat2, lon2] ];
                                                var polyline = L.polyline(latlngs, {{color: 'red', weight: 4}}).addTo(map);
                                                
                                                L.marker([lat1, lon1]).addTo(map).bindPopup("Berangkat");
                                                L.marker([lat2, lon2]).addTo(map).bindPopup("Tujuan");
                                                
                                                map.fitBounds(polyline.getBounds(), {{padding: [30,30]}});
                                                
                                                setTimeout(function(){{ window.print(); }}, 1500);
                                            }} else {{
                                                document.getElementById('map').innerHTML = "<div style='text-align:center; padding-top:100px; color:#94a3b8;'>Peta Koordinat Tidak Tersedia</div>";
                                                setTimeout(function(){{ window.print(); }}, 500);
                                            }}
                                        }};
                                    </script>
                                </body>
                                </html>
                                """
                                b64_html_admin = base64.b64encode(html_admin_um.encode("utf-8")).decode()
                                
                                st.markdown(f"""
                                    <div style="background-color: #ecfdf5; padding: 25px; border-radius: 12px; text-align: center; margin-top: 25px; border: 2px dashed #10B981;">
                                        <h3 style="color: #065f46; margin-top: 0;">📄 Laporan PDF Siap Diunduh!</h3>
                                        <a href="data:text/html;base64,{b64_html_admin}" download="Admin_Surat_Tugas_{pilih_tk_cetak[:10]}.html" target="_blank"
                                           style="display: inline-block; background-color: #10B981; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 1.1em; margin: 15px 0;">
                                           📥 Download PDF Surat Tugas
                                        </a>
                                        <p style="font-size: 0.85em; color: #64748b; margin-bottom: 0;">Buka file yang didownload dan Save as PDF / Print.</p>
                                    </div>
                                """, unsafe_allow_html=True)


# ==========================================
# PAGE 7: MONITORING REQUEST & PJB
# ==========================================
elif st.session_state.page == "👀 Request & PJB Monitoring":
    st.markdown("<div class='header-card'><h2>📋 REQ & PJB MONITORING</h2><p>Pantau Aktivitas Tim Daily, Warning Tiket Gantung & Cek Sisa Dana</p></div>", unsafe_allow_html=True)
    
    nop_mon = st.selectbox("🌐 Pilih Wilayah Database (NOP):", ["-- Pilih NOP --"] + list(MASTER_DATA.keys()))
    if nop_mon != "-- Pilih NOP --":
        target_ss = MASTER_DATA[nop_mon]["spreadsheet_id"]  # <-- Variabel ini yang sebelumnya terlewat
        with st.spinner("Menarik data langsung dari server..."):
            data_all = fetch_spreadsheet_data(target_ss)
            req_r, pjb_r, app_r = data_all[SHEET_REQUEST], data_all[SHEET_PJB], data_all[SHEET_APP]
        
        tab_daily, tab_warning = st.tabs(["📅 1. Daily Realtime (Hari Ini)", "⚠️ 2. Warning List (Gantung & Sisa Dana)"])
        
        with tab_daily:
            st.info("💡 **INFO:** Tab ini menampilkan siapa saja yang hari ini meminta dana, dan siapa saja yang menyetor PJB (beserta nilai dan jaraknya).")
            col_d1, col_d2 = st.columns([1, 3])
            with col_d1: filter_date = st.date_input("Pilih Tanggal Pantau", datetime.now().date())
            
            filter_date_str = filter_date.strftime("%d/%m/%Y")
            
            # --- DAILY REQUEST ---
            st.markdown(f"#### 💸 Request Dana Masuk ({filter_date_str})")
            daily_req = []
            tot_req_daily = 0
            for r in req_r[1:]:
                if len(r) > 13 and str(r[1]).strip() == filter_date_str:
                    nom = clean_nominal(r[9])
                    tot_req_daily += nom
                    daily_req.append({
                        "Waktu": r[0], "Nama": r[5], "Sub-Tiket (Split)": r[3], "Role": r[6],
                        "Keperluan": r[8], "Kategori Item": r[10], 
                        "Jarak/Info": r[13], "Nominal Request": nom
                    })
            
            if daily_req:
                df_dreq = pd.DataFrame(daily_req)
                df_dreq["Nominal Request"] = df_dreq["Nominal Request"].apply(lambda x: f"Rp {x:,.0f}")
                st.dataframe(df_dreq, hide_index=True, use_container_width=True)
                st.markdown(f"<div style='text-align:right; font-size:1.2em; color:#0ea5e9; font-weight:bold;'>Total Request: Rp {tot_req_daily:,.0f}</div>", unsafe_allow_html=True)
                
                st.markdown("##### 🚀 Approval & Pencairan Cepat (Distribusi Tim)")
                um_r_dist = data_all.get(SHEET_UM, [])
                valid_batches = sorted(list(set([r[2].strip() for r in um_r_dist[1:] if len(r) > 2 and r[2].strip() != ""])))
                
                cd1, cd2, cd3 = st.columns(3)
                with cd1:
                    tiket_to_app = st.selectbox("Pilih Tiket (Support):", ["-- Pilih Tiket --"] + [req['Sub-Tiket (Split)'] for req in daily_req])
                
                # Logic Auto-Fill Nominal berdasarkan pilihan dropdown
                auto_nom = 0
                if tiket_to_app != "-- Pilih Tiket --":
                    auto_nom = next((req['Nominal Request'] for req in daily_req if req['Sub-Tiket (Split)'] == tiket_to_app), 0)
                    
                with cd2:
                    sumber_dana_app = st.selectbox("Sumber Dana (Budget)", ["-- Pilih Dana --"] + valid_batches)
                with cd3:
                    nom_dist_app = st.number_input("Nominal Transfer (Rp) [Auto]", min_value=0, step=1000, value=int(auto_nom))
                
                c_act1, c_act2 = st.columns(2)
                with c_act1:
                    btn_approve = st.button("✅ Approve & Support (Catat ke Distribusi)", type="primary", use_container_width=True)
                with c_act2:
                    btn_reject = st.button("❌ Reject Request", use_container_width=True)
                
                if btn_approve:
                    if tiket_to_app != "-- Pilih Tiket --" and sumber_dana_app != "-- Pilih Dana --" and nom_dist_app > 0:
                        nama_penerima = next((r['Nama'] for r in daily_req if r['Sub-Tiket (Split)'] == tiket_to_app), "")
                        
                        # Data otomatis masuk ke Sheet Distribusi UM
                        append_data(SHEET_DISTRIBUSI, [
                            datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                            datetime.now().strftime("%d/%m/%Y"),
                            sumber_dana_app,
                            nama_penerima,
                            nom_dist_app,
                            f"AUTO-SUPPORT: {tiket_to_app}" 
                        ], target_ss)
                        
                        # Data masuk ke Sheet APP sebagai histori approve
                        append_data(SHEET_APP, [
                            datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                            nama_penerima,
                            tiket_to_app,
                            "Request Dana",
                            nom_dist_app,
                            "APPROVED",
                            "Telah didistribusikan"
                        ], target_ss)
                        
                        st.success(f"✅ Berhasil! Dana untuk {tiket_to_app} sebesar Rp {nom_dist_app:,.0f} telah disetujui dan dicatat di Distribusi Tim.")
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("Pilih Tiket, Sumber Dana, dan pastikan Nominal Transfer lebih dari 0!")
                        
                if btn_reject:
                    if tiket_to_app != "-- Pilih Tiket --":
                        nama_penerima = next((r['Nama'] for r in daily_req if r['Sub-Tiket (Split)'] == tiket_to_app), "")
                        
                        # Rekam status REJECTED di Sheet APP agar terbaca oleh sistem block/lepas
                        append_data(SHEET_APP, [
                            datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                            nama_penerima,
                            tiket_to_app,
                            "Request Dana",
                            nom_dist_app,
                            "REJECTED",
                            "Ditolak Admin (Data tidak sesuai)"
                        ], target_ss)
                        
                        st.success(f"❌ Request {tiket_to_app} berhasil di-REJECT. Sistem pemblokiran pada tim telah dilepas, mereka dapat mengajukan ulang.")
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("Silakan pilih tiket yang akan di-reject!")
            else: st.success("Belum ada request dana hari ini.")
            
            st.markdown("<hr>", unsafe_allow_html=True)
            
            # --- DAILY PJB ---
            st.markdown(f"#### ✅ PJB Disubmit ({filter_date_str})")
            daily_pjb = []
            tot_pjb_daily = 0
            for r in pjb_r[1:]:
                if len(r) > 24 and str(r[1]).strip() == filter_date_str:
                    nom = clean_nominal(r[11])
                    tot_pjb_daily += nom
                    tk_info = r[36] if len(r) > 36 and r[36].strip() else r[21]
                    daily_pjb.append({
                        "Waktu Submit": r[0], "Nama": r[4], "Sub-Tiket PJB": tk_info, "Role": r[5],
                        "Kategori Item": r[8], "Jarak Tempuh Trip": f"{r[24]} KM", "Nominal PJB": nom
                    })
            
            if daily_pjb:
                df_dpjb = pd.DataFrame(daily_pjb)
                df_dpjb["Nominal PJB"] = df_dpjb["Nominal PJB"].apply(lambda x: f"Rp {x:,.0f}")
                st.dataframe(df_dpjb, hide_index=True, use_container_width=True)
                st.markdown(f"<div style='text-align:right; font-size:1.2em; color:#10B981; font-weight:bold;'>Total PJB: Rp {tot_pjb_daily:,.0f}</div>", unsafe_allow_html=True)
            else: st.success("Belum ada PJB yang disubmit hari ini.")
            
        with tab_warning:
            st.markdown("### 🚨 Peringatan Otomatis (Data Mulai Agustus 2026 dst)")
            st.info("Sistem melacak siapa yang belum setor PJB lebih dari 3 hari, dan mencocokkan nilai **Sisa Dana (Request awal vs Laporan PJB)**.")
            
            pjb_dict = {}
            pjb_tickets_all_set = set()
            for r in pjb_r[1:]:
                if len(r) > 21 and str(r[21]).strip() != "":
                    tk = str(r[21]).strip().upper()
                    if tk not in pjb_dict: pjb_dict[tk] = 0
                    pjb_dict[tk] += clean_nominal(r[11]) if len(r)>11 else 0
                    
                    tk_str = r[36].strip() if (len(r) > 36 and r[36].strip()) else r[21].strip()
                    pjb_tickets_all_set.update([t.strip().upper() for t in tk_str.split(",")])
                    
            # Ambil data tiket yang sudah di reject Admin (Agar tidak muncul sebagai Warning Gantung)
            req_reject_set = set()
            for r in app_r[1:]:
                if len(r) > 5 and r[3] == "Request Dana" and str(r[5]).strip().upper() == "REJECTED":
                    req_reject_set.add(str(r[2]).strip().upper())
                    
            list_gantung = []
            list_sisa = []
            today_date = datetime.now().date()
            
            for r in req_r[1:]:
                if len(r) > 9:
                    tgl_req_str = str(r[1]).strip()
                    req_date = parse_date(tgl_req_str)
                    
                    if req_date >= CUTOFF_DATE:
                        req_tk_raw = str(r[3]).strip().upper()
                        
                        # Lewati tiket kosong atau yang statusnya sudah ditolak Admin di Daily Realtime
                        if not req_tk_raw or req_tk_raw in req_reject_set: continue
                        
                        req_tk_list = [t.strip() for t in req_tk_raw.split(",") if t.strip()]
                        req_set = set(req_tk_list)
                        
                        nama = str(r[5])
                        nom_req = clean_nominal(r[9])
                        
                        if not req_set.issubset(pjb_tickets_all_set):
                            aging = (today_date - req_date).days
                            if aging > 3:
                                list_gantung.append({
                                    "Tanggal Request": tgl_req_str,
                                    "Aging": f"{aging} Hari",
                                    "Nama Petugas": nama,
                                    "Sub-Tiket Gantung": req_tk_raw,
                                    "Nominal Request": nom_req
                                })
                        else:
                            nom_pjb = pjb_dict.get(req_tk_raw, 0)
                            sisa = nom_req - nom_pjb
                            if sisa > 0:
                                list_sisa.append({
                                    "Tanggal Request": tgl_req_str,
                                    "Nama Petugas": nama,
                                    "Sub-Tiket PJB": req_tk_raw,
                                    "Nominal Request": nom_req,
                                    "Nominal PJB Total": nom_pjb,
                                    "Sisa Dana (Tarik)": sisa
                                })
                                
            col_w1, col_w2 = st.columns(2)
            with col_w1:
                st.error(f"🔴 **PJB Gantung > 3 Hari ({len(list_gantung)} Tiket)**")
                if list_gantung:
                    df_gantung = pd.DataFrame(list_gantung)
                    df_gantung["Nominal Request"] = df_gantung["Nominal Request"].apply(lambda x: f"Rp {x:,.0f}")
                    st.dataframe(df_gantung, hide_index=True, use_container_width=True)
                else: st.success("Aman! Tidak ada tiket gantung >3 hari.")
                
            with col_w2:
                st.warning(f"⚠️ **Sisa Dana PJB ({len(list_sisa)} Tiket)**")
                if list_sisa:
                    df_sisa = pd.DataFrame(list_sisa)
                    df_sisa["Nominal Request"] = df_sisa["Nominal Request"].apply(lambda x: f"Rp {x:,.0f}")
                    df_sisa["Nominal PJB Total"] = df_sisa["Nominal PJB Total"].apply(lambda x: f"Rp {x:,.0f}")
                    df_sisa["Sisa Dana (Tarik)"] = df_sisa["Sisa Dana (Tarik)"].apply(lambda x: f"Rp {x:,.0f}")
                    st.dataframe(df_sisa, hide_index=True, use_container_width=True)
                else: st.success("Aman! Semua pengajuan PM/Reguler nominalnya sesuai (Tidak ada sisa dana di tim).")
