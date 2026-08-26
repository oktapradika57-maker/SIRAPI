import streamlit as st
import pandas as pd
import gspread
import base64
import cloudinary
import cloudinary.uploader
import requests
import math
import os
import time
import re
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials

# ==========================================
# 0. KONFIGURASI HALAMAN & SUPER PREMIUM UI
# ==========================================
st.set_page_config(page_title="SiRAPI Enterprise", page_icon="💎", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800;900&display=swap');
        .main { background: #f4f7f6; font-family: 'Plus Jakarta Sans', sans-serif; }
        .header-card { background: linear-gradient(135deg, #0F2027 0%, #203A43 50%, #2C5364 100%); padding: 35px 20px; border-radius: 20px; color: white; text-align: center; box-shadow: 0 15px 30px rgba(0,0,0,0.2); margin-bottom: 30px; margin-top: 15px; border-bottom: 5px solid #00F2FE; }
        .header-card h1 { font-weight: 900; font-size: 2.2rem; margin-bottom: 5px; }
        .header-card p { font-size: 1rem; color: #cbd5e1; margin-bottom: 0; }
        div[data-testid="stButton"] > button { background: rgba(255, 255, 255, 0.95) !important; border: 1px solid #e2e8f0 !important; border-radius: 16px !important; box-shadow: 0 8px 15px rgba(0,0,0,0.05) !important; height: auto !important; padding: 20px 10px !important; transition: all 0.3s ease !important; display: flex; flex-direction: column; align-items: center; justify-content: center; }
        div[data-testid="stButton"] > button:hover { background: linear-gradient(135deg, #4FACFE 0%, #00F2FE 100%) !important; transform: translateY(-5px) !important; border: none !important; }
        div[data-testid="stButton"] > button p { color: #1e293b !important; font-size: 1.1rem !important; font-weight: 800 !important; margin:0; text-align:center; }
        div[data-testid="stButton"] > button:hover p { color: white !important; }
        .btn-admin div[data-testid="stButton"] > button { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important; }
        .btn-admin div[data-testid="stButton"] > button p { color: white !important; font-size: 1rem !important;}
        .btn-admin div[data-testid="stButton"] > button:hover { background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%) !important; }
        .section-title { color: #0F2027; font-size: 1.2rem; font-weight: 900; border-bottom: 3px solid #cbd5e1; padding-bottom: 8px; margin-top: 25px; margin-bottom: 20px;}
        .metric-3d { background: white; padding: 20px; border-radius: 16px; text-align: center; box-shadow: 0 10px 20px rgba(0, 0, 0, 0.05); border-top: 5px solid #4FACFE; margin-bottom: 15px; }
        .metric-title { font-size: 0.8rem; color: #64748b; font-weight: 800; text-transform: uppercase; }
        .metric-value { font-size: 1.6rem; font-weight: 900; margin-top: 5px; color: #0F2027;}
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
            poly = decode_polyline(res["routes"][0]["geometry"])
            return dist_km, poly
    except: pass
    dist_km = haversine(lat1, lon1, lat2, lon2) * 1.3 
    return dist_km, [[lon1, lat1], [lon2, lat2]]

@st.cache_resource
def get_credentials():
    with open("credentials.json", "w") as f: f.write(st.secrets["gcp_json"])
    return Credentials.from_service_account_file("credentials.json", scopes=SCOPES)

@st.cache_data(ttl=600)
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
                    if pic_name: tim_dict[pic_name]['NOPOL'] = nopol_val
    except Exception: pass
    return site_dict, site_list, tim_dict, list_nopol_csv

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
            else: history.append({"Tiket": tkt, "Tanggal": tgl, "Status": "🔴 Menunggu PJB (Belum Input)"})
        else:
            app_data = pjb_app_status.get(tkt, {"status": "APPROVED", "catatan": ""})
            if app_data["status"] == "PENDING":
                outstanding_all.append(tkt); outstanding_lock.append(tkt)
                history.append({"Tiket": tkt, "Tanggal": tgl, "Status": "⏳ PJB Menunggu Verifikasi Admin"})
            elif app_data["status"] == "REJECTED":
                outstanding_all.append(tkt); outstanding_lock.append(tkt)
                history.append({"Tiket": tkt, "Tanggal": tgl, "Status": f"❌ PJB DITOLAK: {app_data['catatan']}"})
            else: history.append({"Tiket": tkt, "Tanggal": tgl, "Status": "🟢 PJB Selesai & Approved"})
            
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
                with open(file_name, "a") as f: f.write(f"\n{new_plat}")
        else:
            with open(file_name, "w") as f: f.write(f"NOPOL,PIC\n{new_plat},")
    except Exception: pass

# ==========================================
# GENERATOR SURAT TUGAS & UANG MAKAN (PDF/HTML)
# ==========================================
def generate_surat_tugas_html(data_dict):
    nop_name = data_dict.get("NOP", "Palangka Raya")
    
    # Kalkulasi Uang Makan & Penginapan
    lama = int(data_dict.get("Lama Tugas", 1))
    um_hari = int(data_dict.get("Uang Makan", 0))
    tot_um = lama * um_hari
    
    inap_malam = int(data_dict.get("Uang Inap", 0))
    malam = lama - 1 if lama > 1 else 0
    tot_inap = malam * inap_malam
    grand_total = tot_um + tot_inap

    img_tags = ""
    for idx, f in enumerate(data_dict.get("Fotos", [])):
        if f and f.startswith("http"):
            img_tags += f'<div class="photo-box"><img src="{f}"><p>Lampiran Foto {idx+1}</p></div>'

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Surat Tugas & Uang Makan - {data_dict.get('Tiket')}</title>
        <style>
            body {{ font-family: 'Arial', sans-serif; margin: 0; padding: 0; background: #fff; color: #000; }}
            .page {{ width: 210mm; min-height: 297mm; padding: 20mm; margin: 10mm auto; box-sizing: border-box; position: relative; background: white; border: 1px solid #eee; }}
            .header {{ display: flex; align-items: center; justify-content: space-between; border-bottom: 3px solid #E63946; padding-bottom: 10px; margin-bottom: 20px; }}
            .logo-text h1 {{ margin: 0; font-size: 24px; color: #1D3557; text-transform: uppercase; }}
            .logo-text p {{ margin: 0; font-size: 14px; color: #E63946; font-style: italic; font-weight: bold; }}
            .footer {{ position: absolute; bottom: 20mm; left: 20mm; right: 20mm; border-top: 1px solid #ccc; padding-top: 10px; font-size: 10px; color: #555; text-align: right; }}
            h3 {{ text-align: center; text-decoration: underline; margin-bottom: 25px; font-size: 18px; }}
            p, td, th {{ font-size: 14px; line-height: 1.5; }}
            .table-main {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 20px; }}
            .table-main th, .table-main td {{ border: 1px solid #000; padding: 8px; text-align: center; }}
            .table-main th {{ background-color: #f0f0f0; }}
            .table-layout {{ width: 100%; margin-bottom: 15px; }}
            .table-layout td {{ padding: 3px 0; vertical-align: top; }}
            .signature-box {{ width: 100%; margin-top: 40px; text-align: center; }}
            .signature-box td {{ width: 50%; padding-top: 60px; }}
            .photo-grid {{ display: flex; flex-wrap: wrap; justify-content: space-between; gap: 15px; margin-top: 20px; }}
            .photo-box {{ width: 48%; text-align: center; border: 1px solid #ddd; padding: 5px; box-sizing: border-box; }}
            .photo-box img {{ width: 100%; height: 250px; object-fit: contain; }}
            .photo-box p {{ font-size: 12px; margin: 5px 0 0 0; font-weight: bold; }}
            @media print {{ body {{ background: none; }} .page {{ margin: 0; border: none; page-break-after: always; }} .btn-print {{ display: none; }} }}
            .btn-print {{ position: fixed; top: 20px; right: 20px; background: #0ea5e9; color: white; padding: 15px 30px; border-radius: 8px; font-weight: bold; text-decoration: none; font-size: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); cursor: pointer; border: none; }}
        </style>
    </head>
    <body>
        <button class="btn-print" onclick="window.print()">🖨️ Print / Save PDF</button>

        <!-- HALAMAN 1: SURAT TUGAS -->
        <div class="page">
            <div class="header">
                <div class="logo-text"><h1>KINARYA UTAMA TEKNIK</h1><p>by Kisel Group</p></div>
            </div>
            <h3>SURAT TUGAS</h3>
            <p>Saya yang bertanda tangan di bawah ini:</p>
            <table class="table-layout">
                <tr><td width="20%">Nama</td><td width="5%">:</td><td>Okta Pradika</td></tr>
                <tr><td>NIK</td><td>:</td><td>B0924649</td></tr>
                <tr><td>Jabatan</td><td>:</td><td>Koordinator NOP {nop_name}</td></tr>
            </table>
            <p>Dengan ini menugaskan sebagai berikut :</p>
            
            <table class="table-main">
                <tr><th>No.</th><th>Nama</th><th>NIK</th><th>Jabatan</th><th>Lokasi Kerja</th></tr>
                <tr><td>1</td><td>{data_dict.get('Nama')}</td><td>{data_dict.get('NIK')}</td><td>{data_dict.get('Role')}</td><td>{data_dict.get('Cluster')}</td></tr>
            </table>

            <table class="table-layout">
                <tr><td width="25%">No Ticket</td><td width="5%">:</td><td>{data_dict.get('Tiket')}</td></tr>
                <tr><td>Tujuan</td><td>:</td><td>{data_dict.get('Tujuan')}</td></tr>
                <tr><td>Estimasi Jarak</td><td>:</td><td>{data_dict.get('Jarak')}</td></tr>
                <tr><td>Lama tugas dinas</td><td>:</td><td>{lama} Hari</td></tr>
                <tr><td>Tgl. Berangkat</td><td>:</td><td>{data_dict.get('Tgl Berangkat')}</td></tr>
                <tr><td>Tgl. Kembali</td><td>:</td><td>{data_dict.get('Tgl Kembali')}</td></tr>
                <tr><td>Keperluan</td><td>:</td><td>{data_dict.get('Keperluan')}</td></tr>
            </table>

            <p style="margin-top: 30px;">Demikianlah Surat Penugasan ini dibuat agar dapat dilaksanakan dengan sebaik-baiknya dan melaporkan hasilnya setelah selesai pelaksanaan tugas.</p>
            
            <table class="signature-box">
                <tr><td colspan="2" style="text-align:left; padding-top:10px;">{nop_name}, {data_dict.get('Tgl Berangkat')}</td></tr>
                <tr>
                    <td align="left">Koordinator NOP {nop_name},<br><br><br><br><b>Okta Pradika</b><br>NIK. B0924649</td>
                    <td align="right">POH. SPV Operation,<br><br><br><br><b>Rian Sharon</b><br>NIK. 79058</td>
                </tr>
            </table>
            <div class="footer">HEAD OFFICE - PT. KINARYA UTAMA TEKNIK | Graha Sucofindo Lt. 1, Jl. Raya Pasar Minggu Kav. 34, Jakarta Selatan</div>
        </div>

        <!-- HALAMAN 2: SURAT PENGAJUAN UANG MAKAN -->
        <div class="page">
            <div class="header">
                <div class="logo-text"><h1>KINARYA UTAMA TEKNIK</h1><p>by Kisel Group</p></div>
            </div>
            <h3>SURAT PENGAJUAN UANG MAKAN</h3>
            <p>Nomor : {data_dict.get('ID_UM')}</p>
            <p>Koordinator ENOM NOP {nop_name} PT. Kinarya Utama Teknik, dengan ini menugaskan kepada :</p>
            <table class="table-layout">
                <tr><td width="20%">Nama</td><td width="5%">:</td><td>{data_dict.get('Nama')}</td></tr>
                <tr><td>NIK</td><td>:</td><td>{data_dict.get('NIK')}</td></tr>
                <tr><td>Jabatan</td><td>:</td><td>{data_dict.get('Role')}</td></tr>
            </table>
            
            <table class="table-main">
                <tr><th>No.</th><th>Tujuan Tugas</th><th>Berangkat</th><th>Kembali</th><th>Uraian Penugasan</th></tr>
                <tr><td>1</td><td>{data_dict.get('Tujuan')}</td><td>{data_dict.get('Tgl Berangkat')}</td><td>{data_dict.get('Tgl Kembali')}</td><td>{data_dict.get('Keperluan')}</td></tr>
            </table>
            <p>Harap dilaksanakan dan segera memberikan laporan perjalanan dinas setelah kembali.</p>
            
            <table class="table-main" style="text-align: left;">
                <tr style="background:#f0f0f0;"><th colspan="3" style="text-align: left;">Bantuan Perjalanan Dinas</th><th style="text-align: left;">Perhitungan</th><th style="text-align: right;">Jumlah</th></tr>
                <tr>
                    <td colspan="3">Uang Makan ({lama} Hari)</td>
                    <td>{lama} Hari x Rp. {um_hari:,}</td>
                    <td align="right">Rp. {tot_um:,}</td>
                </tr>
                <tr>
                    <td colspan="3">Bantuan Penginapan</td>
                    <td>{malam} Malam x Rp. {inap_malam:,}</td>
                    <td align="right">Rp. {tot_inap:,}</td>
                </tr>
                <tr style="font-weight: bold; background:#f0f0f0;">
                    <td colspan="4" align="right">Jumlah Total</td>
                    <td align="right">Rp. {grand_total:,}</td>
                </tr>
            </table>

            <table class="signature-box" style="margin-top:20px;">
                <tr><td colspan="2" style="text-align:left; padding-top:0px;">
                    Dikeluarkan di : {nop_name}<br>
                    Pada Tanggal &nbsp;&nbsp;: {data_dict.get('Tgl Berangkat')}
                </td></tr>
                <tr>
                    <td align="left">Koordinator NOP {nop_name},<br><br><br><br><b>Okta Pradika</b><br>NIK. B0924649</td>
                    <td align="right">POH. SPV Operation,<br><br><br><br><b>Rian Sharon</b><br>NIK. 79058</td>
                </tr>
            </table>
            <div class="footer">HEAD OFFICE - PT. KINARYA UTAMA TEKNIK | Graha Sucofindo Lt. 1, Jl. Raya Pasar Minggu Kav. 34, Jakarta Selatan</div>
        </div>

        <!-- HALAMAN 3: LAMPIRAN FOTO PRESISI -->
        <div class="page">
            <div class="header">
                <div class="logo-text"><h1>KINARYA UTAMA TEKNIK</h1><p>by Kisel Group</p></div>
            </div>
            <h3>LAMPIRAN DOKUMENTASI AKOMODASI & LOKASI</h3>
            <div class="photo-grid">
                {img_tags if img_tags else "<p style='text-align:center; width:100%; color:#888;'>Tidak ada lampiran foto yang diunggah.</p>"}
            </div>
            <div class="footer">HEAD OFFICE - PT. KINARYA UTAMA TEKNIK | Graha Sucofindo Lt. 1, Jl. Raya Pasar Minggu Kav. 34, Jakarta Selatan</div>
        </div>
    </body>
    </html>
    """
    return html

# ==========================================
# INISIALISASI SESSION STATE & NAVIGASI
# ==========================================
if 'page' not in st.session_state: st.session_state.page = "🏠 Hub Menu Utama"
if 'admin_logged_in' not in st.session_state: st.session_state.admin_logged_in = False

if st.session_state.page != "🏠 Hub Menu Utama":
    if st.button("⬅️ KEMBALI KE MENU UTAMA", use_container_width=True):
        st.session_state.page = "🏠 Hub Menu Utama"
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

    st.markdown("""<div class="header-card"><h1>SiRAPI Enterprise</h1><p>Sistem Rekapitulasi Anggaran Pertanggungjawaban Informasi</p></div>""", unsafe_allow_html=True)

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
        pass_input = st.text_input("Masukkan Password Admin (Pusat):", type="password")
        if st.button("Buka Kunci Akses Admin"):
            if pass_input in AUTHORIZED_PASSWORDS:
                st.session_state.admin_logged_in = True; st.rerun()
            else: st.error("Password Salah!")
    else:
        st.success("✅ Akses Admin Terbuka")
        if st.button("🔒 Keluar Mode Admin"): st.session_state.admin_logged_in = False; st.rerun()
        st.markdown("<div class='btn-admin'>", unsafe_allow_html=True)
        c_a1, c_a2 = st.columns(2)
        with c_a1:
            if st.button("🛡️ APPROVAL CENTER\n(Validasi PJB)", use_container_width=True): st.session_state.page = "🛡️ Approval Center"; st.rerun()
            if st.button("📈 LIVE MONITORING\n(Dashboard Analisa)", use_container_width=True): st.session_state.page = "📈 Live Monitoring"; st.rerun()
            if st.button("👀 REQ & PJB MONITORING\n(Pantau Tim & Warning)", use_container_width=True): st.session_state.page = "👀 Request & PJB Monitoring"; st.rerun()
        with c_a2:
            if st.button("🏦 MANAJEMEN KAS\n(Distribusi Dana)", use_container_width=True): st.session_state.page = "🏦 Manajemen Kas & Distribusi"; st.rerun()
            if st.button("🖨️ REPORT & AUTO PJB\n(Export Laporan)", use_container_width=True): st.session_state.page = "🖨️ Auto PJB Report"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='text-align: center; color: #94a3b8; font-size: 0.8rem; margin-top:50px;'>Created by Okta Pradika<br>KUT SYSTEM - v6.0 Enterprise Mobile Edition</div>", unsafe_allow_html=True)


# ==========================================
# PAGE 1: FORM REQUEST DANA
# ==========================================
elif st.session_state.page == "📝 Form Request Dana":
    st.markdown("<div class='header-card'><h2>📝 PORTAL PENGAJUAN DANA</h2><p>Operational System - Input Pengajuan Baru / Revisi</p></div>", unsafe_allow_html=True)
    
    nop = st.selectbox("📌 1. Pilih Database Regional (NOP)", [""] + list(MASTER_DATA.keys()))
    
    if nop != "":
        st.markdown("<div class='section-title'>📋 2. Informasi Petugas & Tiket</div>", unsafe_allow_html=True)
        target_ss = MASTER_DATA[nop]["spreadsheet_id"]
        data_all = fetch_spreadsheet_data(target_ss)
        req_r, pjb_r, app_r = data_all[SHEET_REQUEST], data_all[SHEET_PJB], data_all[SHEET_APP]
        
        all_requested_tickets = [r[3].strip().upper() for r in req_r[1:] if len(r) > 3]
        site_dict, site_list, tim_dict, list_nopol_csv = load_excel_data()
        
        history_nopols = set()
        for r in req_r[1:]:
            if len(r) > 16 and r[16].strip(): history_nopols.add(r[16].strip().upper())
        for r in pjb_r[1:]:
            if len(r) > 12 and r[12].strip(): history_nopols.add(r[12].strip().upper())
            
        list_nopol = sorted(list(set([n.strip().upper() for n in list_nopol_csv if n.strip()] + list(history_nopols))))
        auto_lat_tujuan, auto_long_tujuan, auto_lat_brgkt, auto_long_brgkt = "0", "0", "0", "0"

        if "rev_req" not in st.session_state: st.session_state.rev_req = {}
        rev_data = st.session_state.rev_req
        status_app_motor = "NONE"
        motor_limit_lock = False

        col1, col2 = st.columns(2)
        with col1:
            tanggal = st.date_input("Tanggal Pengajuan")
            cluster = st.selectbox("Cluster Regional", [""] + MASTER_DATA[nop]["clusters"])
            nama = st.selectbox("Nama Petugas / Pemohon (PIC Utama)", [""] + MASTER_DATA[nop]["names"])
            nama_lookup = nama.strip().upper()
            
            out_all, out_lock, aging_august, hist_cek = get_user_tickets_status(nama, req_r, pjb_r, app_r)
            if aging_august: st.warning(f"🔔 PENGINGAT: Anda memiliki **{len(aging_august)}** tiket bulan Agustus tertunda >3 Hari!")
            
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
                            st.session_state.rev_req = {"kebutuhan": clean_nominal(r[9]), "desc": r[11], "km_awal": clean_indicator(r[12]), "plat": r[16]}
                            found = True; break
                    if found: st.success("Data Ditemukan!"); time.sleep(1); st.rerun()
                    else: st.error("Tiket Tidak Ditemukan!")
            
            is_duplicate = (tiket.strip().upper() in all_requested_tickets) and tiket.strip() != ""
            role = st.selectbox("Role Jabatan", ["-- Pilih Role --", "PM", "TE", "MBP", "CME"])
            
            if nop == "Palangkaraya" and len(site_list) > 0:
                site_id = st.selectbox("ID Site / Lokasi", [""] + site_list)
                if site_id != "-- Pilih Site ID --" and site_id in site_dict:
                    auto_lat_tujuan, auto_long_tujuan = str(site_dict[site_id].get("Latitude Tujuan", "0")), str(site_dict[site_id].get("Longtitude Tujuan", "0"))
            else: site_id = st.text_input("ID Site / Lokasi")
            
        with col2:
            keperluan = st.selectbox("Klasifikasi Keperluan Dana", LIST_KEPERLUAN)
            jns_kendaraan = st.selectbox("Jenis Kendaraan / Peralatan", ["", "Mobil", "Motor", "Genset", "Lainnya"])
            
            tim_bareng, tim_terkunci = [], []
            if jns_kendaraan.lower() == "mobil":
                list_nama_tim = [n for n in MASTER_DATA[nop]["names"] if n.strip().upper() != nama_lookup and n != ""]
                tim_bareng = st.multiselect("👥 Pilih Rekan Tim yang Berangkat Bersama (Opsional)", list_nama_tim)
                if role in ["TE", "MBP", "CME"] and tim_bareng:
                    for member in tim_bareng:
                        _, m_out_lock, _, _ = get_user_tickets_status(member, req_r, pjb_r, app_r)
                        if len(m_out_lock) > 0: tim_terkunci.append(member)
            
            kebutuhan = 0
            jenis_bahan_bakar = ""
            motor_anomali, total_motor_this_month = False, 0
            
            if jns_kendaraan.lower() == "motor":
                k_tangki = st.number_input("Kapasitas Tangki (Liter)", min_value=0.0, step=0.1)
                h_satuan = st.number_input("Harga Satuan BBM (Rp/Liter)", min_value=0, step=500)
                l_butuh = st.number_input("Berapa Liter Kebutuhan?", min_value=0.0, step=0.1)
                kebutuhan = int(l_butuh * h_satuan)
                jenis_bahan_bakar = st.selectbox("Pilih Jenis BBM (Wajib)", ["", "Pertalite", "Pertamax"])
                final_bbm = f"{jns_kendaraan} - {jenis_bahan_bakar}" if jenis_bahan_bakar else jns_kendaraan
                
                if l_butuh > k_tangki and k_tangki > 0: motor_anomali = True
                
                current_month_str = datetime.now().strftime("%m/%Y")
                for r in req_r[1:]:
                    if len(r) > 10:
                        try:
                            if parse_date(r[1]).strftime("%m/%Y") == current_month_str and str(r[5]).strip().upper() == nama_lookup and "motor" in str(r[10]).lower():
                                total_motor_this_month += clean_nominal(r[9])
                        except: pass
                
                if (total_motor_this_month + kebutuhan) > 500000:
                    for r in reversed(app_r):
                        if len(r) > 5 and str(r[2]).strip().upper() == tiket.strip().upper() and r[3] == "Limit Motor":
                            status_app_motor = str(r[5]).strip().upper(); break
                    if status_app_motor != "APPROVED": motor_limit_lock = True
            elif jns_kendaraan.lower() in ["mobil", "genset"]:
                jenis_bahan_bakar = st.selectbox("Pilih Jenis BBM (Wajib)", ["", "Pertalite", "Pertamax", "Dexlite", "Bio Solar", "Pertamina Dex"])
                final_bbm = f"{jns_kendaraan} - {jenis_bahan_bakar}" if jenis_bahan_bakar else jns_kendaraan
                kebutuhan = st.number_input("Estimasi Kebutuhan Dana (Rp)", min_value=0, step=1000, value=rev_data.get("kebutuhan", 0))
            else:
                final_bbm = jns_kendaraan
                kebutuhan = st.number_input("Estimasi Kebutuhan Dana (Rp)", min_value=0, step=1000, value=rev_data.get("kebutuhan", 0))
            
            auto_nopol = rev_data.get("plat", "")
            if auto_nopol == "" and nama_lookup != "" and nama_lookup in tim_dict:
                auto_nopol = str(tim_dict[nama_lookup].get("NOPOL", "")).strip()
                if auto_nopol in ["nan", "0", "None"]: auto_nopol = ""
                
            plat_choice_is_manual = False
            if role in ["PM", "MBP", "CME"]: plat = st.text_input("Plat Nomor", value=auto_nopol, disabled=(auto_nopol!=""))
            elif role != "-- Pilih Role --":
                plat_choice = st.selectbox("Pilih Plat Nomor Kendaraan", ["-- Pilih NOPOL --"] + list_nopol + ["Lainnya (Ketik Manual)"])
                if plat_choice == "Lainnya (Ketik Manual)": 
                    plat = st.text_input("Ketik Plat Nomor Baru", value=auto_nopol)
                    plat_choice_is_manual = True
                else: plat = "" if plat_choice == "-- Pilih NOPOL --" else plat_choice
            else: plat = st.text_input("Plat Nomor Kendaraan / ID Genset", value=auto_nopol)
                
            plat_clean = plat.strip().replace(" ", "").upper()
            
            last_indikator = 0.0
            if plat_clean != "" and jns_kendaraan.lower() in ["mobil", "motor", "genset"]:
                for r in reversed(pjb_r[1:]): 
                    if len(r) > 12 and str(r[12]).strip().replace(" ", "").upper() == plat_clean:
                        last_indikator = clean_indicator(r[10]); break

            label_indikator = f"Ketik Angka {'RH Genset' if jns_kendaraan.lower()=='genset' else 'KM'} AKTUAL SAAT INI (Wajib)"
            km_awal = st.number_input(label_indikator, min_value=0.0, value=float(rev_data.get("km_awal", 0.0)), step=0.1)
            deskripsi = st.text_area("Deskripsi Pekerjaan / Justifikasi", value=rev_data.get("desc", ""))
            deskripsi_final = deskripsi + f"\n\n[Berangkat bersama tim: {', '.join(tim_bareng)}]" if tim_bareng else deskripsi

        is_vehicle = jns_kendaraan.lower() in ['mobil', 'motor']
        st.markdown("<div class='section-title'>📍 3. Rute Peta (Satelit) & Keuangan</div>", unsafe_allow_html=True)
        
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
            nominal_tf_str = st.text_input("Total Nominal Transfer (TANPA TITIK/KOMA, Cth: 100000)", value="0")
            try: nominal_tf = int(nominal_tf_str.replace(".", "").replace(",", "").strip())
            except: nominal_tf = 0

        jarak_final_text, jarak_angka, invalid_coords = "", 0, False
        if is_vehicle:
            c_lat1, c_lon1 = clean_coord(lat_berangkat), clean_coord(long_berangkat)
            c_lat2, c_lon2 = clean_coord(lat_tujuan), clean_coord(long_tujuan)
            if c_lat1 != 0 and c_lon1 != 0 and c_lat2 != 0 and c_lon2 != 0:
                with st.spinner("Satelit sedang menarik data jalan raya..."):
                    jarak_km_oneway, _ = get_route_and_distance(c_lon1, c_lat1, c_lon2, c_lat2)
                jarak_angka = jarak_km_oneway * 2
                jarak_final_text = f"{jarak_angka:.1f} Km (PP)"
            else: invalid_coords = True

        # FITUR BARU: AUTO AKOMODASI (>=80KM)
        st.markdown("<div class='section-title'>🏨 4. Akomodasi & Surat Tugas (Otomatis)</div>", unsafe_allow_html=True)
        akomodasi_perlu = "Tidak"
        if jarak_angka >= 80:
            st.warning("⚠️ Jarak tempuh (PP) >= 80km. Akomodasi otomatis terpilih 'Perlu'.")
            akomodasi_perlu = "Perlu"
            
        akomodasi_choice = st.radio("Apakah Perlu Akomodasi & Surat Uang Makan?", ["Perlu", "Tidak"], index=0 if akomodasi_perlu == "Perlu" else 1)
        
        nik_tim, lama_tugas, uang_makan, uang_inap = "", 1, 0, 0
        tgl_kembali = tanggal
        f_akom1, f_akom2, f_akom3, f_akom4 = None, None, None, None
        
        if akomodasi_choice == "Perlu":
            st.markdown("<div style='background:#F8FAFC; padding:15px; border-radius:10px; border-left: 5px solid #F59E0B;'>", unsafe_allow_html=True)
            c_a1, c_a2 = st.columns(2)
            with c_a1:
                st.text_input("Nama (Auto)", value=nama, disabled=True)
                nik_tim = st.text_input("NIK Petugas (Wajib Diisi)")
                st.text_input("Jabatan (Auto)", value=role, disabled=True)
                st.text_input("Lokasi Kerja (Auto)", value=cluster, disabled=True)
                st.text_input("No Tiket (Auto)", value=tiket, disabled=True)
                st.text_input("Tujuan (Auto)", value=site_id, disabled=True)
                st.text_input("Estimasi Jarak (Auto)", value=f"{jarak_angka:.2f} KM", disabled=True)
            with c_a2:
                lama_tugas = st.number_input("Lama Tugas (Hari)", min_value=1, step=1)
                tgl_kembali = tanggal + timedelta(days=lama_tugas)
                st.text_input("Tgl Berangkat (Auto)", value=tanggal.strftime("%d/%m/%Y"), disabled=True)
                st.text_input("Tgl Kembali (Auto)", value=tgl_kembali.strftime("%d/%m/%Y"), disabled=True)
                st.text_area("Keperluan (Auto)", value=deskripsi_final, disabled=True)
                uang_makan = st.number_input("Bantuan Uang Makan per Hari (Rp)", min_value=0, step=50000)
                uang_inap = st.number_input("Bantuan Penginapan per Malam (Rp)", min_value=0, step=50000)
                
            st.markdown("<b>📸 Bukti Evidance Akomodasi & Lokasi (Wajib Isi)</b>", unsafe_allow_html=True)
            c_f1, c_f2, c_f3, c_f4 = st.columns(4)
            with c_f1: f_akom1 = st.file_uploader("Foto Evidance 1", type=["jpg", "png", "jpeg"])
            with c_f2: f_akom2 = st.file_uploader("Foto Evidance 2", type=["jpg", "png", "jpeg"])
            with c_f3: f_akom3 = st.file_uploader("Foto Evidance 3", type=["jpg", "png", "jpeg"])
            with c_f4: f_akom4 = st.file_uploader("Foto Evidance 4", type=["jpg", "png", "jpeg"])
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='section-title'>📸 5. Bukti Lampiran Fisik (Request)</div>", unsafe_allow_html=True)
        c_up1, c_up2 = st.columns(2)
        with c_up1: foto_km = st.file_uploader("Upload Foto KM / RH Genset Awal", type=["jpg", "png", "jpeg"])
        with c_up2: foto_evidance = st.file_uploader("Upload Foto Kendaraan/Pekerjaan", type=["jpg", "png", "jpeg"])
        
        form_invalid = (nama == "" or cluster == "" or role == "-- Pilih Role --" or keperluan == "" or jns_kendaraan == "")
        if akomodasi_choice == "Perlu" and not nik_tim.strip(): form_invalid = True

        if is_locked_user or motor_anomali or motor_limit_lock or len(tim_terkunci) > 0:
            st.error("⛔ AKSES DITOLAK: Terdapat tiket pending/limit tercapai pada Anda atau rekan tim Anda.")
            if st.text_input("🔑 Password Khusus (Bypass Admin):", type="password") in AUTHORIZED_PASSWORDS:
                if st.button("💡 Paksakan Kirim Request Dana (Bypass)", type="primary"):
                    if form_invalid or not tiket.strip() or invalid_coords: st.error("Lengkapi form!")
                    else:
                        with st.spinner("Processing..."):
                            id_um = f"UM-{nop[:3].upper()}-{datetime.now().strftime('%m%Y')}-{str(int(time.time()))[-4:]}" if akomodasi_choice == "Perlu" else "-"
                            data_req = [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), tanggal.strftime("%d/%m/%Y"), nop, tiket, cluster, nama, role, site_id, keperluan, kebutuhan, final_bbm, deskripsi_final, str(km_awal), jarak_final_text, lat_berangkat, long_berangkat, plat_clean, rek_penerima, no_rek, nominal_tf, upload_foto(foto_km), upload_foto(foto_evidance), lat_tujuan, long_tujuan, akomodasi_choice, nik_tim, str(lama_tugas), tgl_kembali.strftime("%d/%m/%Y"), str(uang_makan), str(uang_inap), upload_foto(f_akom1), upload_foto(f_akom2), upload_foto(f_akom3), upload_foto(f_akom4), id_um]
                            append_data(SHEET_REQUEST, data_req, target_ss)
                            if plat_choice_is_manual and plat_clean not in list_nopol: save_new_nopol_to_csv(plat_clean)
                            st.session_state.rev_req = {}; st.balloons(); st.success("🎉 Berhasil Bypass!"); time.sleep(2); st.session_state.page = "🏠 Hub Menu Utama"; st.rerun()
        else:
            if st.button("📤 Kirim Form Request Dana / Revisi", type="primary", use_container_width=True):
                if form_invalid or not tiket.strip() or invalid_coords: st.error("Lengkapi form (Semua isian wajib)!")
                elif nominal_tf <= 0: st.error("❌ PENGIRIMAN DITOLAK: Total Nominal Transfer tidak boleh 0 / kosong!")
                elif (jns_kendaraan.lower() in ["mobil", "motor", "genset"]) and (km_awal < last_indikator):
                    st.error(f"❌ PENGIRIMAN DITOLAK: Angka yang Anda ketik ({km_awal}) tidak boleh lebih kecil dari histori terakhir ({last_indikator})!")
                else:
                    with st.spinner("Mengunggah foto dan menyimpan data..."):
                        id_um = f"UM-{nop[:3].upper()}-{datetime.now().strftime('%m%Y')}-{str(int(time.time()))[-4:]}" if akomodasi_choice == "Perlu" else "-"
                        data_req = [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), tanggal.strftime("%d/%m/%Y"), nop, tiket, cluster, nama, role, site_id, keperluan, kebutuhan, final_bbm, deskripsi_final, str(km_awal), jarak_final_text, lat_berangkat, long_berangkat, plat_clean, rek_penerima, no_rek, nominal_tf, upload_foto(foto_km), upload_foto(foto_evidance), lat_tujuan, long_tujuan, akomodasi_choice, nik_tim, str(lama_tugas), tgl_kembali.strftime("%d/%m/%Y"), str(uang_makan), str(uang_inap), upload_foto(f_akom1), upload_foto(f_akom2), upload_foto(f_akom3), upload_foto(f_akom4), id_um]
                        append_data(SHEET_REQUEST, data_req, target_ss)
                        if plat_choice_is_manual and plat_clean not in list_nopol: save_new_nopol_to_csv(plat_clean)
                        st.session_state.rev_req = {}; st.balloons(); st.success("🎉 Data Anda Berhasil Dikirim / Direvisi!"); time.sleep(2.5); st.session_state.page = "🏠 Hub Menu Utama"; st.rerun()


# ==========================================
# PAGE 2: FORM PJB OPERASIONAL 
# ==========================================
elif st.session_state.page == "✅ Form PJB Operasional":
    st.markdown("<div class='header-card'><h2>✅ PORTAL PJB (PENYELESAIAN)</h2><p>Lengkapi nota realisasi untuk diverifikasi oleh Admin. Bisa untuk Revisi PJB.</p></div>", unsafe_allow_html=True)
    
    nop_cari = st.selectbox("📂 1. Pilih Database (NOP):", ["-- Pilih NOP --"] + list(MASTER_DATA.keys()))
    
    if nop_cari != "-- Pilih NOP --":
        target_ss = MASTER_DATA[nop_cari]["spreadsheet_id"]
        data_all = fetch_spreadsheet_data(target_ss)
        req_r, pjb_r, app_r = data_all[SHEET_REQUEST], data_all[SHEET_PJB], data_all[SHEET_APP]
        
        pjb_tickets_all = {str(r[21]).strip().upper() for r in pjb_r[1:] if len(r) > 21}
        
        status_verif_dict, catatan_verif_dict = {}, {}
        for r in app_r[1:]:
            if len(r) > 5 and r[3] == "Verifikasi PJB":
                tk = str(r[2]).strip().upper()
                if tk != "":
                    status_verif_dict[tk] = str(r[5]).strip()
                    if len(r) > 6: catatan_verif_dict[tk] = r[6]
        
        st.markdown("<div class='section-title'>🔍 2. Identifikasi Tim & Tarik Data</div>", unsafe_allow_html=True)
        col_id1, col_id2 = st.columns([2, 2])
        with col_id1: nama_pjb = st.selectbox("👤 Pilih Nama Anda:", ["-- Pilih Nama --"] + MASTER_DATA[nop_cari]["names"])
        with col_id2: pass_nominal = st.text_input("🔑 Akses Nominal (Admin):", type="password")
            
        pending_options = []
        for r in req_r[1:]:
            if len(r)>5 and str(r[3]).strip() != "":
                tk = str(r[3]).strip().upper()
                nm = str(r[5]).strip().upper()
                is_ready = (tk not in pjb_tickets_all) or (status_verif_dict.get(tk) == "REJECTED")
                if is_ready and nama_pjb != "-- Pilih Nama --" and nm == nama_pjb.strip().upper(): pending_options.append(tk)
        
        col_s2, col_s3 = st.columns([3, 1])
        with col_s2: 
            pilihan_tiket = st.selectbox("🎫 Pilih Nomor Tiket Pending:", ["-- Pilih Tiket --"] + pending_options + ["-- Ketik Manual --"]) if pending_options else "-- Ketik Manual --"
            cari_tiket = st.text_input("Ketik Manual (Termasuk Tiket Lama untuk Revisi):") if pilihan_tiket == "-- Ketik Manual --" else ("" if pilihan_tiket == "-- Pilih Tiket --" else pilihan_tiket)
        
        valid_cari_tiket = str(cari_tiket).strip().upper()

        with col_s3: 
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Tarik Data PJB", type="primary", use_container_width=True) and valid_cari_tiket:
                ditemukan_req, ditemukan_pjb = None, None
                for r in reversed(req_r[1:]):
                    if len(r) > 3 and str(r[3]).strip().upper() == valid_cari_tiket:
                        ditemukan_req = {
                            "Tgl Berangkat": r[1], "NOP": r[2], "Tiket": r[3], "Cluster": r[4], "Nama": r[5], "Role": r[6], "Tujuan": r[7], "Site": r[7], "Keperluan": r[8], "NominalReq": clean_nominal(r[9]) if len(r)>9 else 0, "BBM": r[10] if len(r)>10 else "", "Desc": r[11] if len(r)>11 else "", "KMAwal": clean_indicator(r[12]) if len(r)>12 else 0.0, "Jarak": r[13] if len(r)>13 else "", "Plat": r[16] if len(r)>16 else "",
                            "Akomodasi": r[24] if len(r)>24 else "Tidak", "NIK": r[25] if len(r)>25 else "", "Lama Tugas": r[26] if len(r)>26 else "1", "Tgl Kembali": r[27] if len(r)>27 else r[1], "Uang Makan": r[28] if len(r)>28 else 0, "Uang Inap": r[29] if len(r)>29 else 0, "Fotos": [r[30] if len(r)>30 else "", r[31] if len(r)>31 else "", r[32] if len(r)>32 else "", r[33] if len(r)>33 else ""], "ID_UM": r[34] if len(r)>34 else "-"
                        }
                        break
                        
                for r in reversed(pjb_r[1:]):
                    if len(r) > 21 and str(r[21]).strip().upper() == valid_cari_tiket:
                        ditemukan_pjb = r; break
                        
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
                    st.error("❌ Tiket Tidak ditemukan di Database Request.")

        if st.session_state.get("pjb_data"):
            d = st.session_state.pjb_data
            
            # TOMBOL CETAK SURAT TUGAS & UANG MAKAN
            if d.get("Akomodasi") == "Perlu":
                st.markdown("<div style='background:#E0F2FE; padding:15px; border-radius:10px; margin-top:20px; text-align:center;'>", unsafe_allow_html=True)
                st.write("📄 **Dokumen Akomodasi Tersedia (Surat Tugas & Pengajuan Uang Makan)**")
                html_surat = generate_surat_tugas_html(d)
                b64_html = base64.b64encode(html_surat.encode("utf-8")).decode()
                st.markdown(f"""
                    <a href="data:text/html;base64,{b64_html}" download="Surat_Tugas_{d['Tiket']}.html" 
                    style="display: inline-block; background-color: #0ea5e9; color: white; padding: 12px 25px; text-decoration: none; border-radius: 8px; font-weight: bold; margin-top: 10px;">
                    🖨️ Download & Cetak PDF Surat Tugas
                    </a>
                    <p style="font-size:12px; color:#555; margin-top:10px;">(Buka file HTML yang didownload, lalu klik tombol Print atau tekan Ctrl+P untuk menyimpannya sebagai PDF)</p>
                """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='section-title'>💸 Validasi Budget & Bukti Transfer</div>", unsafe_allow_html=True)
            f_transfer = st.file_uploader("Upload Foto Bukti Transfer Dana (WAJIB)", type=["jpg", "png", "jpeg"])
            
            if f_transfer is None:
                st.warning("⚠️ **AKSES TERKUNCI:** Silakan upload Bukti Transfer dari Admin terlebih dahulu agar form pengisian PJB terbuka.")
            else:
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
                is_genset = "genset" in str(d["BBM"]).lower()
                is_vehicle = "mobil" in str(d["BBM"]).lower() or "motor" in str(d["BBM"]).lower()
                label_akhir = "RH Genset Akhir" if is_genset else "KM Akhir Kendaraan"
                
                with c_c:
                    d_km_awal = float(d["KMAwal"])
                    st.info(f"📍 KM/RH saat Request awal: **{d_km_awal}**")
                    km_akhir = st.number_input(f"Ketik Angka {label_akhir} AKTUAL (Wajib)", min_value=0.0, value=float(d.get("km_akhir_lama", 0.0)), step=0.1)
                    total_km_tempuh = km_akhir - d_km_awal
                with c_d:
                    tot_liter = st.text_input("Total Liter BBM/Material", value=d.get("liter_lama", "0"))
                    harga_satuan = st.number_input("Harga Satuan (BBM/Material)", min_value=0, step=500, value=d.get("harga_lama", 0))
                    tot_nilai_nota = st.number_input("Total Fisik Sesuai Nota (Rp)", min_value=0, step=1000, value=d.get("nota_lama", 0))
                
                st.markdown("<div class='section-title'>📸 Lampiran Bukti (Foto)</div>", unsafe_allow_html=True)
                p1, p2, p3 = st.columns(3)
                with p1: f_isi = st.file_uploader("Evidance Pengisian", type=["jpg","png"]); f_nota_bbm = st.file_uploader("Nota BBM", type=["jpg","png"])
                with p2: f_mat = st.file_uploader("Foto Material", type=["jpg","png"]); f_notamat = st.file_uploader("Nota Material", type=["jpg","png"])
                with p3: f_inap = st.file_uploader("Nota Penginapan", type=["jpg","png"]); f_kerja = st.file_uploader("Evidance Pekerjaan", type=["jpg","png"]); f_km = st.file_uploader("Foto KM/RH Akhir (Disanding)", type=["jpg","png"])

                if st.button("🚀 Sahkan Pelaporan PJB / Submit Revisi", type="primary", use_container_width=True):
                    if (is_vehicle or is_genset) and (km_akhir < d_km_awal):
                        st.error(f"❌ PENGIRIMAN DITOLAK: Angka yang dimasukkan ({km_akhir}) LEBIH KECIL dari KM/RH Awal Anda ({d_km_awal})!")
                    else:
                        with st.spinner("Mengupload foto dan memproses PJB..."):
                            data_pjb = [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), tgl_pjb.strftime("%d/%m/%Y"), d["NOP"], d["Cluster"], d["Nama"], d["Role"], d["Site"], d["Keperluan"], d["BBM"], d["Desc"], str(km_akhir), nominal_pjb, d["Plat"], upload_foto(f_isi), upload_foto(f_nota_bbm), upload_foto(f_km), upload_foto(f_mat), upload_foto(f_notamat), upload_foto(f_inap), upload_foto(f_kerja), tot_nilai_nota, valid_cari_tiket, tot_liter, harga_satuan, str(round(total_km_tempuh, 2)), "", "", upload_foto(f_transfer)]
                            append_data(SHEET_PJB, [(r+[""]*28)[:28] for r in [data_pjb]][0], target_ss)
                            append_data(SHEET_APP, [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), d["Nama"], valid_cari_tiket, "Verifikasi PJB", nominal_pjb, "PENDING", "-"], target_ss)
                            st.balloons(); st.success("🎉 PJB Berhasil Dikirim untuk Verifikasi Admin!"); st.session_state.pjb_data = None; time.sleep(2.5); st.session_state.page = "🏠 Hub Menu Utama"; st.rerun()

# ==========================================
# PAGE 3: APPROVAL CENTER (KHUSUS ADMIN)
# ==========================================
elif st.session_state.page == "🛡️ Approval Center":
    st.markdown("<div class='header-card'><h2>🛡️ APPROVAL CENTER</h2><p>Pusat Verifikasi PJB & Harga BBM Anomali</p></div>", unsafe_allow_html=True)
    
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
                        "Row Index": idx, "Waktu": str(r[0]), "Nama": str(r[1]), "No Tiket": str(r[2]), 
                        "Jenis Pengajuan": str(r[3]), "Nominal": f"Rp {clean_nominal(r[4]):,.0f}", 
                        "Status": str(r[5]).strip(), "Keterangan": str(r[6]) if len(r) > 6 else "-"
                    }
                    if r[3] == "Verifikasi PJB": pending_pjb.append(item)
                    else: pending_anomali.append(item)
        
        tab_app1, tab_app2 = st.tabs(["📸 Verifikasi Foto PJB", "⛽ Approval Limit Motor & Anomali BBM"])
        with tab_app1:
            st.markdown("### 🔍 Daftar Tunggu Verifikasi PJB")
            if pending_pjb:
                st.dataframe(pd.DataFrame(pending_pjb).drop(columns=["Row Index"]), hide_index=True, use_container_width=True)
                target_tiket_pjb = st.selectbox("Pilih Tiket PJB untuk divalidasi:", [p["No Tiket"] for p in pending_pjb], key="sel_pjb")
                
                pjb_target = None
                for r in reversed(pjb_r[1:]):
                    if len(r) > 21 and str(r[21]).strip().upper() == target_tiket_pjb.strip().upper(): pjb_target = r; break
                        
                if pjb_target:
                    st.markdown("<div style='background:#F8FAFC; padding:15px; border-radius:10px; margin-bottom:15px;'><b>Bukti Terlampir:</b></div>", unsafe_allow_html=True)
                    cf1, cf2 = st.columns(2)
                    with cf1:
                        if len(pjb_target) > 14 and pjb_target[14]: st.image(pjb_target[14], caption="Kolom O: Foto Nota BBM / Material", use_container_width=True)
                        else: st.info("Tidak ada Foto Nota.")
                    with cf2:
                        if len(pjb_target) > 19 and pjb_target[19]: st.image(pjb_target[19], caption="Kolom T: Foto Evidance Pekerjaan", use_container_width=True)
                        else: st.info("Tidak ada Foto Pekerjaan.")
                
                st.markdown("### ⚡ Eksekusi Keputusan")
                ca1, ca2 = st.columns(2)
                with ca1: action_pjb = st.radio("Keputusan Admin:", ["Setujui PJB (APPROVE)", "Tolak PJB (REJECT)"], key="rad_pjb")
                with ca2: remark_pjb = st.text_input("Catatan / Remark (Wajib diisi jika ditolak):", key="rem_pjb")
                
                if st.button("Proses Verifikasi PJB", type="primary"):
                    if "REJECT" in action_pjb and not remark_pjb.strip():
                        st.error("⚠️ Mohon berikan Alasan / Catatan Penolakan agar tim tahu bagian yang harus direvisi.")
                    else:
                        target_indices = [p["Row Index"] for p in pending_pjb if p["No Tiket"] == target_tiket_pjb]
                        new_status = "APPROVED" if "APPROVE" in action_pjb else "REJECTED"
                        with st.spinner("Memperbarui database..."):
                            for idx in target_indices:
                                update_approval_status(target_ss, idx, new_status, remark_pjb if remark_pjb else "-")
                            st.success(f"✅ Tiket {target_tiket_pjb} berhasil di-{new_status}!")
                            time.sleep(2); st.rerun()
            else: st.success("✅ Tidak ada PJB yang menunggu verifikasi (Inbox Kosong).")
                
        with tab_app2:
            st.markdown("### 🚨 Daftar Tunggu Approval Harga / Limit Motor")
            if pending_anomali:
                st.dataframe(pd.DataFrame(pending_anomali).drop(columns=["Row Index"]), hide_index=True, use_container_width=True)
                ce1, ce2 = st.columns(2)
                with ce1: target_tiket_anm = st.selectbox("Pilih Tiket / Pengajuan:", [p["No Tiket"] for p in pending_anomali], key="sel_anm")
                with ce2: action_anm = st.radio("Keputusan Admin:", ["Setujui (APPROVE)", "Tolak (REJECT)"], key="rad_anm")
                
                if st.button("Proses Keputusan Harga/Limit", type="primary"):
                    target_indices = [p["Row Index"] for p in pending_anomali if p["No Tiket"] == target_tiket_anm]
                    new_status = "APPROVED" if "APPROVE" in action_anm else "REJECTED"
                    with st.spinner("Memperbarui database..."):
                        for idx in target_indices:
                            update_approval_status(target_ss, idx, new_status, "-")
                        st.success(f"✅ Pengajuan untuk {target_tiket_anm} berhasil di-{new_status}!")
                        time.sleep(2); st.rerun()
            else: st.success("✅ Tidak ada anomali harga atau limit yang menggantung.")


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
        
        tab_in, tab_out, tab_report, tab_pjb = st.tabs(["📥 1. Dana Masuk (Debit)", "📤 2. Distribusi Tim (Kredit)", "📊 3. Buku Besar Saldo Batch", "📋 4. List PJB & Dana Ops"])
        
        with tab_in:
            st.markdown("<div class='section-title'>📥 Tambah Kas Masuk Baru</div>", unsafe_allow_html=True)
            st.info("💡 **INFO:** Gunakan form ini saat Anda menerima dropping dana (misal dari Pusat).")
            with st.form("form_tambah_um"):
                c_u1, c_u2, c_u3 = st.columns([1, 2, 1])
                with c_u1: tgl_um = st.date_input("Tanggal UM Turun / Diterima")
                with c_u2: um_nobis = st.text_input("Nama Batch / Sumber Dana (Misal: 'UM Ops Tahap 3')")
                with c_u3: um_nominal = st.number_input("Nominal (Rp)", min_value=0, step=100000)
                
                if st.form_submit_button("💾 Rekam Kas Masuk"):
                    if um_nominal > 0 and um_nobis.strip():
                        append_data(SHEET_UM, [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), tgl_um.strftime("%d/%m/%Y"), um_nobis.strip(), um_nominal], target_ss)
                        st.success("✅ Dana Masuk berhasil direkam ke database!"); time.sleep(1.5); st.rerun()
                    else: st.error("Harap isi Nama Batch dan Nominal dengan benar.")
            
            if len(um_r) > 1:
                st.markdown("#### Histori Dana Masuk")
                padded_um = [(r + [""] * 4)[:4] for r in um_r[1:]]
                df_um_view = pd.DataFrame(padded_um, columns=["Waktu", "Tanggal", "Nama Batch Dana", "Nominal"])
                df_um_view["Nominal"] = df_um_view["Nominal"].apply(lambda x: f"Rp {clean_nominal(x):,.0f}")
                st.dataframe(df_um_view, hide_index=True, use_container_width=True)

        with tab_out:
            valid_batches = sorted(list(set([r[2].strip() for r in um_r[1:] if len(r) > 2 and r[2].strip() != ""])))
            
            st.markdown("<div class='section-title'>📤 Transfer Dana ke Tim Lapangan</div>", unsafe_allow_html=True)
            if not valid_batches: st.warning("⚠️ Belum ada Data 'Dana Masuk'. Silakan tambahkan dana masuk di tab pertama terlebih dahulu.")
            else:
                st.info("💡 **INFO:** Sistem ini mencatat transfer uang dari rekening kasbon Anda ke petugas, dan memotongnya otomatis dari Batch Sumber Dana yang dipilih.")
                with st.form("form_distribusi"):
                    c_d1, c_d2 = st.columns(2)
                    with c_d1:
                        tgl_dist = st.date_input("Tanggal Transfer")
                        sumber_dana = st.selectbox("Ambil dari Sumber Dana mana?", valid_batches)
                        nama_tim = st.selectbox("Pilih Petugas Penerima:", ["-- Pilih Nama --"] + MASTER_DATA[nop_admin]["names"])
                    with c_d2:
                        nom_dist = st.number_input("Nominal Transfer (Rp)", min_value=0, step=50000)
                        bukti_tf = st.file_uploader("Upload Bukti Transfer / Mutasi", type=['jpg','png','jpeg'])
                        
                    if st.form_submit_button("🚀 Kirim & Catat Distribusi"):
                        if nama_tim != "-- Pilih Nama --" and nom_dist > 0 and bukti_tf is not None:
                            with st.spinner("Mengupload foto bukti transfer..."):
                                url_bukti = upload_foto(bukti_tf)
                                data_dist = [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), tgl_dist.strftime("%d/%m/%Y"), sumber_dana, nama_tim, nom_dist, url_bukti]
                                append_data(SHEET_DISTRIBUSI, data_dist, target_ss)
                                st.success(f"✅ Berhasil mencatat transfer Rp {nom_dist:,.0f} ke {nama_tim} dari dana {sumber_dana}."); time.sleep(2.5); st.rerun()
                        else: st.error("Lengkapi form (Pilih Nama, Nominal, dan wajib Upload Bukti Transfer).")

            if len(dist_r) > 1:
                st.markdown("#### Histori Distribusi Terakhir")
                padded_dist = [(r + [""] * 6)[:6] for r in reversed(dist_r[1:])]
                df_dist_view = pd.DataFrame(padded_dist, columns=["Timestamp", "Tgl Transfer", "Sumber Dana", "Nama Penerima", "Nominal", "Link Bukti"])
                df_dist_view["Nominal"] = df_dist_view["Nominal"].apply(lambda x: f"Rp {clean_nominal(x):,.0f}")
                st.dataframe(df_dist_view.drop(columns=["Timestamp", "Link Bukti"]), hide_index=True, use_container_width=True)

        with tab_report:
            st.markdown("<div class='section-title'>📊 Buku Besar Saldo per Batch Dana</div>", unsafe_allow_html=True)
            
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
                
                st.markdown("#### Detail Saldo per Batch")
                st.dataframe(df_view_report, hide_index=True, use_container_width=True)
                
                csv_neraca = df_report.to_csv(index=False).encode('utf-8')
                st.download_button(label="📥 Download Detail Saldo CSV", data=csv_neraca, file_name=f"Saldo_Batch_{nop_admin}.csv", mime='text/csv', use_container_width=True)
            else: st.info("Belum ada perputaran dana pada NOP ini.")

        with tab_pjb:
            st.markdown("<div class='section-title'>📋 Rekap PJB (Cek Target per Dana Ops & Periode)</div>", unsafe_allow_html=True)
            
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
                            "Kolom A (Periode)": val_a,
                            "Tanggal": r[1] if len(r) > 1 else "-",
                            "Nama Tim": r[4] if len(r) > 4 else "-",
                            "Role": r[6] if len(r) > 6 else "-",
                            "Keperluan": r[8] if len(r) > 8 else "-",
                            "No Tiket / Deskripsi": r[9] if len(r) > 9 else "-",
                            "Kolom Q (Dana Ops)": val_q,
                            "Nominal PJB": nom
                        })
                        
                st.markdown(f"<div class='metric-3d' style='border-top: 6px solid #10B981;'><div class='metric-title'>Total Nominal PJB (Filtered)</div><div class='metric-value' style='background: -webkit-linear-gradient(45deg, #10B981, #059669); -webkit-background-clip: text;'>Rp {total_nominal_pjb:,.0f}</div></div>", unsafe_allow_html=True)
                
                if filtered_pjb:
                    df_pjb_ops = pd.DataFrame(filtered_pjb)
                    df_pjb_ops["Nominal PJB"] = df_pjb_ops["Nominal PJB"].apply(lambda x: f"Rp {x:,.0f}")
                    st.dataframe(df_pjb_ops, hide_index=True, use_container_width=True)
                    csv_pjb_ops = df_pjb_ops.to_csv(index=False).encode('utf-8')
                    st.download_button(label="📥 Export List PJB (CSV)", data=csv_pjb_ops, file_name=f"Rekap_PJB_DanaOps_{nop_admin}.csv", mime='text/csv', use_container_width=True)
                else: st.info("Tidak ada data PJB yang cocok dengan kombinasi filter di atas.")
            else: st.info("⚠️ Data pada sheet 'Rekap PJB' masih kosong atau belum disinkronisasi.")

# ==========================================
# PAGE 5: LIVE MONITORING
# ==========================================
elif st.session_state.page == "📈 Live Monitoring":
    st.markdown("<div class='header-card'><h2>📈 LIVE MONITORING DASHBOARD</h2><p>Sistem Analisa Kas, Daily Pengeluaran, Tracker Satelit, & Anomali BBM</p></div>", unsafe_allow_html=True)
    
    nop_live = st.selectbox("🌐 Pilih Market (NOP):", ["-- Pilih NOP --"] + list(MASTER_DATA.keys()))
    if nop_live != "-- Pilih NOP --":
        data_all = fetch_spreadsheet_data(MASTER_DATA[nop_live]["spreadsheet_id"])
        um_r, rekap_r, pjb_r, req_r, app_r = data_all[SHEET_UM], data_all["Rekap PJB"], data_all[SHEET_PJB], data_all[SHEET_REQUEST], data_all[SHEET_APP]
        
        t1, t2, t3 = st.tabs(["💰 1. Sisa Kas, Daily Graph & Kategori BBM", "🚨 2. Record Anomali & Warning Tim", "🕵️ 3. Evaluasi Kinerja (Track KM/RH)"])
        
        with t1:
            total_um = sum([clean_nominal(r[3]) for r in um_r[1:] if len(r)>3]) if len(um_r)>1 else 0
            tot_serap = sum([clean_nominal(r[15]) for r in rekap_r[1:] if len(r)>15]) if len(rekap_r)>1 else 0
            sisa_kas = total_um - tot_serap
            burn_rate = (tot_serap / total_um * 100) if total_um > 0 else 0
            
            m1, m2, m3 = st.columns(3)
            m1.markdown(f"<div class='metric-3d'><div class='metric-title'>Total Kas Masuk</div><div class='metric-value'>Rp {total_um:,.0f}</div></div>", unsafe_allow_html=True)
            m2.markdown(f"<div class='metric-3d'><div class='metric-title'>Total Penyerapan PJB</div><div class='metric-value'>Rp {tot_serap:,.0f}</div></div>", unsafe_allow_html=True)
            m3.markdown(f"<div class='metric-3d'><div class='metric-title'>Sisa Kas (Burn Rate: {burn_rate:.1f}%)</div><div class='metric-value'>Rp {sisa_kas:,.0f}</div></div>", unsafe_allow_html=True)
            
            if len(pjb_r) > 1:
                df_pjb_all = pd.DataFrame([(r + [""] * 28)[:28] for r in pjb_r[1:]], columns=["Waktu","Tanggal","N","C","Nama","R","S","Keperluan","BBM","D","KMAkhir","Nominal","Pl","u1","u2","u3","u4","u5","u6","u7","NN","NoTiket","Lt","Hs","TKM_RH","u8","u9","BuktiTF"])
                df_pjb_all['Nominal_Clean'] = df_pjb_all['Nominal'].apply(clean_nominal)
                df_pjb_all['Tanggal_PJB'] = pd.to_datetime(df_pjb_all['Tanggal'], format='%d/%m/%Y', errors='coerce')
                df_daily = df_pjb_all.dropna(subset=['Tanggal_PJB']).groupby('Tanggal_PJB')['Nominal_Clean'].sum().reset_index().sort_values('Tanggal_PJB')
                
                if not df_daily.empty:
                    df_daily.columns = ['Tanggal PJB', 'Total Pengeluaran (Rp)_num']
                    st.markdown("#### 📈 Grafik Tren Pengeluaran Harian")
                    st.area_chart(df_daily.set_index('Tanggal PJB')['Total Pengeluaran (Rp)_num'], use_container_width=True)
                    col_d1, col_d2 = st.columns(2)
                    with col_d1:
                        df_daily_tabel = df_daily.copy().sort_values('Tanggal PJB', ascending=False)
                        df_daily_tabel['Tanggal PJB'] = df_daily_tabel['Tanggal PJB'].dt.strftime('%d/%m/%Y')
                        df_daily_tabel['Total Pengeluaran (Rp)'] = df_daily_tabel['Total Pengeluaran (Rp)_num'].apply(lambda x: f"Rp {x:,.0f}")
                        st.dataframe(df_daily_tabel[['Tanggal PJB', 'Total Pengeluaran (Rp)']], hide_index=True, use_container_width=True)
                    with col_d2:
                        df_cat = df_pjb_all.groupby('BBM')['Nominal_Clean'].sum().reset_index().sort_values('Nominal_Clean', ascending=False)
                        if not df_cat.empty:
                            df_cat.columns = ['Jenis BBM / Kategori', 'Total Nominal (Rp)']
                            df_cat['Total Nominal (Rp)'] = df_cat['Total Nominal (Rp)'].apply(lambda x: f"Rp {x:,.0f}")
                            st.dataframe(df_cat, hide_index=True, use_container_width=True)
            else: st.info("Belum ada data PJB untuk direkap.")
        
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
                            
                        if is_boros: warning_list.append({"Nama Tim": nama_petugas, "Tiket": no_tiket, "Nominal PJB": f"Rp {nominal_pjb_val:,.0f}", "Kategori": kategori_bbm, "Total Jarak/RH": f"{total_km:.2f}", "Liter": liter_val, "Status Warning": ket_status})
                        
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

                        if not is_genset:
                            if angka_satelit > 0: status_jarak = "🟢 Aman & Wajar" if total_input_tim > angka_satelit else "🟢 Aman"
                            else: status_jarak = "⚪ Data Satelit Kosong"
                        else: status_jarak = "⏱️ (RH Genset)"

                        eval_list.append({"Nama Tim": req_match[5], "Tiket": no_tiket, "Nominal PJB": f"Rp {nominal_pjb_val:,.0f}", "Kategori": kategori, "KM/RH Awal": km_awal, "KM/RH Akhir": km_akhir, "Total Jarak": f"{total_input_tim:.2f}", "Jarak Satelit": f"{angka_satelit}" if not is_genset and angka_satelit > 0 else "-", "Status Jarak": status_jarak, "Rasio Aktual": analisa_bbm, "Status Konsumsi": status_bbm})
            
            if eval_list:
                def highlight_markup(s): return ['background-color: #FEE2E2; color: #DC2626; font-weight: bold' if '🔴' in str(v) else '' for v in s]
                st.dataframe(pd.DataFrame(eval_list).style.apply(highlight_markup, subset=['Status Jarak', 'Status Konsumsi']), hide_index=True, use_container_width=True)
            else: st.info("Belum ada data realisasi PJB yang dapat disandingkan dengan Satelit.")

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
        
        tab_report1, tab_report2 = st.tabs(["📑 1. Auto PJB (Generator Teks & Foto Laporan)", "📊 2. Rekap Keseluruhan (Request vs PJB)"])
        
        with tab_report1:
            if len(rekap_r) > 1 and len(pjb_r) > 1:
                dict_photos = {}
                for r in reversed(pjb_r[1:]):
                    if len(r) > 21:
                        tk = str(r[21]).strip().upper()
                        if tk and tk not in dict_photos:
                            dict_photos[tk] = {
                                "N (Evidance Pengisian)": r[13] if len(r)>13 else "",
                                "O (Nota BBM)": r[14] if len(r)>14 else "",
                                "P (Foto KM/RH)": r[15] if len(r)>15 else "",
                                "Q (Foto Material)": r[16] if len(r)>16 else "",
                                "R (Nota Material)": r[17] if len(r)>17 else "",
                                "S (Nota Penginapan)": r[18] if len(r)>18 else "",
                                "T (Evidance Pekerjaan)": r[19] if len(r)>19 else ""
                            }
                
                list_periode = sorted(list(set([r[16].strip() for r in rekap_r[1:] if len(r) > 16 and r[16].strip() != ""])))
                list_role = sorted(list(set([r[6].strip() for r in rekap_r[1:] if len(r) > 6 and r[6].strip() != ""])))
                
                st.markdown("<div class='section-title'>🔍 Parameter Filter Laporan</div>", unsafe_allow_html=True)
                col_f1, col_f2 = st.columns(2)
                with col_f1: filter_periode = st.selectbox("📅 Periode Dana Ops (Dari Kolom Q Rekap):", ["Semua Periode"] + list_periode)
                with col_f2: filter_role = st.multiselect("💼 Role Pekerjaan (Pilih Banyak):", list_role, default=list_role)

                st.markdown("<div class='section-title'>📸 Pilih Lampiran Foto (Multi-Select)</div>", unsafe_allow_html=True)
                pilihan_foto = st.multiselect(
                    "Pilih kolom foto yang ingin ditarik dari Form PJB:",
                    ["N (Evidance Pengisian)", "O (Nota BBM)", "P (Foto KM/RH)", "Q (Foto Material)", "R (Nota Material)", "S (Nota Penginapan)", "T (Evidance Pekerjaan)"],
                    default=["O (Nota BBM)", "T (Evidance Pekerjaan)"]
                )
                
                if st.button("🚀 Generate Laporan & PDF", type="primary", use_container_width=True):
                    html_content = ""
                    count_match = 0
                    
                    for idx, row in enumerate(rekap_r[1:]):
                        row_periode = row[16].strip() if len(row) > 16 else ""
                        row_role = row[6].strip() if len(row) > 6 else ""
                        
                        pass_periode = (filter_periode == "Semua Periode") or (row_periode == filter_periode)
                        pass_role = (len(filter_role) == 0) or (row_role in filter_role)
                        
                        if pass_periode and pass_role:
                            found_tiket = None
                            for cell in row:
                                if str(cell).strip().upper() in dict_photos:
                                    found_tiket = str(cell).strip().upper(); break
                            
                            if found_tiket:
                                count_match += 1
                                html_content += f"""
                                <div class='ticket-card'>
                                    <div class='ticket-header'>🎫 TIKET: {found_tiket}</div>
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
                                        url_foto = dict_photos[found_tiket].get(p_name, "")
                                        if url_foto and url_foto.startswith("http"):
                                            html_content += f"<div class='photo-box'><img src='{url_foto}'><br>{p_name}</div>"
                                        else:
                                            html_content += f"<div class='photo-box'><br><br>🚫 Tidak Ada<br>{p_name}</div>"
                                            
                                html_content += "</div></div>"
                    
                    if count_match > 0:
                        full_html = f"""
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <meta charset="UTF-8">
                            <title>Laporan Auto PJB - {nop_report}</title>
                            <style>
                                body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #333; margin: 0; padding: 20px; }}
                                h1 {{ text-align: center; color: #0F2027; border-bottom: 2px solid #00F2FE; padding-bottom: 10px; }}
                                .ticket-card {{ border: 1px solid #ddd; border-left: 5px solid #00F2FE; border-radius: 8px; padding: 15px; margin-bottom: 25px; page-break-inside: avoid; }}
                                .ticket-header {{ background-color: #f8fafc; padding: 10px; border-radius: 5px; margin-bottom: 10px; font-weight: bold; font-size: 1.1em; }}
                                table {{ width: 100%; border-collapse: collapse; margin-bottom: 15px; font-size: 0.9em; }}
                                td {{ padding: 5px; border-bottom: 1px solid #f1f5f9; }}
                                .photo-container {{ display: flex; flex-wrap: wrap; gap: 15px; justify-content: flex-start; }}
                                .photo-box {{ width: 220px; text-align: center; font-size: 0.85em; color: #64748b; border: 1px solid #e2e8f0; border-radius: 5px; padding: 5px; }}
                                .photo-box img {{ max-width: 100%; max-height: 220px; object-fit: contain; border-radius: 4px; display:block; margin:0 auto 5px auto; }}
                                @media print {{ body {{ padding: 0; }} .ticket-card {{ margin-bottom: 20px; box-shadow: none; }} }}
                            </style>
                        </head>
                        <body>
                            <h1>Laporan Lumpsum & PJB - {nop_report}</h1>
                            <p style="text-align:center; color:#64748b; font-size:0.9em; margin-bottom:30px;">Filter Periode: {filter_periode} | Total: {count_match} Tiket</p>
                            {html_content}
                            <script> window.onload = function() {{ window.print(); }} </script>
                        </body>
                        </html>
                        """
                        
                        st.success(f"✅ Berhasil merangkum **{count_match}** tiket. Silakan klik tombol di bawah untuk Download File dan Print (Save as PDF).")
                        b64_html = base64.b64encode(full_html.encode("utf-8")).decode()
                        
                        st.markdown(f"""
                            <a href="data:text/html;base64,{b64_html}" download="Laporan_PJB_{nop_report}.html" 
                            style="display: block; text-align: center; background-color: #0ea5e9; color: white; padding: 15px 20px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 1.1em;">
                            📥 Download Laporan (Buka file lalu Save as PDF)
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
                        pjb_map[tk] = {"Tgl PJB": r[1] if len(r)>1 else "", "Nominal PJB": clean_nominal(r[11]) if len(r)>11 else 0}
                
                rekap_all = []
                for r in req_r[1:]:
                    if len(r) > 5 and str(r[3]).strip() != "":
                        tk = str(r[3]).strip().upper()
                        nom_req = clean_nominal(r[9]) if len(r)>9 else 0
                        has_pjb = tk in pjb_map
                        nom_pjb = pjb_map[tk]["Nominal PJB"] if has_pjb else 0
                        selisih = nom_req - nom_pjb
                        
                        rekap_all.append({
                            "No Tiket": tk, "Tgl Request": r[1] if len(r)>1 else "", "Nama": r[5] if len(r)>5 else "", "Role Jabatan": r[6] if len(r)>6 else "",
                            "Keperluan": r[8] if len(r)>8 else "", "Nominal Request": nom_req, "Status Laporan": "✅ Selesai PJB" if has_pjb else "⏳ Menunggu PJB",
                            "Tgl PJB": pjb_map[tk]["Tgl PJB"] if has_pjb else "-", "Nominal PJB": nom_pjb, "Selisih (Req - PJB)": selisih
                        })
                
                if rekap_all:
                    df_rekap_all = pd.DataFrame(rekap_all)
                    df_view = df_rekap_all.copy()
                    df_view['Nominal Request'] = df_view['Nominal Request'].apply(lambda x: f"Rp {x:,.0f}")
                    df_view['Nominal PJB'] = df_view['Nominal PJB'].apply(lambda x: f"Rp {x:,.0f}" if x > 0 else "-")
                    df_view['Selisih (Req - PJB)'] = df_view['Selisih (Req - PJB)'].apply(lambda x: f"Rp {x:,.0f}")
                    
                    def highlight_status(val):
                        color = '#10B981' if '✅' in str(val) else '#F59E0B'
                        return f'color: {color}; font-weight: bold;'
                        
                    st.dataframe(df_view.style.map(highlight_status, subset=['Status Laporan']), hide_index=True, use_container_width=True)
                    csv_rekap = df_rekap_all.to_csv(index=False).encode('utf-8')
                    st.download_button(label="📥 Export Tabel Rekap ke CSV/Excel", data=csv_rekap, file_name=f"Rekap_All_Data_{nop_report}.csv", mime='text/csv', use_container_width=True)
                else: st.info("Tidak ada data Request Dana.")
            else: st.info("⚠️ Data Sheet 'Request Dana' masih kosong.")

# ==========================================
# PAGE 7: MONITORING REQUEST & PJB
# ==========================================
elif st.session_state.page == "👀 Request & PJB Monitoring":
    st.markdown("<div class='header-card'><h2>📋 REQ & PJB MONITORING</h2><p>Pantau Aktivitas Tim Daily, Warning Tiket Gantung & Cek Sisa Dana</p></div>", unsafe_allow_html=True)
    
    nop_mon = st.selectbox("🌐 Pilih Wilayah Database (NOP):", ["-- Pilih NOP --"] + list(MASTER_DATA.keys()))
    if nop_mon != "-- Pilih NOP --":
        with st.spinner("Menarik data langsung dari server..."):
            data_all = fetch_spreadsheet_data(MASTER_DATA[nop_mon]["spreadsheet_id"])
            req_r, pjb_r = data_all[SHEET_REQUEST], data_all[SHEET_PJB]
        
        tab_daily, tab_warning = st.tabs(["📅 1. Daily Realtime (Hari Ini)", "⚠️ 2. Warning List (Gantung & Sisa Dana)"])
        
        with tab_daily:
            st.info("💡 **INFO:** Tab ini menampilkan siapa saja yang hari ini meminta dana, dan siapa saja yang menyetor PJB (beserta nilai dan jaraknya).")
            col_d1, col_d2 = st.columns([1, 3])
            with col_d1: filter_date = st.date_input("Pilih Tanggal Pantau", datetime.now().date())
            filter_date_str = filter_date.strftime("%d/%m/%Y")
            
            st.markdown(f"#### 💸 Request Dana Masuk ({filter_date_str})")
            daily_req, tot_req_daily = [], 0
            for r in req_r[1:]:
                if len(r) > 13 and str(r[1]).strip() == filter_date_str:
                    nom = clean_nominal(r[9])
                    tot_req_daily += nom
                    daily_req.append({
                        "Waktu": r[0], "Nama": r[5], "Tiket": r[3], "Role": r[6],
                        "Keperluan": r[8], "Kategori": r[10], "Jarak/Info": r[13], "Nominal Request": nom
                    })
            
            if daily_req:
                df_dreq = pd.DataFrame(daily_req)
                df_dreq["Nominal Request"] = df_dreq["Nominal Request"].apply(lambda x: f"Rp {x:,.0f}")
                st.dataframe(df_dreq, hide_index=True, use_container_width=True)
                st.markdown(f"<div style='text-align:right; font-size:1.2em; color:#0ea5e9; font-weight:bold;'>Total Request: Rp {tot_req_daily:,.0f}</div>", unsafe_allow_html=True)
            else: st.success("Belum ada request dana hari ini.")
            
            st.markdown("<hr>", unsafe_allow_html=True)
            
            st.markdown(f"#### ✅ PJB Disubmit ({filter_date_str})")
            daily_pjb, tot_pjb_daily = [], 0
            for r in pjb_r[1:]:
                if len(r) > 24 and str(r[1]).strip() == filter_date_str:
                    nom = clean_nominal(r[11])
                    tot_pjb_daily += nom
                    daily_pjb.append({
                        "Waktu Submit": r[0], "Nama": r[4], "Tiket": r[21], "Role": r[5],
                        "Kategori": r[8], "Jarak Tempuh": f"{r[24]} KM", "Nominal PJB": nom
                    })
            
            if daily_pjb:
                df_dpjb = pd.DataFrame(daily_pjb)
                df_dpjb["Nominal PJB"] = df_dpjb["Nominal PJB"].apply(lambda x: f"Rp {x:,.0f}")
                st.dataframe(df_dpjb, hide_index=True, use_container_width=True)
                st.markdown(f"<div style='text-align:right; font-size:1.2em; color:#10B981; font-weight:bold;'>Total PJB: Rp {tot_pjb_daily:,.0f}</div>", unsafe_allow_html=True)
            else: st.success("Belum ada PJB yang disubmit hari ini.")
            
        with tab_warning:
            st.markdown("### 🚨 Peringatan Otomatis (Data Sejak Agustus 2026)")
            st.info("Sistem melacak siapa yang belum setor PJB lebih dari 3 hari, dan mencocokkan nilai **Sisa Dana (Request awal vs Laporan PJB)**.")
            
            pjb_dict = {}
            for r in pjb_r[1:]:
                if len(r) > 21 and str(r[21]).strip() != "":
                    tk = str(r[21]).strip().upper()
                    pjb_dict[tk] = clean_nominal(r[11]) if len(r)>11 else 0
                    
            list_gantung, list_sisa = [], []
            today_date = datetime.now().date()
            
            for r in req_r[1:]:
                if len(r) > 9:
                    tgl_req_str = str(r[1]).strip()
                    req_date = parse_date(tgl_req_str)
                    
                    if req_date >= CUTOFF_DATE:
                        tk = str(r[3]).strip().upper()
                        if not tk: continue
                        
                        nama = str(r[5])
                        nom_req = clean_nominal(r[9])
                        
                        if tk not in pjb_dict:
                            aging = (today_date - req_date).days
                            if aging > 3:
                                list_gantung.append({"Tanggal Request": tgl_req_str, "Aging": f"{aging} Hari", "Nama Petugas": nama, "Tiket": tk, "Nominal Request": nom_req})
                        else:
                            nom_pjb = pjb_dict[tk]
                            sisa = nom_req - nom_pjb
                            if sisa > 0:
                                list_sisa.append({"Tanggal Request": tgl_req_str, "Nama Petugas": nama, "Tiket": tk, "Nominal Request": nom_req, "Nominal PJB": nom_pjb, "Sisa Belum Lapor": sisa})
                                
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
                    df_sisa["Nominal PJB"] = df_sisa["Nominal PJB"].apply(lambda x: f"Rp {x:,.0f}")
                    df_sisa["Sisa Belum Lapor"] = df_sisa["Sisa Belum Lapor"].apply(lambda x: f"Rp {x:,.0f}")
                    st.dataframe(df_sisa, hide_index=True, use_container_width=True)
                else: st.success("Aman! Semua tiket yang sudah di-PJB nominalnya sesuai (Tidak ada sisa/kekurangan).")
