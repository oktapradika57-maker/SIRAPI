import streamlit as st
import pandas as pd
import requests
import re
import difflib
import altair as alt
import time
from datetime import datetime, timedelta, date

# --- KONFIGURASI HALAMAN (Wajib di baris paling atas) ---
st.set_page_config(layout="wide", page_title="Enterprise Dashboard 348", page_icon="🚀")

# ==========================================
# 🔒 SISTEM LOGIN (PROFESIONAL & CLEAN)
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""

if not st.session_state['logged_in']:
    st.markdown("""
        <style>
            [data-testid="collapsedControl"] { display: none; }
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.markdown("""
        <div style='text-align: center; margin-bottom: 20px;'>
            <h1 style='font-weight: 900; font-size: 42px; color: #0072ff;'>🚀 TASK FORCE 348</h1>
            <p style='color: #666; font-size: 16px; font-weight: 600;'>INTEGRATED MONITORING SYSTEM</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form_pro", clear_on_submit=False):
            st.markdown("### 🔒 Secure Authentication")
            username_input = st.text_input("Username", placeholder="Masukkan Username")
            password_input = st.text_input("Password", type="password", placeholder="••••••••")
            
            # Tombol login agar bisa menggunakan "Enter" di keyboard
            submitted = st.form_submit_button("Access Dashboard", use_container_width=True)
            
            if submitted:
                is_valid_user1 = (username_input == "KinaryaUT" and password_input == "G348T")
                is_valid_user2 = (username_input == "Kut2026" and password_input == "Hit&hup")
                
                if is_valid_user1 or is_valid_user2:
                    st.success("✅ Autentikasi Berhasil! Memuat Dashboard...")
                    time.sleep(1)
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username_input
                    st.rerun()
                else:
                    st.error("🚨 Kredensial tidak valid. Akses ditolak.")
    
    st.stop() 

# ==========================================
# 🚀 KONTEN UTAMA DASHBOARD
# ==========================================
with st.sidebar:
    st.markdown("### 👤 User Profile")
    st.success(f"Log: **{st.session_state['username']}**")
    if st.button("🚪 Logout Securely", use_container_width=True):
        st.session_state['logged_in'] = False
        st.session_state['username'] = ""
        st.rerun()

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; }
    [data-testid="stMetricValue"] { font-size: 28px !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- KREDENSIAL & DATA SOURCE MASTER ---
GOOGLE_SHEET_ID = "1FGKOzWoUrbf3PXN_ahgG1t-83JZT4H4sioQepePbBxM"
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxCQUGt5_Jybed2AwFP4xXFru6GxuMoSwQpUZ63aK9o0WlUFnumOoseRWwgRmxZZ9XYtQ/exec"
SUPABASE_URL = "https://sfyfijndolnwqklqnpmj.supabase.co"
SUPABASE_KEY = "sb_publishable_digs5GILs-TEe4lEpPj4qQ_VRrQ7FCm"
SUPABASE_TABLE_DAPOT = "dapot_data"
SUPABASE_TABLE_INAP = "inap_data"

# --- FUNGSI STANDARISASI ---
def format_site_id(site_id):
    if pd.isna(site_id) or str(site_id).strip() == "": return "-"
    s = str(site_id).strip().upper().replace(" ", "").replace("-", "").replace("_", "")
    match = re.search(r'([A-Z]{2,4})(\d+)', s)
    if match: return f"{match.group(1)}{match.group(2).zfill(3)}"
    return re.sub(r'^K+P', 'KKP', s)

def clean_label_name(name):
    if "Log Rectifier" in name: return "Log Recty"
    return re.sub(r'\s*\(.*?\)\s*', '', str(name)).strip()

def cari_site_terdekat(site_appsheet, list_site_supabase):
    if site_appsheet == "-": return None
    cocok = difflib.get_close_matches(site_appsheet, list_site_supabase, n=1, cutoff=0.6)
    return cocok[0] if cocok else None

def konversi_link_gdrive(url_tunggal):
    if not url_tunggal or str(url_tunggal).strip() == "": return None, None, None, None
    link_bytes = str(url_tunggal).strip()
    file_id = None
    if "id=" in link_bytes:
        id_match = re.search(r'id=([a-zA-Z0-9_-]+)', link_bytes)
        if id_match: file_id = id_match.group(1)
    elif "drive.google.com/file/d/" in link_bytes:
        id_match = re.search(r'/file/d/([a-zA-Z0-9_-]+)', link_bytes)
        if id_match: file_id = id_match.group(1)
            
    if file_id:
        thumb_url = f"https://drive.google.com/thumbnail?id={file_id}&sz=w400"
        zoom_url = f"https://drive.google.com/thumbnail?id={file_id}&sz=w1600"
        dl_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        return thumb_url, zoom_url, dl_url, None
    return link_bytes, link_bytes, link_bytes, None

def dapatkan_nilai_teknis(row, kolom_sheet, kolom_supabase):
    val_sheet = None
    if kolom_sheet in row: val_sheet = row.get(kolom_sheet)
    elif "Type Batter" in kolom_sheet and "Type Battery" in row: val_sheet = row.get("Type Battery")
    elif "Type Batteri.1" in kolom_sheet and "Type Battery 2" in row: val_sheet = row.get("Type Battery 2")
    elif "Type Batteri.1" in kolom_sheet and "Type Battery.1" in row: val_sheet = row.get("Type Battery.1")
        
    if pd.notna(val_sheet) and str(val_sheet).strip() not in ["", "-", "nan", "None"]:
        return str(val_sheet).strip()
    
    val_sup = row.get(f"{kolom_supabase}_dapot") if f"{kolom_supabase}_dapot" in row else row.get(kolom_supabase)
    if pd.notna(val_sup) and str(val_sup).strip() not in ["", "-", "nan", "None"]:
        return str(val_sup).strip()
    
    return "Cek data Utama ⚠️"

def update_tech_specs_gsheet(site_id_asli, dict_specs):
    try:
        payload = {"site_id": str(site_id_asli).strip(), "tech_specs": dict_specs}
        response = requests.post(APPS_SCRIPT_URL, json=payload, timeout=15)
        if response.status_code == 200 and "Sukses" in response.text: return True, "Sukses"
        return False, response.text
    except Exception as e: return False, str(e)

# --- PULL DATA DARI GOOGLE SHEETS & SUPABASE ---
@st.cache_data(ttl=60)
def load_data_from_google_sheets():
    url = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/export?format=csv"
    try: return pd.read_csv(url)
    except: return pd.DataFrame()

@st.cache_data(ttl=60)
def load_backup_data():
    url_backup = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/export?format=csv&gid=445265067"
    try: return pd.read_csv(url_backup)
    except: return pd.DataFrame()

@st.cache_data(ttl=60)
def load_bcp_data():
    # Menggunakan metode query tqx agar lebih stabil menarik Sheet BCP
    url_bcp = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/gviz/tq?tqx=out:csv&sheet=BCP"
    try: return pd.read_csv(url_bcp)
    except: return pd.DataFrame()

@st.cache_data(ttl=600)
def load_data_from_supabase_dapot():
    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE_DAPOT}?select=*&limit=5000"
    headers = { "apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}" }
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200: return pd.DataFrame(res.json())
        return pd.DataFrame()
    except: return pd.DataFrame()

