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
from PIL import Image, ExifTags
import io
import cv2
import numpy as np

# ==========================================
# 0. KONFIGURASI HALAMAN & UI 3D MODERN
# ==========================================
st.set_page_config(page_title="SiRAPI Enterprise", page_icon="💸", layout="wide", initial_sidebar_state="collapsed")

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
SHEET_ABSENSI = "Data Absensi"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

MASTER_DATA = {
    "Palangkaraya": {"spreadsheet_id": "1HvgVicTWwO4RMQI6ZR3Mu3IgGicwjcLZl9mDN1auvJU", "clusters": ["Palangkaraya", "Barito Raya"], "names": ["OKTA PRADIKA", "MUHAMAD KIKI FIRMANSYAH", "MAWARDAH", "JUMADI", "REYNALDI RICARDO PUTRA", "JAMES JIMBRIS TAMAILANG", "MUHAMMAD MUKHLIS", "ADI BOWO SANTOSO", "YAHYA MUHAMAD", "FAHMI", "OKY BANGKIT PAMUNGKAS", "MUHAMMAD MUKTI", "LEONARD HARA", "MELKY OKTAVIA TULANGOW", "AHMAD SETIAWAN", "SARUL SAPUTRA", "AHMAD", "MUHAMAD RAYHAN", "AULIA RAHMAN", "ARMADI", "INDRA", "DARLI SUTANTO", "RIKI HIDAYAT", "PUJIANTO", "MUNAWIR AHMAD", "MURJANI", "NURHAYAT", "PRADILA KANDI", "PUTRA WARDANA", "RIKO SETIADI", "SAILILLAH", "SARWONO", "TAKLIM", "TIVIANSYAH", "TRISNO SUSANTO", "M KIKI FIRMANSYAH", "HD", "IRJAN TORO", "AHMAD MUZAKIR", "ALFI SYAHRI", "DIDI RIYADI", "FRANS EJHA ADITYA", "GYLLBRHED ALFARY LOLOMSAIT", "HARUN NURASYID", "HORY YUSMANTO", "KHILAL DAWAI KATIRI", "M. RIFANI"]},
    "Pangkalanbun": {"spreadsheet_id": "1bc0lDhR5iMtXZsKiKIdEwPY8JTaASeHFtaJSeXkywE4", "clusters": ["Ketapang", "Sampit", "Pangkalanbun"], "names": ["RIRIH HARIANTO", "MUKHAMAD ABDUL KHOLIP", "YAMA DEWANTA", "BAGUS SANTOSO", "IMRON SETIAWAN", "JOENDRIS HERDIAN KARA", "STEVEN HERDIAN KARA", "YUDIONO", "DADANG WAHYU SYAHPUTRA", "CAVIN ANDREAN EKA PUTRA", "RAHMAT RIYAN WAHYUDIN", "SUWITO", "DIDIK PRIYONO", "GUNTUR WAHYU PRADANA", "UTI MUHAMMAD KHAIRUL HUDA", "IDRUS MAULANA", "M. RIZKY", "TRIYONO", "ERIK SETIAWAN", "AGUS SUGANDA", "AJI SAPUTRA", "DIAN WAHYUDI", "HAFID BUDIANTO", "IWAN ZAINAL ABIDIN", "DANDI PUTRA", "PONIRAN", "PARYADI KUSUMA", "HERWANI", "DIAN WILDANI", "IPAN HARIONO", "FIRDAUS", "RONI YUDI ISYANTO", "AYU NUR ISLAMIAH", "ARDIANSYAH.", "DAYU SHANDY", "WAHYUDI", "TAJAM SAPUTRA", "MUJHAHID ALWI", "NANDA FIRMANSYAH", "WAHYU RAHMADANI", "TEGUH WICAKSONO", "FERI HARIADI", "NASUKI", "ANDARIANTO PUJI SURO", "BONDAN PRAMUDYA ANANTATUR", "SOLEKHAN", "RIZAL IHZAMAHENDRA", "MUHAMMAD ROIS FERDIANSYAH", "WIDI ARYANTO", "FHANNY AGUSTIAWAN"]},
    "Tarakan": {"spreadsheet_id": "1lRj1YdZGQwY5vHg8P4wudK9V1O_lJuEYjdyHkXoB-Wg", "clusters": ["Tarakan Inner", "Tarakan Outer"], "names": ["HENDRA WIRTASI SIMANULLANG", "ARIZONA ROSADI", "KUKUH BHASKARA", "NATAL SIMBOLON", "HERMAWAN", "IRVAN DINATA VANDITYAWAN", "ENDRAS SAPTA", "AHMADI", "EDI PANJI ERMAYANA", "HANS RISKY RONI TUAH GIRSANG", "IRMANSYAH B. SANGAJI", "REMO REMOLDUS MANALU", "MOHAMMAD RAFAI", "FIRMAN SYAHRUL", "AZMIR", "PETRUS RESI KELORE", "ANIR REZKY", "AHDAN", "PARJON SIMANULLANG", "RUSDI", "HASRIADI", "PURO SUGONDO", "ALIMUDIN M. SAER", "KORNELIUS USI KELORE", "RUSDIANSYAH", "JONTES YUSDA SIMANULLANG", "NANI SETIANINGSIH", "UNGGUL NUGRAHA", "YOGABITA INDOTENO", "JHON KENNEDI SIMANULLANG", "RAFI MUHAMAD SYARIF", "AGRIVA", "SEPTIAN ALVITO", "M. DEDI RIZALDI", "SAHARUDDIN.", "MUHAMMAD RASYID", "SUPRIADI", "JULIMAT SIHITE", "EFNI NURYADIN", "ERWIN SAPUTRA ARIANSYAH", "ALVEUS", "SUPRIADI BANDANGAN"]},
    "Pontianak": {"spreadsheet_id": "1VmoWPImNFMjnaIQpBXEVYdMiTEzsz3P4tpmzfA0EMDE", "clusters": ["Sintang", "Singkawang", "Pontianak"], "names": ["ALOYSIUS", "RUDI", "RONIYANTO", "SUKADI", "HAIRIL", "AZMI ASHADIQI", "SUYADI", "ARIEF DARUL IKHWAN", "MUHAMMAD AL FATAH", "YUDIANSYAH", "RAHMAD INDRA IRAWAN", "MATIUS MARTIN", "RYVAEEL DEWANGGA", "AMIRDA ANGGA SAPUTRA", "IZHARUDDIN", "VINSENSIUS YOGI", "GUSTI ARIZAL", "MUHAMMAD MIFTAHUDIN, A.MD", "BAYU ANGGARA PUTRA", "YONI IRAWAN", "SUGANDI", "IRVAN ANDRIYANA", "ALDIANSYAH", "ABANG HAMDANI", "ABANG KUSDIANSYAH", "SUMAN", "SANGGARA ISMARAWARI", "IBIN", "VALENTINUS PETRO", "DWI KURNIAWAN ISMANTO", "ARISAFRIADI", "DONATUS DONI", "NUR AHMAD KARDIYANTO", "AGRI PERDANA", "AKHSANUL FIKI", "ALI ALAMSYAH", "MUHAMMAD FIRZHA GIANNI HARSYA", "RICKY ARDILAY", "FAISAL", "WIJI SANTOSO", "HISYAM MUTHOYIB", "ARIF RAHMAN NUGROHO", "TOTOK SUGIARTO", "PURWANDI SETIAWAN", "JULIANTO BHAKTI PUTRO, SH", "ILHAMMUDIN", "AGUNG", "ROSIDI", "ABRAR ELZAH FATHALIF", "HENDRI YULIANSYAH", "JAMIL", "GORO SUKARTONO", "OKTAPIANUS JUMIN", "ONNIE SYAEFUDDIN", "BUDI", "ULUL AMRY", "RUHIAT, A.MD", "SUPIANDI", "WAHYUDI", "SUHENDRIK", "M. ARKAM", "SYAFRI APRIJAL", "ARIANTO SUMANTRI", "TUTU AGE ANDIKA", "VIRANDA SAPTA, A.MD", "TOTO HERMANSYAH", "KURNIAWAN", "ROBI ISKANDAR MASDIANSYAH", "MUTIIN CHANDRA", "MISJANI", "KHAIRUL FARISD", "ANDRA", "DODI RATMAYANTO", "WAWAN DARYANA", "MISWARDI", "JUPRILIAUS PICO", "DEDY PURNOMO", "EDI KURNIAWAN", "DEDE GUNAWAN", "WANDALA JAGOARDI PANDALO", "KARIYADI", "REZQI AL BARQAH", "FIRMANSYAH, SP"]}
}
LIST_KEPERLUAN = ["", "Tshoot", "Backup", "Support", "PM", "Program BCP", "Program Quikwin", "Program G348T", "Pengiriman Material SPMS", "Pembelian Material","Transportasi Air"]