def fetch_inap_for_site(site_clean, site_asli):
    variants = set()
    for s in [site_clean, site_asli]:
        if pd.isna(s) or str(s).strip() in ["", "-", "nan"]: continue
        v = str(s).strip().upper()
        variants.update([v, v.replace(" ", "")])
        match_space = re.search(r'([A-Z]{2,4})[-_ ]*(\d+)', v.replace(" ", ""))
        if match_space:
            letters, digits = match_space.group(1), match_space.group(2)
            padded_digits = digits.zfill(3)
            variants.update([f"{letters}{padded_digits}", f"{letters} {padded_digits}", f"{letters}-{padded_digits}"])
    if not variants: return pd.DataFrame()
    or_filter = ",".join([f"site_id.eq.{v}" for v in variants])
    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE_INAP}"
    headers = { "apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}" }
    params = { "or": f"({or_filter})", "limit": 2000 }
    
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        if res.status_code == 200: return pd.DataFrame(res.json())
    except: pass
    return pd.DataFrame()

# --- PROSES DATA & PENGGABUNGAN ---
df_sheet_main = load_data_from_google_sheets()
df_backup = load_backup_data()
df_bcp = load_bcp_data()
df_sup_dapot = load_data_from_supabase_dapot()

frames = []
if not df_sheet_main.empty: frames.append(df_sheet_main)
if not df_backup.empty: frames.append(df_backup)

if frames:
    df_sheet = pd.concat(frames, ignore_index=True)
else:
    st.error("🚨 Gagal memuat data utama dari Google Sheets! Periksa koneksi Anda.")
    st.stop()

kolom_site_sheet = 'Site' if 'Site' in df_sheet.columns else ([c for c in df_sheet.columns if "site" in c.lower() or "id" in c.lower()] + [df_sheet.columns[0]])[0]
df_sheet['site_clean_sheet'] = df_sheet[kolom_site_sheet].apply(format_site_id)

if not df_sup_dapot.empty:
    df_sup_dapot['site_clean_sup'] = df_sup_dapot['site_id'].apply(format_site_id)
    list_site_sup = df_sup_dapot['site_clean_sup'].dropna().unique().tolist()
    mapping_fuzzy = {site_s: (site_s if site_s in list_site_sup else cari_site_terdekat(site_s, list_site_sup)) for site_s in df_sheet['site_clean_sheet'].unique()}
    df_sheet['matched_site_sup'] = df_sheet['site_clean_sheet'].map(mapping_fuzzy)
    df_merged = pd.merge(df_sheet, df_sup_dapot, left_on='matched_site_sup', right_on='site_clean_sup', how='left', suffixes=('', '_dapot'))
else:
    df_merged = df_sheet.copy()
    df_merged['matched_site_sup'] = None

def susun_nama_dropdown(row):
    s_id = row['site_clean_sheet'] if pd.isna(row.get('matched_site_sup')) or not row['matched_site_sup'] else row['matched_site_sup']
    s_name = row.get('site_name') if pd.notna(row.get('site_name')) else "Belum Terdata di DB"
    return f"[{s_id}] ➔ {s_name}"
    
df_merged['dropdown_label'] = df_merged.apply(susun_nama_dropdown, axis=1)

if 'Timestamp' in df_merged.columns:
    df_merged['parsed_timestamp'] = pd.to_datetime(df_merged['Timestamp'], errors='coerce', dayfirst=True)
    df_merged['date_obj'] = df_merged['parsed_timestamp'].dt.date
else:
    df_merged['date_obj'] = date.today()
    df_merged['parsed_timestamp'] = pd.to_datetime("today")

hari_kemarin = date.today() - timedelta(days=1)


st.title("🚀 TASK FORCE 348 | NOP PALANGKARAYA")
st.caption("GERAKAN G348T - Monitoring & Update Terintegrasi")

# ==========================================
# 📊 1. METRIK UTAMA (348 SITE)
# ==========================================
TOTAL_TARGET = 348

sites_done = len(df_sheet[~df_sheet[kolom_site_sheet].isna()])
sites_remaining = max(TOTAL_TARGET - sites_done, 0)
progress_percent = min(sites_done / TOTAL_TARGET, 1.0)

list_data_implementasi = []

if not df_sheet_main.empty and df_sheet_main.shape[1] > 107:
    for _, row in df_sheet_main.iterrows():
        val = str(row.iloc[107]).strip()
        if val.lower() not in ['', '-', 'nan', 'none', 'null']:
            site_id = format_site_id(str(row.get(kolom_site_sheet, row.iloc[0])).strip())
            list_data_implementasi.append({"Site ID": site_id, "Tindakan Implementasi": val, "Sumber": "Sheet Utama"})

if not df_backup.empty and df_backup.shape[1] > 114:
    kolom_site_backup = df_backup.columns[0]
    for _, row in df_backup.iterrows():
        val = str(row.iloc[114]).strip()
        if val.lower() not in ['', '-', 'nan', 'none', 'null']:
            site_id = format_site_id(str(row.get(kolom_site_backup, row.iloc[0])).strip())
            list_data_implementasi.append({"Site ID": site_id, "Tindakan Implementasi": val, "Sumber": "Sheet Backup"})

df_implementasi = pd.DataFrame(list_data_implementasi)
implementasi_count = len(df_implementasi)
implementasi_percent = min(implementasi_count / TOTAL_TARGET, 1.0) if TOTAL_TARGET > 0 else 0

st.markdown("### 📊 Progress 348 Site")
col_k1, col_k2, col_k3, col_k4 = st.columns(4)
with col_k1:
    with st.container(border=True): st.metric("🎯 Total Target Site", f"{TOTAL_TARGET} Site")