# ==========================================
# 2. FUNGSI INTI & CACHING
# ==========================================
def ai_image_checker(uploaded_file, file_name_label):
    if uploaded_file is None:
        return True, "Tidak ada file"
    try:
        img = Image.open(uploaded_file)
        exif = img.getexif()
        uploaded_file.seek(0)
        if exif:
            suspicious_software = ['photoshop', 'canva', 'picsart', 'lightroom', 'snapseed', 'gimp', 'coreldraw', 'illustrator', 'capcut', 'pics', 'edit']
            for tag_id, value in exif.items():
                tag = ExifTags.TAGS.get(tag_id, tag_id)
                if tag == 'Software':
                    val_lower = str(value).lower()
                    for sw in suspicious_software:
                        if sw in val_lower:
                            return False, f"🚨 FORENSIK DITOLAK: Gambar {file_name_label} terdeteksi sebagai hasil editan aplikasi ({value})."
    except Exception:
        uploaded_file.seek(0)
        pass

    try:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        img_cv = cv2.imdecode(file_bytes, 1)
        uploaded_file.seek(0)
        if img_cv is not None:
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            if blur_score < 40.0:  
                return False, f"🌫️ KUALITAS DITOLAK: Gambar {file_name_label} SANGAT BLUR / BURAM (Skor: {blur_score:.1f})."
    except Exception:
        uploaded_file.seek(0)
        pass
    return True, "Aman"

def ui_image_uploader(label, key=None):
    file = st.file_uploader(label, type=["jpg", "png", "jpeg"], key=key)
    if file:
        with st.status("🤖 AI Memindai Kualitas & Metadata Gambar...", expanded=True) as status:
            is_valid, msg = ai_image_checker(file, label)
            if is_valid:
                status.update(label="✅ Lolos Uji AI: Gambar Asli & Jelas", state="complete")
            else:
                status.update(label="🚨 Peringatan AI: Gambar Bermasalah", state="error")
                st.error(msg)
    return file

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
    durasi_sec = (dist_km / 40.0) * 3600
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
    ws_names = [SHEET_REQUEST, SHEET_PJB, SHEET_UM, SHEET_DISTRIBUSI, SHEET_APP, "Rekap PJB", SHEET_TIKET_PM, SHEET_ABSENSI]
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
        col_nama = next((c for c in df_tim.columns if 'nama' in c.lower()), None)
        col_lat = next((c for c in df_tim.columns if 'lat' in c.lower()), None)
        col_lon = next((c for c in df_tim.columns if 'lon' in c.lower() or 'lng' in c.lower()), None)
        if col_nama and col_lat and col_lon:
            for _, row in df_tim.iterrows():
                nama_key = str(row[col_nama]).strip().upper()
                tim_dict[nama_key] = {'Latitude': row.get(col_lat, 0), 'Longtitude': row.get(col_lon, 0)}
    except Exception: pass
        
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
    if nama == "-- Pilih Nama --" or nama == "": return [], [], [], [], []
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

    outstanding_all, outstanding_lock, aging_tickets, history, actionable_pjb = [], [], [], [], []
    today = datetime.now().date()
    
    for req_tk_raw, tgl in req_tickets.items():
        req_tk_list = [t.strip() for t in req_tk_raw.split(",") if t.strip()]
        req_set = set(req_tk_list)
        
        if req_app_status.get(req_tk_raw) == "REJECTED":
            history.append({"Tiket": req_tk_raw, "Tanggal": tgl, "Status": "❌ REQUEST DITOLAK Admin"})
            continue
            
        if not req_set.issubset(pjb_tickets_all_set):
            outstanding_all.append(req_tk_raw)
            actionable_pjb.append(req_tk_raw) # Tiket ini siap untuk di-PJB-kan oleh user
            req_date = parse_date(tgl)
            if req_date >= CUTOFF_DATE: outstanding_lock.append(req_tk_raw)
            aging_days = (today - req_date).days
            
            if req_date >= CUTOFF_DATE and aging_days > 3:
                aging_tickets.append(req_tk_raw)
                history.append({"Tiket": req_tk_raw, "Tanggal": tgl, "Status": f"🚨 Telat {aging_days} Hari"})
            else: history.append({"Tiket": req_tk_raw, "Tanggal": tgl, "Status": "🔴 Menunggu PJB"})
        else:
            app_data = pjb_app_status.get(req_tk_raw, {"status": "APPROVED", "catatan": ""})
            if app_data["status"] == "PENDING":
                outstanding_all.append(req_tk_raw)
                outstanding_lock.append(req_tk_raw)
                history.append({"Tiket": req_tk_raw, "Tanggal": tgl, "Status": "⏳ PJB Menunggu Verifikasi Admin"})
            elif app_data["status"] == "REJECTED":
                outstanding_all.append(req_tk_raw)
                outstanding_lock.append(req_tk_raw)
                actionable_pjb.append(req_tk_raw) # Tiket ini ditolak admin, harus di-PJB-kan ulang
                history.append({"Tiket": req_tk_raw, "Tanggal": tgl, "Status": f"❌ PJB DITOLAK: {app_data['catatan']}"})
            else: history.append({"Tiket": req_tk_raw, "Tanggal": tgl, "Status": "🟢 PJB Selesai"})
            
    return outstanding_all, outstanding_lock, aging_tickets, sorted(history, key=lambda x: x["Status"], reverse=True), actionable_pjb

def upload_foto(file):
    if file is None: return ""
    try:
        encoded = base64.b64encode(file.getvalue()).decode('utf-8')
        return cloudinary.uploader.upload(f"data:{file.type};base64,{encoded}", resource_type="auto").get("secure_url") 
    except Exception: return ""

def upload_foto_compressed(file):
    if file is None: return ""
    try:
        img = Image.open(file)
        if img.mode != 'RGB': img = img.convert('RGB')
        img.thumbnail((1024, 1024))
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=60)
        img_byte_arr.seek(0)
        encoded = base64.b64encode(img_byte_arr.read()).decode('utf-8')
        return cloudinary.uploader.upload(f"data:image/jpeg;base64,{encoded}", resource_type="auto").get("secure_url") 
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
    except Exception: pass 

# ==========================================
# 0.5. SISTEM KEAMANAN & LOGIN KARYAWAN (AUTO NIK)
# ==========================================
@st.cache_data(ttl=60)
def load_user_credentials():
    try:
        df = pd.read_excel("pass and username.xlsx")
        df.columns = df.columns.astype(str).str.strip().str.upper() 
        creds = {}
        if 'NAMA' in df.columns and 'NIK' in df.columns:
            for _, row in df.iterrows():
                nama = str(row['NAMA']).strip().upper()
                nik = str(row['NIK']).replace('.0', '').strip() 
                if nama != 'NAN' and nik != 'NAN' and nama != '':
                    creds[nama] = nik
        else:
            st.error("⚠️ Kolom 'NAMA' dan 'NIK' tidak ditemukan di baris pertama Excel!")
        return creds
    except Exception as e:
        st.error(f"⚠️ Gagal membaca file Excel 'pass and username.xlsx'. Error: {e}")
        return {}