with col_k2:
    with st.container(border=True): st.metric("✅ Selesai Dikerjakan", f"{sites_done} Site", f"{(progress_percent*100):.1f}% Eksekusi")
with col_k3:
    with st.container(border=True): st.metric("🚀 Implementasi", f"{implementasi_count} Site", f"{(implementasi_percent*100):.1f}% Progress")
with col_k4:
    with st.container(border=True): st.metric("⏳ Sisa Target", f"{sites_remaining} Site")

# Progress bar resmi (Native Streamlit)
st.progress(progress_percent, text=f"Status Eksekusi: {sites_done} dari {TOTAL_TARGET} Site (Gabungan List + Backup)")

with st.expander("📋 Klik untuk melihat Rincian Data Site Implementasi"):
    if not df_implementasi.empty: st.dataframe(df_implementasi, hide_index=True, use_container_width=True)
    else: st.info("ℹ️ Belum ada tindakan implementasi yang tercatat.")

st.divider()

# ==========================================
# ⚡ 2. METRIK BCP - QUICK WIN
# ==========================================
TOTAL_QW = 53
qw_done = 0
qw_ongoing = 0
qw_notyet = 0
list_qw_detail = []

if not df_bcp.empty:
    # Memeriksa baris demi baris secara aman
    for idx, row in df_bcp.iterrows():
        # Kolom I=8, J=9, K=10 (Dibungkus Exception Guard)
        try:
            val_i = str(row.iloc[8]).strip() if len(row) > 8 else ""
            val_j = str(row.iloc[9]).strip() if len(row) > 9 else ""
            val_k = str(row.iloc[10]).strip() if len(row) > 10 else ""
        except IndexError:
            continue
        
        val_j_lower = val_j.lower()
        
        # Abaikan jika kolom J murni kosong atau 'nan'
        if val_j_lower in ['nan', 'none', 'null', '']:
            continue
            
        # Hitungan murni berdasarkan teks di dalam Kolom J
        if 'done' in val_j_lower: qw_done += 1
        elif 'on going' in val_j_lower or 'ongoing' in val_j_lower: qw_ongoing += 1
        elif 'not yet' in val_j_lower: qw_notyet += 1
            
        list_qw_detail.append({
            "Kategori Progress (J)": val_j,
            "Program Quick Win (I)": val_i if val_i.lower() not in ['nan', 'none'] else "-",
            "Additional Remark (K)": val_k if val_k.lower() not in ['nan', 'none'] else "-"
        })

df_qw_detail = pd.DataFrame(list_qw_detail)
qw_percent = min(qw_done / TOTAL_QW, 1.0) if TOTAL_QW > 0 else 0

st.markdown("### ⚡ BCP - Quick Win Progress")
col_qw1, col_qw2, col_qw3, col_qw4 = st.columns(4)

with col_qw1:
    with st.container(border=True): st.metric("🎯 Total Quick Win", f"{TOTAL_QW} Program")
with col_qw2:
    with st.container(border=True): st.metric("✅ Status: Done", f"{qw_done} Program", f"{(qw_percent*100):.1f}% Pencapaian")
with col_qw3:
    with st.container(border=True): st.metric("🔄 Status: On Going", f"{qw_ongoing} Program", "Sedang Dikerjakan", delta_color="off")
with col_qw4:
    with st.container(border=True): st.metric("⚠️ Status: Not Yet", f"{qw_notyet} Program", "Belum Ter-Planning", delta_color="inverse")

# Progress bar resmi (Native Streamlit)
st.progress(qw_percent, text=f"Pencapaian Quick Win: {qw_done} Selesai dari {TOTAL_QW} Program BCP")

with st.expander("📋 Klik untuk melihat Rincian Data Quick Win (Kolom I, J, K)"):
    if not df_qw_detail.empty:
        # Pewarnaan Tabel agar mudah dibaca
        def color_progress(val):
            val_lower = str(val).lower()
            if 'done' in val_lower: return 'background-color: #d4edda; color: #155724; font-weight: bold;'
            elif 'on going' in val_lower or 'ongoing' in val_lower: return 'background-color: #cce5ff; color: #004085; font-weight: bold;'
            elif 'not yet' in val_lower: return 'background-color: #f8d7da; color: #721c24; font-weight: bold;'
            return ''
            
        st.dataframe(df_qw_detail.style.map(color_progress, subset=['Kategori Progress (J)']), hide_index=True, use_container_width=True)
    else:
        st.info("ℹ️ Saat ini belum ada data Quick Win yang tercatat. Pastikan Kolom J pada Sheet BCP sudah terisi.")