if 'is_authenticated' not in st.session_state: st.session_state.is_authenticated = False
if 'logged_in_user' not in st.session_state: st.session_state.logged_in_user = ""
if 'needs_routing' not in st.session_state: st.session_state.needs_routing = False
if 'has_absent' not in st.session_state: st.session_state.has_absent = False

if not st.session_state.is_authenticated:
    user_creds = load_user_credentials()
    list_users = ["-- Pilih Nama Anda --"] + sorted(list(user_creds.keys()))
    
    c_log1, c_log2, c_log3 = st.columns([1, 2, 1])
    with c_log2:
        st.markdown("<div style='margin-top: 80px;'></div>", unsafe_allow_html=True)
        try: st.image("koperasi-jasa-konstruksi-tower-event-organizer-network-monitoring-telekomunikasi-kisel-group-logo-kut.webp", use_container_width=True)
        except: pass
        
        st.markdown("""
            <div class="header-card" style="margin-bottom: 25px;">
                <h2>🔒 PORTAL LOGIN TIM</h2>
                <p>Silakan masuk menggunakan identitas Anda</p>
            </div>
        """, unsafe_allow_html=True)
        
        # PENGHAPUSAN st.form AGAR BISA AUTO-FILL DINAMIS SAAT DROP-DOWN DIPILIH
        selected_user = st.selectbox("👤 Nama Karyawan:", list_users)
        
        # Tarik NIK otomatis jika nama sudah dipilih
        auto_nik = user_creds.get(selected_user, "") if selected_user != "-- Pilih Nama Anda --" else ""
        
        # Input password kini menjadi disable (Terkunci) dan otomatis terisi dari variabel auto_nik
        st.text_input("🔑 Password (NIK):", value=auto_nik, type="password", disabled=True, help="Otomatis terisi setelah nama dipilih")
        
        submit_login = st.button("🚀 MASUK KE SISTEM", use_container_width=True, type="primary")
        
        if submit_login:
            if selected_user == "-- Pilih Nama Anda --":
                st.error("⚠️ Silakan pilih nama Anda terlebih dahulu!")
            else:
                st.session_state.is_authenticated = True
                st.session_state.logged_in_user = selected_user
                
                # Pengecualian Absensi & Routing Khusus Bos/Admin
                if selected_user in ["OKTA PRADIKA", "MAWARDAH"]:
                    st.session_state.has_absent = True
                    st.session_state.needs_routing = True
                else:
                    # 🔍 CEK DATABASE: Apakah user sudah absen HARI INI? (Jadi cukup 1x sehari)
                    sudah_absen_hari_ini = False
                    try:
                        found_nop_cek = ""
                        for nop_key, nop_data in MASTER_DATA.items():
                            if selected_user in nop_data["names"]:
                                found_nop_cek = nop_key
                                break
                        
                        if found_nop_cek:
                            data_cek = fetch_spreadsheet_data(MASTER_DATA[found_nop_cek]["spreadsheet_id"])
                            absen_r = data_cek.get(SHEET_ABSENSI, [])
                            today_str = datetime.now().strftime("%d/%m/%Y")
                            
                            for r in absen_r[1:]:
                                if len(r) > 1 and str(r[1]).strip().upper() == selected_user.strip().upper():
                                    tgl_absen = str(r[0]).split(" ")[0] # Potong jam-nya, ambil DD/MM/YYYY saja
                                    if tgl_absen == today_str:
                                        sudah_absen_hari_ini = True
                                        break
                    except Exception:
                        pass # Abaikan jika gagal ditarik, biarkan turun ke form absensi untuk jaga-jaga
                        
                    if sudah_absen_hari_ini:
                        st.session_state.has_absent = True
                        st.session_state.needs_routing = True # Lewati form absen, langsung routing ke tiket
                    else:
                        st.session_state.has_absent = False 
                        st.session_state.needs_routing = False # Tahap awal: Munculkan Form Absen
                        
                st.success(f"✅ Login Berhasil! Selamat datang, {selected_user}.")
                time.sleep(1)
                st.rerun()
    st.stop() 

# ==========================================
# 0.6. INTERCEPTOR: ABSENSI HARIAN WAJIB
# ==========================================
if st.session_state.is_authenticated and not st.session_state.has_absent:
    st.markdown("<div class='header-card'><h2>📸 ABSENSI HARIAN TIM</h2><p>Anda wajib melakukan absensi (Selfie & Lokasi) sebelum memulai aktivitas di sistem. (Cukup 1x Sehari)</p></div>", unsafe_allow_html=True)
    
    c_ab1, c_ab2, c_ab3 = st.columns([1, 2, 1])
    with c_ab2:
        with st.form("form_absen"):
            st.info(f"👤 **Identitas Absen:** {st.session_state.logged_in_user}")
            status_absen = st.selectbox("Status Kehadiran Hari Ini:", ["Hadir / Bekerja", "Izin", "Sakit", "Cuti"])
            lokasi_absen = st.text_input("Ketik Lokasi Bekerja Saat Ini (Contoh: Basecamp Palangkaraya)")
            foto_absen = st.file_uploader("Upload Foto Selfie Absen (WAJIB)", type=["jpg", "png", "jpeg"])
            
            submit_absen = st.form_submit_button("✅ Submit Absen & Masuk Ruang Kerja", use_container_width=True)
            
            if submit_absen:
                if not lokasi_absen or not foto_absen:
                    st.error("⚠️ Lokasi Pekerjaan dan Foto Selfie WAJIB diisi untuk verifikasi kehadiran!")
                else:
                    with st.spinner("Menyimpan data absensi ke server..."):
                        url_foto_absen = upload_foto_compressed(foto_absen)
                        
                        found_nop_absen = ""
                        for nop_key, nop_data in MASTER_DATA.items():
                            if st.session_state.logged_in_user in nop_data["names"]:
                                found_nop_absen = nop_key
                                break
                                
                        if found_nop_absen:
                            try:
                                target_ss = MASTER_DATA[found_nop_absen]["spreadsheet_id"]
                                append_data(SHEET_ABSENSI, [
                                    datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                                    st.session_state.logged_in_user,
                                    status_absen,
                                    lokasi_absen,
                                    url_foto_absen
                                ], target_ss)
                            except Exception as e:
                                st.warning(f"Catatan: Sheet 'Data Absensi' mungkin belum dibuat di database {found_nop_absen}. Absen tetap dilanjutkan secara lokal.")
                                
                        st.session_state.has_absent = True
                        st.session_state.needs_routing = True
                        st.success("✅ Absensi Berhasil Disimpan! Meneruskan ke sistem...")
                        time.sleep(1.5)
                        st.rerun()
    st.stop() # Hentikan eksekusi kode bawah, kunci akses sebelum absen selesai!

# ==========================================
# 0.7. SMART ROUTING ENGINE (AUTO-DIRECT PJB / REQ)
# ==========================================
if st.session_state.get('needs_routing'):
    with st.spinner("🔍 Menganalisa status tiket & mengatur rute otomatis..."):
        user_now = st.session_state.logged_in_user
        
        found_nop = ""
        for nop_key, nop_data in MASTER_DATA.items():
            if user_now in nop_data["names"]:
                found_nop = nop_key
                break
        st.session_state.auto_nop = found_nop
        
        if user_now in ["OKTA PRADIKA", "MAWARDAH"]:
            st.session_state.page = "🏠 Hub Menu Utama"
        else:
            if found_nop:
                try:
                    data_cek = fetch_spreadsheet_data(MASTER_DATA[found_nop]["spreadsheet_id"])
                    # act_pjb adalah tiket yang benar-benar siap/wajib di-PJB-kan (bukan yang sedang menunggu admin)
                    _, _, _, _, act_pjb = get_user_tickets_status(user_now, data_cek[SHEET_REQUEST], data_cek[SHEET_PJB], data_cek[SHEET_APP])
                    
                    if len(act_pjb) > 0: 
                        st.session_state.page = "✅ Form PJB Operasional" # Langsung arahkan ke PJB
                    else: 
                        st.session_state.page = "📝 Form Request Dana" # Langsung arahkan ke Req Dana
                except:
                    st.session_state.page = "🏠 Hub Menu Utama"
            else:
                st.session_state.page = "🏠 Hub Menu Utama"
        
        st.session_state.needs_routing = False
        st.rerun()

# ==========================================
# INISIALISASI SESSION STATE & NAVIGASI
# ==========================================
if 'page' not in st.session_state: st.session_state.page = "🏠 Hub Menu Utama"
if 'admin_logged_in' not in st.session_state: st.session_state.admin_logged_in = False
if 'pdf_ready' not in st.session_state: st.session_state.pdf_ready = False

c_nav1, c_nav2, c_nav3 = st.columns([4, 1, 1])
with c_nav3:
    if st.button(f"🚪 Logout", help=f"Keluar dari akun {st.session_state.logged_in_user}", use_container_width=True):
        st.session_state.is_authenticated = False
        st.session_state.logged_in_user = ""
        st.session_state.has_absent = False
        st.session_state.page = "🏠 Hub Menu Utama"
        st.rerun()

if st.session_state.page != "🏠 Hub Menu Utama":
    with c_nav1:
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
        
    if st.button("📝\nREPORT LAPANGAN\n(Update Progress & Generate WA)", use_container_width=True): st.session_state.page = "📝 Report Lapangan"; st.rerun()

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
                        out_all, out_lock, aging_tickets, hist_tkt, _ = get_user_tickets_status(cek_nama, data_cek[SHEET_REQUEST], data_cek[SHEET_PJB], data_cek[SHEET_APP])
                    if hist_tkt:
                        st.dataframe(pd.DataFrame(hist_tkt), hide_index=True, use_container_width=True)
                        if aging_tickets: st.warning(f"🔔 Ada {len(aging_tickets)} request tertunda >3 Hari.")
                        if out_all: st.error(f"⚠️ {len(out_all)} Request memblokir status Anda.")
                        else: st.success("✅ Seluruh tiket aman dan Approved!")
                    else: st.info("Tidak ada data.")
                    
        with tab_tim_pending:
            if st.button("🔍 Tarik Data Tim Belum PJB", use_container_width=True, type="primary"):
                with st.spinner("Memindai seluruh data tim..."):
                    data_cek = fetch_spreadsheet_data(MASTER_DATA[cek_nop]["spreadsheet_id"])
                    req_r, pjb_r, app_r = data_cek[SHEET_REQUEST], data_cek[SHEET_PJB], data_cek[SHEET_APP]
                    list_blm_pjb = []
                    for nm in MASTER_DATA[cek_nop]["names"]:
                        if not nm.strip(): continue
                        _, _, _, hist_tkt, _ = get_user_tickets_status(nm, req_r, pjb_r, app_r)
                        for h in hist_tkt:
                            tgl_req = parse_date(h["Tanggal"])
                            if tgl_req >= CUTOFF_DATE:
                                if "Menunggu PJB" in h["Status"] or "Telat" in h["Status"]:
                                    list_blm_pjb.append({"Nama Petugas": nm, "No Tiket": h["Tiket"], "Tanggal": h["Tanggal"], "Status": h["Status"]})
                    if list_blm_pjb:
                        st.error(f"⚠️ Ditemukan {len(list_blm_pjb)} tiket aktif belum PJB!")
                        st.dataframe(pd.DataFrame(list_blm_pjb), hide_index=True, use_container_width=True)
                    else:
                        st.success("🎉 Seluruh tim sudah menyelesaikan PJB.")

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
        if st.button("🎫 MASTER TIKET PM", use_container_width=True): st.session_state.page = "🎫 Master Tiket PM"; st.rerun()
        c_a1, c_a2 = st.columns(2)
        with c_a1:
            if st.button("🛡️ APPROVAL CENTER", use_container_width=True): st.session_state.page = "🛡️ Approval Center"; st.rerun()
            if st.button("📈 LIVE MONITORING", use_container_width=True): st.session_state.page = "📈 Live Monitoring"; st.rerun()
            if st.button("👀 REQ & PJB MONITORING", use_container_width=True): st.session_state.page = "👀 Request & PJB Monitoring"; st.rerun()
        with c_a2:
            if st.button("🏦 MANAJEMEN KAS", use_container_width=True): st.session_state.page = "🏦 Manajemen Kas & Distribusi"; st.rerun()
            if st.button("🖨️ REPORT & AUTO PJB", use_container_width=True): st.session_state.page = "🖨️ Auto PJB Report"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='text-align: center; color: #94a3b8; font-size: 0.8rem; margin-top:50px;'>Created by Okta Pradika<br>KUT SYSTEM - v8.7 Enterprise Mobile Edition (3D)</div>", unsafe_allow_html=True)


# ==========================================
# PAGE ADMIN: MASTER TIKET PM
# ==========================================
elif st.session_state.page == "🎫 Master Tiket PM":
    st.markdown("<div class='header-card'><h2>🎫 MASTER DATA TIKET PM</h2><p>Push/Upload Daftar Tiket Preventative Maintenance Bulanan</p></div>", unsafe_allow_html=True)
    nop_pm = st.selectbox("📂 Pilih Database Regional (NOP):", ["-- Pilih NOP --"] + list(MASTER_DATA.keys()))
    if nop_pm != "-- Pilih NOP --":
        target_ss = MASTER_DATA[nop_pm]["spreadsheet_id"]
        data_all = fetch_spreadsheet_data(target_ss)
        pm_r = data_all.get(SHEET_TIKET_PM, [])
        c_pm1, c_pm2 = st.columns([1, 2])
        with c_pm1:
            with st.form("form_tiket_pm"):
                bulan_pm = st.selectbox("Bulan / Periode", [f"{m} {datetime.now().year}" for m in ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]])
                site_pm = st.selectbox("Cluster / Site Target", MASTER_DATA[nop_pm]["clusters"])
                raw_tickets = st.text_area("Masukkan Nomor Tiket", height=150)
                if st.form_submit_button("💾 Push ke Database"):
                    if not raw_tickets.strip(): st.error("Kosong!")
                    else:
                        parsed = [t.strip().upper() for t in re.split(r'[,\n]+', raw_tickets) if t.strip()]
                        if parsed:
                            with st.spinner("Memasukkan tiket..."):
                                client = gspread.authorize(get_credentials()).open_by_key(target_ss)
                                ws = client.worksheet(SHEET_TIKET_PM)
                                new_rows, ts = [], datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                                for t in parsed: new_rows.append([ts, nop_pm, bulan_pm, t, site_pm, "AVAILABLE"])
                                ws.append_rows(new_rows)
                                fetch_spreadsheet_data.clear()
                                st.success(f"✅ Berhasil menambah {len(parsed)} Tiket!")
                                time.sleep(1.5); st.rerun()
        with c_pm2:
            avail_pm_view = [{"Periode": r[2], "No Tiket": r[3], "Site/Cluster": r[4], "Status": r[5]} for r in pm_r[1:] if len(r)>=6 and str(r[1]).strip().upper() == nop_pm.strip().upper() and str(r[5]).strip().upper() == "AVAILABLE"]
            if avail_pm_view: st.dataframe(pd.DataFrame(avail_pm_view), hide_index=True, use_container_width=True)
            else: st.info("Tidak ada tiket PM tersedia.")