st.divider()

# ==========================================
# 🎯 3. FILTER & SELEKSI TARGET MONITORING
# ==========================================
st.markdown("### 🔎 Detail Monitoring Site")
with st.container(border=True):
    col_f1, col_f2 = st.columns([1, 2])
    with col_f1:
        pilihan_tanggal = st.date_input("📅 Rentang Waktu:", value=(hari_kemarin - timedelta(days=3), hari_kemarin), format="DD/MM/YYYY")
        if isinstance(pilihan_tanggal, tuple):
            if len(pilihan_tanggal) == 2: start_date, end_date = pilihan_tanggal
            else: start_date = end_date = pilihan_tanggal[0]
        else:
            start_date = end_date = pilihan_tanggal

    df_filtered_view = df_merged[(df_merged['date_obj'] >= start_date) & (df_merged['date_obj'] <= end_date)]

    with col_f2:
        if not df_filtered_view.empty:
            list_dropdown_pilihan = sorted(df_filtered_view['dropdown_label'].unique())
            label_pilihan = st.multiselect("🎯 Pilih Site:", list_dropdown_pilihan, default=list_dropdown_pilihan[:1] if list_dropdown_pilihan else None)
        else:
            st.warning("⚠️ Tidak ada data di rentang waktu ini.")
            label_pilihan = []

if not label_pilihan:
    st.info("💡 Silakan pilih minimal 1 site pada menu di atas untuk menampilkan detail teknis & foto.")
    st.stop()

# ==========================================
# 📑 4. KONTEN DASHBOARD PER-SITE
# ==========================================
df_latest_view = df_filtered_view.sort_values('parsed_timestamp', ascending=False).drop_duplicates('dropdown_label')
tabs = st.tabs(label_pilihan)