# ==========================================
# PAGE 1: FORM REQUEST DANA (DENGAN HISTORI DI BAWAH)
# ==========================================
elif st.session_state.page == "📝 Form Request Dana":
    st.markdown("<div class='header-card'><h2>📝 PORTAL PENGAJUAN DANA</h2><p>Operational System - Input Pengajuan Baru</p></div>", unsafe_allow_html=True)
    
    nop_options = [""] + list(MASTER_DATA.keys())
    default_nop_idx = nop_options.index(st.session_state.get('auto_nop', '')) if st.session_state.get('auto_nop', '') in nop_options else 0
    nop = st.selectbox("📌 1. Pilih Database Regional (NOP)", nop_options, index=default_nop_idx)
    
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
            
        list_nopol_bersih = sorted(list(set([n.strip().upper() for n in list_nopol_csv if n.strip()] + list(history_nopols))))
        options_nopol = ["-- Pilih Nopol / Ketik Baru --"] + list_nopol_bersih
        
        auto_lat_tujuan, auto_long_tujuan, auto_lat_brgkt, auto_long_brgkt = "0", "0", "0", "0"
        status_app_motor, motor_limit_lock = "NONE", False

        col1, col2 = st.columns(2)
        with col1:
            tanggal = st.date_input("Tanggal Pengajuan")
            cluster = st.selectbox("Cluster Regional", [""] + MASTER_DATA[nop]["clusters"])
            
            # AUTO-FILL NAMA TERKUNCI (Kecuali Admin/Bos)
            is_boss_admin_global = st.session_state.logged_in_user in ["OKTA PRADIKA", "MAWARDAH"]
            if is_boss_admin_global:
                nama = st.selectbox("Nama Petugas / Pemohon (Hak Akses Admin)", [""] + MASTER_DATA[nop]["names"])
            else:
                nama = st.session_state.logged_in_user
                st.text_input("👤 Nama Petugas (Auto-Locked)", value=nama, disabled=True)
                
            nama_lookup = nama.strip().upper()
            
            # Ambil Status Tiket User untuk Blokir Pengajuan Baru (jika ada) dan untuk Tabel Histori di bawah
            out_all, out_lock, aging_tickets, hist_cek, _ = get_user_tickets_status(nama, req_r, pjb_r, app_r)
            if aging_tickets: st.warning(f"🔔 PENGINGAT: Anda memiliki {len(aging_tickets)} pengajuan tertunda PJB >3 Hari!")
            
            default_bank, default_no_rek = "BNI", ""
            if nama_lookup != "" and nama_lookup in tim_dict:
                auto_lat_brgkt, auto_long_brgkt = str(tim_dict[nama_lookup].get("Latitude", "0")), str(tim_dict[nama_lookup].get("Longtitude", "0"))
                for r in reversed(req_r[1:]): 
                    if len(r) > 18 and str(r[5]).strip().upper() == nama_lookup:
                        if str(r[17]).strip() in ["BNI", "BCA", "MANDIRI", "BRI"]:
                            default_bank, default_no_rek = str(r[17]).strip(), str(r[18]).strip(); break
                            
            is_locked_user = len(out_lock) > 0 # Jika ada tiket expired / pending approval, form di-lock
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
                pm_r = data_all.get(SHEET_TIKET_PM, [])
                avail_pm = [str(r[3]).strip().upper() for r in pm_r[1:] if len(r)>=6 and str(r[1]).strip().upper() == nop.strip().upper() and "AVAILABLE" in str(r[5]).strip().upper() and str(r[3]).strip() != ""]
                pm_selected_list = st.multiselect("Pilih Tiket PM:", avail_pm)
                tiket_string = ", ".join(pm_selected_list)
                if not tiket_string: tiket = st.text_input("Atau ketik Manual Tiket PM:")
                else: tiket = st.text_input("Tiket (Auto-Fill):", value=tiket_string, disabled=True)
            else:
                tiket = st.text_input("Nomor Tiket SWFM (WAJIB)")
                
            base_tiket_clean = tiket.strip().upper()
            is_duplicate, is_rejected_request = False, False
            for r in reversed(app_r[1:]):
                if len(r) > 5 and r[3] == "Request Dana" and str(r[2]).strip().upper() == base_tiket_clean:
                    if str(r[5]).strip().upper() == "REJECTED": is_rejected_request = True
                    break
            if base_tiket_clean != "" and not is_rejected_request:
                for t in all_requested_tickets:
                    if base_tiket_clean in t: is_duplicate = True; break
                        
            status_izin = "NONE"
            if is_duplicate:
                for r in reversed(app_r[1:] if len(app_r) > 1 else []):
                    if len(r) > 5 and r[3] == "Izin Revisi" and str(r[2]).strip().upper() == base_tiket_clean:
                        status_izin = str(r[5]).strip(); break
                if status_izin != "APPROVED":
                    st.error(f"⛔ Akses Terkunci: Tiket **{base_tiket_clean}** sudah terdaftar. Minta Izin Revisi ke Admin.")
                    if st.button("🚨 Minta Izin Revisi ke Admin Sekarang", type="primary", use_container_width=True):
                        append_data(SHEET_APP, [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), nama, base_tiket_clean, "Izin Revisi", 0, "PENDING", "-"], target_ss)
                        st.success("Terkirim!"); time.sleep(2.5); st.rerun()
                    st.stop()

            deskripsi = st.text_area("Deskripsi Pekerjaan / Justifikasi")
            list_nama_tim = [n for n in MASTER_DATA[nop]["names"] if n.strip().upper() != nama_lookup and n != ""]
            tim_bareng = st.multiselect("👥 Rekan Tim Bersama (Opsional)", list_nama_tim)

        st.markdown("<div class='section-title'>📍 3. Rute Peta (Satelit)</div>", unsafe_allow_html=True)
        c_lat1, c_lon1, c_lat2, c_lon2 = st.columns(4)
        with c_lat1: lat_berangkat = st.text_input("Lat Berangkat", value=auto_lat_brgkt)
        with c_lon1: long_berangkat = st.text_input("Long Berangkat", value=auto_long_brgkt)
        with c_lat2: lat_tujuan = st.text_input("Lat Tujuan", value=auto_lat_tujuan)
        with c_lon2: long_tujuan = st.text_input("Long Tujuan", value=auto_long_tujuan)

        jarak_km_oneway, jarak_km_pp, jarak_final_text, invalid_coords = 0.0, 0.0, "", False
        clat1, clon1 = clean_coord(lat_berangkat), clean_coord(long_berangkat)
        clat2, clon2 = clean_coord(lat_tujuan), clean_coord(long_tujuan)
        if clat1 != 0 and clon1 != 0 and clat2 != 0 and clon2 != 0:
            jarak_km_oneway, poly, durasi_sec = get_route_and_distance(clon1, clat1, clon2, clat2)
            jarak_km_pp = jarak_km_oneway * 2
            dur_jam_pp = (durasi_sec * 2) / 3600.0
            jarak_final_text = f"{jarak_km_pp:.1f} Km (PP) | {int(dur_jam_pp)} Jam {int((dur_jam_pp - int(dur_jam_pp))*60)} Mnt"
            st.info(f"🛣️ Jarak Peta: **{jarak_km_pp:.1f} Km (PP)**")
        else:
            invalid_coords = True
            st.warning("⚠️ Koordinat belum lengkap.")

        # Ambil NOPOL dasar dari database
        auto_nopol = tim_dict.get(nama_lookup, {}).get("NOPOL", "")
        if auto_nopol in ["nan", "0", "None"]: auto_nopol = ""

        st.markdown("<div class='section-title'>🛒 4. Rincian Kebutuhan Dana</div>", unsafe_allow_html=True)
        kebutuhan_dana_list = st.multiselect("Pilih jenis pengeluaran:", ["BBM", "Uang Makan", "Penginapan", "Material", "Fery Reguler/Carter", "Klotok/Kapal Carter"])
        
        sub_requests = []
        is_mobil = is_motor = is_genset = False
        
        if "BBM" in kebutuhan_dana_list:
            jns_bbm_list = st.multiselect("BBM untuk Kendaraan/Peralatan apa saja?", ["Mobil", "Motor", "Genset"])
            if "Mobil" in jns_bbm_list:
                is_mobil = True
                with st.expander("🚙 BBM Mobil", expanded=True):
                    c_m1, c_m2 = st.columns(2)
                    with c_m1:
                        jb_mobil = st.selectbox("Jenis BBM", ["Pertalite", "Pertamax", "Dexlite", "Bio Solar", "Pertamina Dex"], key="b_mob")
                        est_liter_mob = round(jarak_km_pp / 9.0, 1) if jarak_km_pp > 0 else 5.0
                        keb_mobil = st.number_input("Estimasi Dana (Rp)", min_value=0, step=1000, value=int(est_liter_mob * 10000), key="k_mob")
                    with c_m2:
                        # AUTO-FILL NOPOL KHUSUS MBP & PM
                        if role in ["MBP", "PM"] and auto_nopol:
                            st.success(f"🚙 Plat Mobil Diisi Otomatis (Akses {role})")
                            idx_mob = options_nopol.index(auto_nopol) if auto_nopol in options_nopol else 0
                        else:
                            idx_mob = options_nopol.index(auto_nopol) if auto_nopol in options_nopol else 0
                            
                        plat_mobil = st.selectbox("Plat Mobil", options_nopol, index=idx_mob, key="p_mob")
                        if plat_mobil == "-- Pilih Nopol / Ketik Baru --": plat_mobil = st.text_input("Ketik Manual:", key="pmob_man").strip().upper()
                        last_km_mob = get_last_indicator(plat_mobil, "Mobil", pjb_r)
                        km_awal_mob = st.number_input("KM Awal Mobil", min_value=0.0, step=0.1, value=float(last_km_mob), key="km_mob")
                    sub_requests.append({"tiket": f"{base_tiket_clean} [MOBIL]", "kategori": f"Mobil - {jb_mobil}", "kebutuhan": keb_mobil, "plat": plat_mobil, "indikator": km_awal_mob, "last_ind": last_km_mob, "tipe": "Mobil"})
                    
            if "Motor" in jns_bbm_list:
                is_motor = True
                with st.expander("🏍️ BBM Motor", expanded=True):
                    c_mt1, c_mt2 = st.columns(2)
                    with c_mt1:
                        l_butuh = st.number_input("Berapa Liter?", min_value=0.0, step=0.1, value=round(jarak_km_pp / 35.0, 1), key="lb_mot")
                        keb_motor = int(l_butuh * 10000)
                        jb_motor = st.selectbox("Jenis BBM", ["Pertalite", "Pertamax"], key="b_mot")
                    with c_mt2:
                        idx_mot = options_nopol.index(auto_nopol) if auto_nopol in options_nopol else 0
                        plat_motor = st.selectbox("Plat Motor", options_nopol, index=idx_mot, key="p_mot")
                        if plat_motor == "-- Pilih Nopol / Ketik Baru --": plat_motor = st.text_input("Ketik Manual:", key="pmot_man").strip().upper()
                        last_km_mot = get_last_indicator(plat_motor, "Motor", pjb_r)
                        km_awal_mot = st.number_input("KM Awal Motor", min_value=0.0, step=0.1, value=float(last_km_mot), key="km_mot")
                    sub_requests.append({"tiket": f"{base_tiket_clean} [MOTOR]", "kategori": f"Motor - {jb_motor}", "kebutuhan": keb_motor, "plat": plat_motor, "indikator": km_awal_mot, "last_ind": last_km_mot, "tipe": "Motor"})
                    
            if "Genset" in jns_bbm_list:
                is_genset = True
                with st.expander("⚡ BBM Genset", expanded=True):
                    c_g1, c_g2 = st.columns(2)
                    with c_g1:
                        jb_genset = st.selectbox("Jenis BBM", ["Dexlite", "Bio Solar", "Pertalite"], key="b_gen")
                        keb_genset = st.number_input("Estimasi Dana (Rp)", min_value=0, step=1000, value=150000, key="k_gen")
                    with c_g2:
                        plat_genset = st.selectbox("ID/Plat Genset", options_nopol, key="p_gen")
                        if plat_genset == "-- Pilih Nopol / Ketik Baru --": plat_genset = st.text_input("Ketik Manual:", key="pgen_man").strip().upper()
                        last_rh_gen = get_last_indicator(plat_genset, "Genset", pjb_r)
                        rh_awal_gen = st.number_input("RH Awal Genset", min_value=0.0, step=0.1, value=float(last_rh_gen), key="rh_gen")
                    sub_requests.append({"tiket": f"{base_tiket_clean} [GENSET]", "kategori": f"Genset - {jb_genset}", "kebutuhan": keb_genset, "plat": plat_genset, "indikator": rh_awal_gen, "last_ind": last_rh_gen, "tipe": "Genset"})

        if "Uang Makan" in kebutuhan_dana_list or "Penginapan" in kebutuhan_dana_list:
            c_um1, c_um2 = st.columns(2)
            with c_um1: hari_req = st.number_input("Rencana Berapa Hari?", min_value=1, step=1, value=1)
            jml_org = 1 + len(tim_bareng)
            if "Uang Makan" in kebutuhan_dana_list:
                with c_um2: nom_req_um = st.number_input("Nominal UM/Hari (Maks Rp 60k)", min_value=0, max_value=60000*jml_org, step=5000, value=60000*jml_org)
                tot_um = hari_req * nom_req_um
                sub_requests.append({"tiket": f"{base_tiket_clean} [UM]", "kategori": "Akomodasi", "kebutuhan": tot_um, "plat": "", "indikator": 0.0, "last_ind": 0.0, "tipe": "UM", "hari": hari_req, "nom_um": nom_req_um})
            if "Penginapan" in kebutuhan_dana_list:
                with c_um2: nom_req_inap = st.number_input("Nominal Inap/Malam (Maks Rp 150k)", min_value=0, max_value=150000*jml_org, step=10000, value=150000*jml_org)
                tot_inap = hari_req * nom_req_inap
                sub_requests.append({"tiket": f"{base_tiket_clean} [INAP]", "kategori": "Penginapan", "kebutuhan": tot_inap, "plat": "", "indikator": 0.0, "last_ind": 0.0, "tipe": "Inap", "hari": hari_req, "nom_inap": nom_req_inap})

        if "Material" in kebutuhan_dana_list:
            keb_mat = st.number_input("Estimasi Material (Rp)", min_value=0, step=1000)
            sub_requests.append({"tiket": f"{base_tiket_clean} [MATERIAL]", "kategori": "Material", "kebutuhan": keb_mat, "plat": "", "indikator": 0.0, "last_ind": 0.0, "tipe": "Material"})

        total_kebutuhan_all = sum([r['kebutuhan'] for r in sub_requests])
        if sub_requests: st.markdown(f"<div class='metric-3d'><div class='metric-title'>Total Kalkulasi Kebutuhan</div><div class='metric-value'>Rp {total_kebutuhan_all:,.0f}</div></div>", unsafe_allow_html=True)

        st.markdown("<div class='section-title'>🏦 5. Pembayaran & Lampiran</div>", unsafe_allow_html=True)
        col_pay1, col_pay2 = st.columns(2)
        with col_pay1:
            rek_penerima = st.selectbox("Bank Penerima", ["BNI", "BCA", "MANDIRI", "BRI"])
            no_rek = st.text_input("Nomor Rekening")
        with col_pay2:
            nominal_tf_str = st.text_input("Total Nominal Transfer Final", str(total_kebutuhan_all))
            nominal_tf = clean_nominal(nominal_tf_str)

        c_up1, c_up2 = st.columns(2)
        with c_up1: foto_km = ui_image_uploader("1. Foto KM / RH Awal", key="req_km")
        with c_up2: foto_evidance = ui_image_uploader("2. Foto Evidance Request", key="req_ev")
        
        form_invalid = (nama == "" or cluster == "" or role == "-- Pilih Role --" or keperluan == "" or not base_tiket_clean)

        if is_locked_user:
            st.error(f"⛔ Akses Terkunci: Anda tidak bisa melakukan Request Dana karena masih ada PJB yang belum dikirim atau tiket Expired.")
        else:
            if st.button("📤 Submit Request Dana (Generate Split)", type="primary", use_container_width=True):
                if form_invalid: st.error("❌ Form belum lengkap!"); st.stop()
                if not sub_requests: st.error("❌ Pilih minimal 1 kebutuhan dana!"); st.stop()
                
                with st.spinner("Mengupload & menyimpan ke server..."):
                    url_km = upload_foto(foto_km)
                    url_evidance = upload_foto(foto_evidance)
                    ts_now, tgl_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S"), tanggal.strftime("%d/%m/%Y")
                    
                    for req in sub_requests:
                        desc_final = deskripsi
                        if tim_bareng: desc_final += f"\n\n[Tim: {', '.join(tim_bareng)}]"
                        data_req = [ts_now, tgl_str, nop, req['tiket'], cluster, nama, role, site_id, keperluan, req['kebutuhan'], req['kategori'], desc_final, str(req['indikator']), jarak_final_text, lat_berangkat, long_berangkat, req['plat'], rek_penerima, no_rek, nominal_tf, url_km, url_evidance, lat_tujuan, long_tujuan]
                        append_data(SHEET_REQUEST, data_req, target_ss)
                        if req['plat'] and req['plat'] not in list_nopol_bersih: save_new_nopol_to_csv(req['plat'])
                            
                    if pm_selected_list: update_pm_ticket_status(target_ss, pm_selected_list, "REQUESTED")
                    st.balloons(); st.success("🎉 Berhasil disubmit!"); time.sleep(2); st.session_state.page = "🏠 Hub Menu Utama"; st.rerun()

        # TABEL HISTORI DI BAGIAN BAWAH FORM REQUEST DANA (BISA DIAKSES KAPAN SAJA)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>📊 6. Histori & Pengecekan Tiket Anda</div>", unsafe_allow_html=True)
        if hist_cek:
            st.dataframe(pd.DataFrame(hist_cek), hide_index=True, use_container_width=True)
        else:
            st.info("Belum ada histori tiket untuk Anda.")

# ==========================================
# PAGE 2: FORM PJB OPERASIONAL (AUTO-OPEN UPLOAD FORM)
# ==========================================
elif st.session_state.page == "✅ Form PJB Operasional":
    st.markdown("<div class='header-card'><h2>✅ PORTAL PJB (PENYELESAIAN)</h2><p>Selesaikan sub-tiket Anda secara spesifik.</p></div>", unsafe_allow_html=True)
    
    nop_cari_options = ["-- Pilih NOP --"] + list(MASTER_DATA.keys())
    default_nop_cari_idx = nop_cari_options.index(st.session_state.get('auto_nop', '')) if st.session_state.get('auto_nop', '') in nop_cari_options else 0
    nop_cari = st.selectbox("📂 1. Pilih Database (NOP):", nop_cari_options, index=default_nop_cari_idx)
    
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
        
        status_verif_dict = {str(r[2]).strip().upper(): str(r[5]).strip() for r in app_r[1:] if len(r) > 5 and r[3] == "Verifikasi PJB"}
        req_app_status = {str(r[2]).strip().upper(): str(r[5]).strip().upper() for r in app_r[1:] if len(r) > 5 and r[3] == "Request Dana"}
        
        col_id1, col_id2 = st.columns([2, 2])
        with col_id1: 
            idx_nama_pjb = MASTER_DATA[nop_cari]["names"].index(st.session_state.logged_in_user) if st.session_state.logged_in_user in MASTER_DATA[nop_cari]["names"] else 0
            nama_pjb = st.selectbox("👤 Pilih Nama Anda:", ["-- Pilih Nama --"] + MASTER_DATA[nop_cari]["names"], index=idx_nama_pjb+1 if idx_nama_pjb != 0 else 0)
        with col_id2: pass_nominal = st.text_input("🔑 Akses Nominal (Admin):", type="password")
            
        pending_list, pending_options = [], []
        for r in req_r[1:]:
            if len(r)>5 and str(r[3]).strip() != "":
                req_tk_raw = str(r[3]).strip().upper()
                req_tk_list = [t.strip() for t in req_tk_raw.split(",") if t.strip()]
                nm = str(r[5]).strip().upper()
                req_set = set(req_tk_list)
                is_ready_to_pjb = False
                
                # Cek apakah tiket benar-benar butuh di-PJB (belum masuk sama sekali atau di-Reject)
                if not req_set.issubset(pjb_tickets_all_set):
                    if req_app_status.get(req_tk_raw) != "REJECTED": is_ready_to_pjb = True
                elif status_verif_dict.get(req_tk_raw) == "REJECTED": is_ready_to_pjb = True 
                    
                if is_ready_to_pjb:
                    item = {"Tanggal": r[1], "Nama": r[5], "No Request": req_tk_raw, "Kategori": r[10] if len(r)>10 else "", "Keperluan": r[8] if len(r)>8 else ""}
                    if pass_nominal == "B0924649": item["Nominal"] = f"Rp {clean_nominal(r[9]):,.0f}" if len(r)>9 else "Rp 0"
                    if nama_pjb != "-- Pilih Nama --":
                        if nm == nama_pjb.strip().upper(): pending_list.append(item); pending_options.append(req_tk_raw)
                    else: pending_list.append(item)
        
        if pending_list: st.dataframe(pd.DataFrame(pending_list), hide_index=True, use_container_width=True)
        else: st.success("💎 Seluruh sub-tiket Anda sudah di-PJB, menunggu Verifikasi Admin!")
        
        # AUTO-SELECT TIKET PERTAMA JIKA ADA PENDINGAN -> LANGSUNG MENU UPLOAD
        st.markdown("<div class='section-title'>📂 Pilih & Upload PJB</div>", unsafe_allow_html=True)
        if pending_options:
            pilihan_tiket = st.selectbox("🎫 Pilih Sub-Tiket Pending:", ["-- Pilih Tiket --"] + pending_options + ["-- Ketik Manual --"], index=1)
        else:
            pilihan_tiket = st.selectbox("🎫 Pilih Sub-Tiket Pending:", ["-- Pilih Tiket --", "-- Ketik Manual --"])
            
        cari_tiket = ""
        if pilihan_tiket not in ["-- Pilih Tiket --", "-- Ketik Manual --"]:
            cari_tiket = pilihan_tiket
        elif pilihan_tiket == "-- Ketik Manual --":
            cari_tiket = st.text_input("Ketik Manual:")
            
        # TARIK DATA OTOMATIS TANPA TOMBOL JIKA TIKET DIPILIH DARI DROPDOWN
        if cari_tiket.strip():
            ditemukan_req = None
            for r in reversed(req_r[1:]):
                if len(r) > 3 and str(r[3]).strip().upper() == cari_tiket.strip().upper():
                    ditemukan_req = {
                        "NOP": r[2], "Cluster": r[4], "Nama": r[5], "Role": r[6], "Site": r[7], "Keperluan": r[8], 
                        "BBM": r[10] if len(r)>10 else "", "Desc": r[11] if len(r)>11 else "", 
                        "KMAwal": clean_indicator(r[12]) if len(r)>12 else 0.0, 
                        "NominalReq": clean_nominal(r[9]) if len(r)>9 else 0, 
                        "Jarak": r[13] if len(r)>13 else "", "Plat": r[16] if len(r)>16 else "",
                        "LatBerangkat": r[14] if len(r)>14 else "0", "LongBerangkat": r[15] if len(r)>15 else "0",
                        "LatTujuan": r[22] if len(r)>22 else "0", "LongTujuan": r[23] if len(r)>23 else "0",
                    }
                    break
            st.session_state.pjb_data = ditemukan_req
        else:
            st.session_state.pjb_data = None

        if st.session_state.get("pjb_data"):
            d = st.session_state.pjb_data
            valid_cari_tiket = cari_tiket.strip().upper()
            
            # LANGSUNG MENAMPILKAN MENU UPLOAD BUKTI TRANSFER DLL
            st.info(f"✅ Data tiket **{valid_cari_tiket}** ditarik otomatis. Silakan lengkapi form PJB di bawah ini:")
            f_transfer = st.file_uploader("Upload Foto Bukti Transfer Admin (WAJIB)", type=["jpg", "png", "jpeg"])
            
            if f_transfer is not None:
                tgl_pjb = st.date_input("Tanggal PJB")
                nominal_pjb = st.number_input("Nominal PJB Terpakai", value=int(d["NominalReq"]))
                
                is_genset = "genset" in str(d["BBM"]).lower()
                is_vehicle = "mobil" in str(d["BBM"]).lower() or "motor" in str(d["BBM"]).lower() or is_genset
                
                km_akhir, tot_liter, harga_satuan, tot_nilai_nota = 0.0, "0", 0, 0
                f_isi = f_nota_bbm = f_mat = f_notamat = f_inap = f_kerja = None
                
                if is_vehicle:
                    km_akhir = st.number_input("KM/RH Akhir Aktual", min_value=0.0, value=float(d["KMAwal"]), step=0.1)
                    tot_liter = st.text_input("Total Liter", "0")
                    harga_satuan = st.number_input("Harga Satuan", min_value=0, step=500, value=0)
                    tot_nilai_nota = st.number_input("Total Nota (Rp)", min_value=0, step=1000, value=0)
                    
                    p1, p2, p3 = st.columns(3)
                    with p1: f_isi = ui_image_uploader("Foto Pengisian", key="p_isi")
                    with p2: f_km = ui_image_uploader("Foto Nota KM", key="p_km")
                    with p3: f_kerja = ui_image_uploader("Foto Pekerjaan", key="p_krj")

                if st.button("🚀 Kirim PJB", type="primary", use_container_width=True):
                    with st.spinner("Mengirim..."):
                        url_isi = upload_foto(f_isi) if f_isi else ""
                        url_km = upload_foto(f_km) if 'f_km' in locals() and f_km else ""
                        url_kerja = upload_foto(f_kerja) if f_kerja else ""
                        
                        data_pjb = [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), tgl_pjb.strftime("%d/%m/%Y"), d["NOP"], d["Cluster"], d["Nama"], d["Role"], d["Site"], d["Keperluan"], d["BBM"], d["Desc"], str(km_akhir), nominal_pjb, d["Plat"], url_isi, "", url_km, "", "", "", url_kerja, tot_nilai_nota, valid_cari_tiket, tot_liter, harga_satuan, str(km_akhir - d["KMAwal"]), "", "", upload_foto(f_transfer)]
                        data_pjb_padded = (data_pjb + [""] * 37)[:37]
                        
                        if append_data(SHEET_PJB, data_pjb_padded, target_ss):
                            append_data(SHEET_APP, [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), d["Nama"], valid_cari_tiket, "Verifikasi PJB", nominal_pjb, "PENDING", "-"], target_ss)
                            st.balloons(); st.success("🎉 PJB Berhasil Dikirim!"); st.session_state.pjb_data = None; time.sleep(2); st.session_state.page = "🏠 Hub Menu Utama"; st.rerun()