for index_tab, site_label in enumerate(label_pilihan):
    with tabs[index_tab]:
        data_site = df_latest_view[df_latest_view['dropdown_label'] == site_label].iloc[0]
        
        raw_timestamp = data_site.get('Timestamp', '-')
        formatted_ts = data_site['parsed_timestamp'].strftime('%d/%m/%Y %H:%M:%S') if pd.notna(data_site.get('parsed_timestamp')) else raw_timestamp
        st.write(f"**🕒 Update Terakhir:** `{formatted_ts}`")
        
        t_id_asli = str(data_site.get(kolom_site_sheet, '')).strip()
        t_id_clean = str(data_site.get('site_clean_sheet', '')).strip()

        c1, c2, c3, c4 = st.columns(4)

        # KARTU 1: MASTER SPECS
        with c1:
            with st.container(border=True):
                st.subheader("📋 Master Specs")
                st.divider()
                st.dataframe(pd.DataFrame({
                    "Parameter": ["Site ID", "Site Name", "Class", "Grid", "Hub", "Phase", "Grounding KWH"],
                    "Value": [
                        data_site.get(kolom_site_sheet, '-'), data_site.get('site_name', '-'),
                        data_site.get('site_class', '-'), data_site.get('grid_category_new', '-'),
                        data_site.get('hub_site', '-'), data_site.get('Phase PLN', '-'),
                        data_site.get('Grounding KWH', '-')
                    ]
                }), hide_index=True, use_container_width=True) 

        # KARTU 2: TECHNICAL SPECS
        with c2:
            with st.container(border=True):
                st.subheader("⚙️ Technical Specs")
                st.divider()
                tech_mapping = [
                    ("Main Power", "Main Power", "Power Type"), ("Daya PLN", "Daya PLN", "Capacity"), 
                    ("Kapasitas MCB", "Kapasitas MCB", "Kapasitas MCB"), ("Tegangan R - N", "Tegangan PLN (R-N)", "Tegangan PLN (R-N)"), 
                    ("Tegangan S - N", "Tegangan PLN (S-N)", "Tegangan PLN (S-N)"), ("Tegangan T - N", "Tegangan PLN (T-N)", "Tegangan PLN (T-N)"),
                    ("Arus R", "Beban PLN (R)", "Beban PLN (R)"), ("Arus S", "Beban PLN (S)", "Beban PLN (S)"), 
                    ("Arus T", "Beban PLN (T)", "Beban PLN (T)"), ("Type recti 1", "Type Rectifier", "Type Rectifier"), 
                    ("Jumlah Module 1", "Jumlah Module", "Jumlah Module"), ("Type batt 1", "Type Batteri", "Type Battery"),        
                    ("Jumlah batt 1", "Jumlah Battery", "Jumlah Battery"), ("DC Voltage 1", "DC Voltage", "DC Voltage"), 
                    ("Load Current 1", "Rectifier Current", "Rectifier Current"), ("Type recti 2", "Type Rectifier 2", "Type Rectifier 2"), 
                    ("Jumlah Module 2", "Jumlah Module 2", "Jumlah Module 2"), ("Type batt 2", "Type Batteri.1", "Type Battery 2"),    
                    ("Jumlah batt 2", "Jumlah Battery 2", "Jumlah Battery 2"), ("Load current recti 2", "Load current recti 2", "Load current recti 2")
                ]
                tech_rows = [{"Parameter": l, "Value": dapatkan_nilai_teknis(data_site, cs, csb)} for l, cs, csb in tech_mapping]
                
                edited_df = st.data_editor(pd.DataFrame(tech_rows), hide_index=True, use_container_width=True, disabled=["Parameter"], key=f"tech_editor_{t_id_clean}_{index_tab}")
                
                if st.button("💾 Push Spek Teknis", use_container_width=True, key=f"btn_tech_{t_id_clean}_{index_tab}"):
                    payload_specs = {}
                    for _, row in edited_df.iterrows():
                        real_col = next((m[1] for m in tech_mapping if m[0] == row["Parameter"]), None)
                        if real_col: payload_specs[real_col.replace(".1", "")] = row["Value"]
                    
                    with st.spinner("Pushing to GSheet..."):
                        s_ok, msg = update_tech_specs_gsheet(t_id_asli, payload_specs)
                        if s_ok:
                            st.success("Berhasil Update!"); st.cache_data.clear(); st.rerun()
                        else: st.error(f"Gagal API: {msg}")

        # KARTU 3: FIELD FINDINGS & TREND
        with c3:
            with st.container(border=True):
                st.subheader("🔍 Field Findings")
                st.divider()
                st.markdown(f"""
                - **Arus Recty:** `{data_site.get('Rectifier Current', '-')} A`
                - **Modul / Faulty:** `{data_site.get('Jumlah Module', '-')} / {data_site.get('Total Module faulty', '-')}`
                - **BBT >4 Jam:** `{data_site.get('BBT >4 Jam', '-')}`
                - **Enva Validasi:** `{data_site.get('Enva Validasi', '-')}`
                - **Kondisi LPU:** `{data_site.get('Kondisi Modul Enva LPU', '-')}`
                - **Arrester:** `{data_site.get('Arrester Rectifier', '-')}`
                """)
                st.divider()
                
                st.markdown("**📈 Daily Availability Trend**")
                df_trend = fetch_inap_for_site(t_id_clean, t_id_asli)
                if not df_trend.empty:
                    col_date = next((c for c in df_trend.columns if any(k in str(c).lower() for k in ['period', 'periode', 'date', 'waktu', 'tgl', 'tanggal', 'time'])), None)
                    col_avail = next((c for c in df_trend.columns if 'avail' in str(c).lower() and 'power' not in str(c).lower()), None)
                    if col_date and col_avail:
                        chart_data = df_trend[[col_date, col_avail]].copy()
                        chart_data[col_date] = pd.to_datetime(chart_data[col_date], errors='coerce')
                        chart_data[col_avail] = pd.to_numeric(chart_data[col_avail].astype(str).str.replace('%', '').str.replace(',', '.'), errors='coerce')
                        chart_data = chart_data.dropna().sort_values(by=col_date)
                        
                        site_class = str(data_site.get('site_class', '')).upper().strip()
                        target_val = 99.6 if 'DIAMOND' in site_class else 99.2 if 'PLATINUM' in site_class else 99.0 if 'GOLD' in site_class else 97.0 if 'SILVER' in site_class else 95.0
                        chart_data['Target'] = target_val
                        
                        base = alt.Chart(chart_data.reset_index(drop=True)).encode(x=alt.X(f'{col_date}:T', axis=alt.Axis(format='%d/%m', title=None)))
                        line_avail = base.mark_area(line={'color': '#0072ff', 'strokeWidth': 3}, color=alt.Gradient(gradient='linear', stops=[alt.GradientStop(color='#00c6ff', offset=0), alt.GradientStop(color='rgba(0,0,0,0)', offset=1)], x1=1, x2=1, y1=1, y2=0), interpolate='monotone').encode(y=alt.Y(f'{col_avail}:Q', scale=alt.Scale(zero=False), title='Avail (%)'), tooltip=[f'{col_date}:T', f'{col_avail}:Q'])
                        line_target = base.mark_line(color='#ff5252', strokeDash=[5, 5]).encode(y=alt.Y('Target:Q'))
                        st.altair_chart(alt.layer(line_avail, line_target).properties(height=200), use_container_width=True)
                else: st.caption("Belum ada data history Inap.")

        # KARTU 4: ACTION PLAN (Read-Only)
        with c4:
            with st.container(border=True):
                st.subheader("📝 Action Plan")
                st.divider()
                
                kolom_finding = next((c for c in df_sheet.columns if "hasil" in str(c).lower() and "analis" in str(c).lower()), None)
                finding_raw = str(data_site.get(kolom_finding, '')) if kolom_finding and pd.notna(data_site.get(kolom_finding)) else ""
                finding_val = finding_raw if finding_raw.strip() not in ['', 'nan', 'None'] else "Belum ada hasil analisa."
                st.markdown("**🔍 Hasil Analisa:**")
                st.info(finding_val)
                
                kolom_reko = next((c for c in df_sheet.columns if "rekomendasi" in str(c).lower()), 'Rekomendasi Perbaikan')
                reko_raw = str(data_site.get(kolom_reko, '')) if pd.notna(data_site.get(kolom_reko)) else ""
                reko_val = reko_raw if reko_raw.strip() not in ['', 'nan', 'None'] else "Belum ada rekomendasi tindakan."
                st.markdown("**💡 Rekomendasi Tindakan:**")
                st.success(reko_val)
                st.caption("*(Catatan: Input/Edit Action Plan dilakukan secara manual langsung melalui Google Sheets)*")

        # EVIDENCE & DOKUMENTASI
        all_photos, all_csvs, seen_urls = [], [], set()
        for col_name in df_sheet.columns:
            val = data_site.get(col_name)
            if pd.isna(val) or not val: continue
            urls = re.findall(r'(https?://[^\s,"\'\}]+)', str(val))
            for idx, url in enumerate(urls):
                if url in seen_urls: continue
                seen_urls.add(url)
                
                is_csv = any(k in url.lower() or k in col_name.lower() for k in ["csv", ".xlsx", "data"])
                thumb_url, zoom_url, dl_url, embed_url = konversi_link_gdrive(url)
                label = f"{clean_label_name(col_name)} #{idx+1}" if len(urls) > 1 else clean_label_name(col_name)
                
                if thumb_url and not is_csv: all_photos.append({'label': label, 'thumb': zoom_url, 'dl_url': dl_url})
                elif is_csv: all_csvs.append({'label': label, 'url': dl_url if dl_url else url})

        if all_photos or all_csvs:
            with st.container(border=True):
                st.subheader("📁 Evidence & Dokumentasi Lapangan")
                st.divider()
                
                if all_csvs:
                    st.write("**File Data:**")
                    csv_cols = st.columns(len(all_csvs))
                    for i, f in enumerate(all_csvs):
                        with csv_cols[i]: st.link_button(f"📥 Unduh {f['label']}", f['url'], use_container_width=True)
                    st.write("---")

                if all_photos:
                    st.write("**Foto Dokumentasi:**")
                    cols_per_row = 5
                    chunks = [all_photos[i:i + cols_per_row] for i in range(0, len(all_photos), cols_per_row)]
                    for chunk in chunks:
                        img_cols = st.columns(len(chunk))
                        for i, p in enumerate(chunk):
                            with img_cols[i]:
                                try:
                                    st.image(str(p["thumb"]), caption=str(p["label"]), use_container_width=True)
                                except Exception:
                                    st.warning(f"⚠️ Gambar tidak valid: {p['label']}")
                                st.link_button("Unduh 📥", str(p["dl_url"]), use_container_width=True)
        else:
            st.info("ℹ️ Belum ada lampiran foto dokumentasi atau file yang tersedia untuk site ini.")

st.markdown("<br><hr><center><b>✨ © 2026 | TASK FORCE 348 ✨</b></center>", unsafe_allow_html=True)