# ==========================================
# PAGE: APPROVAL CENTER, MANAJEMEN KAS, LIVE MONITORING, AUTO PJB REPORT, MONITORING, REPORT LAPANGAN
# ==========================================
elif st.session_state.page == "🛡️ Approval Center":
    st.markdown("<div class='header-card'><h2>🛡️ APPROVAL CENTER</h2><p>Pusat Verifikasi PJB & Revisi</p></div>", unsafe_allow_html=True)
    nop_admin = st.selectbox("📂 Wilayah (NOP):", ["-- Pilih NOP --"] + list(MASTER_DATA.keys()))
    if nop_admin != "-- Pilih NOP --":
        target_ss = MASTER_DATA[nop_admin]["spreadsheet_id"]
        data_all = fetch_spreadsheet_data(target_ss)
        app_r, pjb_r = data_all[SHEET_APP], data_all[SHEET_PJB]
        pending_pjb = [{"Row Index": idx, "Waktu": str(r[0]), "Nama": str(r[1]), "Tiket": str(r[2]), "Status": str(r[5])} for idx, r in enumerate(app_r) if len(r) > 5 and str(r[5]).strip() == "PENDING" and r[3] == "Verifikasi PJB"]
        if pending_pjb:
            st.dataframe(pd.DataFrame(pending_pjb).drop(columns=["Row Index"]), hide_index=True, use_container_width=True)
            sel_t = st.selectbox("Pilih Tiket PJB:", [p["Tiket"] for p in pending_pjb])
            act = st.radio("Keputusan:", ["APPROVE", "REJECT"])
            if st.button("Proses"):
                idxs = [p["Row Index"] for p in pending_pjb if p["Tiket"] == sel_t]
                for idx in idxs: update_approval_status(target_ss, idx, "APPROVED" if act=="APPROVE" else "REJECTED")
                st.success("Berhasil!"); time.sleep(1); st.rerun()
        else: st.success("Tidak ada pending PJB.")

elif st.session_state.page == "🏦 Manajemen Kas & Distribusi":
    st.markdown("<div class='header-card'><h2>🏦 MANAJEMEN KAS</h2><p>Rekap Kas Masuk & Distribusi</p></div>", unsafe_allow_html=True)
    nop_admin = st.selectbox("📂 Wilayah (NOP):", ["-- Pilih NOP --"] + list(MASTER_DATA.keys()))
    if nop_admin != "-- Pilih NOP --":
        target_ss = MASTER_DATA[nop_admin]["spreadsheet_id"]
        data_all = fetch_spreadsheet_data(target_ss)
        if st.button("Refresh Data Kas"): fetch_spreadsheet_data.clear(); st.rerun()
        st.info("Gunakan tab manajemen kas sesuai kebutuhan operasional.")

elif st.session_state.page == "📈 Live Monitoring":
    st.markdown("<div class='header-card'><h2>📈 LIVE MONITORING</h2><p>Dashboard Analisa Kas & Performa</p></div>", unsafe_allow_html=True)
    nop_live = st.selectbox("🌐 Pilih NOP:", ["-- Pilih NOP --"] + list(MASTER_DATA.keys()))
    if nop_live != "-- Pilih NOP --": st.info("Monitoring aktif.")

elif st.session_state.page == "🖨️ Auto PJB Report":
    st.markdown("<div class='header-card'><h2>🖨️ REPORT CENTER</h2><p>Export & Auto Laporan</p></div>", unsafe_allow_html=True)
    nop_report = st.selectbox("📂 Pilih NOP:", ["-- Pilih NOP --"] + list(MASTER_DATA.keys()))
    if nop_report != "-- Pilih NOP --": st.info("Report center siap.")

elif st.session_state.page == "👀 Request & PJB Monitoring":
    st.markdown("<div class='header-card'><h2>📋 REQ & PJB MONITORING</h2><p>Pantau Aktivitas Tim</p></div>", unsafe_allow_html=True)
    nop_mon = st.selectbox("🌐 Pilih NOP:", ["-- Pilih NOP --"] + list(MASTER_DATA.keys()))
    if nop_mon != "-- Pilih NOP --": st.info("Monitoring siap.")

elif st.session_state.page == "📝 Report Lapangan":
    st.markdown("<div class='header-card'><h2>📝 REPORT LAPANGAN</h2><p>Auto-Generate Laporan WA</p></div>", unsafe_allow_html=True)
    nop_rep = st.selectbox("📂 Pilih NOP:", ["-- Pilih NOP --"] + list(MASTER_DATA.keys()))
    if nop_rep != "-- Pilih NOP --":
        target_ss = MASTER_DATA[nop_rep]["spreadsheet_id"]
        data_all = fetch_spreadsheet_data(target_ss)
        nama_rep = st.selectbox("👤 Nama:", ["-- Pilih --"] + MASTER_DATA[nop_rep]["names"])
        if nama_rep != "-- Pilih --":
            analisa = st.text_area("Analisa Pekerjaan")
            if st.button("Generate WA Text"):
                st.code(f"UPDATE PROGRESS\nNama: {nama_rep}\nAnalisa: {analisa}", language="markdown")
