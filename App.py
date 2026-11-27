import streamlit as st
import random
import pandas as pd
import gspread
import base64
import cloudinary
import cloudinary.uploader
import requests
import math
import os
import tempfile
import gc
from urllib.parse import quote
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import time
import re
from collections import defaultdict
from PIL import Image, ExifTags
import io
import numpy as np

try:
    import cv2
except Exception:
    cv2 = None

try:
    import pytesseract
except Exception:
    pytesseract = None

# ==========================================
# 0. KONFIGURASI HALAMAN (WAJIB BARIS PERTAMA!)
# ==========================================
st.set_page_config(page_title="SiRAPI NOP PLK & PBU Dashboard", page_icon="🦺", layout="wide", initial_sidebar_state="collapsed")

# =================================================================
# 🎨 TEMA TAMPILAN SiRAPI (bersih, satu warna aksen, minim gangguan)
# =================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    :root {
        --canvas: #F4F7FE;
        --surface: #FFFFFF;
        --line: #D5DBE5;
        --line-soft: #E6EAF1;
        --ink: #0F172A;
        --muted: #566275;
        --brand: #0A5BD3;
        --brand-dark: #084BB0;
        --brand-soft: #EAF2FF;
        --plk: #0A5BD3;
        --pbu: #D92D3A;
        --r-ctl: 8px;
        --r-card: 12px;
        color-scheme: light;
    }

    /* 1. Sembunyikan menu bar atas, toolbar, footer */
    #MainMenu, footer, header,
    header[data-testid="stHeader"], div[data-testid="stHeader"],
    div[data-testid="stToolbar"], div[data-testid="stDecoration"],
    div[data-testid="stStatusWidget"], [data-testid="collapsedControl"],
    [data-testid="stHeaderActionElements"] {
        visibility: hidden !important; display: none !important;
        height: 0 !important; width: 0 !important; margin: 0 !important; padding: 0 !important;
    }

    /* 2. Kanvas & font */
    html, body, .stApp, .main {
        background-color: var(--canvas) !important;
        color: var(--ink) !important;
        font-family: 'Plus Jakarta Sans', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif !important;
        color-scheme: light;
    }
    .main .block-container {
        padding-top: 0 !important; padding-bottom: 3rem !important;
        max-width: 1180px !important; margin: 0 auto !important;
    }
    hr { margin: 26px 0 !important; border: 0 !important; border-top: 1px solid var(--line) !important; }

    /* 3. Teks selalu gelap & terbaca (aman walau HP memakai mode gelap) */
    p, label, h1, h2, h3, h4, h5, h6, li,
    div[data-testid="stMarkdownContainer"] p, div[data-testid="stMarkdownContainer"] li,
    div[data-testid="stWidgetLabel"] p, div[data-testid="stWidgetLabel"] label, div[data-testid="stWidgetLabel"] span,
    div[data-testid="stCheckbox"] label span, div[data-testid="stCheckbox"] p,
    div[role="radiogroup"] label p, div[role="radiogroup"] label span { color: var(--ink) !important; }
    div[data-testid="stWidgetLabel"] p, div[data-testid="stWidgetLabel"] label {
        font-weight: 600 !important; font-size: 0.88rem !important;
    }

    /* 4. Kolom isian */
    div[data-baseweb="input"], div[data-baseweb="textarea"],
    div[data-baseweb="base-input"]:not(div[data-baseweb="input"] *):not(div[data-baseweb="textarea"] *) {
        background-color: var(--surface) !important;
        border: 1px solid var(--line) !important;
        border-radius: var(--r-ctl) !important;
        box-shadow: none !important;
    }
    div[data-baseweb="input"] div[data-baseweb="base-input"],
    div[data-baseweb="textarea"] div[data-baseweb="base-input"] {
        background: transparent !important; border: 0 !important; box-shadow: none !important;
    }
    div[data-baseweb="input"]:focus-within, div[data-baseweb="textarea"]:focus-within,
    div[data-baseweb="select"] > div:focus-within {
        border-color: var(--brand) !important; box-shadow: 0 0 0 3px rgba(10, 91, 211, 0.16) !important;
    }
    div[data-baseweb="input"] input, div[data-baseweb="base-input"] input,
    div[data-baseweb="textarea"] textarea, .stTextInput input, .stNumberInput input,
    .stDateInput input, .stTextArea textarea {
        background-color: transparent !important;
        color: var(--ink) !important; -webkit-text-fill-color: var(--ink) !important;
        caret-color: var(--ink) !important;
        font-weight: 500 !important; font-size: 0.95rem !important;
        font-variant-numeric: tabular-nums;
        padding: 10px 14px !important;
    }
    input:disabled, textarea:disabled {
        background-color: #EEF1F6 !important; color: var(--ink) !important;
        -webkit-text-fill-color: var(--ink) !important; opacity: 1 !important; font-weight: 600 !important;
    }
    input::placeholder, textarea::placeholder {
        color: #6B7686 !important; -webkit-text-fill-color: #6B7686 !important; opacity: 1 !important;
    }
    div[data-testid="stNumberInput"] button, div[data-baseweb="input"] button {
        background-color: #F5F7FA !important; color: var(--ink) !important;
    }
    div[data-testid="stNumberInput"] button svg, div[data-baseweb="input"] button svg {
        fill: var(--ink) !important; color: var(--ink) !important;
    }

    /* 5. Dropdown & multiselect */
    div[data-baseweb="select"] > div {
        background-color: var(--surface) !important;
        border: 1px solid var(--line) !important;
        border-radius: var(--r-ctl) !important;
        min-height: 44px !important;
    }
    div[data-baseweb="select"] span, div[data-baseweb="select"] div, div[data-baseweb="select"] input {
        color: var(--ink) !important; -webkit-text-fill-color: var(--ink) !important; font-weight: 500 !important;
    }
    div[data-baseweb="select"] svg { fill: var(--muted) !important; color: var(--muted) !important; }
    span[data-baseweb="tag"] {
        background-color: var(--brand-soft) !important; border: 1px solid #BFD6FA !important; border-radius: 6px !important;
    }
    span[data-baseweb="tag"] span {
        color: var(--brand-dark) !important; -webkit-text-fill-color: var(--brand-dark) !important; font-weight: 600 !important;
    }
    div[data-baseweb="popover"], div[data-baseweb="popover"] > div, div[data-baseweb="menu"],
    ul[role="listbox"], li[role="option"] { background-color: var(--surface) !important; color: var(--ink) !important; }
    li[role="option"] span, li[role="option"] div { color: var(--ink) !important; font-weight: 500 !important; }
    li[role="option"]:hover, li[role="option"][aria-selected="true"] { background-color: var(--brand-soft) !important; }

    /* 6. Tombol: satu aksen. Utama = biru penuh, sekunder = garis. Tanpa efek naik-turun. */
    div[data-testid="stButton"] > button, div[data-testid="stFormSubmitButton"] > button,
    div[data-testid="stDownloadButton"] > button {
        border-radius: var(--r-ctl) !important; min-height: 46px !important; padding: 10px 16px !important;
        width: 100% !important; box-shadow: none !important; transform: none !important;
        transition: background-color .12s ease, border-color .12s ease !important;
    }
    div[data-testid="stButton"] > button *, div[data-testid="stFormSubmitButton"] > button *,
    div[data-testid="stDownloadButton"] > button * {
        font-weight: 600 !important; font-size: 0.92rem !important; letter-spacing: 0 !important;
    }
    div[data-testid="stButton"] > button[kind="primary"], div[data-testid="stFormSubmitButton"] > button {
        background: var(--brand) !important; border: 1px solid var(--brand) !important; color: #FFFFFF !important;
    }
    div[data-testid="stButton"] > button[kind="primary"] *, div[data-testid="stFormSubmitButton"] > button * {
        color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important;
    }
    div[data-testid="stButton"] > button[kind="primary"]:hover, div[data-testid="stFormSubmitButton"] > button:hover {
        background: var(--brand-dark) !important; border-color: var(--brand-dark) !important;
    }
    div[data-testid="stButton"] > button[kind="secondary"] {
        background: var(--surface) !important; border: 1px solid var(--brand) !important; color: var(--brand) !important;
    }
    div[data-testid="stButton"] > button[kind="secondary"] * {
        color: var(--brand) !important; -webkit-text-fill-color: var(--brand) !important;
    }
    div[data-testid="stButton"] > button[kind="secondary"]:hover { background: var(--brand-soft) !important; }
    div[data-testid="stButton"] > button:disabled, div[data-testid="stFormSubmitButton"] > button:disabled {
        background: #E9EDF3 !important; border: 1px solid var(--line) !important; color: #7A8494 !important;
    }
    div[data-testid="stButton"] > button:disabled *, div[data-testid="stFormSubmitButton"] > button:disabled * {
        color: #7A8494 !important; -webkit-text-fill-color: #7A8494 !important;
    }
    div[data-testid="stDownloadButton"] > button {
        background: #0F8F63 !important; border: 1px solid #0F8F63 !important;
    }
    div[data-testid="stDownloadButton"] > button * { color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important; }
    div[data-testid="stDownloadButton"] > button:hover { background: #0B7551 !important; }

    /* Tombol berbentuk tautan (WhatsApp, SiDATA). Kelas lama tetap dipakai di banyak halaman. */
    .btn-sidata-blue, .btn-sidata-red {
        display: block; width: 100%; text-align: center; color: #FFFFFF !important;
        padding: 13px 18px; border-radius: var(--r-ctl); font-weight: 600; font-size: 0.92rem;
        text-decoration: none !important; margin-top: 6px; box-sizing: border-box;
        transition: background-color .12s ease;
    }
    .btn-sidata-blue { background: var(--brand); }
    .btn-sidata-blue:hover { background: var(--brand-dark); }
    .btn-sidata-red { background: var(--pbu); }
    .btn-sidata-red:hover { background: #B8232F; }

    /* 7. Upload, expander, tab */
    section[data-testid="stFileUploaderDropzone"] {
        background-color: var(--surface) !important; border: 1.5px dashed #A9B4C4 !important; border-radius: 10px !important;
    }
    section[data-testid="stFileUploaderDropzone"] * { color: var(--ink) !important; }
    section[data-testid="stFileUploaderDropzone"] button {
        background-color: #F5F7FA !important; border: 1px solid var(--line) !important; color: var(--ink) !important;
    }
    div[data-testid="stExpander"] {
        background-color: var(--surface) !important; border: 1px solid var(--line) !important;
        border-radius: 10px !important; box-shadow: none !important;
    }
    div[data-testid="stExpander"] summary p, div[data-testid="stExpander"] summary span {
        color: var(--ink) !important; font-weight: 600 !important;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 4px; background: transparent !important; border-bottom: 1px solid var(--line); }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important; border-radius: 8px 8px 0 0 !important;
        padding: 10px 16px !important; font-weight: 600 !important;
    }
    .stTabs [data-baseweb="tab"] * { color: var(--muted) !important; }
    .stTabs [aria-selected="true"] * { color: var(--brand) !important; }
    .stTabs [data-baseweb="tab-highlight"] { background-color: var(--brand) !important; height: 3px !important; }
    .stTabs [data-baseweb="tab-border"] { display: none !important; }

    /* Pesan status (info / sukses / peringatan / error) */
    div[data-testid="stAlert"] { border-radius: 10px !important; }

    /* 8. Minim gangguan saat rerun: elemen tidak berkedip pudar & tidak ada gerakan hover */
    div[data-stale="true"], [data-stale="true"] { opacity: 0.8 !important; transition: none !important; }
    *:focus-visible { outline: 2px solid var(--brand); outline-offset: 2px; }
    @media (prefers-reduced-motion: reduce) { * { transition: none !important; animation: none !important; } }

    /* 9. Beranda */
    .hub-head { display: flex; align-items: center; gap: 16px; padding: 22px 0 6px 0; }
    .hub-logo {
        background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-card);
        padding: 9px 14px; display: flex; align-items: center; flex: 0 0 auto;
    }
    .hub-logo img { height: 34px; width: auto; display: block; }
    .hub-title { font-size: 1.55rem; font-weight: 700; letter-spacing: -0.01em; color: var(--ink) !important; line-height: 1.2; margin: 0; }
    .hub-sub { font-size: 0.92rem; color: var(--muted) !important; margin: 3px 0 0 0; line-height: 1.4; }
    .hub-lead { font-size: 0.95rem; font-weight: 600; color: var(--ink) !important; margin: 22px 0 10px 0; }

    .st-key-area_plk, .st-key-area_pbu {
        background: var(--surface); border: 1px solid var(--line); border-top: 4px solid var(--plk);
        border-radius: var(--r-card); padding: 18px 20px 16px 20px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    }
    .st-key-area_pbu { border-top-color: var(--pbu); }
    .area-name { font-size: 1.2rem; font-weight: 700; color: var(--ink) !important; margin: 0; line-height: 1.3; }
    .area-cluster { font-size: 0.9rem; color: var(--muted) !important; margin: 3px 0 0 0; line-height: 1.45; }
    .area-meta { font-size: 0.85rem; color: var(--muted) !important; margin: 10px 0 14px 0; }
    .area-meta b { color: var(--ink) !important; font-weight: 700; }
    .area-link {
        display: inline-block; margin-top: 8px; font-size: 0.88rem; font-weight: 600;
        color: var(--brand) !important; text-decoration: none !important;
    }
    .area-link:hover { text-decoration: underline !important; }
    .hub-note { font-size: 0.86rem; color: var(--muted) !important; margin: 14px 0 0 0; line-height: 1.5; }
    .hub-foot { text-align: center; color: #7A8494 !important; font-size: 0.8rem; margin-top: 36px; }

    /* Bilah atas halaman dalam */
    .area-chip {
        display: flex; align-items: center; gap: 8px; min-height: 46px;
        font-size: 0.9rem; font-weight: 600; color: var(--ink) !important; white-space: nowrap;
    }
    .area-chip i { width: 10px; height: 10px; border-radius: 50%; background: var(--plk); display: inline-block; flex: 0 0 auto; }
    .area-chip.pbu i { background: var(--pbu); }

    /* 10. Judul halaman & seksi */
    .header-card {
        background: transparent !important; padding: 18px 0 14px 0 !important; margin: 4px 0 18px 0 !important;
        border: 0 !important; border-bottom: 1px solid var(--line) !important; border-radius: 0 !important;
        text-align: left !important; box-shadow: none !important;
    }
    .header-card h1, .header-card h2, .header-card h3 {
        color: var(--ink) !important; font-weight: 700 !important; font-size: 1.45rem !important;
        letter-spacing: -0.01em; margin: 0 0 4px 0 !important; text-align: left !important; text-shadow: none !important;
    }
    .header-card p, .header-card span, .header-card div {
        color: var(--muted) !important; font-size: 0.95rem !important; font-weight: 400 !important;
        margin: 0 !important; text-align: left !important;
    }
    .section-title {
        color: var(--ink) !important; font-size: 1.05rem !important; font-weight: 700 !important;
        margin: 26px 0 12px 0 !important; padding-bottom: 8px; border-bottom: 1px solid var(--line-soft);
        display: block !important;
    }
    .metric-3d {
        background: var(--surface) !important; padding: 14px 18px !important; border-radius: var(--r-card) !important;
        text-align: left !important; box-shadow: none !important; border: 1px solid var(--line) !important;
        border-left: 4px solid var(--brand) !important; margin-bottom: 14px !important;
    }
    .metric-title { font-size: 0.8rem !important; color: var(--muted) !important; font-weight: 600 !important; }
    .metric-value {
        font-size: 1.5rem !important; font-weight: 700 !important; margin-top: 4px !important;
        color: var(--ink) !important; font-variant-numeric: tabular-nums;
    }
    /* Kelas lama yang masih dipakai halaman "Report Lapangan" */
    .sidata-area-card {
        background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-card);
        padding: 24px 22px; text-align: center; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        display: flex; flex-direction: column; justify-content: space-between; align-items: center;
    }
    .sidata-card-heading { font-size: 1.25rem !important; font-weight: 700 !important; color: var(--ink) !important; margin: 6px 0 8px 0 !important; text-align: center !important; }
    .sidata-card-desc { font-size: 0.92rem !important; color: var(--muted) !important; line-height: 1.6 !important; margin: 0 !important; text-align: center !important; }
</style>
""", unsafe_allow_html=True)

# =================================================================
# 📱🖥️ PILIHAN TAMPILAN: WEB / HP  (BLOK TAMBAHAN)
#   - Default otomatis: HP kalau dibuka dari smartphone, Web kalau dari komputer
#   - Bisa diganti manual lewat tombol "Web | HP" di pojok kanan atas
#   - Link langsung untuk tim lapangan:  https://<alamat-app>/?view=hp
# =================================================================
def _terdeteksi_hp() -> bool:
    """Tebak perangkat dari User-Agent (butuh Streamlit >= 1.37). Kalau gagal -> dianggap komputer."""
    try:
        ua = (st.context.headers.get("User-Agent") or "").lower()
        return any(k in ua for k in ("iphone", "ipod", "mobile"))
    except Exception:
        return False

if "view_mode" not in st.session_state:
    _qp = str(st.query_params.get("view", "")).lower()
    st.session_state.view_mode = _qp if _qp in ("web", "hp") else ("hp" if _terdeteksi_hp() else "web")

def _ganti_tampilan():
    pilihan = st.session_state.get("_view_pick", "")
    st.session_state.view_mode = "hp" if "HP" in pilihan else "web"
    st.query_params["view"] = st.session_state.view_mode

IS_HP = st.session_state.view_mode == "hp"

_CSS_COMMON = """
<style>
    /* Tombol pilih tampilan (segmented) */
    .st-key-view_switch { display:flex; justify-content:flex-end; padding:10px 0 2px 0; }
    .st-key-view_switch div[role="radiogroup"] {
        display:inline-flex; gap:2px; background:#E2E8F0; padding:3px; border-radius:999px;
    }
    .st-key-view_switch div[role="radiogroup"] label {
        margin:0 !important; padding:6px 16px !important; border-radius:999px; cursor:pointer;
    }
    .st-key-view_switch div[role="radiogroup"] label > div:first-child { display:none !important; }
    .st-key-view_switch div[role="radiogroup"] label:has(input:checked) {
        background:#FFFFFF; box-shadow:0 1px 3px rgba(15,23,42,.18);
    }
    .st-key-view_switch div[role="radiogroup"] label p {
        font-size:.82rem !important; font-weight:700 !important; margin:0 !important;
    }

    /* Layar sentuh: jangan biarkan efek hover "menempel" setelah ditekan */
    @media (hover: none) {
        div[data-testid="stButton"] > button:hover,
        div[data-testid="stFormSubmitButton"] > button:hover,
        .btn-sidata-blue:hover, .btn-sidata-red:hover, .sidata-area-card:hover {
            transform: none !important;
        }
    }
</style>
"""

_CSS_WEB = """
<style>
    /* Selector lama (.main .block-container) tidak cocok di Streamlit versi baru,
       sehingga lebar maksimal 1180px tidak pernah aktif. Ini menutup celah itu. */
    [data-testid="stMainBlockContainer"], .stMainBlockContainer {
        max-width: 1180px !important;
        margin: 0 auto !important;
        padding: 0.25rem 1.25rem 3rem 1.25rem !important;
    }
</style>
"""

_CSS_HP = """
<style>
    /* ---------- Kanvas: satu kolom ala aplikasi HP ---------- */
    .stApp { background:#E9EEF8 !important; }
    [data-testid="stMainBlockContainer"], .stMainBlockContainer, .main .block-container {
        max-width: 480px !important;
        margin: 0 auto !important;
        padding: 0.4rem 0.85rem 5rem 0.85rem !important;
        background: #F4F7FE;
    }
    @media (min-width: 700px) {   /* pratinjau di komputer: tampil seperti bingkai HP */
        [data-testid="stMainBlockContainer"], .stMainBlockContainer, .main .block-container {
            min-height: 100vh;
            box-shadow: 0 0 0 1px #DCE3F0, 0 24px 60px rgba(15,23,42,.12);
        }
    }
    .st-key-view_switch { justify-content:stretch; }
    .st-key-view_switch div[role="radiogroup"] { display:flex; width:100%; }
    .st-key-view_switch div[role="radiogroup"] label { flex:1; justify-content:center; padding:10px 0 !important; }

    /* ---------- Kolom: ditumpuk ke bawah (4 kolom -> 2x2) ---------- */
    div[data-testid="stHorizontalBlock"] {
        flex-direction: row !important; flex-wrap: wrap !important; gap: 0.6rem !important;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"],
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        flex: 1 1 100% !important; width: 100% !important; min-width: 100% !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) > div[data-testid="stColumn"],
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4):last-child) > div[data-testid="column"] {
        flex: 1 1 calc(50% - 0.3rem) !important; width: calc(50% - 0.3rem) !important; min-width: calc(50% - 0.3rem) !important;
    }

    /* Baris atas halaman dalam: tombol Beranda + badge area, menempel di atas saat scroll */
    div[data-testid="stHorizontalBlock"]:has(.st-key-btn_home) {
        flex-wrap: nowrap !important; position: sticky; top: 0; z-index: 60;
        background: #F4F7FE; padding: 8px 0 6px 0; margin-bottom: 4px;
    }
    div[data-testid="stHorizontalBlock"]:has(.st-key-btn_home) > div[data-testid="stColumn"],
    div[data-testid="stHorizontalBlock"]:has(.st-key-btn_home) > div[data-testid="column"] {
        flex: 0 0 auto !important; width: auto !important; min-width: 0 !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.st-key-btn_home) > div:first-child { flex: 1 1 auto !important; }
    div[data-testid="stHorizontalBlock"]:has(.st-key-btn_home) div[data-testid="stMarkdownContainer"] > div {
        padding: 12px 10px !important; font-size: .72rem !important; white-space: nowrap;
    }

    /* ---------- Tipografi & kartu ---------- */
    .sidata-logo-badge { width:170px; padding:14px 18px 12px 18px; margin-bottom:14px; }
    .sidata-logo-badge img { width:118px; }
    .sidata-top-wrapper { margin-bottom:18px; }
    .sidata-main-title { font-size:1.45rem !important; line-height:1.25 !important; }
    .sidata-main-sub { font-size:.86rem !important; line-height:1.45 !important; }
    .sidata-area-card { min-height:0; padding:22px 16px 18px 16px; border-radius:18px; }
    .sidata-card-heading { font-size:1.15rem !important; }
    .sidata-card-desc { font-size:.84rem !important; line-height:1.55 !important; }
    .header-card { padding:16px 14px !important; border-radius:16px !important; margin-bottom:16px !important; }
    .header-card h1, .header-card h2, .header-card h3 { font-size:1.2rem !important; }
    .header-card p, .header-card span, .header-card div { font-size:.84rem !important; }
    .section-title { font-size:1.05rem !important; margin:22px 0 10px 0 !important; }
    .metric-3d { padding:14px 12px !important; margin-bottom:10px !important; }
    .metric-value { font-size:1.45rem !important; }
    div[data-testid="stWidgetLabel"] p, div[data-testid="stWidgetLabel"] label { font-size:.88rem !important; }
    div[data-testid="stAlert"] { font-size:.88rem; }

    /* ---------- Input: 16px agar iPhone tidak zoom sendiri, area sentuh >= 48px ---------- */
    div[data-baseweb="input"] input, div[data-baseweb="base-input"] input,
    div[data-baseweb="textarea"] textarea, .stTextInput input, .stNumberInput input,
    .stDateInput input, .stTextArea textarea, div[data-baseweb="select"] input {
        font-size: 16px !important;
    }
    div[data-baseweb="input"] input, div[data-baseweb="base-input"] input,
    .stTextInput input, .stNumberInput input, .stDateInput input { padding: 12px 14px !important; }
    div[data-baseweb="select"] > div { min-height: 50px !important; }
    li[role="option"] { min-height: 46px !important; }
    div[data-testid="stCheckbox"] label { min-height: 44px; align-items: center; }
    div[role="radiogroup"] label { padding: 6px 0; }

    /* ---------- Tombol ---------- */
    div[data-testid="stButton"] > button, div[data-testid="stFormSubmitButton"] > button,
    div[data-testid="stDownloadButton"] > button {
        min-height: 54px !important; border-radius: 12px !important; padding: 10px 12px !important;
    }
    div[data-testid="stButton"] > button *, div[data-testid="stFormSubmitButton"] > button * {
        font-size: .9rem !important; line-height: 1.25 !important; white-space: normal !important;
    }
    .btn-sidata-blue, .btn-sidata-red {
        padding: 16px 14px !important; font-size: .9rem !important; border-radius: 12px !important;
    }

    /* ---------- Tab, expander, upload ---------- */
    .stTabs [data-baseweb="tab-list"] { overflow-x: auto; flex-wrap: nowrap; scrollbar-width: none; }
    .stTabs [data-baseweb="tab"] { padding: 10px 14px !important; white-space: nowrap; flex: 0 0 auto; }
    div[data-testid="stExpander"] summary { min-height: 48px; }
    section[data-testid="stFileUploaderDropzone"] {
        flex-direction: column; align-items: stretch; gap: .6rem; padding: 1rem;
    }
    section[data-testid="stFileUploaderDropzone"] button { width: 100%; min-height: 48px; }
</style>
"""

st.markdown(_CSS_COMMON + (_CSS_HP if IS_HP else _CSS_WEB), unsafe_allow_html=True)

_CSS_POLISH = """
<style>
    .st-key-view_switch div[role="radiogroup"] label p { font-size: .76rem !important; font-weight: 600 !important; color: var(--muted) !important; }
    .st-key-view_switch div[role="radiogroup"] label:has(input:checked) p { color: var(--ink) !important; }
    .area-chip { box-sizing: border-box; }
</style>
"""
st.markdown(_CSS_POLISH, unsafe_allow_html=True)

try:
    _sw = st.container(key="view_switch")   # butuh Streamlit >= 1.39
except TypeError:
    _sw = st.container()
with _sw:
    st.radio(
        "Tampilan", ["🖥️ Web", "📱 HP"],
        index=1 if IS_HP else 0, horizontal=True,
        key="_view_pick", on_change=_ganti_tampilan, label_visibility="collapsed",
    )


# =================================================================
# 🧭 WIZARD FORM REQUEST DANA (khusus mode HP) — form dipecah 6 langkah
#   - Mode Web: form tetap satu halaman seperti biasa (tidak ada yang berubah)
#   - Mode HP : tiap langkah tampil sendiri, tombol Kembali/Lanjut menempel di bawah layar
#   - Semua isian TETAP hidup di semua langkah (hanya disembunyikan), jadi hitungan
#     jarak, split tiket, dan validasi lama berjalan persis seperti sebelumnya
# =================================================================
import inspect as _inspect

HAS_KEYED = "key" in _inspect.signature(st.container).parameters   # butuh Streamlit >= 1.39
WZ_ON = IS_HP and HAS_KEYED
WZ_STEPS = ["Petugas & Tiket", "Pekerjaan", "Rute", "Rincian Dana", "Pembayaran", "Kirim"]

def _wz_box(key):
    """Pembungkus satu langkah. Di mode Web tidak mengubah tampilan sama sekali."""
    return st.container(key=key) if HAS_KEYED else st.container()

def _wz_go(n):
    st.session_state.wz_step = max(1, min(len(WZ_STEPS), int(n)))
    st.session_state.wz_scroll = st.session_state.get("wz_scroll", 0) + 1

def _wz_clamp(n):
    """Dipanggil tepat sebelum st.stop(). Kalau pengguna sudah melangkah lewat langkah n,
    tarik balik ke langkah n supaya pesan error-nya terlihat (bukan halaman kosong)."""
    if WZ_ON and st.session_state.get("wz_step", 1) > n:
        _wz_go(n)
        st.rerun()

_CSS_WZ = """
<style>
    [data-testid="stMainBlockContainer"], .stMainBlockContainer, .main .block-container {
        padding-bottom: 7.5rem !important;
    }
    /* Header langkah */
    .wz-head { background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px;
               padding:12px 14px; margin:2px 0 12px 0; box-shadow:0 2px 8px rgba(15,23,42,.05); }
    .wz-top { display:flex; justify-content:space-between; align-items:baseline; gap:8px; margin-bottom:9px; }
    .wz-top span { font-size:.68rem; font-weight:800; letter-spacing:.06em; color:#64748B; }
    .wz-top b { font-size:1rem; color:#0F172A; }
    .wz-bar { display:flex; gap:4px; }
    .wz-bar i { flex:1; height:6px; border-radius:99px; background:#E2E8F0; }
    .wz-bar i.done { background:#10B981; }
    .wz-bar i.cur { background:var(--brand); }

    /* Ringkasan kelengkapan di langkah terakhir */
    .wz-row { display:flex; gap:8px; padding:9px 11px; border-radius:10px; margin-bottom:6px;
              font-size:.86rem; line-height:1.4; }
    .wz-row.ok   { background:#ECFDF5; color:#065F46; }
    .wz-row.warn { background:#FFFBEB; color:#92400E; }
    .wz-row.err  { background:#FEF2F2; color:#991B1B; }

    /* Bar Kembali / Lanjut menempel di bawah layar */
    .st-key-wz_nav {
        position: fixed; left: 50%; bottom: 0; transform: translateX(-50%);
        width: min(480px, 100vw); box-sizing: border-box; z-index: 900;
        background: rgba(255,255,255,.97); backdrop-filter: blur(8px);
        border-top: 1px solid #E2E8F0; box-shadow: 0 -6px 20px rgba(15,23,42,.10);
        padding: 10px 12px calc(10px + env(safe-area-inset-bottom, 0px)) 12px;
    }
    .st-key-wz_nav div[data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; gap: .5rem !important; }
    .st-key-wz_nav div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"],
    .st-key-wz_nav div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        flex: 1 1 0 !important; width: auto !important; min-width: 0 !important;
    }
    .st-key-wz_nav div[data-testid="stHorizontalBlock"] > div:nth-child(2) { flex: 2 1 0 !important; }

    /* Iframe 0px (skrip scroll-ke-atas) jangan memakan ruang */
    div[data-testid="stElementContainer"]:has(iframe[height="0"]) {
        position: absolute; height: 0; overflow: hidden; margin: 0; padding: 0;
    }
</style>
"""

def _wz_render():
    """Gambar header langkah + bar navigasi bawah, dan sembunyikan langkah yang tidak aktif."""
    if not WZ_ON:
        return
    if not st.session_state.get("req_nop"):      # belum pilih NOP / baru masuk halaman -> mulai dari langkah 1
        st.session_state.wz_step = 1
        return

    n = len(WZ_STEPS)
    step = min(max(int(st.session_state.get("wz_step", 1)), 1), n)
    sembunyi = ",".join('[class*="st-key-wz%d_"]' % i for i in range(1, n + 1) if i != step)
    st.markdown(_CSS_WZ + "<style>" + sembunyi + "{display:none !important;}</style>", unsafe_allow_html=True)

    segmen = "".join(
        '<i class="%s"></i>' % ("done" if i < step else ("cur" if i == step else ""))
        for i in range(1, n + 1)
    )
    st.markdown(
        '<div class="wz-head"><div class="wz-top"><span>LANGKAH %d DARI %d</span><b>%s</b></div>'
        '<div class="wz-bar">%s</div></div>' % (step, n, WZ_STEPS[step - 1], segmen),
        unsafe_allow_html=True,
    )

    with st.container(key="wz_nav"):
        c_prev, c_next = st.columns([1, 2])
        with c_prev:
            st.button("⬅️ Kembali", key="wz_prev", on_click=_wz_go, args=(step - 1,),
                      disabled=(step == 1), use_container_width=True)
        with c_next:
            if step < n:
                st.button("Lanjut: %s ➡️" % WZ_STEPS[step], key="wz_next", type="primary",
                          on_click=_wz_go, args=(step + 1,), use_container_width=True)
            else:
                st.button("Langkah terakhir ☝️", key="wz_next_off", disabled=True, use_container_width=True)

    if st.session_state.get("wz_scroll"):        # setiap ganti langkah, gulir kembali ke atas
        st.components.v1.html(
            "<script>try{var d=window.parent.document;"
            "var m=d.querySelector('[data-testid=\"stMain\"]')||d.querySelector('section.main');"
            "if(m){m.scrollTo({top:0});}window.parent.scrollTo(0,0);}catch(e){}</script>"
            "<!--" + str(st.session_state.wz_scroll) + "-->",
            height=0,
        )

def _wz_ringkasan(items):
    """items = [(no_langkah, nama, 'ok'|'warn'|'err', pesan)]. Ditampilkan di langkah terakhir."""
    ikon = {"ok": "✅", "warn": "⚠️", "err": "❌"}
    baris = ""
    for no, nama_langkah, status, pesan in items:
        teks = nama_langkah if status == "ok" else nama_langkah + " — " + pesan
        baris += '<div class="wz-row %s"><span>%s</span><span>%s</span></div>' % (status, ikon[status], teks)
    st.markdown('<div class="section-title">📋 Ringkasan Kelengkapan</div>' + baris, unsafe_allow_html=True)
    for no, nama_langkah, status, pesan in items:
        if status != "ok":
            st.button("✏️ Perbaiki Langkah %d: %s" % (no, nama_langkah), key="wz_fix_%d" % no,
                      on_click=_wz_go, args=(no,), use_container_width=True)


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

cloudinary.config(cloud_name="ji9i1hei", api_key="277523771179144", api_secret="7eg20WV-Bzf9DXEoT8rg3H99V6c", secure=True)

SHEET_REQUEST = "Form Request dana"        
SHEET_PJB = "Form PJB"
SHEET_UM = "Data UM"
SHEET_DISTRIBUSI = "Distribusi UM"
SHEET_APP = "Approval BBM"
SHEET_TIKET_PM = "PM Tiketing"
SHEET_ABSENSI = "Data Absensi" 
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

MASTER_DATA = {
    "Palangkaraya": {"spreadsheet_id": "1HvgVicTWwO4RMQI6ZR3Mu3IgGicwjcLZl9mDN1auvJU", "clusters": ["Palangkaraya", "Barito Raya"], "names": ["ADI BOWO SANTOSO", "IRJAN TORO", "AHMAD", "AHMAD MUZAKIR", "AHMAD SETIAWAN", "ALFI SYAHRI", "ARMADI", "AULIA RAHMAN", "DARLI SUTANTO", "DIDI RIYADI", "FAHMI", "FRANS EJHA ADITYA", "GYLLBRHED ALFARY LOLOMSAIT", "HARUN NURASYID", "HORY YUSMANTO", "INDRA", "JAMES JIMBRIS TAMAILANG", "JUMADI", "KHILAL DAWAI KATIRI", "LEONARD HARA", "M. RIFANI", "MUHAMMAD MUKHLIS", "MUHAMMAD MUKTI", "MUNAWIR AHMAD", "MURJANI", "NURHAYAT", "OKY BANGKIT PAMUNGKAS", "PRADILA KANDI", "PUJIANTO", "PUTRA WARDANA", "REYNALDI RICARDO PUTRA", "RIKI HIDAYAT", "RIKO SETIADI", "SAILILLAH", "SARUL SAPUTRA", "SARWONO", "RIO ARDINATA", "TAKLIM", "TIVIANSYAH", "TRISNO SUSANTO", "YAHYA MUHAMAD", "OKTA PRDIKA", "OKTA PRADIKA", "M KIKI FIRMANSYAH", "MAWARDAH", "HD"]},
    "Pangkalanbun": {"spreadsheet_id": "1bc0lDhR5iMtXZsKiKIdEwPY8JTaASeHFtaJSeXkywE4", "clusters": ["Ketapang", "Sampit", "Pangkalanbun"], "names": ["AGUS SUGANDA", "AJI SAPUTRA", "DANDI PUTRA", "DIAN WAHYUDI", "DIAN WILDANI", "HAFID BUDIANTO", "HERWANI", "IWAN ZAINAL ABIDIN", "PARYADI KUSUMA", "PONIRAN", "ANDARIANTO PUJI SURO", "ARDI", "CAVIN ANDREAN EKA PUTRA", "DADANG WAHYU SYAHPUTRA", "FERI HARIADI", "JOENDRIS HERDIAN KARA", "NASUKI", "REDI CANDRA SINAGA", "RIZAL IHZAMAHENDRA", "SOLEKHAN", "STEVEN HERDIAN KARA", "TEGUH WICAKSONO", "YUDIONO", "IPAN HARIONO", "DIDIK PRIYONO", "MUHAMAD ROIS FERDIANSYAH", "WIDI ARYANTO", "HERMANSYAH", "MUHAMMAD RIZKY", "RIDWANSYAH", "TRIYONO", "UTI MUHAMMAD KHAIRUL HUDA", "ARDIANSYAH", "BAGUS SANTOSO", "BONDAN PRAMUDYA ANANTATUR", "M.ABDUL KHOLIP", "MUJHAHID ALWI", "RIRIH HARIANTO", "TAJAM SAPUTRA", "WAHYUDI", "DAYU SHANDY", "MEI NUGROHO DWI LAKSONO", "ARIF JONIAWAN", "FIRDAUS", "AYU NUR ISLAMIAH", "RAHMAT RIYAN WAHYUDIN", "RONI YUDI ISYANTO", "FHANNY AGUSTIAWAN", "GUNTUR WAHYU PRADANA", "SUWITO"]},
    "Tarakan": {"spreadsheet_id": "1lRj1YdZGQwY5vHg8P4wudK9V1O_lJuEYjdyHkXoB-Wg", "clusters": ["Tarakan Inner", "Tarakan Outer"], "names": ["HENDRA WIRTASI SIMANULLANG", "ARIZONA ROSADI", "KUKUH BHASKARA", "NATAL SIMBOLON", "HERMAWAN", "IRVAN DINATA VANDITYAWAN", "ENDRAS SAPTA", "AHMADI", "EDI PANJI ERMAYANA", "HANS RISKY RONI TUAH GIRSANG", "IRMANSYAH B. SANGAJI", "REMO REMOLDUS MANALU", "MOHAMMAD RAFAI", "FIRMAN SYAHRUL", "AZMIR", "PETRUS RESI KELORE", "ANIR REZKY", "AHDAN", "PARJON SIMANULLANG", "RUSDI", "HASRIADI", "PURO SUGONDO", "ALIMUDIN M. SAER", "KORNELIUS USI KELORE", "RUSDIANSYAH", "JONTES YUSDA SIMANULLANG", "NANI SETIANINGSIH", "UNGGUL NUGRAHA", "YOGABITA INDOTENO", "JHON KENNEDI SIMANULLANG", "RAFI MUHAMAD SYARIF", "AGRIVA", "SEPTIAN ALVITO", "M. DEDI RIZALDI", "SAHARUDDIN.", "MUHAMMAD RASYID", "SUPRIADI", "JULIMAT SIHITE", "EFNI NURYADIN", "ERWIN SAPUTRA ARIANSYAH", "ALVEUS", "SUPRIADI BANDANGAN"]},
    "Pontianak": {"spreadsheet_id": "1VmoWPImNFMjnaIQpBXEVYdMiTEzsz3P4tpmzfA0EMDE", "clusters": ["Sintang", "Singkawang", "Pontianak"], "names": ["ALOYSIUS", "RUDI", "RONIYANTO", "SUKADI", "HAIRIL", "AZMI ASHADIQI", "SUYADI", "ARIEF DARUL IKHWAN", "MUHAMMAD AL FATAH", "YUDIANSYAH", "RAHMAD INDRA IRAWAN", "MATIUS MARTIN", "RYVAEEL DEWANGGA", "AMIRDA ANGGA SAPUTRA", "IZHARUDDIN", "VINSENSIUS YOGI", "GUSTI ARIZAL", "MUHAMMAD MIFTAHUDIN, A.MD", "BAYU ANGGARA PUTRA", "YONI IRAWAN", "SUGANDI", "IRVAN ANDRIYANA", "ALDIANSYAH", "ABANG HAMDANI", "ABANG KUSDIANSYAH", "SUMAN", "SANGGARA ISMARAWARI", "IBIN", "VALENTINUS PETRO", "DWI KURNIAWAN ISMANTO", "ARISAFRIADI", "DONATUS DONI", "NUR AHMAD KARDIYANTO", "AGRI PERDANA", "AKHSANUL FIKI", "ALI ALAMSYAH", "MUHAMMAD FIRZHA GIANNI HARSYA", "RICKY ARDILAY", "FAISAL", "WIJI SANTOSO", "HISYAM MUTHOYIB", "ARIF RAHMAN NUGROHO", "TOTOK SUGIARTO", "PURWANDI SETIAWAN", "JULIANTO BHAKTI PUTRO, SH", "ILHAMMUDIN", "AGUNG", "ROSIDI", "ABRAR ELZAH FATHALIF", "HENDRI YULIANSYAH", "JAMIL", "GORO SUKARTONO", "OKTAPIANUS JUMIN", "ONNIE SYAEFUDDIN", "BUDI", "ULUL AMRY", "RUHIAT, A.MD", "SUPIANDI", "WAHYUDI", "SUHENDRIK", "M. ARKAM", "SYAFRI APRIJAL", "ARIANTO SUMANTRI", "TUTU AGE ANDIKA", "VIRANDA SAPTA, A.MD", "TOTO HERMANSYAH", "KURNIAWAN", "ROBI ISKANDAR MASDIANSYAH", "MUTIIN CHANDRA", "MISJANI", "KHAIRUL FARISD", "ANDRA", "DODI RATMAYANTO", "WAWAN DARYANA", "MISWARDI", "JUPRILIAUS PICO", "DEDY PURNOMO", "EDI KURNIAWAN", "DEDE GUNAWAN", "WANDALA JAGOARDI PANDALO", "KARIYADI", "REZQI AL BARQAH", "FIRMANSYAH, SP"]}
}
LIST_KEPERLUAN = ["", "Tshoot", "Backup", "Support", "PM", "Program BCP", "Program Quikwin", "Program G348T", "Pengiriman Material SPMS", "Pembelian Material", "Transportasi Air", "Lainnya (Ketik Manual)"]

# ==============================================================================
# ATURAN HARGA SATUAN BBM AKTUAL: SPBU vs ECERAN (VALIDASI KETAT ANTI MARK-UP)
# ==============================================================================
BBM_PRICE_RULES_SPBU = {
    "Pertalite":     {"default": 10000, "min": 9000,  "max": 10000},
    "Pertamax":      {"default": 16500, "min": 11500, "max": 16500},
    "Bio Solar":     {"default": 6000,  "min": 5500,  "max": 6000},
    "Dexlite":       {"default": 25000, "min": 12500, "max": 25000},
    "Pertamina Dex": {"default": 18500, "min": 13000, "max": 18500},
}

BBM_PRICE_RULES_ECERAN = {
    "Pertalite":     {"default": 15000, "min": 13000, "max": 20000},
    "Pertamax":      {"default": 20000, "min": 19000, "max": 25000},
    "Bio Solar":     {"default": 18000, "min": 15000, "max": 28000},
    "Dexlite":       {"default": 29000, "min": 29000, "max": 30000},
    "Pertamina Dex": {"default": 25000, "min": 20000, "max": 30000},
}

# Alias kompatibilitas
BBM_PRICE_RULES = BBM_PRICE_RULES_SPBU

def get_now_wib():
    """Mengembalikan waktu aktual WIB (UTC+7) secara akurat di server cloud."""
    return datetime.utcnow() + timedelta(hours=7)

def get_bbm_rule(jenis_bbm_str, sumber_beli="SPBU"):
    is_eceran = ("eceran" in str(sumber_beli).lower()) or ("eceran" in str(jenis_bbm_str).lower())
    rules_dict = BBM_PRICE_RULES_ECERAN if is_eceran else BBM_PRICE_RULES_SPBU
    s = str(jenis_bbm_str).lower()
    matched_key = None
    for k in rules_dict:
        if k.lower() in s:
            matched_key = k
            break
    if not matched_key:
        if "solar" in s: matched_key = "Bio Solar"
        elif "pertamina dex" in s: matched_key = "Pertamina Dex"
        elif "dex" in s: matched_key = "Dexlite"
        elif "pertamax" in s: matched_key = "Pertamax"
        elif "pertalite" in s: matched_key = "Pertalite"
    return matched_key, ("Eceran" if is_eceran else "SPBU"), (rules_dict.get(matched_key) if matched_key else None)

def validate_bbm_price(jenis_bbm_str, harga_satuan, sumber_beli="SPBU"):
    """Validasi ketat harga satuan BBM aktual berdasarkan sumber pembelian (SPBU vs Eceran)."""
    try:
        harga_val = int(round(float(harga_satuan)))
    except Exception:
        harga_val = 0
    matched_key, mode_lbl, rule = get_bbm_rule(jenis_bbm_str, sumber_beli)
    if not rule:
        max_fallback = 30000 if mode_lbl == "Eceran" else 25000
        if harga_val <= 0:
            return False, "Harga satuan BBM wajib diisi (> Rp 0)."
        if harga_val > max_fallback:
            return False, f"Harga satuan BBM {mode_lbl} (Rp {harga_val:,.0f}/L) melebihi batas maksimum (Rp {max_fallback:,.0f}/L)!"
        return True, f"Harga {mode_lbl} wajar"
    if harga_val <= 0:
        return False, f"Harga satuan {matched_key} ({mode_lbl}) wajib diisi (> Rp 0)."
    if harga_val < rule["min"]:
        return False, f"Harga satuan {matched_key} {mode_lbl} (Rp {harga_val:,.0f}/L) di bawah batas minimal (Min Rp {rule['min']:,.0f}/L). Cek kembali input Anda!"
    if harga_val > rule["max"]:
        return False, f"Harga satuan {matched_key} {mode_lbl} (Rp {harga_val:,.0f}/L) MELEBIHI batas wajar (Maks Rp {rule['max']:,.0f}/L)! Wajib menggunakan harga actual."
    if mode_lbl == "SPBU":
        return True, f"Harga {matched_key} SPBU valid (Maks Rp {rule['max']:,.0f}/L)"
    return True, f"Harga {matched_key} Eceran valid (Range Rp {rule['min']:,.0f} - Rp {rule['max']:,.0f}/L)"

def format_id_number(val):
    """Format angka gaya Indonesia (titik ribuan, koma desimal) agar mudah dibaca tim."""
    try:
        f = float(val)
        if abs(f - round(f)) < 1e-6:
            return f"{int(round(f)):,}".replace(",", ".")
        s = f"{f:,.2f}".rstrip("0").rstrip(".")
        return s.replace(",", "_").replace(".", ",").replace("_", ".")
    except Exception:
        return str(val)

def parse_indonesian_indicator(raw_val, last_ind=0.0, unit="KM"):
    """
    Parser pintar angka KM / RH / Liter Indonesia (kebal salah ketik titik vs koma).
    Mengembalikan: (nilai_float, level ['ok'|'info'|'warn'|'err'], pesan_analisa)
    """
    if raw_val is None:
        return 0.0, "err", f"Angka {unit} masih kosong."
    s_orig = str(raw_val).strip()
    if s_orig == "":
        return 0.0, "err", f"Angka {unit} wajib diisi."

    s = re.sub(r"(?i)\b(km|rh|jam|liter|l)\b", "", s_orig).replace(" ", "").strip()
    if not re.match(r"^-?[\d\.,]+$", s):
        return 0.0, "err", f"Format '{s_orig}' tidak valid! Hanya ketik angka murni (contoh: 125450 atau 1250,5)."

    val = 0.0
    level = "ok"
    note = ""
    has_dot = "." in s
    has_comma = "," in s

    try:
        if has_dot and has_comma:
            if s.rfind(",") > s.rfind("."):
                val = float(s.replace(".", "").replace(",", "."))
                level = "info"
                note = f"Format titik ribuan & koma desimal terdeteksi: '{s_orig}' dibaca **{format_id_number(val)} {unit}**."
            else:
                val = float(s.replace(",", ""))
                level = "info"
                note = f"Format koma ribuan & titik desimal terdeteksi: '{s_orig}' dibaca **{format_id_number(val)} {unit}**."
        elif has_dot and not has_comma:
            parts = s.split(".")
            if len(parts) > 2:
                if all(len(p) == 3 for p in parts[1:]):
                    val = float("".join(parts))
                    level = "warn"
                    note = f"⚠️ **Deteksi Titik Ribuan:** '{s_orig}' dibaca **{format_id_number(val)} {unit}**. Sebaiknya ketik angka polos tanpa titik (`{int(val)}`)."
                else:
                    return 0.0, "err", f"Penulisan titik pada '{s_orig}' tidak valid (titik ganda)! Ketik angka polos tanpa titik ribuan (contoh: 125450)."
            else:
                left_p, right_p = parts[0], parts[1]
                if len(right_p) == 3 and len(left_p) >= 1 and left_p != "0" and unit != "Liter":
                    as_thousands = float(left_p + right_p)
                    as_decimal = float(s)
                    if last_ind > 0 and last_ind < 50 and abs(as_decimal - last_ind) < abs(as_thousands - last_ind):
                        val = as_decimal
                        level = "info"
                        note = f"Titik dibaca desimal: **{format_id_number(val)} {unit}**."
                    else:
                        val = as_thousands
                        level = "warn"
                        note = f"⚠️ **Deteksi Titik Ribuan:** '{s_orig}' otomatis dibaca sebagai **{format_id_number(val)} {unit}** (bukan {as_decimal}). Ketik angka polos tanpa titik (`{int(val)}`) agar tidak salah baca!"
                else:
                    val = float(s)
                    if unit != "Liter" and last_ind >= 1000 and val < (last_ind / 100.0):
                        level = "err"
                        note = f"🚨 **SALAH PENULISAN TITIK/KOMA!** Input '{s_orig}' terbaca **{format_id_number(val)} {unit}**, jauh di bawah histori terakhir **{format_id_number(last_ind)} {unit}**! Hapus titik pemisah ribuan!"
                    else:
                        level = "ok"
                        note = f"Terbaca sistem: **{format_id_number(val)} {unit}**."
        elif has_comma and not has_dot:
            parts = s.split(",")
            if len(parts) > 2:
                if all(len(p) == 3 for p in parts[1:]):
                    val = float("".join(parts))
                    level = "warn"
                    note = f"⚠️ **Deteksi Koma Ribuan:** '{s_orig}' dibaca **{format_id_number(val)} {unit}**. Ketik angka polos tanpa koma ribuan."
                else:
                    return 0.0, "err", f"Penulisan koma pada '{s_orig}' tidak valid (koma ganda)!"
            else:
                left_p, right_p = parts[0], parts[1]
                if unit != "Liter" and len(right_p) == 3 and len(left_p) >= 1 and left_p != "0":
                    as_thousands_c = float(left_p + right_p)
                    as_decimal_c = float(s.replace(",", "."))
                    if last_ind > 0 and last_ind < 50 and abs(as_decimal_c - last_ind) < abs(as_thousands_c - last_ind):
                        val = as_decimal_c
                        level = "info"
                        note = f"Koma dibaca desimal: **{format_id_number(val)} {unit}**."
                    else:
                        val = as_thousands_c
                        level = "warn"
                        note = f"⚠️ **Deteksi Koma Ribuan:** '{s_orig}' dibaca **{format_id_number(val)} {unit}**. Ketik angka polos tanpa koma ribuan (`{int(val)}`)."
                else:
                    val = float(s.replace(",", "."))
                    if unit != "Liter" and last_ind >= 1000 and val < (last_ind / 100.0):
                        level = "err"
                        note = f"🚨 **SALAH PENULISAN KOMA!** Input '{s_orig}' terbaca **{format_id_number(val)} {unit}**, jauh di bawah histori **{format_id_number(last_ind)} {unit}**! Hapus koma jika maksudnya ribuan."
                    else:
                        level = "ok"
                        note = f"Terbaca sistem: **{format_id_number(val)} {unit}**."
        else:
            val = float(s)
            level = "ok"
            note = f"Terbaca sistem: **{format_id_number(val)} {unit}**."
    except Exception:
        return 0.0, "err", f"Gagal membaca angka '{s_orig}'. Gunakan angka murni."

    if val < 0:
        return 0.0, "err", f"Nilai {unit} tidak boleh negatif!"
    return round(val, 2), level, note

def parse_timestamp_dt(ts_str, tgl_str=""):
    """Parsing timestamp penuh (DD/MM/YYYY HH:MM:SS) untuk kontrol waktu live."""
    for raw in [ts_str, tgl_str]:
        s = str(raw or "").strip()
        if not s or s.upper() in ["NAN", "NONE", "-"]:
            continue
        for fmt in ("%d/%m/%Y %H:%M:%S", "%m/%d/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M", "%d-%m-%Y %H:%M:%S"):
            try:
                dt = datetime.strptime(s, fmt)
                if dt.year == 2026 and dt.month < 9 and dt.day >= 9:
                    dt = dt.replace(month=dt.day, day=dt.month)
                return dt
            except ValueError:
                continue
    d = parse_date(tgl_str, ts_str)
    if d != datetime(1970, 1, 1).date():
        return datetime(d.year, d.month, d.day, 0, 0, 0)
    return None

def format_elapsed_time(hours_float):
    if hours_float is None or hours_float < 0:
        return "-"
    total_mins = int(round(hours_float * 60))
    days = total_mins // (24 * 60)
    rem_mins = total_mins % (24 * 60)
    hrs = rem_mins // 60
    mins = rem_mins % 60
    parts = []
    if days > 0: parts.append(f"{days} Hari")
    if hrs > 0: parts.append(f"{hrs} Jam")
    if mins > 0 or not parts: parts.append(f"{mins} Mnt")
    return " ".join(parts)

def evaluate_live_indicator_control(current_val, last_info, now_wib, tipe="Mobil"):
    """
    Analisa Live Kontrol Waktu & Kewajaran KM Mobil/Motor atau RH Genset.
    Mengembalikan dict: {is_blocking, level, elapsed_text, elapsed_hours, selisih, status_short, detail_lines}
    """
    unit = "RH" if tipe == "Genset" else "KM"
    last_val = float(last_info.get("value", 0.0))
    last_dt = last_info.get("dt_obj")
    elapsed_hours = None
    elapsed_text = "-"
    if last_dt is not None:
        diff_sec = (now_wib - last_dt).total_seconds()
        if diff_sec >= 0:
            elapsed_hours = diff_sec / 3600.0
            elapsed_text = format_elapsed_time(elapsed_hours)
        else:
            elapsed_hours = 0.0
            elapsed_text = "Baru saja"

    selisih = round(current_val - last_val, 2) if last_val > 0 else 0.0
    is_blocking = False
    level = "ok"
    status_short = "VALID"
    lines = []

    if last_val > 0:
        lines.append(f"- **Histori Terakhir ({last_info.get('source', 'Histori')}):** **{format_id_number(last_val)} {unit}** | Tgl/Jam: `{last_info.get('timestamp_str', '-')}` *(Selisih waktu live: **{elapsed_text}**)*")
        lines.append(f"- **Input Sekarang ({now_wib.strftime('%d/%m/%Y %H:%M WIB')}):** **{format_id_number(current_val)} {unit}** → **Selisih: `{selisih:+g} {unit}`**")
    else:
        lines.append(f"- **Input Sekarang ({now_wib.strftime('%d/%m/%Y %H:%M WIB')}):** **{format_id_number(current_val)} {unit}** *(Belum ada histori {unit} sebelumnya untuk unit ini)*")

    if current_val <= 0:
        is_blocking = True
        level = "err"
        status_short = f"INVALID ({unit}<=0)"
        lines.append(f"- 🚨 **ERROR:** Angka {unit} wajib lebih dari 0!")
    elif last_val > 0 and current_val < last_val:
        is_blocking = True
        level = "err"
        status_short = f"ERROR ({unit} MUNDUR)"
        lines.append(f"- 🚨 **ERROR {unit} MUNDUR / SALAH TITIK-KOMA:** Input (**{format_id_number(current_val)}**) lebih kecil dari histori terakhir (**{format_id_number(last_val)}**). Cek ulang odometer/hourmeter atau hapus titik ribuan!")
    elif last_val >= 100 and current_val > last_val * 5 and selisih > (500 if tipe == "Genset" else 5000):
        is_blocking = True
        level = "err"
        status_short = "ERROR (LONJAKAN DIGIT)"
        lines.append(f"- 🚨 **ANOMALI LONJAKAN DIGIT / SALAH KETIK:** {unit} melompat **+{format_id_number(selisih)} {unit}** (lebih dari 5x lipat histori {format_id_number(last_val)}). Periksa apakah kelebihan angka 0 atau salah koma!")
    elif tipe == "Genset" and last_val > 0 and elapsed_hours is not None and selisih > (elapsed_hours + 2.0):
        level = "warn"
        status_short = f"ANOMALI WAKTU RH (+{selisih:g} RH > {elapsed_hours:.1f} Jam)"
        lines.append(f"- ⚠️ **PERINGATAN KONTROL WAKTU GENSET:** Kenaikan RH (**+{format_id_number(selisih)} Jam**) MELEBIHI waktu riil yang berlalu sejak pengisian terakhir (**{elapsed_text}** / {elapsed_hours:.1f} Jam)! Harap cek ulang penulisan angka & koma RH Genset.")
    elif tipe in ("Mobil", "Motor") and last_val > 0 and elapsed_hours is not None and elapsed_hours >= 0.25 and (selisih / elapsed_hours) > 100.0:
        avg_spd = selisih / elapsed_hours
        level = "warn"
        status_short = f"ANOMALI KM (+{selisih:g} KM dlm {elapsed_text})"
        lines.append(f"- ⚠️ **PERINGATAN KONTROL WAKTU {tipe.upper()}:** Kenaikan **+{format_id_number(selisih)} KM** dalam **{elapsed_text}** (rata-rata **{avg_spd:.1f} KM/jam nonstop**) sangat tidak wajar! Periksa apakah ada salah ketik digit atau titik/koma.")
    elif tipe in ("Mobil", "Motor") and last_val > 0 and selisih == 0 and (elapsed_hours or 0) > 6:
        level = "warn"
        status_short = "KM TIDAK BERUBAH"
        lines.append(f"- ⚠️ **PERINGATAN:** Angka KM sama persis dengan pengisian terakhir ({elapsed_text} lalu). Pastikan Anda menginput angka KM odometer terbaru, bukan angka lama.")
    else:
        if last_val > 0 and elapsed_hours is not None and elapsed_hours > 0:
            if tipe == "Genset":
                util_pct = min(100.0, (selisih / max(elapsed_hours, 0.1)) * 100.0)
                lines.append(f"- ✅ **Status Kontrol Live:** **VALID & WAJAR** (Running {format_id_number(selisih)} Jam dalam rentang {elapsed_text} | Utilisasi {util_pct:.0f}%).")
            else:
                km_per_day = selisih / max(elapsed_hours / 24.0, 1.0 / 24.0)
                lines.append(f"- ✅ **Status Kontrol Live:** **VALID & WAJAR** (Pemakaian +{format_id_number(selisih)} KM dalam {elapsed_text} | Rata-rata ±{format_id_number(round(km_per_day, 1))} KM/Hari).")
        else:
            lines.append(f"- ✅ **Status Kontrol Live:** **VALID** (Format angka {unit} bersih & terbaca jelas).")

    return {
        "is_blocking": is_blocking,
        "level": level,
        "elapsed_text": elapsed_text,
        "elapsed_hours": elapsed_hours,
        "selisih": selisih,
        "status_short": status_short,
        "detail_lines": lines
    }


# ==========================================
# 2. FUNGSI INTI & CACHING (AKURAT & HEMAT RAM)
# ==========================================
def ai_nota_checker(uploaded_file, expected_nominal, expected_date=None):
    return True, "Valid"

def ai_image_checker(uploaded_file, file_name_label):
    return True, "Aman"

def ai_eceran_checker(f_botol, f_bayar, expected_liter, expected_harga_satuan, expected_total_nota):
    """
    Analisa AI untuk PJB Pembelian BBM ECERAN:
    1. Foto Full Isi BBM sesuai jumlah botol/jerigen liter (cek keaslian, resolusi, ketajaman, kecerahan, EXIF, anti-duplikat).
    2. Foto Bukti Bayar Cash / Transfer ke Toko Eceran (cek keaslian + OCR nominal bayar jika mesin OCR tersedia).
    """
    import hashlib
    findings = []
    warnings_found = []

    if f_botol is None or f_bayar is None:
        return False, "BELUM LENGKAP", ["❌ Wajib mengunggah kedua foto Eceran (Foto Full Botol/Liter & Foto Bukti Bayar Toko)."], "Foto Eceran belum lengkap"

    try:
        b1 = f_botol.getvalue()
        b2 = f_bayar.getvalue()
    except Exception as e:
        return False, "ERROR", [f"❌ Gagal membaca file gambar: {e}"], "Error baca gambar Eceran"

    # 1. Cek Duplikat Identik (Anti-Curang Upload Foto yang Sama)
    h1 = hashlib.md5(b1).hexdigest()
    h2 = hashlib.md5(b2).hexdigest()
    if h1 == h2:
        warnings_found.append("Foto Botol/Liter dan Foto Bukti Bayar adalah file gambar yang IDENTIK (sama persis)!")

    def _analyze_single_img(raw_bytes, label_name):
        img_notes = []
        img_warn = []
        ocr_text = ""
        try:
            with Image.open(io.BytesIO(raw_bytes)) as im:
                w, h = im.size
                exif_info = None
                try:
                    exif_info = im.getexif()
                except Exception:
                    exif_info = None
                has_exif = bool(exif_info and len(exif_info) > 0)

                rgb = im.convert("RGB")
                arr = np.asarray(rgb.resize((min(w, 640), min(h, 640))), dtype=np.float32)
                gray = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
                brightness = float(np.mean(gray))
                gx = np.diff(gray, axis=1)
                gy = np.diff(gray, axis=0)
                sharpness = float(np.var(gx) + np.var(gy))

                if w < 300 or h < 300:
                    img_warn.append(f"{label_name}: Resolusi terlalu kecil ({w}x{h} px), sulit diaudit.")
                if brightness < 25:
                    img_warn.append(f"{label_name}: Foto terlalu gelap/hitam (brightness {brightness:.0f}).")
                elif brightness > 245:
                    img_warn.append(f"{label_name}: Foto terlalu putih/kosong (brightness {brightness:.0f}).")
                if sharpness < 18:
                    img_warn.append(f"{label_name}: Foto terdeteksi sangat buram/blur (skor ketajaman {sharpness:.1f}).")

                exif_txt = "Kamera Asli (EXIF ada)" if has_exif else "Tanpa EXIF (WA/Screenshot)"
                img_notes.append(f"**{label_name}:** {w}×{h} px | Ketajaman {sharpness:.0f} | {exif_txt}")

                if pytesseract is not None:
                    try:
                        ocr_text = pytesseract.image_to_string(rgb)
                    except Exception:
                        ocr_text = ""
        except Exception as e:
            img_warn.append(f"{label_name}: Gagal analisa citra ({e}).")
        return img_notes, img_warn, ocr_text

    n1, w1, _ = _analyze_single_img(b1, "Foto 1 (Full Botol/Liter BBM)")
    n2, w2, ocr_bayar = _analyze_single_img(b2, "Foto 2 (Bukti Bayar Toko Eceran)")
    findings.extend(n1 + n2)
    warnings_found.extend(w1 + w2)

    exp_tot = int(round(float(expected_total_nota or 0)))
    exp_l = float(expected_liter or 0)
    exp_hrg = int(round(float(expected_harga_satuan or 0)))

    if ocr_bayar and ocr_bayar.strip():
        nums_raw = re.findall(r"\d[\d\.\,]{2,}", ocr_bayar)
        parsed_nums = []
        for nr in nums_raw:
            try:
                v_clean = int(re.sub(r"[^\d]", "", nr))
                if v_clean >= 1000:
                    parsed_nums.append(v_clean)
            except Exception:
                pass
        if exp_tot > 0 and parsed_nums:
            matched_nom = any(abs(vn - exp_tot) <= max(5000, 0.05 * exp_tot) for vn in parsed_nums)
            if matched_nom:
                findings.append(f"✅ **AI OCR Bukti Bayar:** Nominal **Rp {exp_tot:,.0f}** terdeteksi cocok pada bukti bayar toko.")
            else:
                warnings_found.append(f"AI OCR tidak menemukan nominal cocok Rp {exp_tot:,.0f} pada bukti bayar toko (terbaca: {parsed_nums[:5]}). Perlu verifikasi manual Admin.")
        else:
            findings.append(f"ℹ️ **AI Bukti Bayar:** Siap audit nominal **Rp {exp_tot:,.0f}** ({format_id_number(exp_l)} L × Rp {exp_hrg:,.0f}/L).")
    else:
        findings.append(f"ℹ️ **Target Verifikasi AI Eceran:** **{format_id_number(exp_l)} Liter** (Full Botol/Jerigen) | Total Bayar **Rp {exp_tot:,.0f}** (@Rp {exp_hrg:,.0f}/L).")

    if warnings_found:
        for wf in warnings_found:
            findings.append(f"⚠️ **Temuan AI:** {wf}")
        short_rem = "⚠️ AI Eceran Flag: " + " ; ".join(warnings_found[:2])
        return False, "PERLU AUDIT ADMIN", findings, short_rem

    short_rem = f"✅ AI Eceran OK ({format_id_number(exp_l)} L @Rp {exp_hrg:,.0f} = Rp {exp_tot:,.0f})"
    return True, "LOLOS ANALISA AI", findings, short_rem

def ui_image_uploader(label, key=None):
    return st.file_uploader(label, type=["jpg", "png", "jpeg"], key=key)

def parse_date(date_str, fallback_ts=""):
    from datetime import datetime, date
    for raw_val in [date_str, fallback_ts]:
        if raw_val is None or pd.isna(raw_val):
            continue
        s = str(raw_val).strip()
        if not s or s.upper() in ["NAN", "NONE", "-", "NAT"]:
            continue
        s_date = s.split(" ")[0].strip()

        # 1. Prioritas Utama: Format Standar Tanggal/Bulan/Tahun (DD/MM/YYYY) seperti Palangkaraya
        for fmt_id in ("%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y"):
            try:
                d = datetime.strptime(s_date, fmt_id).date()
                if d.year == 2026 and d.month < 9 and d.day >= 9:
                    return date(d.year, d.day, d.month)
                return d
            except ValueError:
                continue

        # 2. Cadangan jika angka hari > 12 berada di tengah (contoh: 10/31/2026) atau YYYY-MM-DD
        for fmt_other in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d", "%m-%d-%Y", "%m/%d/%y"):
            try:
                return datetime.strptime(s_date, fmt_other).date()
            except ValueError:
                continue

    return datetime(1970, 1, 1).date()

def clean_nominal(val):
    if pd.isna(val) or val == "": return 0
    v = str(val).replace('Rp', '').replace(' ', '').strip()
    if v.endswith(',00'): v = v[:-3]
    if v.endswith('.00'): v = v[:-3]
    v = v.replace('.', '').replace(',', '')
    try: return int(v)
    except: return 0

def clean_indicator(val):
    """Membersihkan angka indikator KM/RH dari Google Sheets dengan cerdas (anti rusak titik ribuan)."""
    try:
        if pd.isna(val) or val == "": return 0.0
        v_parsed, _, _ = parse_indonesian_indicator(val, last_ind=0.0, unit="KM")
        return float(v_parsed)
    except Exception:
        return 0.0

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

@st.cache_data(ttl=86400, max_entries=200, show_spinner=False)
def get_route_and_distance(lon1, lat1, lon2, lat2):
    try:
        url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=simplified"
        res = requests.get(url, timeout=5).json()
        if res.get("code") == "Ok":
            dist_km = res["routes"][0]["distance"] / 1000
            durasi_sec = res["routes"][0]["duration"]
            poly = decode_polyline(res["routes"][0]["geometry"])
            return dist_km, poly, durasi_sec
    except Exception:
        pass
    dist_km = haversine(lat1, lon1, lat2, lon2) * 1.3 
    durasi_sec = (dist_km / 40.0) * 3600
    return dist_km, [[lon1, lat1], [lon2, lat2]], durasi_sec

@st.cache_resource
def get_credentials():
    if "gcp_json" in st.secrets:
        import json
        creds_info = json.loads(st.secrets["gcp_json"], strict=False)
        return Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    return Credentials.from_service_account_file("credentials.json", scopes=SCOPES)

@st.cache_data(ttl=180, max_entries=6, show_spinner=False)
def fetch_spreadsheet_data(spreadsheet_id):
    ws_names = [SHEET_REQUEST, SHEET_PJB, SHEET_UM, SHEET_DISTRIBUSI, SHEET_APP, "Rekap PJB", SHEET_TIKET_PM, SHEET_ABSENSI]
    data = {name: [] for name in ws_names}
    
    # Sistem Auto-Retry: Jika Google Sheets sedang sibuk (Error 429), tunggu & coba lagi otomatis hingga 4x
    for attempt in range(4):
        try:
            client = gspread.authorize(get_credentials()).open_by_key(spreadsheet_id)
            for name in ws_names:
                try:
                    raw_rows = client.worksheet(name).get_all_values()
                    clean_rows = [r[:40] for r in raw_rows if any(str(cell).strip() != "" for cell in r)]
                    data[name] = clean_rows
                    del raw_rows
                except Exception:
                    data[name] = []
            gc.collect()
            return data
        except Exception:
            if attempt < 3:
                time.sleep(2.5 * (attempt + 1))
            else:
                break
    gc.collect()
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

@st.cache_resource(ttl=3600, show_spinner=False)
def load_excel_data():
    site_dict, site_list = {}, []
    try:
        df_site_pky = pd.read_excel("Hasil_910_Site.xlsx").fillna(0)
        try:
            df_site_pbun = pd.read_excel("Site ID Sidata Pangkalanbun.xlsx").fillna(0)
            df_site = pd.concat([df_site_pky, df_site_pbun], ignore_index=True)
            del df_site_pbun
        except Exception:
            df_site = df_site_pky
        del df_site_pky
        site_dict = df_site.set_index('Site ID')[['Latitude Tujuan', 'Longtitude Tujuan']].to_dict('index')
        site_list = df_site['Site ID'].astype(str).tolist()
        del df_site
    except Exception: pass
    
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
        del df_tim
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
        del df_nopol
    except Exception: pass

    try:
        # Nama file disesuaikan dengan file terbaru Mas Okta
        df_tim_pbun = pd.read_excel("NAMA NOP PANGKALANBUN.xlsx").fillna("")
        
        col_lat_pbun = next((c for c in df_tim_pbun.columns if 'lat' in str(c).lower()), None)
        col_lon_pbun = next((c for c in df_tim_pbun.columns if 'lon' in str(c).lower() or 'lng' in str(c).lower()), None)

        for _, row in df_tim_pbun.iterrows():
            nama = str(row.get('NAMA', '')).strip().upper()
            if nama and nama not in ["NAN", ""]:
                if nama not in tim_dict:
                    tim_dict[nama] = {'Latitude': 0.0, 'Longtitude': 0.0}
                
                if col_lat_pbun and str(row.get(col_lat_pbun, "")).strip() not in ["", "0", "NAN"]:
                    try: tim_dict[nama]['Latitude'] = float(str(row[col_lat_pbun]).replace(',', '.'))
                    except: pass
                if col_lon_pbun and str(row.get(col_lon_pbun, "")).strip() not in ["", "0", "NAN"]:
                    try: tim_dict[nama]['Longtitude'] = float(str(row[col_lon_pbun]).replace(',', '.'))
                    except: pass
                    
                if str(row.get('ROLE', '')).strip():
                    tim_dict[nama]['ROLE'] = str(row.get('ROLE', '')).strip().upper()
                    
                nopol = str(row.get('NOPOL', '')).strip().upper()
                if nopol and nopol not in ["NAN", "0", "NONE", ""]:
                    tim_dict[nama]['NOPOL'] = nopol
                    if nopol not in list_nopol_csv:
                        list_nopol_csv.append(nopol)
        del df_tim_pbun
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
                del df_nik
    except Exception: pass
        
    gc.collect()
    return site_dict, site_list, tim_dict, list_nopol_csv, nik_dict
SHEET_MASTER_TIM = "Master Tim"

@st.cache_data(ttl=600, max_entries=6, show_spinner=False)
def fetch_master_tim_sheet(spreadsheet_id):
    """Membaca tab 'Master Tim' dari Google Sheets (Cache 10 menit agar hemat kuota API)."""
    try:
        client = gspread.authorize(get_credentials()).open_by_key(spreadsheet_id)
        ws = client.worksheet(SHEET_MASTER_TIM)
        rows = ws.get_all_values()
        return rows if len(rows) > 1 else []
    except Exception:
        return []

def save_master_tim_sheet(spreadsheet_id, list_of_rows):
    """Menyimpan tabel Master Tim & Nopol secara permanen ke Google Sheets."""
    for attempt in range(4):
        try:
            client = gspread.authorize(get_credentials()).open_by_key(spreadsheet_id)
            try:
                ws = client.worksheet(SHEET_MASTER_TIM)
            except Exception:
                ws = client.add_worksheet(title=SHEET_MASTER_TIM, rows=300, cols=10)
            ws.clear()
            header = [["NAMA", "ROLE", "NOPOL", "NIK", "LATITUDE", "LONGITUDE", "STATUS"]]
            ws.update("A1", header + list_of_rows, value_input_option="USER_ENTERED")
            fetch_master_tim_sheet.clear()
            load_excel_data.clear()
            return True
        except Exception as e:
            if attempt < 3:
                time.sleep(2.0 * (attempt + 1))
            else:
                st.error(f"⚠️ Gagal menyimpan Master Tim ke Google Sheets: {e}")
                return False

def sync_dynamic_master_data():
    """Menyinkronkan data dari tab 'Master Tim' Google Sheets ke MASTER_DATA & memori Excel."""
    site_dict, site_list, tim_dict, list_nopol_csv, nik_dict = load_excel_data()
    for nop_key, nop_info in MASTER_DATA.items():
        rows = fetch_master_tim_sheet(nop_info["spreadsheet_id"])
        if len(rows) > 1:
            active_names = []
            for r in rows[1:]:
                r_pad = (r + [""] * 7)[:7]
                nm = str(r_pad[0]).strip().upper()
                rl = str(r_pad[1]).strip()
                npl = str(r_pad[2]).strip().upper()
                nik_v = str(r_pad[3]).strip()
                lat_v = clean_coord(r_pad[4])
                lon_v = clean_coord(r_pad[5])
                st_aktif = str(r_pad[6]).strip().upper() or "AKTIF"

                if npl and npl not in ["", "0", "NAN", "NONE", "-"] and npl not in list_nopol_csv:
                    list_nopol_csv.append(npl)

                if nm and nm not in ["", "NAN", "NONE", "-"]:
                    if st_aktif == "AKTIF" and nm not in active_names:
                        active_names.append(nm)
                    if nm not in tim_dict:
                        tim_dict[nm] = {"Latitude": 0.0, "Longtitude": 0.0}
                    if lat_v != 0.0:
                        tim_dict[nm]["Latitude"] = lat_v
                    if lon_v != 0.0:
                        tim_dict[nm]["Longtitude"] = lon_v
                    if rl and rl not in ["", "-"]:
                        tim_dict[nm]["ROLE"] = rl
                    if npl and npl not in ["", "0", "NAN", "NONE", "-"]:
                        tim_dict[nm]["NOPOL"] = npl
                    if nik_v and nik_v not in ["", "0", "NAN", "NONE", "-"]:
                        nik_dict[nm] = nik_v
            if active_names:
                MASTER_DATA[nop_key]["names"] = active_names

sync_dynamic_master_data()
SHEET_MASTER_KMRH = "Master KM RH"

def normalize_plat_key(plat_raw):
    """Normalisasi Nopol/ID Genset agar 'KH 1234 AB', 'KH-1234-AB', dan 'KH1234AB' terbaca sebagai 1 unit."""
    s = re.sub(r"[^A-Z0-9]", "", str(plat_raw or "").strip().upper())
    return "" if s in ["", "0", "NAN", "NONE"] else s

def _detect_unit_tipe_from_cat(kat_str):
    k = str(kat_str or "").lower()
    if "genset" in k:
        return "Genset"
    if "mobil" in k:
        return "Mobil"
    if "motor" in k:
        return "Motor"
    return ""

@st.cache_data(ttl=300, max_entries=6, show_spinner=False)
def fetch_master_kmrh_sheet(spreadsheet_id):
    """Membaca tab 'Master KM RH' (Patokan / Reset Resmi Admin) dengan cache 5 menit."""
    try:
        client = gspread.authorize(get_credentials()).open_by_key(spreadsheet_id)
        ws = client.worksheet(SHEET_MASTER_KMRH)
        rows = ws.get_all_values()
        return rows if len(rows) > 1 else []
    except Exception:
        return []

def save_master_kmrh_sheet(spreadsheet_id, list_of_rows):
    """Menyimpan daftar Patokan / Override KM & RH secara permanen ke tab 'Master KM RH'."""
    for attempt in range(4):
        try:
            client = gspread.authorize(get_credentials()).open_by_key(spreadsheet_id)
            try:
                ws = client.worksheet(SHEET_MASTER_KMRH)
            except Exception:
                ws = client.add_worksheet(title=SHEET_MASTER_KMRH, rows=300, cols=8)
            ws.clear()
            header = [["PLAT_UNIT", "TIPE", "PATOKAN_TERAKHIR", "TANGGAL_SET", "MODE", "CATATAN", "STATUS"]]
            ws.update("A1", header + list_of_rows, value_input_option="USER_ENTERED")
            fetch_master_kmrh_sheet.clear()
            fetch_spreadsheet_data.clear()
            return True
        except Exception as e:
            if attempt < 3:
                time.sleep(2.0 * (attempt + 1))
            else:
                st.error(f"⚠️ Gagal menyimpan Master KM/RH ke Google Sheets: {e}")
                return False

def get_kmrh_override_map(spreadsheet_id):
    """Mengembalikan dictionary override aktif keyed by (plat_norm, tipe_lower)."""
    ov_map = {}
    if not spreadsheet_id:
        return ov_map
    rows = fetch_master_kmrh_sheet(spreadsheet_id)
    for r in rows[1:]:
        r_pad = (r + [""] * 7)[:7]
        p_raw = str(r_pad[0]).strip().upper()
        p_norm = normalize_plat_key(p_raw)
        tp = str(r_pad[1]).strip()
        val = clean_indicator(r_pad[2])
        tgl_s = str(r_pad[3]).strip()
        mode_s = str(r_pad[4]).strip().upper() or "AUTO"
        cat_s = str(r_pad[5]).strip() or "-"
        st_s = str(r_pad[6]).strip().upper() or "AKTIF"
        if p_norm and st_s == "AKTIF":
            ov_map[(p_norm, tp.lower())] = {
                "plat_display": p_raw,
                "tipe": tp,
                "value": float(val),
                "timestamp_str": tgl_s or "-",
                "dt_obj": parse_timestamp_dt(tgl_s, tgl_s),
                "mode": mode_s,
                "catatan": cat_s
            }
    return ov_map

def fetch_raw_sheet_rows(spreadsheet_id, sheet_name):
    """Membaca baris mentah Google Sheets TANPA membuang baris kosong agar nomor baris (1-indexed) 100% akurat untuk edit."""
    for attempt in range(4):
        try:
            client = gspread.authorize(get_credentials()).open_by_key(spreadsheet_id)
            ws = client.worksheet(sheet_name)
            return ws.get_all_values()
        except Exception:
            if attempt < 3:
                time.sleep(2.0 * (attempt + 1))
            else:
                return []
    return []

def batch_update_sheet_cells(spreadsheet_id, sheet_name, updates_list):
    """
    Update massal banyak sel dalam 1x API call (hemat kuota Google Sheets + Auto-Retry).
    updates_list = [{"range": "M15", "values": [["125450"]]}, ...]
    """
    if not updates_list:
        return True
    for attempt in range(4):
        try:
            client = gspread.authorize(get_credentials()).open_by_key(spreadsheet_id)
            ws = client.worksheet(sheet_name)
            ws.batch_update(updates_list, value_input_option="USER_ENTERED")
            fetch_spreadsheet_data.clear()
            return True
        except Exception as e:
            if attempt < 3:
                time.sleep(2.5 * (attempt + 1))
            else:
                st.error(f"⚠️ Gagal menyimpan edit ke sheet '{sheet_name}': {e}")
                return False

def _build_rejected_ticket_sets(app_r):
    """Membangun set tiket PJB & Request yang berstatus REJECTED agar tidak meracuni urutan KM/RH."""
    rej_pjb, rej_req = set(), set()
    if not app_r or len(app_r) <= 1:
        return rej_pjb, rej_req
    pjb_latest, req_latest = {}, {}
    for a in app_r[1:]:
        a_pad = (a + [""] * 7)[:7]
        tk = str(a_pad[2]).strip().upper()
        jns = str(a_pad[3]).strip()
        stt = str(a_pad[5]).strip().upper()
        if not tk:
            continue
        if jns == "Verifikasi PJB":
            pjb_latest[tk] = stt
        elif jns == "Request Dana":
            req_latest[tk] = stt
    rej_pjb = {tk for tk, s in pjb_latest.items() if s == "REJECTED"}
    rej_req = {tk for tk, s in req_latest.items() if s == "REJECTED"}
    return rej_pjb, rej_req

def get_last_indicator(plat_raw, jns, pjb_r, app_r=None, spreadsheet_id=None):
    info = get_last_indicator_detail(plat_raw, jns, pjb_r, req_r=None, app_r=app_r, spreadsheet_id=spreadsheet_id)
    return float(info.get("value", 0.0))

def get_last_indicator_detail(plat_raw, jns, pjb_r, req_r=None, app_r=None, spreadsheet_id=None):
    """
    Pembacaan KM Mobil/Motor & RH Genset Terakhir yang AMAN:
    1. Normalisasi Nopol/ID Genset (abaikan spasi & tanda hubung).
    2. Melewati tiket PJB/Request yang berstatus REJECTED (anti keracunan salah ketik).
    3. Menghormati Patokan/Reset Resmi Admin di sheet 'Master KM RH' (mode AUTO maupun PAKSA/RESET_METER).
    4. Menyaring angka korup ekstrem (>2.000.000 KM atau >100.000 RH) agar tim tidak pernah terkunci oleh typo masa lalu.
    """
    empty_res = {"value": 0.0, "timestamp_str": "-", "dt_obj": None, "source": "-", "tiket": "-", "pic": "-", "override_note": ""}
    plat_norm = normalize_plat_key(plat_raw)
    if not plat_norm:
        return empty_res

    jns_low = str(jns or "").strip().lower()
    max_sane = 100000.0 if jns_low == "genset" else 2000000.0
    rej_pjb, rej_req = _build_rejected_ticket_sets(app_r)

    # 1. Cek apakah ada Patokan/Override Admin aktif di 'Master KM RH'
    ov_rec = None
    if spreadsheet_id:
        ov_map = get_kmrh_override_map(spreadsheet_id)
        ov_rec = ov_map.get((plat_norm, jns_low))

    # Jika mode PAKSA, langsung gunakan patokan Admin
    if ov_rec and ov_rec.get("mode") == "PAKSA":
        return {
            "value": ov_rec["value"],
            "timestamp_str": ov_rec["timestamp_str"],
            "dt_obj": ov_rec["dt_obj"],
            "source": f"Patokan Admin ({ov_rec['catatan']})",
            "tiket": "ADMIN-OVERRIDE",
            "pic": "Admin",
            "override_note": ov_rec["catatan"]
        }

    # 2. Cari histori valid terbaru di Form PJB (prioritas utama), lalu cadangan di Form Request dana
    candidates = []
    if pjb_r and len(pjb_r) > 1:
        for row_i, r in enumerate(pjb_r[1:], start=2):
            if len(r) > 12:
                h_plat = normalize_plat_key(r[12])
                kat_p = str(r[8]).lower() if len(r) > 8 else ""
                if h_plat == plat_norm and (jns_low in kat_p):
                    tk = str(r[21]).strip().upper() if len(r) > 21 else ""
                    if tk and tk in rej_pjb:
                        continue
                    val = clean_indicator(r[10])
                    if 0 < val <= max_sane:
                        ts_s = str(r[0]).strip() if len(r) > 0 else ""
                        tgl_s = str(r[1]).strip() if len(r) > 1 else ""
                        dt_o = parse_timestamp_dt(ts_s, tgl_s)
                        candidates.append({
                            "prio": 2,
                            "dt_sort": dt_o or datetime(1970, 1, 1),
                            "row_i": row_i,
                            "value": val,
                            "timestamp_str": ts_s or tgl_s or "-",
                            "dt_obj": dt_o,
                            "source": "PJB Terakhir",
                            "tiket": tk or "-",
                            "pic": str(r[4]).strip() if len(r) > 4 else "-",
                            "override_note": ""
                        })

    if req_r and len(req_r) > 1:
        for row_i, r in enumerate(req_r[1:], start=2):
            if len(r) > 16:
                h_plat = normalize_plat_key(r[16])
                kat_r = str(r[10]).lower() if len(r) > 10 else ""
                if h_plat == plat_norm and (jns_low in kat_r):
                    tk = str(r[3]).strip().upper() if len(r) > 3 else ""
                    if tk and tk in rej_req:
                        continue
                    val = clean_indicator(r[12])
                    if 0 < val <= max_sane:
                        ts_s = str(r[0]).strip() if len(r) > 0 else ""
                        tgl_s = str(r[1]).strip() if len(r) > 1 else ""
                        dt_o = parse_timestamp_dt(ts_s, tgl_s)
                        candidates.append({
                            "prio": 1,
                            "dt_sort": dt_o or datetime(1970, 1, 1),
                            "row_i": row_i,
                            "value": val,
                            "timestamp_str": ts_s or tgl_s or "-",
                            "dt_obj": dt_o,
                            "source": "Request Terakhir",
                            "tiket": tk or "-",
                            "pic": str(r[5]).strip() if len(r) > 5 else "-",
                            "override_note": ""
                        })

    # Jika ada Patokan Admin (AUTO / RESET_METER), bandingkan waktunya dengan histori PJB/Request
    if ov_rec:
        ov_dt = ov_rec.get("dt_obj") or datetime(1970, 1, 1)
        # Hanya ambil transaksi PJB/Request yang terjadi SETELAH Admin menetapkan patokan
        newer_cands = [c for c in candidates if c["dt_sort"] > ov_dt]
        if newer_cands:
            newer_cands.sort(key=lambda x: (x["dt_sort"], x["prio"], x["row_i"]))
            best = newer_cands[-1]
            return {k: best[k] for k in ["value", "timestamp_str", "dt_obj", "source", "tiket", "pic", "override_note"]}
        return {
            "value": ov_rec["value"],
            "timestamp_str": ov_rec["timestamp_str"],
            "dt_obj": ov_rec["dt_obj"],
            "source": f"Patokan Admin ({ov_rec['mode']})",
            "tiket": "ADMIN-PATOKAN",
            "pic": "Admin",
            "override_note": ov_rec["catatan"]
        }

    if not candidates:
        return empty_res

    # Utamakan PJB terbaru; jika ada Request yang lebih baru dari PJB terakhir, pakai yang paling kronologis terbaru
    pjb_cands = [c for c in candidates if c["prio"] == 2]
    if pjb_cands:
        pjb_cands.sort(key=lambda x: (x["dt_sort"], x["row_i"]))
        best_pjb = pjb_cands[-1]
        # Cek apakah ada Request valid yang lebih baru dari PJB terakhir dengan nilai >= PJB terakhir
        req_newer = [c for c in candidates if c["prio"] == 1 and c["dt_sort"] > best_pjb["dt_sort"] and c["value"] >= best_pjb["value"]]
        if req_newer:
            req_newer.sort(key=lambda x: (x["dt_sort"], x["row_i"]))
            best = req_newer[-1]
        else:
            best = best_pjb
        return {k: best[k] for k in ["value", "timestamp_str", "dt_obj", "source", "tiket", "pic", "override_note"]}

    candidates.sort(key=lambda x: (x["dt_sort"], x["row_i"]))
    best = candidates[-1]
    return {k: best[k] for k in ["value", "timestamp_str", "dt_obj", "source", "tiket", "pic", "override_note"]}

def build_unit_full_history(req_r, pjb_r, app_r=None, spreadsheet_id=None):
    """
    Membangun historikal lengkap kronologis KM (Mobil/Motor) & RH (Genset MBP)
    untuk setiap nomor plat / ID genset beserta deteksi urutan (Lurus / Mundur / Lonjakan).
    """
    rej_pjb, rej_req = _build_rejected_ticket_sets(app_r)
    ov_map = get_kmrh_override_map(spreadsheet_id) if spreadsheet_id else {}

    req_by_tiket = {}
    unit_records = defaultdict(list)
    unit_meta = {}

    for idx_r, r in enumerate(req_r[1:], start=2):
        r_pad = (r + [""] * 25)[:25]
        tp = _detect_unit_tipe_from_cat(r_pad[10])
        p_raw = re.sub(r'\s+', ' ', str(r_pad[16]).strip().upper())
        p_norm = normalize_plat_key(p_raw)
        if not tp or not p_norm:
            continue
        tk = str(r_pad[3]).strip().upper()
        val_ind = clean_indicator(r_pad[12])
        dt_o = parse_timestamp_dt(r_pad[0], r_pad[1])
        tgl_d = parse_date(r_pad[1], r_pad[0])
        tgl_str = tgl_d.strftime("%d/%m/%Y") if tgl_d != datetime(1970, 1, 1).date() else str(r_pad[1]).strip()
        is_rej = tk in rej_req

        req_by_tiket[tk] = {"km_awal": val_ind, "tgl": tgl_str, "plat": p_raw}
        ukey = (p_norm, tp)
        if ukey not in unit_meta:
            unit_meta[ukey] = {"plat": p_raw, "tipe": tp, "unit": "RH" if tp == "Genset" else "KM"}
        unit_records[ukey].append({
            "dt_sort": dt_o or datetime(1970, 1, 1),
            "order_type": 0,
            "row_idx": idx_r,
            "Tanggal": tgl_str,
            "Timestamp": str(r_pad[0]).strip() or tgl_str,
            "Sumber": "📝 Request",
            "No Tiket": tk,
            "Nama PIC": str(r_pad[5]).strip(),
            "Kategori": str(r_pad[10]).strip(),
            "KM/RH Awal": val_ind,
            "KM/RH Akhir": None,
            "Nilai Utama": val_ind,
            "Trip/Run": 0.0,
            "Liter": 0.0,
            "Nominal": clean_nominal(r_pad[9]),
            "Rejected": is_rej
        })

    for idx_p, p in enumerate(pjb_r[1:], start=2):
        p_pad = (p + [""] * 40)[:40]
        tp = _detect_unit_tipe_from_cat(p_pad[8])
        p_raw = re.sub(r'\s+', ' ', str(p_pad[12]).strip().upper())
        p_norm = normalize_plat_key(p_raw)
        if not tp or not p_norm:
            continue
        tk = str(p_pad[21]).strip().upper()
        val_akhir = clean_indicator(p_pad[10])
        val_awal = req_by_tiket.get(tk, {}).get("km_awal", 0.0)
        trip_c = clean_indicator(p_pad[24])
        if trip_c > 0:
            trip_v = trip_c
        elif val_akhir > val_awal and val_awal > 0:
            trip_v = round(val_akhir - val_awal, 2)
        else:
            trip_v = 0.0
        lit_v, _, _ = parse_indonesian_indicator(p_pad[22], 0.0, "Liter") if str(p_pad[22]).strip() else (0.0, "ok", "")
        dt_o = parse_timestamp_dt(p_pad[0], p_pad[1])
        tgl_d = parse_date(p_pad[1], p_pad[0])
        tgl_str = tgl_d.strftime("%d/%m/%Y") if tgl_d != datetime(1970, 1, 1).date() else str(p_pad[1]).strip()
        is_rej = tk in rej_pjb

        ukey = (p_norm, tp)
        if ukey not in unit_meta:
            unit_meta[ukey] = {"plat": p_raw, "tipe": tp, "unit": "RH" if tp == "Genset" else "KM"}
        unit_records[ukey].append({
            "dt_sort": dt_o or datetime(1970, 1, 1),
            "order_type": 1,
            "row_idx": idx_p,
            "Tanggal": tgl_str,
            "Timestamp": str(p_pad[0]).strip() or tgl_str,
            "Sumber": "✅ PJB",
            "No Tiket": tk,
            "Nama PIC": str(p_pad[4]).strip(),
            "Kategori": str(p_pad[8]).strip(),
            "KM/RH Awal": val_awal if val_awal > 0 else None,
            "KM/RH Akhir": val_akhir,
            "Nilai Utama": val_akhir,
            "Trip/Run": round(trip_v, 2),
            "Liter": round(lit_v, 2),
            "Nominal": clean_nominal(p_pad[11]),
            "Rejected": is_rej
        })

    # Tambahkan unit yang hanya ada di Master KM RH
    for (p_norm, tp_low), ov in ov_map.items():
        tp_cap = ov["tipe"]
        ukey = (p_norm, tp_cap)
        if ukey not in unit_meta:
            unit_meta[ukey] = {"plat": ov["plat_display"], "tipe": tp_cap, "unit": "RH" if tp_cap == "Genset" else "KM"}

    summary_units = []
    history_by_unit = {}

    for ukey, meta in sorted(unit_meta.items(), key=lambda kv: (kv[1]["tipe"], kv[1]["plat"])):
        p_norm, tp = ukey
        unit_lbl = meta["unit"]
        recs = sorted(unit_records.get(ukey, []), key=lambda x: (x["dt_sort"], x["order_type"], x["row_idx"]))

        prev_valid = 0.0
        anom_cnt = 0
        tot_trip = 0.0
        tot_liter = 0.0
        tot_dana = 0
        last_val = 0.0
        last_tgl = "-"
        last_pic = "-"
        pjb_cnt = 0
        req_cnt = 0

        enriched = []
        for rec in recs:
            v = float(rec["Nilai Utama"] or 0.0)
            if rec["Sumber"] == "✅ PJB":
                pjb_cnt += 1
            else:
                req_cnt += 1

            if rec["Rejected"]:
                st_urut = "❌ REJECTED (Diabaikan)"
                sel_prev = 0.0
            else:
                if rec["Sumber"] == "✅ PJB":
                    tot_trip = round(tot_trip + max(0.0, rec["Trip/Run"]), 2)
                    tot_liter = round(tot_liter + max(0.0, rec["Liter"]), 2)
                    tot_dana += rec["Nominal"]
                if v <= 0:
                    st_urut = "⚠️ Kosong / 0"
                    sel_prev = 0.0
                    anom_cnt += 1
                elif prev_valid > 0 and v < prev_valid:
                    sel_prev = round(v - prev_valid, 2)
                    st_urut = f"🔴 MUNDUR ({sel_prev:+g} {unit_lbl})"
                    anom_cnt += 1
                elif prev_valid >= 100 and v > prev_valid * 5 and (v - prev_valid) > (500 if tp == "Genset" else 5000):
                    sel_prev = round(v - prev_valid, 2)
                    st_urut = f"🚨 LONJAKAN (+{format_id_number(sel_prev)} {unit_lbl})"
                    anom_cnt += 1
                else:
                    sel_prev = round(v - prev_valid, 2) if prev_valid > 0 else 0.0
                    st_urut = "✅ Lurus"
                    prev_valid = v
                    last_val = v
                    last_tgl = rec["Tanggal"]
                    last_pic = rec["Nama PIC"]

            enriched.append({
                "Tanggal": rec["Tanggal"],
                "Waktu": rec["Timestamp"],
                "Sumber": rec["Sumber"],
                "No Tiket": rec["No Tiket"],
                "Nama PIC": rec["Nama PIC"],
                "Kategori": rec["Kategori"],
                f"{unit_lbl} Awal": rec["KM/RH Awal"],
                f"{unit_lbl} Akhir": rec["KM/RH Akhir"],
                f"Angka {unit_lbl}": v,
                f"Selisih Urutan ({unit_lbl})": sel_prev,
                f"Trip/Run PJB ({unit_lbl})": rec["Trip/Run"],
                "BBM (Liter)": rec["Liter"],
                "Nominal (Rp)": rec["Nominal"],
                "Status Urutan": st_urut
            })

        ov_r = ov_map.get((p_norm, tp.lower()))
        ov_txt = f"{format_id_number(ov_r['value'])} {unit_lbl} [{ov_r['mode']}]" if ov_r else "-"
        if ov_r and last_val == 0:
            last_val = ov_r["value"]
            last_tgl = ov_r["timestamp_str"]

        if tp == "Genset":
            eff_txt = f"{(tot_liter / tot_trip):.2f} L/RH" if tot_trip > 0 and tot_liter > 0 else "-"
        else:
            eff_txt = f"{(tot_trip / tot_liter):.2f} KM/L" if tot_liter > 0 and tot_trip > 0 else "-"

        status_unit = "🟢 Lurus / Aman" if anom_cnt == 0 else f"🔴 {anom_cnt} Anomali Urutan"

        summary_units.append({
            "unit_key": ukey,
            "Nopol / ID Unit": meta["plat"],
            "Tipe": tp,
            "PIC Terakhir": last_pic,
            "Tgl Terakhir": last_tgl,
            "KM/RH Terakhir": last_val,
            "Satuan": unit_lbl,
            "Req / PJB": f"{req_cnt} / {pjb_cnt}",
            "Total Akumulasi Trip/Run": tot_trip,
            "Total Liter": tot_liter,
            "Total Dana PJB": tot_dana,
            "Efisiensi": eff_txt,
            "Patokan Admin": ov_txt,
            "Anomali": anom_cnt,
            "Status Urutan": status_unit
        })
        history_by_unit[ukey] = enriched

    return summary_units, history_by_unit

def build_nopol_distance_summary(pjb_r, req_r):
    """Membangun rekapitulasi jarak & odometer/RH terakhir per Nopol/ID Unit serta KM awal per tiket."""
    req_info_map = {}
    for rq in req_r[1:]:
        if len(rq) > 12 and str(rq[3]).strip():
            tk = str(rq[3]).strip().upper()
            req_info_map[tk] = {
                "km_awal": float(clean_indicator(rq[12])),
                "jarak_satelit": str(rq[13]).strip() if len(rq) > 13 else "-",
                "desc": str(rq[11]).strip() if len(rq) > 11 else "",
                "plat": str(rq[16]).strip().upper() if len(rq) > 16 else "",
                "tgl": str(rq[1]).strip() if len(rq) > 1 else ""
            }

    nopol_stats = {}
    for pjb in pjb_r[1:]:
        if len(pjb) > 12:
            plat_raw = str(pjb[12]).strip().upper()
            plat_clean = re.sub(r'\s+', ' ', plat_raw)
            if not plat_clean or plat_clean in ["0", "NONE", "NAN", "-"]:
                continue
            kat_str = str(pjb[8]).lower() if len(pjb) > 8 else ""
            is_gen = "genset" in kat_str
            is_veh = is_gen or ("mobil" in kat_str) or ("motor" in kat_str)
            if not is_veh:
                continue

            tk = str(pjb[21]).strip().upper() if len(pjb) > 21 else ""
            km_akhir_v = float(clean_indicator(pjb[10])) if len(pjb) > 10 else 0.0
            trip_col_v = float(clean_indicator(pjb[24])) if len(pjb) > 24 else 0.0
            km_awal_v = req_info_map.get(tk, {}).get("km_awal", 0.0)
            if trip_col_v > 0:
                trip_v = trip_col_v
            elif km_akhir_v > km_awal_v and km_awal_v > 0:
                trip_v = round(km_akhir_v - km_awal_v, 2)
            else:
                trip_v = 0.0

            tgl_d = parse_date(pjb[1] if len(pjb) > 1 else "", pjb[0] if len(pjb) > 0 else "")
            tgl_fmt = tgl_d.strftime("%d/%m/%Y") if tgl_d != datetime(1970, 1, 1).date() else "-"

            if plat_clean not in nopol_stats:
                nopol_stats[plat_clean] = {
                    "unit": "RH" if is_gen else "KM",
                    "last_odo": 0.0,
                    "total_trip": 0.0,
                    "trip_count": 0,
                    "last_date": tgl_fmt,
                    "last_pic": str(pjb[4]).strip() if len(pjb) > 4 else "-"
                }
            st_n = nopol_stats[plat_clean]
            st_n["trip_count"] += 1
            st_n["total_trip"] = round(st_n["total_trip"] + max(0.0, trip_v), 2)
            if km_akhir_v >= st_n["last_odo"]:
                st_n["last_odo"] = km_akhir_v
                st_n["last_date"] = tgl_fmt
                st_n["last_pic"] = str(pjb[4]).strip() if len(pjb) > 4 else "-"
    return nopol_stats, req_info_map

def generate_daily_finance_wa_report(nop_name, target_date, data_all, selected_batch="Semua Batch", extra_note=""):
    """Menyusun teks WA Report Harian Penggunaan Dana & Sisa Saldo Uang Muka (UM)."""
    um_r = data_all.get(SHEET_UM, [])
    dist_r = data_all.get(SHEET_DISTRIBUSI, [])
    req_r = data_all.get(SHEET_REQUEST, [])
    pjb_r = data_all.get(SHEET_PJB, [])
    rekap_r = data_all.get("Rekap PJB", [])
    app_r = data_all.get(SHEET_APP, [])

    now_wib = get_now_wib()
    tgl_str = target_date.strftime("%d/%m/%Y")
    d1 = target_date.strftime("%d/%m/%Y")
    d2 = target_date.strftime("%m/%d/%Y")
    d3 = target_date.strftime("%Y-%m-%d")

    def _is_date_match(raw_tgl, raw_ts):
        rt1, rt2 = str(raw_tgl or "").strip(), str(raw_ts or "").strip()
        if (d1 in rt1 or d2 in rt1 or d3 in rt1) or (d1 in rt2 or d2 in rt2 or d3 in rt2):
            return True
        return parse_date(rt1, rt2) == target_date

    # 1. Hitung Kas / Uang Muka Masuk & Distribusi per Batch
    in_by_batch = {}
    for r in um_r[1:]:
        if len(r) > 3 and str(r[2]).strip():
            b = str(r[2]).strip()
            in_by_batch[b] = in_by_batch.get(b, 0) + clean_nominal(r[3])

    out_by_batch = {}
    dist_today_items = []
    tot_dist_today = 0
    for r in dist_r[1:]:
        if len(r) > 4 and str(r[2]).strip():
            b = str(r[2]).strip()
            nom_d = clean_nominal(r[4])
            out_by_batch[b] = out_by_batch.get(b, 0) + nom_d
            if selected_batch == "Semua Batch" or b == selected_batch:
                if _is_date_match(r[1] if len(r) > 1 else "", r[0] if len(r) > 0 else ""):
                    tot_dist_today += nom_d
                    pic_d = str(r[3]).strip() if len(r) > 3 else "-"
                    ket_d = str(r[5]).strip() if len(r) > 5 else ""
                    ket_short = ket_d.replace("AUTO-SUPPORT:", "").strip() if not ket_d.startswith("http") else "Transfer Manual"
                    dist_today_items.append(f"  • {pic_d} ({ket_short}): Rp {nom_d:,.0f}")

    if selected_batch != "Semua Batch":
        tot_um_in = in_by_batch.get(selected_batch, 0)
        tot_dist_all = out_by_batch.get(selected_batch, 0)
        batch_label = selected_batch
    else:
        tot_um_in = sum(in_by_batch.values())
        tot_dist_all = sum(out_by_batch.values())
        batch_label = f"Semua Batch ({len(in_by_batch)} Batch)"

    sisa_um_dist = tot_um_in - tot_dist_all

    # Total Penyerapan Rekap PJB
    tot_rekap_pjb = 0
    for r in rekap_r[1:]:
        if len(r) > 15:
            val_q = str(r[16]).strip() if len(r) > 16 else ""
            if selected_batch == "Semua Batch" or val_q == selected_batch:
                tot_rekap_pjb += clean_nominal(r[15])
    sisa_um_pjb = tot_um_in - tot_rekap_pjb

    # 2. Request Dana Hari Ini (Pending vs Total)
    processed_req = set()
    rejected_req = set()
    for a in app_r[1:]:
        a_pad = (a + [""] * 8)[:8]
        if str(a_pad[3]).strip() == "Request Dana":
            st_a = str(a_pad[5]).strip().upper()
            tk_a = str(a_pad[2]).strip().upper()
            if st_a in ["APPROVED", "REJECTED"] and tk_a:
                processed_req.add(tk_a)
            if st_a == "REJECTED" and tk_a:
                rejected_req.add(tk_a)

    req_today_cnt = 0
    req_today_nom = 0
    req_pending_cnt = 0
    req_pending_nom = 0
    for r in req_r[1:]:
        if len(r) > 9:
            tk_r = str(r[3]).strip().upper()
            if tk_r in rejected_req:
                continue
            if _is_date_match(r[1], r[0]):
                nom_r = clean_nominal(r[9])
                req_today_cnt += 1
                req_today_nom += nom_r
                if tk_r not in processed_req:
                    req_pending_cnt += 1
                    req_pending_nom += nom_r

    # 3. PJB Disubmit Hari Ini + Breakdown Kategori
    pjb_today_cnt = 0
    pjb_today_nom = 0
    pjb_kat_breakdown = defaultdict(int)
    pjb_done_set = set()
    for p in pjb_r[1:]:
        p_pad = (p + [""] * 40)[:40]
        tk_s = str(p_pad[36]).strip().upper()
        tk_b = str(p_pad[21]).strip().upper()
        if tk_s and tk_s not in ["-", "NAN", "NONE", "0"]: pjb_done_set.add(tk_s)
        if tk_b and tk_b not in ["-", "NAN", "NONE", "0"]: pjb_done_set.add(tk_b)
        if _is_date_match(p_pad[1], p_pad[0]):
            nom_p = clean_nominal(p_pad[11])
            pjb_today_cnt += 1
            pjb_today_nom += nom_p
            kat_raw = str(p_pad[8]).strip() or "Lainnya"
            kl = kat_raw.lower()
            if "mobil" in kl: kat_grp = "BBM Mobil"
            elif "motor" in kl: kat_grp = "BBM Motor"
            elif "genset" in kl: kat_grp = "BBM Genset"
            elif "uang makan" in kl or "akomodasi" in kl: kat_grp = "Uang Makan"
            elif "penginapan" in kl: kat_grp = "Penginapan"
            elif "material" in kl: kat_grp = "Material"
            elif "fery" in kl or "klotok" in kl: kat_grp = "Transportasi Air"
            else: kat_grp = "Support / Lainnya"
            pjb_kat_breakdown[kat_grp] += nom_p

    # 4. Hitung PJB Gantung (Aging)
    out_cnt = 0
    out_nom = 0
    overdue_cnt = 0
    for r in req_r[1:]:
        r_pad = (r + [""] * 15)[:15]
        tk_c = str(r_pad[3]).strip().upper()
        if not tk_c or tk_c in rejected_req or tk_c in pjb_done_set:
            continue
        tgl_r = parse_date(r_pad[1], r_pad[0])
        if tgl_r >= CUTOFF_DATE:
            out_cnt += 1
            out_nom += clean_nominal(r_pad[9])
            if (now_wib.date() - tgl_r).days > 7:
                overdue_cnt += 1

    # Rincian Batch Aktif (yang masih bersaldo != 0, maks 6 batch terbaru)
    batch_lines = []
    if selected_batch == "Semua Batch":
        for b_name in sorted(in_by_batch.keys(), reverse=True)[:6]:
            b_in = in_by_batch[b_name]
            b_out = out_by_batch.get(b_name, 0)
            b_sisa = b_in - b_out
            batch_lines.append(f"  • {b_name}: Sisa *Rp {b_sisa:,.0f}* (UM Rp {b_in:,.0f} | Cair Rp {b_out:,.0f})")

    lines_wa = [
        f"*📊 REPORT HARIAN PENGGUNAAN DANA & SISA UM (SiRAPI)*",
        f"🌐 Wilayah : *NOP {nop_name.upper()}*",
        f"📅 Tanggal : {tgl_str} (Update {now_wib.strftime('%H:%M WIB')})",
        f"💼 Filter UM : {batch_label}",
        "",
        "*1. 🏦 POSISI SALDO UANG MUKA (UM)*",
        f"• Total Uang Muka Masuk : Rp {tot_um_in:,.0f}",
        f"• Total Distribusi ke Tim : Rp {tot_dist_all:,.0f}",
        f"• *Sisa Saldo UM (Kas) : Rp {sisa_um_dist:,.0f}*",
        f"• Total Serapan Rekap PJB : Rp {tot_rekap_pjb:,.0f} (Sisa vs PJB: Rp {sisa_um_pjb:,.0f})",
    ]
    if batch_lines:
        lines_wa.append("*📌 Rincian Saldo per Batch UM:*")
        lines_wa.extend(batch_lines)

    lines_wa.extend([
        "",
        f"*2. 💸 PENGGUNAAN DANA HARI INI ({tgl_str})*",
        f"• Dana Cair / Distribusi Hari Ini : *Rp {tot_dist_today:,.0f}* ({len(dist_today_items)} transaksi)",
    ])
    if dist_today_items:
        lines_wa.extend(dist_today_items[:12])
        if len(dist_today_items) > 12:
            lines_wa.append(f"  • ...dan {len(dist_today_items) - 12} transaksi lainnya")
    lines_wa.extend([
        f"• Request Masuk Hari Ini : {req_today_cnt} tiket (Rp {req_today_nom:,.0f})",
        f"• Menunggu Approval Hari Ini : {req_pending_cnt} tiket (Rp {req_pending_nom:,.0f})",
        "",
        f"*3. ✅ LAPORAN PJB DISUBMIT HARI INI ({tgl_str})*",
        f"• Total PJB Masuk : {pjb_today_cnt} tiket (*Rp {pjb_today_nom:,.0f}*)",
    ])
    if pjb_kat_breakdown:
        for k_grp, k_nom in sorted(pjb_kat_breakdown.items(), key=lambda x: -x[1]):
            lines_wa.append(f"  • {k_grp} : Rp {k_nom:,.0f}")
    lines_wa.extend([
        "",
        "*4. 🚨 STATUS TIKET BELUM PJB (AGING)*",
        f"• Total Tiket Gantung : {out_cnt} tiket (Rp {out_nom:,.0f})",
        f"• Overdue (>7 Hari) : {overdue_cnt} tiket",
    ])
    if extra_note and extra_note.strip():
        lines_wa.extend(["", f"*📝 Catatan Admin:*", extra_note.strip()])
    lines_wa.extend(["", "_Generated automatically via SiRAPI KUT System_"])

    return "\n".join(lines_wa), {
        "tot_um_in": tot_um_in, "tot_dist_all": tot_dist_all, "sisa_um_dist": sisa_um_dist,
        "tot_dist_today": tot_dist_today, "pjb_today_nom": pjb_today_nom, "out_cnt": out_cnt
    }

def get_user_tickets_status(nama, req_rows, pjb_rows, app_rows):
    if nama == "-- Pilih Nama --" or not str(nama).strip():
        return [], [], [], []
    nama_clean = str(nama).strip().upper()
    
    req_tickets = {}
    for r in req_rows[1:]:
        if len(r) > 5 and str(r[5]).strip().upper() == nama_clean:
            tk_raw = str(r[3]).strip().upper()
            if tk_raw != "":
                req_tickets[tk_raw] = (r[1] if len(r) > 1 else "", r[0] if len(r) > 0 else "")
                
    pjb_tickets_all_set = set()
    for r in pjb_rows[1:]:
        if len(r) > 21 and str(r[4]).strip().upper() == nama_clean and str(r[21]).strip() != "":
            tk_str = r[36].strip() if (len(r) > 36 and str(r[36]).strip()) else str(r[21]).strip()
            pjb_tickets_all_set.update([t.strip().upper() for t in tk_str.split(",") if t.strip()])
            pjb_tickets_all_set.add(str(r[21]).strip().upper())
            
    pjb_app_status = {}
    req_app_status = {}
    for r in app_rows[1:]:
        if len(r) > 5:
            tiket_app = str(r[2]).strip().upper()
            jns_app = str(r[3]).strip()
            st_app = str(r[5]).strip().upper()
            if jns_app == "Verifikasi PJB" and tiket_app != "":
                pjb_app_status[tiket_app] = {"status": st_app, "catatan": r[6] if len(r) > 6 else ""}
            elif jns_app == "Request Dana" and tiket_app != "":
                req_app_status[tiket_app] = st_app

    outstanding_all, outstanding_lock, aging_tickets, history = [], [], [], []
    today = datetime.now().date()
    
    for req_tk_raw, (tgl_str, ts_str) in req_tickets.items():
        req_tk_list = [t.strip() for t in req_tk_raw.split(",") if t.strip()]
        req_set = set(req_tk_list)
        tgl_tampil = tgl_str if str(tgl_str).strip() else str(ts_str).split(" ")[0]
        
        if req_app_status.get(req_tk_raw) == "REJECTED":
            history.append({"Tiket": req_tk_raw, "Tanggal": tgl_tampil, "Status": "❌ REQUEST DITOLAK Admin (Harap Ajukan Ulang)"})
            continue
            
        if not req_set.issubset(pjb_tickets_all_set):
            outstanding_all.append(req_tk_raw)
            req_date = parse_date(tgl_str, ts_str)
            if req_date >= CUTOFF_DATE:
                outstanding_lock.append(req_tk_raw)
            aging_days = (today - req_date).days if req_date != datetime(1970, 1, 1).date() else 0
            
            if req_date >= CUTOFF_DATE and aging_days > 3:
                aging_tickets.append(req_tk_raw)
                history.append({"Tiket": req_tk_raw, "Tanggal": tgl_tampil, "Status": f"🚨 Telat {aging_days} Hari (Belum PJB)"})
            else:
                history.append({"Tiket": req_tk_raw, "Tanggal": tgl_tampil, "Status": "🔴 Menunggu PJB (Belum Selesai)"})
        else:
            app_data = pjb_app_status.get(req_tk_raw, {"status": "APPROVED", "catatan": ""})
            if app_data["status"] == "PENDING":
                outstanding_all.append(req_tk_raw)
                outstanding_lock.append(req_tk_raw)
                history.append({"Tiket": req_tk_raw, "Tanggal": tgl_tampil, "Status": "⏳ PJB Menunggu Verifikasi Admin"})
            elif app_data["status"] == "REJECTED":
                outstanding_all.append(req_tk_raw)
                outstanding_lock.append(req_tk_raw)
                history.append({"Tiket": req_tk_raw, "Tanggal": tgl_tampil, "Status": f"❌ PJB DITOLAK: {app_data['catatan']}"})
            else:
                history.append({"Tiket": req_tk_raw, "Tanggal": tgl_tampil, "Status": "🟢 PJB Selesai & Approved"})
            
    return outstanding_all, outstanding_lock, aging_tickets, sorted(history, key=lambda x: x["Status"], reverse=True)

CLOUDINARY_ACCOUNTS = [
    # 1. Akun Utama Baru (Aktif Sekarang)
    {
        "cloud_name": "ji9i1hei",
        "api_key": "277523771179144",
        "api_secret": "7eg20WV-Bzf9DXEoT8rg3H99V6c"
    },
    # 2. Akun Cadangan (Otomatis dipakai jika akun utama penuh / saat kuota bulanan akun lama sudah reset)
    {
        "cloud_name": "fxm61tjv",
        "api_key": "624877324969231",
        "api_secret": "LIFO6pfEg9fOM3nbsY8FBbVTpSI"
    }
]

def upload_foto(file):
    return upload_foto_compressed(file)

def upload_foto_compressed(file):
    if file is None:
        return ""
    try:
        raw_bytes = file.getvalue()
        with Image.open(io.BytesIO(raw_bytes)) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            # Kompresi optimal 960px (quality 55): gambar tetap jelas di PDF A4 namun hemat kuota Cloudinary hingga 75%
            img.thumbnail((960, 960))
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG', quality=55, optimize=True)
            img_byte_arr.seek(0)
            encoded = base64.b64encode(img_byte_arr.read()).decode('utf-8')
            img_byte_arr.close()
        del raw_bytes

        for acc in CLOUDINARY_ACCOUNTS:
            try:
                cloudinary.config(
                    cloud_name=acc["cloud_name"],
                    api_key=acc["api_key"],
                    api_secret=acc["api_secret"],
                    secure=True
                )
                res = cloudinary.uploader.upload(
                    f"data:image/jpeg;base64,{encoded}",
                    resource_type="auto"
                )
                url = res.get("secure_url", "")
                if url:
                    del encoded
                    gc.collect()
                    return url
            except Exception:
                continue

        del encoded
        gc.collect()
        return ""
    except Exception:
        gc.collect()
        return ""
@st.cache_data(ttl=3600, max_entries=1, show_spinner=False)
def get_local_img_base64(filepath):
    try:
        with open(filepath, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            return f"data:image/webp;base64,{encoded_string}"
    except Exception:
        return ""

def append_data(sheet_name, data, spreadsheet_id):
    safe_data = [str(x) if x is not None else "" for x in data]
    # Coba otomatis hingga 4 kali jika koneksi Google sedang antre
    for attempt in range(4):
        try:
            client = gspread.authorize(get_credentials()).open_by_key(spreadsheet_id)
            ws = client.worksheet(sheet_name)
            ws.append_row(safe_data, value_input_option="USER_ENTERED", table_range="A1", insert_data_option="INSERT_ROWS")
            fetch_spreadsheet_data.clear()
            return True
        except Exception as e:
            if attempt < 3:
                time.sleep(2.5 * (attempt + 1))
            else:
                st.error(f"⚠️ Server Google sedang padat, silakan klik tombol Submit sekali lagi. Detail: {e}")
                return False

def append_data_multiple(sheet_name, list_of_data, spreadsheet_id):
    safe_list = [[str(x) if x is not None else "" for x in data] for data in list_of_data]
    # Coba otomatis hingga 4 kali & kirim dalam 1x paket (Hemat Kuota API & Anti-Tumpuk)
    for attempt in range(4):
        try:
            client = gspread.authorize(get_credentials()).open_by_key(spreadsheet_id)
            ws = client.worksheet(sheet_name)
            try:
                ws.append_rows(safe_list, value_input_option="USER_ENTERED", table_range="A1", insert_data_option="INSERT_ROWS")
            except TypeError:
                for row_data in safe_list:
                    ws.append_row(row_data, value_input_option="USER_ENTERED", table_range="A1", insert_data_option="INSERT_ROWS")
                    time.sleep(1.2)
            fetch_spreadsheet_data.clear()
            return True
        except Exception as e:
            if attempt < 3:
                time.sleep(2.5 * (attempt + 1))
            else:
                st.error(f"⚠️ Server Google sedang padat, silakan klik tombol Submit sekali lagi. Detail: {e}")
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
    except Exception:
        pass 

# ==========================================
# 3. INISIALISASI SESSION STATE & NAVIGASI (BEBAS RECURSION ERROR)
# ==========================================
if 'page' not in st.session_state: st.session_state.page = "🏠 Hub Menu Utama"
if 'admin_logged_in' not in st.session_state: st.session_state.admin_logged_in = False
if 'pdf_ready' not in st.session_state: st.session_state.pdf_ready = False
if 'logged_in_user' not in st.session_state: st.session_state.logged_in_user = ""
if 'selected_nop' not in st.session_state: st.session_state.selected_nop = ""
if 'req_wa_ready' not in st.session_state: st.session_state.req_wa_ready = ""

if st.session_state.page != "🏠 Hub Menu Utama":
    c_nav1, c_nav2 = st.columns([1, 4])
    with c_nav1:
        if st.button("← Beranda", use_container_width=True, key="btn_home"):
            st.session_state.page = "🏠 Hub Menu Utama"
            st.session_state.pdf_ready = False
            st.session_state.req_wa_ready = ""
            st.rerun()
    with c_nav2:
        if st.session_state.selected_nop:
            _cls_area = "pbu" if st.session_state.selected_nop == "Pangkalanbun" else ""
            st.markdown(f"<div class='area-chip {_cls_area}'><i></i>NOP {st.session_state.selected_nop}</div>", unsafe_allow_html=True)

# ==========================================
# 4. SIDEBAR NAVIGATION & SHORTCUT SIDATA
# ==========================================
list_menu_sidebar = ["🏠 Hub Menu Utama", "📝 Form Request Dana", "✅ Form PJB Operasional"]

def ubah_menu():
    st.session_state.page = st.session_state.sb_menu

idx_menu = list_menu_sidebar.index(st.session_state.page) if st.session_state.page in list_menu_sidebar else 0
st.sidebar.selectbox("Navigasi Utama", list_menu_sidebar, index=idx_menu, key="sb_menu", on_change=ubah_menu)

st.sidebar.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)
st.sidebar.markdown("<h3 style='text-align: center; color: #1E293B;'>📊 Wajib Lapor</h3>", unsafe_allow_html=True)
st.sidebar.info("Khusus Role TE, MBP, & CME: Wajib lapor hasil kegiatan lapangan (Tshoot/PM) ke database SIDATA.")
st.sidebar.markdown(
    '''
    <a href="https://sidata.streamlit.app/" target="_blank" style="display: block; text-align: center; background-color: #EF4444; color: white !important; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: 700; font-size: 15px; box-shadow: 0 4px 6px rgba(239,68,68,0.2);">
        👉 BUKA PORTAL SIDATA
    </a>
    ''', unsafe_allow_html=True
)

# ==========================================
# PAGE 0: HUB MENU UTAMA (LENGKAP: AREA OPERASIONAL + CEK TIKET PENDING + MODE ADMIN)
# ==========================================
if st.session_state.page == "🏠 Hub Menu Utama":
    
    # 1. HEADER BERANDA
    logo_b64 = get_local_img_base64("koperasi-jasa-konstruksi-tower-event-organizer-network-monitoring-telekomunikasi-kisel-group-logo-kut.webp")
    if logo_b64:
        logo_html = f'<img src="{logo_b64}" alt="Kinarya Utama Teknik">'
    else:
        logo_html = '<div><div style="font-weight:900; font-size:1.25rem; color:#1E293B !important; letter-spacing:1px;">KINARYA</div><div style="font-weight:600; font-size:0.75rem; color:#64748B !important;">UTAMA TEKNIK</div></div>'

    st.markdown(f"""
        <div class="hub-head">
            <div class="hub-logo">{logo_html}</div>
            <div>
                <div class="hub-title">SiRAPI</div>
                <div class="hub-sub">Request dana dan penyelesaian PJB operasional NOP Palangkaraya &amp; Pangkalan Bun</div>
            </div>
        </div>
        <div class="hub-lead">Pilih area kerja Anda</div>
    """, unsafe_allow_html=True)

    # 2. DUA KARTU AREA (Palangkaraya | Pangkalan Bun)
    _areas = [
        ("area_plk", "Palangkaraya", "NOP Palangkaraya", "plk", "Palangkaraya"),
        ("area_pbu", "Pangkalanbun", "NOP Pangkalan Bun", "pbu", "Pangkalan Bun"),
    ]
    _cols_area = st.columns(2, gap="large")
    for _col, (_key, _nop, _judul, _kode, _nama_link) in zip(_cols_area, _areas):
        with _col:
            with _wz_box(_key):
                st.markdown(
                    f'<div class="area-name">{_judul}</div>'
                    f'<div class="area-cluster">Cluster {", ".join(MASTER_DATA[_nop]["clusters"])}</div>'
                    f'<div class="area-meta"><b>{len(MASTER_DATA[_nop]["names"])}</b> personel terdaftar</div>',
                    unsafe_allow_html=True
                )
                _b1, _b2 = st.columns(2)
                with _b1:
                    if st.button("Request Dana", type="primary", use_container_width=True, key=f"req_{_kode}_card"):
                        st.session_state.selected_nop = _nop
                        st.session_state.req_nop = _nop
                        st.session_state.req_wa_ready = ""
                        st.session_state.page = "📝 Form Request Dana"
                        st.rerun()
                with _b2:
                    if st.button("Penyelesaian PJB", type="secondary", use_container_width=True, key=f"pjb_{_kode}_card"):
                        st.session_state.selected_nop = _nop
                        st.session_state.page = "✅ Form PJB Operasional"
                        st.rerun()
                st.markdown(
                    f'<a class="area-link" href="https://sidata.streamlit.app/" target="_blank" rel="noopener">Isi laporan SiDATA {_nama_link}</a>',
                    unsafe_allow_html=True
                )

    st.markdown('<div class="hub-note">Role TE, MBP, dan CME wajib melapor hasil kegiatan lapangan (Tshoot/PM) ke SiDATA.</div>', unsafe_allow_html=True)

    # 3. CEK STATUS TIKET PRIBADI & TIM BELUM PJB (LANGSUNG TAMPIL TERBUKA DI BERANDA)
    st.markdown("<hr style='margin: 35px 0 20px 0; border-color: #CBD5E1;'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Cek status tiket</div>", unsafe_allow_html=True)
    
    # Default langsung ke Palangkaraya (index=0) agar tab Cek Tiket Pending langsung terbuka di layar!
    cek_nop = st.selectbox("Pilih Area Wilayah Pengecekan", list(MASTER_DATA.keys()), index=0, key="cek_area_hub")
    
    tab_pribadi, tab_tim_pending = st.tabs(["👤 Cek Status Pribadi Anda", "🚨 Daftar Tim Belum PJB (Tiket Pending)"])
    
    with tab_pribadi:
        c_p1, c_p2 = st.columns([3, 1])
        with c_p1:
            cek_nama = st.selectbox("Nama Petugas", ["-- Pilih Nama --"] + MASTER_DATA[cek_nop]["names"], key="cek_nama_hub")
        with c_p2:
            st.markdown("<div style='height: 26px;'></div>", unsafe_allow_html=True)
            btn_cari_pribadi = st.button("🔍 Cari Status Saya", type="secondary", use_container_width=True)
            
        if btn_cari_pribadi:
            if cek_nama != "-- Pilih Nama --" and cek_nama != "":
                with st.spinner("Menarik data server..."):
                    fetch_spreadsheet_data.clear()
                    data_cek = fetch_spreadsheet_data(MASTER_DATA[cek_nop]["spreadsheet_id"])
                    out_all, out_lock, aging_tickets, hist_tkt = get_user_tickets_status(cek_nama, data_cek[SHEET_REQUEST], data_cek[SHEET_PJB], data_cek[SHEET_APP])
                if hist_tkt:
                    st.dataframe(pd.DataFrame(hist_tkt), hide_index=True, use_container_width=True)
                    if aging_tickets: st.warning(f"🔔 PENGINGAT: Ada {len(aging_tickets)} request tertunda >3 Hari. Tolong segera di-PJB!")
                    if out_lock: st.error(f"⚠️ {len(out_lock)} Request aktif memblokir status Anda (Belum PJB / Pending Verifikasi).")
                    else: st.success("✅ Seluruh tiket aktif aman dan Approved!")
                else:
                    st.info("Tidak ada data / belum pernah request.")
            else:
                st.warning("Silakan pilih Nama Petugas terlebih dahulu.")
                
    with tab_tim_pending:
        st.info(f"Menampilkan daftar seluruh tiket tim wilayah **{cek_nop}** yang masih gantung (belum disubmit PJB) mulai Agustus 2026 dst.")
        if st.button(f"🚨 Tarik Data Tim Belum PJB ({cek_nop})", use_container_width=True, type="primary"):
            with st.spinner(f"Memindai seluruh data tim wilayah {cek_nop}..."):
                fetch_spreadsheet_data.clear()
                data_cek = fetch_spreadsheet_data(MASTER_DATA[cek_nop]["spreadsheet_id"])
                req_r, pjb_r, app_r = data_cek[SHEET_REQUEST], data_cek[SHEET_PJB], data_cek[SHEET_APP]
                
                all_names_in_sheet = sorted(list(set(
                    [nm.strip().upper() for nm in MASTER_DATA[cek_nop]["names"] if nm.strip()] +
                    [str(r[5]).strip().upper() for r in req_r[1:] if len(r) > 5 and str(r[5]).strip()]
                )))
                
                list_blm_pjb = []
                for nm in all_names_in_sheet:
                    _, _, _, hist_tkt = get_user_tickets_status(nm, req_r, pjb_r, app_r)
                    for h in hist_tkt:
                        tgl_req = parse_date(h["Tanggal"])
                        if tgl_req >= CUTOFF_DATE:
                            if "Menunggu PJB" in h["Status"] or "Telat" in h["Status"] or "DITOLAK" in h["Status"]:
                                list_blm_pjb.append({
                                    "Nama Petugas": nm,
                                    "No Tiket / Request": h["Tiket"],
                                    "Tanggal Request": h["Tanggal"],
                                    "Status Terkini": h["Status"]
                                })
                if list_blm_pjb:
                    st.error(f"⚠️ Ditemukan {len(list_blm_pjb)} tiket aktif di {cek_nop} yang belum selesai PJB!")
                    st.dataframe(pd.DataFrame(list_blm_pjb), hide_index=True, use_container_width=True)
                else:
                    st.success(f"🎉 Luar biasa! Seluruh tim di wilayah {cek_nop} sudah menyelesaikan PJB aktif.")

    # 4. MENU ADMIN (dilipat agar tidak mengganggu tim lapangan)
    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    with st.expander("Menu admin", expanded=bool(st.session_state.admin_logged_in)):
        if not st.session_state.admin_logged_in:
            c_adm1, c_adm2 = st.columns([3, 1])
            with c_adm1:
                pass_input = st.text_input("Masukkan Password Admin (Pusat):", type="password", placeholder="Ketik kata sandi admin...", key="pwd_admin_main")
            with c_adm2:
                st.markdown("<div style='height: 26px;'></div>", unsafe_allow_html=True)
                if st.button("🔓 Buka Kunci Akses Admin", type="primary", use_container_width=True, key="btn_login_admin_main"):
                    if pass_input in AUTHORIZED_PASSWORDS:
                        st.session_state.admin_logged_in = True
                        st.rerun()
                    else:
                        st.error("❌ Password Admin Salah!")
        else:
            st.success("✅ Akses Mode Admin Terbuka")
            if st.button("🔒 Keluar Mode Admin", type="primary", key="btn_logout_admin_main"):
                st.session_state.admin_logged_in = False
                st.rerun()
            
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            c_top_adm1, c_top_adm2 = st.columns(2)
            with c_top_adm1:
                if st.button("🎫 MASTER TIKET PM (Input Data PM Bulanan)", type="secondary", use_container_width=True):
                    st.session_state.page = "🎫 Master Tiket PM"
                    st.rerun()
            with c_top_adm2:
                if st.button("👥 MASTER TIM & NOPOL (Tambah/Edit Nama & Plat)", type="primary", use_container_width=True):
                    st.session_state.page = "👥 Master Tim & Nopol"
                    st.rerun()
        
            c_a1, c_a2 = st.columns(2)
            with c_a1:
                if st.button("🛡️ APPROVAL CENTER (Validasi PJB & Revisi)", type="secondary", use_container_width=True):
                    st.session_state.page = "🛡️ Approval Center"
                    st.rerun()
                if st.button("📈 LIVE MONITORING (Dashboard Analisa)", type="secondary", use_container_width=True):
                    st.session_state.page = "📈 Live Monitoring"
                    st.rerun()
                if st.button("👀 REQ & PJB MONITORING (Pantau Tim & Warning)", type="primary", use_container_width=True):
                    st.session_state.page = "👀 Request & PJB Monitoring"
                    st.rerun()
                if st.button("🔧 KONTROL, EDIT & HISTORI KM/RH (Mobil & Genset)", type="secondary", use_container_width=True):
                    st.session_state.page = "🔧 Kontrol & Edit KM/RH"
                    st.rerun()
            with c_a2:
                if st.button("🏦 MANAJEMEN KAS (Distribusi Dana)", type="secondary", use_container_width=True):
                    st.session_state.page = "🏦 Manajemen Kas & Distribusi"
                    st.rerun()
                if st.button("🖨️ REPORT & AUTO PJB (Export Laporan)", type="secondary", use_container_width=True):
                    st.session_state.page = "🖨️ Auto PJB Report"
                    st.rerun()
                if st.button("📢 INFO UPDATE SERVER & WA (Broadcast)", type="primary", use_container_width=True):
                    st.session_state.page = "📢 Info Update Server & WA"
                    st.rerun()

    st.markdown("<div class='hub-foot'>Created by Okta Pradika<br>KUT SYSTEM - SiRAPI AI V5 Enterprise Edition</div>", unsafe_allow_html=True)# PAGE ADMIN: MASTER TIKET PM
# ==========================================
# ==========================================
# PAGE ADMIN: KONTROL, EDIT & HISTORI KM MOBIL / MOTOR & RH GENSET MBP
# ==========================================
elif st.session_state.page == "🔧 Kontrol & Edit KM/RH":
    st.markdown("<div class='header-card'><h2>🔧 KONTROL, EDIT & HISTORI KM / RH UNIT</h2><p>Audit Historikal Per Plat & Genset MBP, Edit & Luruskan Urutan KM/RH ke Google Sheets, dan Set Patokan Resmi</p></div>", unsafe_allow_html=True)

    c_kn1, c_kn2 = st.columns([3, 1])
    with c_kn1:
        nop_kmrh = st.selectbox("📂 Pilih Wilayah Database (NOP):", ["-- Pilih NOP --"] + list(MASTER_DATA.keys()), key="sel_nop_kmrh")
    with c_kn2:
        st.markdown("<div style='height: 26px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Refresh Data Live", type="secondary", use_container_width=True, key="btn_ref_kmrh"):
            fetch_spreadsheet_data.clear()
            fetch_master_kmrh_sheet.clear()
            st.rerun()

    if nop_kmrh != "-- Pilih NOP --":
        target_ss = MASTER_DATA[nop_kmrh]["spreadsheet_id"]
        with st.spinner("Menarik database KM/RH & riwayat unit dari server..."):
            data_all = fetch_spreadsheet_data(target_ss)
            req_r = data_all.get(SHEET_REQUEST, [])
            pjb_r = data_all.get(SHEET_PJB, [])
            app_r = data_all.get(SHEET_APP, [])
            summary_units, history_by_unit = build_unit_full_history(req_r, pjb_r, app_r=app_r, spreadsheet_id=target_ss)

        tab_hist, tab_edit, tab_patokan = st.tabs([
            "📊 1. Historikal KM & RH per Plat / Genset",
            "✏️ 2. Edit & Luruskan Urutan KM/RH (Live Sheets)",
            "🎯 3. Set / Reset Patokan KM & RH (Buka Kunci Req)"
        ])

        # ------------------------------------------------------------------
        # TAB 1: HISTORIKAL KM & RH SETIAP PLAT MOBIL/MOTOR & GENSET MBP
        # ------------------------------------------------------------------
        with tab_hist:
            st.markdown("#### 📋 Rekapitulasi Seluruh Nomor Plat Mobil/Motor & ID Genset MBP")
            if summary_units:
                df_units = pd.DataFrame(summary_units)
                cf_t1, cf_t2 = st.columns(2)
                with cf_t1:
                    flt_tipe_u = st.selectbox("🔍 Filter Tipe Unit:", ["Semua Tipe", "Mobil", "Genset", "Motor"], key="flt_tipe_kmrh")
                with cf_t2:
                    flt_st_u = st.selectbox("🛡️ Filter Status Urutan:", ["Semua Status", "🔴 Hanya Yang Ada Anomali Urutan", "🟢 Lurus / Aman"], key="flt_st_kmrh")

                df_u_flt = df_units.copy()
                if flt_tipe_u != "Semua Tipe":
                    df_u_flt = df_u_flt[df_u_flt["Tipe"] == flt_tipe_u]
                if "Anomali" in flt_st_u:
                    df_u_flt = df_u_flt[df_u_flt["Anomali"] > 0]
                elif "Lurus" in flt_st_u:
                    df_u_flt = df_u_flt[df_u_flt["Anomali"] == 0]

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("🚗 Total Unit Terdata", f"{len(df_u_flt)} Unit")
                m2.metric("🟢 Urutan Lurus", f"{len(df_u_flt[df_u_flt['Anomali'] == 0])} Unit")
                m3.metric("🔴 Perlu Diluruskan", f"{len(df_u_flt[df_u_flt['Anomali'] > 0])} Unit")
                m4.metric("🎯 Pakai Patokan Admin", f"{len(df_u_flt[df_u_flt['Patokan Admin'] != '-'])} Unit")

                df_u_show = df_u_flt.drop(columns=["unit_key", "Anomali"], errors="ignore").copy()
                df_u_show["KM/RH Terakhir"] = df_u_show.apply(lambda r: f"{format_id_number(r['KM/RH Terakhir'])} {r['Satuan']}", axis=1)
                df_u_show["Total Akumulasi Trip/Run"] = df_u_show.apply(lambda r: f"{format_id_number(r['Total Akumulasi Trip/Run'])} {r['Satuan']}", axis=1)
                df_u_show["Total Liter"] = df_u_show["Total Liter"].apply(lambda x: f"{format_id_number(x)} L")
                df_u_show["Total Dana PJB"] = df_u_show["Total Dana PJB"].apply(lambda x: f"Rp {x:,.0f}")
                st.dataframe(df_u_show.drop(columns=["Satuan"], errors="ignore"), hide_index=True, use_container_width=True)

                st.download_button(
                    "📥 Download Rekap Seluruh Unit KM/RH (CSV)",
                    data=df_u_flt.drop(columns=["unit_key"], errors="ignore").to_csv(index=False).encode("utf-8"),
                    file_name=f"Rekap_KMRH_Unit_{nop_kmrh}_{get_now_wib().strftime('%d%m%Y')}.csv",
                    mime="text/csv"
                )

                st.markdown("<hr>", unsafe_allow_html=True)
                st.markdown("#### 🔎 Detail Historikal Kronologis per Nopol / Genset MBP")
                unit_options_map = {}
                for _, ur in df_u_flt.iterrows():
                    badge_u = "🔴" if ur["Anomali"] > 0 else "🟢"
                    lbl_u = f"{badge_u} [{ur['Tipe'].upper()}] {ur['Nopol / ID Unit']} — Terakhir: {format_id_number(ur['KM/RH Terakhir'])} {ur['Satuan']}"
                    unit_options_map[lbl_u] = (ur["unit_key"], ur["Nopol / ID Unit"], ur["Tipe"], ur["Satuan"])

                if unit_options_map:
                    pick_unit_lbl = st.selectbox("Pilih Nomor Plat / ID Genset untuk melihat riwayat lengkap:", list(unit_options_map.keys()), key="sel_unit_hist")
                    sel_ukey, sel_plat_disp, sel_tipe_disp, sel_satuan = unit_options_map[pick_unit_lbl]
                    hist_rows = history_by_unit.get(sel_ukey, [])
                    if hist_rows:
                        df_h = pd.DataFrame(hist_rows)
                        df_h_view = df_h.copy()
                        df_h_view["Nominal (Rp)"] = df_h_view["Nominal (Rp)"].apply(lambda x: f"Rp {x:,.0f}")
                        st.dataframe(df_h_view, hide_index=True, use_container_width=True)

                        # Grafik Tren KM / RH
                        col_angka = f"Angka {sel_satuan}"
                        df_chart = df_h[(~df_h["Status Urutan"].str.contains("REJECTED")) & (df_h[col_angka] > 0)].copy()
                        if len(df_chart) >= 2:
                            df_chart["Urutan"] = [f"{i+1}. {t}" for i, t in enumerate(df_chart["Tanggal"])]
                            st.markdown(f"##### 📈 Grafik Tren {sel_satuan} — {sel_plat_disp} ({sel_tipe_disp})")
                            st.line_chart(df_chart.set_index("Urutan")[col_angka], use_container_width=True)

                        st.download_button(
                            f"📥 Export Historikal {sel_plat_disp} (CSV)",
                            data=df_h.to_csv(index=False).encode("utf-8"),
                            file_name=f"Histori_{sel_tipe_disp}_{normalize_plat_key(sel_plat_disp)}.csv",
                            mime="text/csv",
                            key="dl_hist_single"
                        )
                    else:
                        st.info("Belum ada catatan transaksi Request/PJB untuk unit ini (baru terdaftar di Patokan Admin).")
            else:
                st.info("Belum ada data kendaraan atau genset yang tercatat di wilayah ini.")

        # ------------------------------------------------------------------
        # TAB 2: EDIT & LURUSKAN URUTAN KM / RH LANGSUNG KE GOOGLE SHEETS
        # ------------------------------------------------------------------
        with tab_edit:
            st.markdown("#### ✏️ Edit Langsung KM Mobil/Motor & RH Genset (Luruskan Urutan di Google Sheets)")
            st.info(
                "💡 **CARA MELURUSKAN URUTAN KM/RH:** Pilih Nomor Plat / ID Genset yang datanya salah ketik (mundur/lonjakan), "
                "ubah angkanya pada kolom **Edit Baru** (ketik angka polos tanpa titik ribuan, contoh: `125450` atau `1450,5`), "
                "lalu klik **💾 Simpan Koreksi**. Sistem otomatis meluruskan Google Sheets & menghitung ulang `Total Trip/RH`, sehingga tim langsung bisa Request Dana!"
            )

            all_unit_choices = sorted(list(set([f"[{u['Tipe'].upper()}] {u['Nopol / ID Unit']}" for u in summary_units])))
            if not all_unit_choices:
                st.warning("Belum ada unit yang dapat diedit.")
            else:
                c_ed1, c_ed2 = st.columns([3, 1])
                with c_ed1:
                    pilih_unit_edit = st.selectbox("🎯 Pilih Plat Mobil/Motor atau ID Genset yang akan diedit:", all_unit_choices, key="sel_unit_edit")
                with c_ed2:
                    st.markdown("<div style='height: 26px;'></div>", unsafe_allow_html=True)
                    btn_load_raw = st.button("📥 Muat Baris Asli Sheets", type="primary", use_container_width=True, key="btn_load_raw_kmrh")

                # Parse pilihan [TIPE] PLAT
                m_ed = re.match(r"^\[(.*?)\]\s+(.*)$", pilih_unit_edit)
                ed_tipe = m_ed.group(1).title() if m_ed else "Mobil"
                ed_plat_disp = m_ed.group(2).strip() if m_ed else pilih_unit_edit
                ed_plat_norm = normalize_plat_key(ed_plat_disp)
                ed_unit_lbl = "RH" if ed_tipe == "Genset" else "KM"

                if btn_load_raw or st.session_state.get("_kmrh_loaded_key") == f"{nop_kmrh}|{pilih_unit_edit}":
                    if btn_load_raw:
                        with st.spinner("Mengambil nomor baris persis dari Google Sheets..."):
                            st.session_state["_kmrh_raw_req"] = fetch_raw_sheet_rows(target_ss, SHEET_REQUEST)
                            st.session_state["_kmrh_raw_pjb"] = fetch_raw_sheet_rows(target_ss, SHEET_PJB)
                            st.session_state["_kmrh_loaded_key"] = f"{nop_kmrh}|{pilih_unit_edit}"

                    raw_req_rows = st.session_state.get("_kmrh_raw_req", [])
                    raw_pjb_rows = st.session_state.get("_kmrh_raw_pjb", [])

                    req_edit_list = []
                    req_km_map_live = {}
                    for sheet_row_no, r in enumerate(raw_req_rows[1:], start=2):
                        r_pad = (r + [""] * 25)[:25]
                        tp_r = _detect_unit_tipe_from_cat(r_pad[10])
                        if tp_r.lower() == ed_tipe.lower() and normalize_plat_key(r_pad[16]) == ed_plat_norm:
                            tk_r = str(r_pad[3]).strip().upper()
                            v_old = clean_indicator(r_pad[12])
                            req_km_map_live[tk_r] = v_old
                            req_edit_list.append({
                                "Baris Sheet": sheet_row_no,
                                "Tanggal": str(r_pad[1]).strip() or str(r_pad[0]).split(" ")[0],
                                "Sub-Tiket": tk_r,
                                "Nama PIC": str(r_pad[5]).strip(),
                                "Kategori": str(r_pad[10]).strip(),
                                "Plat / ID Unit": str(r_pad[16]).strip().upper(),
                                f"{ed_unit_lbl} Awal (Lama)": str(r_pad[12]).strip(),
                                f"{ed_unit_lbl} Awal (Edit Baru)": str(int(v_old)) if v_old == int(v_old) else str(v_old),
                            })

                    pjb_edit_list = []
                    for sheet_row_no, p in enumerate(raw_pjb_rows[1:], start=2):
                        p_pad = (p + [""] * 40)[:40]
                        tp_p = _detect_unit_tipe_from_cat(p_pad[8])
                        if tp_p.lower() == ed_tipe.lower() and normalize_plat_key(p_pad[12]) == ed_plat_norm:
                            tk_p = str(p_pad[21]).strip().upper()
                            v_old_p = clean_indicator(p_pad[10])
                            v_awal_ref = req_km_map_live.get(tk_p, 0.0)
                            pjb_edit_list.append({
                                "Baris Sheet": sheet_row_no,
                                "Tanggal": str(p_pad[1]).strip() or str(p_pad[0]).split(" ")[0],
                                "Sub-Tiket": tk_p,
                                "Nama PIC": str(p_pad[4]).strip(),
                                "Kategori": str(p_pad[8]).strip(),
                                "Plat / ID Unit": str(p_pad[12]).strip().upper(),
                                f"{ed_unit_lbl} Awal (Ref)": v_awal_ref,
                                f"{ed_unit_lbl} Akhir (Lama)": str(p_pad[10]).strip(),
                                f"{ed_unit_lbl} Akhir (Edit Baru)": str(int(v_old_p)) if v_old_p == int(v_old_p) else str(v_old_p),
                                f"Trip/Run Lama ({ed_unit_lbl})": str(p_pad[24]).strip(),
                            })

                    st.markdown(f"##### 📝 A. Edit Baris `Form Request dana` ({ed_unit_lbl} Awal — Kolom M & Plat Kolom Q)")
                    if req_edit_list:
                        df_re = pd.DataFrame(req_edit_list)
                        edited_req_km = st.data_editor(
                            df_re,
                            hide_index=True,
                            use_container_width=True,
                            disabled=["Baris Sheet", "Tanggal", "Sub-Tiket", "Nama PIC", "Kategori", f"{ed_unit_lbl} Awal (Lama)"],
                            key=f"ed_req_km_{ed_plat_norm}_{ed_tipe}"
                        )
                    else:
                        edited_req_km = pd.DataFrame()
                        st.info("Tidak ada baris Request Dana untuk unit ini.")

                    st.markdown(f"##### ✅ B. Edit Baris `Form PJB` ({ed_unit_lbl} Akhir — Kolom K, Plat Kolom M & Auto-Hitung Trip Kolom Y)")
                    if pjb_edit_list:
                        df_pe = pd.DataFrame(pjb_edit_list)
                        edited_pjb_km = st.data_editor(
                            df_pe,
                            hide_index=True,
                            use_container_width=True,
                            disabled=["Baris Sheet", "Tanggal", "Sub-Tiket", "Nama PIC", "Kategori", f"{ed_unit_lbl} Awal (Ref)", f"{ed_unit_lbl} Akhir (Lama)", f"Trip/Run Lama ({ed_unit_lbl})"],
                            key=f"ed_pjb_km_{ed_plat_norm}_{ed_tipe}"
                        )
                    else:
                        edited_pjb_km = pd.DataFrame()
                        st.info("Tidak ada baris PJB untuk unit ini.")

                    if not edited_req_km.empty or not edited_pjb_km.empty:
                        if st.button(f"💾 SIMPAN KOREKSI & LURUSKAN URUTAN {ed_plat_disp} KE GOOGLE SHEETS", type="primary", use_container_width=True, key="btn_save_kmrh_edits"):
                            req_updates = []
                            pjb_updates = []
                            parse_errs = []
                            updated_req_awal_map = dict(req_km_map_live)

                            # 1. Kumpulkan perubahan Request Dana
                            if not edited_req_km.empty:
                                col_new_r = f"{ed_unit_lbl} Awal (Edit Baru)"
                                col_old_r = f"{ed_unit_lbl} Awal (Lama)"
                                for idx_i, row_e in edited_req_km.iterrows():
                                    r_no = int(row_e["Baris Sheet"])
                                    tk_e = str(row_e["Sub-Tiket"]).strip().upper()
                                    new_plat_e = str(row_e["Plat / ID Unit"]).strip().upper()
                                    raw_new_v = str(row_e[col_new_r]).strip()
                                    val_parsed, lvl_p, msg_p = parse_indonesian_indicator(raw_new_v, 0.0, ed_unit_lbl)
                                    if lvl_p == "err":
                                        parse_errs.append(f"Request Baris {r_no} ({tk_e}): {msg_p}")
                                        continue
                                    updated_req_awal_map[tk_e] = val_parsed
                                    old_val_num = clean_indicator(row_e[col_old_r])
                                    old_plat_orig = str(req_edit_list[idx_i]["Plat / ID Unit"]).strip().upper()
                                    if abs(val_parsed - old_val_num) > 1e-6 or str(row_e[col_old_r]).strip() != str(val_parsed):
                                        val_str_save = str(int(val_parsed)) if val_parsed == int(val_parsed) else str(val_parsed)
                                        req_updates.append({"range": f"M{r_no}", "values": [[val_str_save]]})
                                    if new_plat_e and new_plat_e != old_plat_orig:
                                        req_updates.append({"range": f"Q{r_no}", "values": [[new_plat_e]]})

                            # 2. Kumpulkan perubahan PJB + Auto-recalculate Kolom Y (Total Trip/Run)
                            if not edited_pjb_km.empty:
                                col_new_p = f"{ed_unit_lbl} Akhir (Edit Baru)"
                                col_old_p = f"{ed_unit_lbl} Akhir (Lama)"
                                for idx_i, row_e in edited_pjb_km.iterrows():
                                    r_no = int(row_e["Baris Sheet"])
                                    tk_e = str(row_e["Sub-Tiket"]).strip().upper()
                                    new_plat_e = str(row_e["Plat / ID Unit"]).strip().upper()
                                    raw_new_v = str(row_e[col_new_p]).strip()
                                    val_parsed, lvl_p, msg_p = parse_indonesian_indicator(raw_new_v, 0.0, ed_unit_lbl)
                                    if lvl_p == "err":
                                        parse_errs.append(f"PJB Baris {r_no} ({tk_e}): {msg_p}")
                                        continue
                                    old_val_num = clean_indicator(row_e[col_old_p])
                                    old_plat_orig = str(pjb_edit_list[idx_i]["Plat / ID Unit"]).strip().upper()
                                    km_awal_baru = updated_req_awal_map.get(tk_e, float(row_e[f"{ed_unit_lbl} Awal (Ref)"]))
                                    trip_baru = round(max(0.0, val_parsed - km_awal_baru), 2) if km_awal_baru > 0 else clean_indicator(row_e[f"Trip/Run Lama ({ed_unit_lbl})"])
                                    old_trip_num = clean_indicator(row_e[f"Trip/Run Lama ({ed_unit_lbl})"])

                                    if abs(val_parsed - old_val_num) > 1e-6 or str(row_e[col_old_p]).strip() != str(val_parsed):
                                        val_str_save = str(int(val_parsed)) if val_parsed == int(val_parsed) else str(val_parsed)
                                        pjb_updates.append({"range": f"K{r_no}", "values": [[val_str_save]]})
                                    if abs(trip_baru - old_trip_num) > 1e-6:
                                        pjb_updates.append({"range": f"Y{r_no}", "values": [[str(trip_baru)]]})
                                    if new_plat_e and new_plat_e != old_plat_orig:
                                        pjb_updates.append({"range": f"M{r_no}", "values": [[new_plat_e]]})

                            if parse_errs:
                                st.error("❌ Gagal validasi angka:\n" + "\n".join([f"- {e}" for e in parse_errs]))
                            elif not req_updates and not pjb_updates:
                                st.info("ℹ️ Tidak ada perubahan nilai yang terdeteksi untuk disimpan.")
                            else:
                                with st.spinner("Menyimpan koreksi KM/RH & meluruskan urutan ke Google Sheets..."):
                                    ok1 = batch_update_sheet_cells(target_ss, SHEET_REQUEST, req_updates) if req_updates else True
                                    ok2 = batch_update_sheet_cells(target_ss, SHEET_PJB, pjb_updates) if pjb_updates else True
                                    if ok1 and ok2:
                                        st.session_state["_kmrh_raw_req"] = fetch_raw_sheet_rows(target_ss, SHEET_REQUEST)
                                        st.session_state["_kmrh_raw_pjb"] = fetch_raw_sheet_rows(target_ss, SHEET_PJB)
                                        st.success(f"🎉 Berhasil meluruskan {len(req_updates)} sel di Request Dana & {len(pjb_updates)} sel di Form PJB! Urutan KM/RH `{ed_plat_disp}` kini sudah lurus dan tim dapat langsung melakukan Request Dana.")
                                        time.sleep(1.5)
                                        st.rerun()

        # ------------------------------------------------------------------
        # TAB 3: SET / RESET PATOKAN KM & RH TERAKHIR (BUKA KUNCI REQUEST TIM)
        # ------------------------------------------------------------------
        with tab_patokan:
            st.markdown("#### 🎯 Set / Reset Patokan KM & RH Terakhir Resmi (Tab `Master KM RH`)")
            st.info(
                "💡 Gunakan fitur ini jika **odometer mobil / hourmeter genset baru diganti (reset ke 0/angka kecil)**, "
                "atau jika ingin **langsung menetapkan angka patokan terakhir resmi** agar tim lapangan segera bisa melakukan Request Dana tanpa terkunci histori lama."
            )

            existing_ov_rows = fetch_master_kmrh_sheet(target_ss)
            ov_table = []
            for r in existing_ov_rows[1:]:
                r_pad = (r + [""] * 7)[:7]
                ov_table.append({
                    "PLAT_UNIT": str(r_pad[0]).strip().upper(),
                    "TIPE": str(r_pad[1]).strip() if str(r_pad[1]).strip() in ["Mobil", "Motor", "Genset"] else "Mobil",
                    "PATOKAN_TERAKHIR": str(r_pad[2]).strip(),
                    "TANGGAL_SET": str(r_pad[3]).strip(),
                    "MODE": str(r_pad[4]).strip().upper() if str(r_pad[4]).strip().upper() in ["AUTO", "PAKSA"] else "AUTO",
                    "CATATAN": str(r_pad[5]).strip(),
                    "STATUS": str(r_pad[6]).strip().upper() if str(r_pad[6]).strip().upper() in ["AKTIF", "NONAKTIF"] else "AKTIF"
                })

            existing_plats = sorted(list(set([u["Nopol / ID Unit"] for u in summary_units])))
            with st.form("form_set_patokan_kmrh"):
                cp1, cp2, cp3 = st.columns(3)
                with cp1:
                    pick_p_ov = st.selectbox("Pilih Plat / ID Genset:", ["-- Ketik Manual --"] + existing_plats)
                    man_p_ov = st.text_input("Atau Ketik Plat / ID Genset Baru:").strip().upper()
                    tp_ov = st.selectbox("Tipe Unit:", ["Mobil", "Genset", "Motor"])
                with cp2:
                    val_ov_raw = st.text_input("Angka Patokan KM / RH Terakhir Resmi (Polos tanpa titik ribuan):", placeholder="Misal: 125450 atau 1450,5")
                    mode_ov = st.selectbox(
                        "Mode Patokan:",
                        ["AUTO", "PAKSA"],
                        help="AUTO = Pakai patokan ini sekarang, otomatis ikut maju saat ada PJB baru setelah tanggal set. PAKSA = Selalu kunci patokan ke angka ini sampai Admin menonaktifkan."
                    )
                with cp3:
                    cat_ov = st.text_input("Alasan / Catatan Koreksi:", value="Koreksi luruskan urutan KM/RH oleh Admin")
                    st.caption(f"⏱️ Waktu Set: `{get_now_wib().strftime('%d/%m/%Y %H:%M:%S WIB')}`")

                if st.form_submit_button("💾 Simpan Patokan Resmi & Buka Kunci Request Tim", type="primary", use_container_width=True):
                    final_p = man_p_ov if (pick_p_ov == "-- Ketik Manual --" or man_p_ov) else pick_p_ov.strip().upper()
                    u_lbl_ov = "RH" if tp_ov == "Genset" else "KM"
                    v_ov_num, lvl_ov, msg_ov = parse_indonesian_indicator(val_ov_raw, 0.0, u_lbl_ov)
                    if not final_p:
                        st.error("❌ Harap pilih atau ketik Nomor Plat / ID Genset!")
                    elif lvl_ov == "err":
                        st.error(f"❌ Angka patokan tidak valid: {msg_ov}")
                    else:
                        v_ov_str = str(int(v_ov_num)) if v_ov_num == int(v_ov_num) else str(v_ov_num)
                        ts_ov_now = get_now_wib().strftime("%d/%m/%Y %H:%M:%S")
                        # Update jika sudah ada unit+tipe sama, atau tambah baris baru
                        replaced = False
                        for row_o in ov_table:
                            if normalize_plat_key(row_o["PLAT_UNIT"]) == normalize_plat_key(final_p) and row_o["TIPE"] == tp_ov:
                                row_o["PLAT_UNIT"] = final_p
                                row_o["PATOKAN_TERAKHIR"] = v_ov_str
                                row_o["TANGGAL_SET"] = ts_ov_now
                                row_o["MODE"] = mode_ov
                                row_o["CATATAN"] = cat_ov
                                row_o["STATUS"] = "AKTIF"
                                replaced = True
                                break
                        if not replaced:
                            ov_table.append({
                                "PLAT_UNIT": final_p, "TIPE": tp_ov, "PATOKAN_TERAKHIR": v_ov_str,
                                "TANGGAL_SET": ts_ov_now, "MODE": mode_ov, "CATATAN": cat_ov, "STATUS": "AKTIF"
                            })
                        rows_save_ov = [[d["PLAT_UNIT"], d["TIPE"], d["PATOKAN_TERAKHIR"], d["TANGGAL_SET"], d["MODE"], d["CATATAN"], d["STATUS"]] for d in ov_table]
                        with st.spinner("Menyimpan patokan resmi ke Google Sheets..."):
                            if save_master_kmrh_sheet(target_ss, rows_save_ov):
                                st.success(f"✅ Patokan resmi `{final_p}` ({tp_ov}) ditetapkan ke **{format_id_number(v_ov_num)} {u_lbl_ov}** ({mode_ov})! Tim langsung bisa melakukan Request Dana.")
                                time.sleep(1.5)
                                st.rerun()

            if ov_table:
                st.markdown("##### 📋 Daftar Patokan / Override KM & RH Tersimpan")
                df_ov = pd.DataFrame(ov_table)
                ed_ov = st.data_editor(
                    df_ov,
                    hide_index=True,
                    use_container_width=True,
                    num_rows="dynamic",
                    column_config={
                        "TIPE": st.column_config.SelectboxColumn("Tipe", options=["Mobil", "Genset", "Motor"], required=True),
                        "MODE": st.column_config.SelectboxColumn("Mode", options=["AUTO", "PAKSA"], required=True),
                        "STATUS": st.column_config.SelectboxColumn("Status", options=["AKTIF", "NONAKTIF"], required=True),
                    },
                    key="ed_master_kmrh_tbl"
                )
                if st.button("💾 Simpan Perubahan Tabel Patokan KM/RH", type="secondary", use_container_width=True, key="btn_save_ov_tbl"):
                    clean_ov_save = []
                    for _, ro in ed_ov.iterrows():
                        p_c = str(ro.get("PLAT_UNIT", "")).strip().upper()
                        if not p_c or p_c in ["NAN", "NONE"]:
                            continue
                        clean_ov_save.append([
                            p_c,
                            str(ro.get("TIPE", "Mobil")).strip(),
                            str(ro.get("PATOKAN_TERAKHIR", "0")).strip(),
                            str(ro.get("TANGGAL_SET", get_now_wib().strftime("%d/%m/%Y %H:%M:%S"))).strip(),
                            str(ro.get("MODE", "AUTO")).strip().upper(),
                            str(ro.get("CATATAN", "-")).strip(),
                            str(ro.get("STATUS", "AKTIF")).strip().upper()
                        ])
                    with st.spinner("Menyimpan perubahan tabel Master KM RH..."):
                        if save_master_kmrh_sheet(target_ss, clean_ov_save):
                            st.success("✅ Tabel Patokan Master KM/RH berhasil diperbarui!")
                            time.sleep(1.5)
                            st.rerun()
            else:
                st.caption("ℹ️ Belum ada patokan/override khusus yang tersimpan di wilayah ini (seluruh unit memakai histori normal Form PJB & Request Dana).")

# ==========================================
# PAGE ADMIN: FORM PEMBERITAHUAN PEMBAHARUAN SERVER & GENERATE WA
# ==========================================
elif st.session_state.page == "📢 Info Update Server & WA":
    st.markdown("<div class='header-card'><h2>📢 FORM PEMBERITAHUAN PEMBAHARUAN SERVER</h2><p>Buat Pengumuman Update / Maintenance SiRAPI & Generate Pesan WhatsApp Siap Kirim</p></div>", unsafe_allow_html=True)

    now_wib_srv = get_now_wib()
    c_sv1, c_sv2 = st.columns(2)
    with c_sv1:
        jenis_info_srv = st.selectbox(
            "📌 Jenis Pemberitahuan:",
            [
                "🚀 Pembaharuan Fitur & Versi Server SiRAPI",
                "🛠️ Maintenance / Perbaikan Server Sementara",
                "✅ Server Sudah Normal & Siap Digunakan Kembali",
                "⚠️ Pengumuman Aturan Operasional / SOP Baru"
            ],
            key="srv_jenis"
        )
        target_wilayah_srv = st.multiselect(
            "🌐 Target Wilayah / Tim Penerima:",
            ["Semua NOP (Kalimantan)", "NOP Palangkaraya", "NOP Pangkalan Bun", "NOP Tarakan", "NOP Pontianak"],
            default=["NOP Palangkaraya", "NOP Pangkalan Bun"],
            key="srv_target"
        )
        versi_srv = st.text_input("🏷️ Versi Aplikasi / Build:", value="SiRAPI V5.3 (Update Terbaru)", key="srv_versi")
        link_app_srv = st.text_input("🔗 Link Aplikasi:", value="https://sirapi-kut.streamlit.app/", key="srv_link")

    with c_sv2:
        tgl_update_srv = st.date_input("📅 Tanggal Efektif:", value=now_wib_srv.date(), key="srv_tgl")
        jam_update_srv = st.text_input("⏰ Jam Update / Jadwal (WIB):", value=now_wib_srv.strftime("%H:%M WIB"), key="srv_jam")
        durasi_maint_srv = ""
        if "Maintenance" in jenis_info_srv:
            durasi_maint_srv = st.text_input("⏳ Estimasi Durasi Maintenance:", value="± 15 - 30 Menit", key="srv_dur")
        pengirim_srv = st.text_input("👤 Pengirim / Penandatangan:", value="Okta Pradika — Engineering Project Control (PT Kinarya Utama Teknik)", key="srv_sender")
        no_wa_tujuan_srv = st.text_input("📱 Nomor WA Tujuan Khusus (Opsional, format 628xxx — kosongkan untuk pilih Grup/Kontak bebas):", value="", key="srv_wa_num")

    st.markdown("<div class='section-title'>📝 Poin Pembaharuan & Informasi</div>", unsafe_allow_html=True)
    preset_updates = [
        "Pilihan Pembelian BBM SPBU vs Eceran dengan validasi harga aktual ketat",
        "Khusus Pembelian Eceran: WAJIB 2 foto tambahan saat PJB (Full foto botol/liter & Bukti bayar toko) dianalisa AI",
        "Wajib mengisi Kapasitas Tangki (1x & 2x Pengisian) untuk Mobil, Motor & Genset agar tidak over request",
        "Penambahan opsi Genset Portable (Pertalite / Pertamax)",
        "Pembaruan Uang Makan: Pekerjaan Atas ganti RRU (<80 KM) berhak Rp 30.000/orang; PP >80 KM tetap Rp 60.000/orang",
        "Live Kontrol Waktu (WIB) & validasi penulisan titik/koma KM Mobil dan RH Genset",
        "Cetak PDF PJB diperbarui menjadi Full 1 Lembar per Foto (ukuran asli) + Kalkulasi Jarak Nopol Terakhir",
        "Peningkatan kestabilan server & sistem Auto-Retry anti error antrean Google Sheets"
    ]
    poin_pilihan_srv = st.multiselect(
        "✅ Pilih Poin Pembaharuan Cepat (Bisa Pilih Lebih Dari 1):",
        preset_updates,
        default=preset_updates[:4] if "Pembaharuan" in jenis_info_srv else [],
        key="srv_poin_pick"
    )
    poin_custom_srv = st.text_area(
        "✏️ Tambahan Keterangan / Poin Khusus (Opsional, 1 baris = 1 poin):",
        height=100,
        placeholder="Contoh:\nTim wajib melampirkan foto nota asli dan jelas\nHarap segera selesaikan PJB tertunda sebelum jam 17.00 WIB",
        key="srv_poin_custom"
    )
    instruksi_tim_srv = st.text_area(
        "🔔 Tindakan Wajib Tim Lapangan:",
        value="1. Tutup tab browser lama lalu buka ulang link SiRAPI (atau tekan Ctrl+Shift+R di laptop) agar tampilan terbaru termuat sempurna.\n2. Jika muncul kendala akses setelah update, segera laporkan ke Admin NOP / Koordinator.",
        height=85,
        key="srv_instruksi"
    )

    # Susun Pesan WA Otomatis
    wilayah_txt = ", ".join(target_wilayah_srv) if target_wilayah_srv else "Seluruh Tim Operasional"
    semua_poin = list(poin_pilihan_srv)
    for ln_c in poin_custom_srv.splitlines():
        if ln_c.strip():
            semua_poin.append(ln_c.strip())

    if "Maintenance" in jenis_info_srv:
        header_wa_srv = "*🛠️ PEMBERITAHUAN MAINTENANCE SERVER SiRAPI*"
        pembuka_wa_srv = "Diberitahukan kepada seluruh rekan tim bahwa saat ini sedang dilakukan proses pemeliharaan & pembaharuan server aplikasi SiRAPI."
    elif "Normal" in jenis_info_srv:
        header_wa_srv = "*✅ PEMBERITAHUAN: SERVER SiRAPI SUDAH NORMAL*"
        pembuka_wa_srv = "Alhamdulillah proses pembaharuan server aplikasi SiRAPI telah selesai. Sistem sudah normal dan dapat digunakan kembali untuk pengajuan Request Dana & PJB."
    elif "SOP" in jenis_info_srv:
        header_wa_srv = "*⚠️ PENGUMUMAN ATURAN & SOP OPERASIONAL SiRAPI*"
        pembuka_wa_srv = "Disampaikan kepada seluruh tim terkait pembaruan aturan operasional yang langsung berlaku di sistem SiRAPI:"
    else:
        header_wa_srv = "*🚀 PEMBERITAHUAN PEMBAHARUAN SERVER & FITUR SiRAPI*"
        pembuka_wa_srv = "Diberitahukan kepada seluruh tim operasional bahwa server aplikasi SiRAPI telah diperbarui untuk meningkatkan kestabilan dan ketertiban administrasi."

    wa_srv_lines = [
        header_wa_srv,
        "━━━━━━━━━━━━━━━━━━━━",
        f"📢 *Kepada* : {wilayah_txt}",
        f"📅 *Tanggal* : {tgl_update_srv.strftime('%d/%m/%Y')} ({jam_update_srv})",
        f"🏷️ *Versi* : {versi_srv}",
    ]
    if durasi_maint_srv:
        wa_srv_lines.append(f"⏳ *Estimasi* : {durasi_maint_srv}")
    wa_srv_lines.append(f"🔗 *Link App* : {link_app_srv}")
    wa_srv_lines.extend(["", pembuka_wa_srv])

    if semua_poin:
        wa_srv_lines.append("")
        wa_srv_lines.append("*📋 Rincian Pembaharuan / Informasi:*")
        for idx_p, pt in enumerate(semua_poin, 1):
            wa_srv_lines.append(f"{idx_p}. {pt}")

    if instruksi_tim_srv.strip():
        wa_srv_lines.extend(["", "*⚡ Arahan Untuk Seluruh Tim:*", instruksi_tim_srv.strip()])

    wa_srv_lines.extend([
        "",
        "Terima kasih atas kerja sama dan disiplin seluruh tim di lapangan. Tetap jaga keselamatan kerja (K3) & integritas! 💪",
        "",
        f"Hormat kami,\n*{pengirim_srv}*"
    ])

    wa_srv_final = "\n".join(wa_srv_lines)

    st.markdown("<div class='section-title'>📲 Preview & Generate Pesan WhatsApp</div>", unsafe_allow_html=True)
    st.info("💡 Klik ikon **Copy** di pojok kanan atas kotak teks di bawah ini, atau langsung klik tombol **Kirim via WhatsApp**.")
    st.code(wa_srv_final, language="markdown")

    wa_srv_enc = quote(wa_srv_final)
    clean_phone = re.sub(r"[^\d]", "", no_wa_tujuan_srv)
    if clean_phone.startswith("0"):
        clean_phone = "62" + clean_phone[1:]
    wa_srv_url = f"https://wa.me/{clean_phone}?text={wa_srv_enc}" if clean_phone else f"https://wa.me/?text={wa_srv_enc}"

    c_wa_s1, c_wa_s2 = st.columns(2)
    with c_wa_s1:
        st.markdown(
            f'<a href="{wa_srv_url}" target="_blank" class="btn-sidata-blue" style="background: linear-gradient(135deg, #22C55E 0%, #16A34A 100%) !important;">📲 BUKA & KIRIM PEMBERITAHUAN VIA WHATSAPP</a>',
            unsafe_allow_html=True
        )
    with c_wa_s2:
        st.download_button(
            "📥 Simpan Draft Teks (.txt)",
            data=wa_srv_final.encode("utf-8"),
            file_name=f"Info_Update_Server_{tgl_update_srv.strftime('%d%m%Y')}.txt",
            mime="text/plain",
            use_container_width=True
        )

# PAGE ADMIN: MASTER TIM & NOPOL (DINAMIS & PERMANEN)
# ==========================================
elif st.session_state.page == "👥 Master Tim & Nopol":
    st.markdown("<div class='header-card'><h2>👥 MASTER DATA TIM, ROLE & NOPOL</h2><p>Tambah, Edit, atau Nonaktifkan Nama Personel & Nopol Kendaraan/Genset Secara Permanen</p></div>", unsafe_allow_html=True)
    
    nop_mt = st.selectbox("📂 Pilih Wilayah Database (NOP):", ["-- Pilih NOP --"] + list(MASTER_DATA.keys()), key="sel_nop_mt")
    if nop_mt != "-- Pilih NOP --":
        target_ss = MASTER_DATA[nop_mt]["spreadsheet_id"]
        site_dict, site_list, tim_dict, list_nopol_csv, nik_dict = load_excel_data()
        existing_sheet_rows = fetch_master_tim_sheet(target_ss)
        
        # Jika tab 'Master Tim' di Google Sheets sudah ada isinya, gunakan data tersebut.
        # Jika belum pernah disimpan, muat otomatis dari daftar nama & Excel bawaan aplikasi.
        table_data = []
        if len(existing_sheet_rows) > 1:
            for r in existing_sheet_rows[1:]:
                r_pad = (r + [""] * 7)[:7]
                table_data.append({
                    "NAMA": str(r_pad[0]).strip().upper(),
                    "ROLE": str(r_pad[1]).strip() if str(r_pad[1]).strip() in ["TE", "MBP", "CME", "PM", "Admin", "Koordinator"] else "TE",
                    "NOPOL": str(r_pad[2]).strip().upper(),
                    "NIK": str(r_pad[3]).strip(),
                    "LATITUDE": str(r_pad[4]).strip() or "0",
                    "LONGITUDE": str(r_pad[5]).strip() or "0",
                    "STATUS": str(r_pad[6]).strip().upper() if str(r_pad[6]).strip().upper() in ["AKTIF", "NONAKTIF"] else "AKTIF"
                })
        else:
            for nm in MASTER_DATA[nop_mt]["names"]:
                nm_up = nm.strip().upper()
                if not nm_up:
                    continue
                t_info = tim_dict.get(nm_up, {})
                role_def = t_info.get("ROLE", "TE")
                if role_def not in ["TE", "MBP", "CME", "PM", "Admin", "Koordinator"]:
                    role_def = "TE"
                table_data.append({
                    "NAMA": nm_up,
                    "ROLE": role_def,
                    "NOPOL": str(t_info.get("NOPOL", "")).strip().upper(),
                    "NIK": str(nik_dict.get(nm_up, "")).strip(),
                    "LATITUDE": str(t_info.get("Latitude", "0")),
                    "LONGITUDE": str(t_info.get("Longtitude", "0")),
                    "STATUS": "AKTIF"
                })

        # 1. EXPANDER TAMBAH CEPAT PERSONEL / NOPOL BARU
        with st.expander("➕ Tambah Cepat Personel / Nopol Baru", expanded=False):
            with st.form("form_add_personel_cepat"):
                ca1, ca2, ca3 = st.columns(3)
                with ca1:
                    new_nama = st.text_input("Nama Lengkap Personel (Wajib):").strip().upper()
                    new_role = st.selectbox("Role Jabatan:", ["TE", "MBP", "CME", "PM", "Admin", "Koordinator"])
                with ca2:
                    new_nopol = st.text_input("Nopol Mobil/Motor atau ID Genset:").strip().upper()
                    new_nik = st.text_input("NIK Karyawan (Opsional):").strip()
                with ca3:
                    new_lat = st.text_input("Latitude Homebase (Opsional):", value="0").strip()
                    new_lon = st.text_input("Longitude Homebase (Opsional):", value="0").strip()
                
                if st.form_submit_button("➕ Tambahkan & Simpan ke Database", type="primary", use_container_width=True):
                    if not new_nama and not new_nopol:
                        st.error("❌ Harap isi minimal Nama Personel atau Nopol!")
                    else:
                        nama_isi = new_nama if new_nama else f"UNIT-{new_nopol}"
                        table_data.append({
                            "NAMA": nama_isi,
                            "ROLE": new_role,
                            "NOPOL": new_nopol,
                            "NIK": new_nik,
                            "LATITUDE": new_lat,
                            "LONGITUDE": new_lon,
                            "STATUS": "AKTIF"
                        })
                        rows_to_save = [[d["NAMA"], d["ROLE"], d["NOPOL"], d["NIK"], d["LATITUDE"], d["LONGITUDE"], d["STATUS"]] for d in table_data]
                        with st.spinner("Menyimpan data baru ke Google Sheets..."):
                            if save_master_tim_sheet(target_ss, rows_to_save):
                                st.success(f"✅ Berhasil menambahkan {nama_isi} ({new_nopol}) ke database {nop_mt}!")
                                time.sleep(1.5)
                                st.rerun()

        # 2. TABEL INTERAKTIF EDIT MASSAL
        st.markdown("<div class='section-title'>✏️ Tabel Edit Langsung (Nama Tim, Role, Nopol, NIK & Koordinat)</div>", unsafe_allow_html=True)
        st.info("💡 **CARA EDIT:** Klik dua kali pada sel tabel di bawah ini untuk mengubah **Nama**, **Role**, **Nopol**, atau ubah Status menjadi **NONAKTIF** jika personel sudah resign. Anda juga bisa menambah/menghapus baris di tabel, lalu klik tombol **Simpan Perubahan Permanen** di bawah.")
        
        df_mt = pd.DataFrame(table_data) if table_data else pd.DataFrame(columns=["NAMA", "ROLE", "NOPOL", "NIK", "LATITUDE", "LONGITUDE", "STATUS"])
        edited_mt = st.data_editor(
            df_mt,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            column_config={
                "NAMA": st.column_config.TextColumn("👤 Nama Personel", required=True),
                "ROLE": st.column_config.SelectboxColumn("💼 Role", options=["TE", "MBP", "CME", "PM", "Admin", "Koordinator"], required=True),
                "NOPOL": st.column_config.TextColumn("🚗 Nopol / ID Genset"),
                "NIK": st.column_config.TextColumn("🪪 NIK"),
                "LATITUDE": st.column_config.TextColumn("📍 Latitude HB"),
                "LONGITUDE": st.column_config.TextColumn("📍 Longitude HB"),
                "STATUS": st.column_config.SelectboxColumn("✅ Status", options=["AKTIF", "NONAKTIF"], default="AKTIF", required=True),
            }
        )
        
        if st.button(f"💾 SIMPAN PERUBAHAN PERMANEN ({nop_mt.upper()})", type="primary", use_container_width=True):
            clean_rows_save = []
            for _, r_ed in edited_mt.iterrows():
                nm_c = str(r_ed.get("NAMA", "")).strip().upper()
                npl_c = str(r_ed.get("NOPOL", "")).strip().upper()
                if nm_c in ["", "NAN", "NONE"] and npl_c in ["", "NAN", "NONE"]:
                    continue
                clean_rows_save.append([
                    nm_c,
                    str(r_ed.get("ROLE", "TE")).strip(),
                    "" if npl_c in ["NAN", "NONE"] else npl_c,
                    "" if str(r_ed.get("NIK", "")).strip() in ["nan", "None"] else str(r_ed.get("NIK", "")).strip(),
                    str(r_ed.get("LATITUDE", "0")).strip(),
                    str(r_ed.get("LONGITUDE", "0")).strip(),
                    str(r_ed.get("STATUS", "AKTIF")).strip().upper()
                ])
            with st.spinner("Menyimpan seluruh perubahan ke Google Sheets..."):
                if save_master_tim_sheet(target_ss, clean_rows_save):
                    st.success(f"🎉 Berhasil! Seluruh data personel & Nopol wilayah {nop_mt} telah diperbarui secara permanen.")
                    time.sleep(1.5)
                    st.rerun()
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
    st.markdown("<div class='header-card'><h2>Request Dana</h2><p>Input pengajuan baru atau revisi. Satu tiket dapat dipecah otomatis menjadi beberapa sub-tiket.</p></div>", unsafe_allow_html=True)
    _wz_render()
    
    with _wz_box("wz1_nop"):
        nop = st.selectbox("📌 1. Pilih Database Regional (NOP)", [""] + list(MASTER_DATA.keys()), key="req_nop")
    
    if nop != "":
        with _wz_box("wz1_t"):
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
        
        status_app_motor = "NONE"
        motor_limit_lock = False
        bbm_tank_lock = False
        bbm_price_errors = []
        bbm_ind_errors = []

        col1, col2 = st.columns(2)
        with col1:
            with _wz_box("wz1_a"):
                tanggal = st.date_input("Tanggal Pengajuan")
                cluster = st.selectbox("Cluster Regional", [""] + MASTER_DATA[nop]["clusters"])
            
                idx_nama_login = MASTER_DATA[nop]["names"].index(st.session_state.logged_in_user) if st.session_state.logged_in_user in MASTER_DATA[nop]["names"] else 0
                nama = st.selectbox("Nama Petugas / Pemohon (PIC Utama)", [""] + MASTER_DATA[nop]["names"], index=idx_nama_login+1 if idx_nama_login != 0 else 0)
            
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
            
                default_role_idx = 0
                if nama_lookup in tim_dict and 'ROLE' in tim_dict[nama_lookup]:
                    role_val = tim_dict[nama_lookup]['ROLE']
                    roles_list = ["-- Pilih Role --", "Admin", "Koordinator", "PM", "TE", "MBP", "CME"]
                    if role_val in roles_list:
                        default_role_idx = roles_list.index(role_val)
                    
                role = st.selectbox("Role Jabatan", ["-- Pilih Role --", "Admin", "Koordinator", "PM", "TE", "MBP", "CME"], index=default_role_idx)
            
                if len(site_list) > 0:
                    site_id = st.selectbox("ID Site / Lokasi", [""] + site_list)
                    if site_id != "-- Pilih Site ID --" and site_id in site_dict:
                        auto_lat_tujuan, auto_long_tujuan = str(site_dict[site_id].get("Latitude Tujuan", "0")), str(site_dict[site_id].get("Longtitude Tujuan", "0"))
                else: site_id = st.text_input("ID Site / Lokasi")

        with col2:
            with _wz_box("wz1_b"):
                pilihan_kep = st.selectbox("Klasifikasi Keperluan Dana", LIST_KEPERLUAN)
                
                if pilihan_kep == "Lainnya (Ketik Manual)":
                    keperluan = st.text_input("Ketik Keperluan Secara Manual (Wajib):")
                else:
                    keperluan = pilihan_kep
                
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
            
                for r in reversed(app_r[1:]):
                    if len(r) > 5 and r[3] == "Request Dana" and str(r[2]).strip().upper() == base_tiket_clean:
                        if str(r[5]).strip().upper() == "REJECTED": is_rejected_request = True
                        break
            
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
                            st.warning("⏳ Status: Permintaan Izin Revisi Anda sedang MENUNGGU VERIFIKASI Admin.")
                        else:
                            if st.button("🚨 Minta Izin Revisi ke Admin Sekarang", type="primary", use_container_width=True):
                                append_data(SHEET_APP, [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), nama, base_tiket_clean, "Izin Revisi", 0, "PENDING", "-"], target_ss)
                                st.success("Permintaan Izin Revisi terkirim! Silakan hubungi Admin.")
                                time.sleep(2.5); st.rerun()
                        _wz_clamp(1)
                        st.stop()
                    else:
                        st.success("✅ Izin Revisi DIBERIKAN Admin. Silakan isi kembali data perbaikan Anda di bawah ini.")
                    
                if is_rejected_request:
                    st.info(f"💡 Info: Request dengan tiket **{base_tiket_clean}** sebelumnya ditolak. Anda dapat menginput ulang (Re-Submit) di form ini.")

            with _wz_box("wz2_a"):
                # --- TAMBAHAN KLASIFIKASI PEKERJAAN MULTIPLE (MULAI) ---
                st.markdown("<div class='section-title'>🏗️ Klasifikasi & Detail Pekerjaan</div>", unsafe_allow_html=True)
                st.info("💡 Pilih semua jenis pekerjaan yang dilakukan. Pilihan akan otomatis merangkum Deskripsi, mengunci Uang Makan, dan memunculkan Checklist khusus.")
            
                c_job1, c_job2 = st.columns(2)
                with c_job1:
                    opt_atas = ["RRU", "Antena MW/RF", "Jumper", "Optik", "Odu", "Pindah Mounting", "Lainnya (Ketik Manual)"]
                    val_atas = st.multiselect("📡 Tshoot Bagian Atas", opt_atas)
                    manual_atas = st.text_input("Sebutkan (Atas Lainnya):") if "Lainnya (Ketik Manual)" in val_atas else ""
                
                    is_kirim_mat = st.checkbox("📦 Pengiriman Material")
                    mat_module = st.text_input("Wajib: Nama Module yang dikirim:") if is_kirim_mat else ""
                    mat_site = st.text_input("Wajib: Site ID Tujuan Pengiriman:") if is_kirim_mat else ""
                
                with c_job2:
                    opt_bawah = ["Module APR", "Backplane Rectifier", "Replace Board BTS", "Replace Optik Transmisi", "Replace Idu", "Add Batterai", "Add Rectifier", "Tshoot Power dan rectifier", "Pengecekan MCB", "BCP", "Automasi Genset", "Preventive Maintenance SITE", "Preventive Maintenance GENSET", "Preventive Maintenance SITE & GENSET (Tim PM)", "Lainnya (Ketik Manual)"]
                    val_bawah = st.multiselect("🔌 Tshoot Bagian Bawah", opt_bawah)
                    manual_bawah = st.text_input("Sebutkan (Bawah Lainnya):") if "Lainnya (Ketik Manual)" in val_bawah else ""

                # Merangkum Deskripsi Otomatis dari Pilihan Tim
                auto_desc = []
                if val_atas:
                    c_atas = [x for x in val_atas if x != "Lainnya (Ketik Manual)"]
                    if manual_atas: c_atas.append(manual_atas)
                    if c_atas: auto_desc.append("BAGIAN ATAS: " + ", ".join(c_atas))
                if val_bawah:
                    c_bawah = [x for x in val_bawah if x != "Lainnya (Ketik Manual)"]
                    if manual_bawah: c_bawah.append(manual_bawah)
                    if c_bawah: auto_desc.append("BAGIAN BAWAH: " + ", ".join(c_bawah))
                if is_kirim_mat:
                    auto_desc.append(f"PENGIRIMAN MATERIAL: {mat_module} (Tujuan: Site {mat_site})")
                
                str_auto_desc = "\n".join(auto_desc)
            
                # Text area akan otomatis terisi dari rangkuman di atas!
                deskripsi = st.text_area("Deskripsi Pekerjaan / Justifikasi (Auto-Fill System):", value=str_auto_desc, height=120)
                # --- TAMBAHAN KLASIFIKASI PEKERJAAN MULTIPLE (SELESAI) ---
            
                list_nama_tim = [n for n in MASTER_DATA[nop]["names"] if n.strip().upper() != nama_lookup and n != ""]
                tim_bareng = st.multiselect("👥 Pilih Rekan Tim yang Berangkat Bersama (Opsional)", list_nama_tim)
            
                tim_terkunci = []
                if role in ["TE", "MBP", "CME"] and tim_bareng:
                    for member in tim_bareng:
                        _, m_out_lock, _, _ = get_user_tickets_status(member, req_r, pjb_r, app_r)
                        if len(m_out_lock) > 0: tim_terkunci.append(member)

        with _wz_box("wz3_a"):
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
                st.warning("⚠️ Koordinat masih 0 / belum lengkap. Sistem berpotensi menolak karena tidak bisa menghitung jarak tempuh aktual.")

        auto_nopol = ""
        if nama_lookup != "" and nama_lookup in tim_dict:
            auto_nopol = str(tim_dict[nama_lookup].get("NOPOL", "")).strip()
            if auto_nopol in ["nan", "0", "None"]: auto_nopol = ""

        with _wz_box("wz4_a"):
            st.markdown("<div class='section-title'>🛒 4. Rincian Kebutuhan Dana (Pilih Bisa Lebih Dari 1)</div>", unsafe_allow_html=True)
            st.info("💡 **INFO SPLIT ENGINE:** Anda bisa memilih banyak kebutuhan sekaligus. Sistem akan otomatis memecah form ini menjadi beberapa tiket PJB pending yang terpisah.")
        
            kebutuhan_dana_list = st.multiselect("Silakan pilih seluruh jenis pengeluaran untuk tiket ini:", ["BBM", "Uang Makan", "Penginapan", "Material", "Support", "Fery Reguler/Carter", "Klotok/Kapal Carter"])
        
            sub_requests = []
            is_mobil = is_motor = is_genset = False
            total_motor_this_month = 0
        
            # =========================================================
            # A. LOGIKA BBM (PILIHAN SPBU/ECERAN, WAJIB TANGKI 1x/2x, LIVE KONTROL WAKTU & ANTI SALAH TITIK/KOMA)
            # =========================================================
            if "BBM" in kebutuhan_dana_list:
                now_wib_req = get_now_wib()
                st.markdown("<div style='background-color:#F8FAFC; padding:15px; border-radius:10px; border-left: 5px solid #3B82F6; margin-bottom: 15px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
                st.info(
                    f"⏱️ **LIVE KONTROL WAKTU REQUEST:** `{now_wib_req.strftime('%d/%m/%Y %H:%M:%S WIB')}`  |  "
                    f"📌 **Panduan Angka KM/RH:** Ketik angka polos **tanpa titik ribuan** (contoh: `125450`), gunakan **koma** hanya untuk desimal (contoh: `1250,5`)."
                )
                jns_bbm_list = st.multiselect("BBM untuk Kendaraan/Peralatan apa saja?", ["Mobil", "Motor", "Genset"])
            
                # 1. LOGIKA MOBIL (SPBU vs ECERAN + WAJIB TANGKI + LIVE KONTROL KM & WAKTU)
                if "Mobil" in jns_bbm_list:
                    is_mobil = True
                    with st.expander("🚙 Input BBM Mobil (SPBU / Eceran, Tangki, Harga & Live Kontrol KM)", expanded=True):
                        c_m1, c_m2 = st.columns(2)
                        with c_m1:
                            sumber_mob = st.radio("Sumber Pembelian BBM Mobil:", ["SPBU", "Eceran"], horizontal=True, key="src_mob")
                            if sumber_mob == "Eceran":
                                st.warning("⚠️ **PEMBELIAN ECERAN:** Saat PJB nanti **WAJIB** melampirkan 2 foto tambahan (1. Full foto isi BBM sesuai jumlah botol/jerigen liter, 2. Foto bukti bayar cash/transfer ke toko) yang akan **dianalisa oleh AI**.")
                            jb_mobil = st.selectbox("Jenis BBM Mobil", ["Pertalite", "Pertamax", "Dexlite", "Bio Solar", "Pertamina Dex"], key="b_mob")
                            _, _, rule_mob = get_bbm_rule(jb_mobil, sumber_mob)
                            def_harga_mob = rule_mob["default"] if rule_mob else 10000
                            est_liter_mob = max(0.5, round(jarak_km_pp / 9.0, 1)) if jarak_km_pp > 0 else 5.0

                            mob_price_sig = f"{sumber_mob}|{jb_mobil}"
                            if st.session_state.get("_prev_mob_sig") != mob_price_sig:
                                st.session_state["_prev_mob_sig"] = mob_price_sig
                                st.session_state["hs_mob"] = int(def_harga_mob)
                            
                            k_tangki_mob = st.number_input("Kapasitas Tangki Mobil (Liter) [WAJIB DIISI]", min_value=0.0, max_value=200.0, step=1.0, value=0.0, key="kt_mob", help="Wajib cantumkan kapasitas tangki mobil sebenarnya (misal: Avanza/Xenia 45 L, Hilux/Triton 75 L) agar tidak over request.")
                            if k_tangki_mob <= 0:
                                st.error("🚨 **WAJIB DIISI:** Cantumkan **Kapasitas Tangki Mobil (Liter)** untuk pengisian 1x maupun 2x agar tidak terjadi over request!")
                                bbm_tank_lock = True
                            
                            h_satuan_mob = st.number_input(f"Harga Satuan BBM Mobil ({sumber_mob} - Rp/Liter)", min_value=0, step=100, key="hs_mob")
                            ok_hmob, msg_hmob = validate_bbm_price(jb_mobil, h_satuan_mob, sumber_mob)
                            if not ok_hmob:
                                st.error(f"🚨 **VALIDASI HARGA BBM MOBIL ({sumber_mob.upper()}):** {msg_hmob}")
                                bbm_price_errors.append(f"Mobil {jb_mobil} [{sumber_mob}]: {msg_hmob}")
                            else:
                                st.caption(f"✅ {msg_hmob}")

                            opsi_pengisian_mob = st.radio("Opsi Pengisian Mobil:", ["1x Pengisian", "2x Pengisian (Kapasitas Tangki Kurang)"], key="opt_mob")
                        
                            if opsi_pengisian_mob == "1x Pengisian":
                                l_mob_req = st.number_input("Total Liter BBM Diperlukan (Liter)", min_value=0.0, step=0.5, value=max(0.5, float(est_liter_mob)), key="lmob_req")
                                keb_mobil = int(round(l_mob_req * h_satuan_mob))
                                if l_mob_req <= 0:
                                    st.error("🚨 Total Liter BBM Mobil wajib lebih dari 0 Liter!")
                                    bbm_tank_lock = True
                                elif k_tangki_mob > 0 and l_mob_req > k_tangki_mob:
                                    st.error(f"🚨 **OVER REQUEST TANGKI MOBIL:** Pengisian {l_mob_req:g} Liter melebihi kapasitas tangki ({k_tangki_mob:g} Liter)! Kurangi liter atau pilih **Opsi 2x Pengisian**.")
                                    bbm_tank_lock = True
                            else:
                                st.info("💡 Sistem otomatis memecah tiket ini jadi [MOBIL-1] & [MOBIL-2]. Masing-masing pengisian tidak boleh melebihi kapasitas tangki.")
                                def_split_mob = max(0.5, round(est_liter_mob / 2.0, 1))
                                l_mob_1 = st.number_input("Liter Pengisian 1 (Wajib)", min_value=0.0, step=0.5, value=float(def_split_mob), key="lmob_1")
                                l_mob_2 = st.number_input("Liter Pengisian 2 (Wajib)", min_value=0.0, step=0.5, value=float(def_split_mob), key="lmob_2")
                                l_mob_req = round(l_mob_1 + l_mob_2, 1)
                                keb_mobil_1 = int(round(l_mob_1 * h_satuan_mob))
                                keb_mobil_2 = int(round(l_mob_2 * h_satuan_mob))
                                keb_mobil = keb_mobil_1 + keb_mobil_2
                                if l_mob_1 <= 0 or l_mob_2 <= 0:
                                    st.error("🚨 Liter Pengisian 1 dan Pengisian 2 masing-masing wajib lebih dari 0 Liter!")
                                    bbm_tank_lock = True
                                elif k_tangki_mob > 0 and (l_mob_1 > k_tangki_mob or l_mob_2 > k_tangki_mob):
                                    st.error(f"🚨 **OVER REQUEST TANGKI MOBIL (2x Pengisian):** Setiap tahap pengisian (Isi 1: {l_mob_1:g} L / Isi 2: {l_mob_2:g} L) tidak boleh melebihi kapasitas tangki ({k_tangki_mob:g} L)!")
                                    bbm_tank_lock = True

                            std_biaya_mob = int(round(est_liter_mob * h_satuan_mob))
                            selisih_l_mob = round(l_mob_req - est_liter_mob, 1)
                            selisih_rp_mob = keb_mobil - std_biaya_mob
                            
                            if selisih_l_mob > 0.5:
                                ket_selisih_mob = f"OVER +{selisih_l_mob} L (+Rp {selisih_rp_mob:,.0f})"
                                st.warning(
                                    f"📊 **Komparasi Otomatis BBM Mobil ({sumber_mob}):**\n"
                                    f"- **Request Tim:** {format_id_number(l_mob_req)} Liter × Rp {h_satuan_mob:,.0f} = **Rp {keb_mobil:,.0f}** (Tangki: {k_tangki_mob:g} L)\n"
                                    f"- **Seharusnya (Jarak {jarak_km_pp:.1f} KM | 1:9 KM/L):** {format_id_number(est_liter_mob)} Liter (**Rp {std_biaya_mob:,.0f}**)\n"
                                    f"- **Keterangan Selisih:** ⚠️ **Lebih +{format_id_number(selisih_l_mob)} Liter (+Rp {selisih_rp_mob:,.0f})** dari standar jarak"
                                )
                            elif selisih_l_mob < -0.5:
                                ket_selisih_mob = f"HEMAT {selisih_l_mob} L (-Rp {abs(selisih_rp_mob):,.0f})"
                                st.success(
                                    f"📊 **Komparasi Otomatis BBM Mobil ({sumber_mob}):**\n"
                                    f"- **Request Tim:** {format_id_number(l_mob_req)} Liter × Rp {h_satuan_mob:,.0f} = **Rp {keb_mobil:,.0f}** (Tangki: {k_tangki_mob:g} L)\n"
                                    f"- **Seharusnya (Jarak {jarak_km_pp:.1f} KM | 1:9 KM/L):** {format_id_number(est_liter_mob)} Liter (**Rp {std_biaya_mob:,.0f}**)\n"
                                    f"- **Keterangan Selisih:** ✅ **Hemat {format_id_number(selisih_l_mob)} Liter (-Rp {abs(selisih_rp_mob):,.0f})** di bawah standar"
                                )
                            else:
                                ket_selisih_mob = f"SESUAI STANDAR (Selisih {selisih_l_mob:+.1f} L)"
                                st.info(
                                    f"📊 **Komparasi Otomatis BBM Mobil ({sumber_mob}):**\n"
                                    f"- **Request Tim:** {format_id_number(l_mob_req)} Liter × Rp {h_satuan_mob:,.0f} = **Rp {keb_mobil:,.0f}** (Tangki: {k_tangki_mob:g} L)\n"
                                    f"- **Seharusnya (Jarak {jarak_km_pp:.1f} KM | 1:9 KM/L):** {format_id_number(est_liter_mob)} Liter (**Rp {std_biaya_mob:,.0f}**)\n"
                                    f"- **Keterangan Selisih:** ✅ **Sesuai Standar Sistem**"
                                )

                        with c_m2:
                            idx_mob = options_nopol.index(auto_nopol) if auto_nopol in options_nopol else 0
                            pilihan_mob = st.selectbox("Plat Mobil", options_nopol, index=idx_mob, key="p_mob")
                            if pilihan_mob == "-- Pilih Nopol / Ketik Baru --": plat_mobil = st.text_input("Ketik Plat Mobil:", key="pmob_man").strip().upper()
                            else: plat_mobil = pilihan_mob.strip().upper()
                            
                            last_info_mob = get_last_indicator_detail(plat_mobil, "Mobil", pjb_r, req_r, app_r=app_r, spreadsheet_id=target_ss)
                            last_km_mob = last_info_mob["value"]
                            if st.session_state.get("_prev_plat_mob") != plat_mobil:
                                st.session_state["_prev_plat_mob"] = plat_mobil
                                st.session_state["km_mob_txt"] = str(int(last_km_mob)) if last_km_mob == int(last_km_mob) else str(last_km_mob)

                            km_mob_raw = st.text_input(
                                f"KM Awal Mobil Sekarang (Histori Terakhir: {format_id_number(last_km_mob)} KM)",
                                key="km_mob_txt",
                                placeholder="Ketik angka polos tanpa titik, misal: 125450",
                                help="Jangan gunakan titik sebagai pemisah ribuan! Contoh benar: 125450 (bukan 125.450)."
                            )
                            km_awal_mob, lvl_kmm, note_kmm = parse_indonesian_indicator(km_mob_raw, last_km_mob, "KM")
                            if lvl_kmm == "err":
                                st.error(note_kmm)
                                bbm_ind_errors.append(f"Mobil ({plat_mobil}): {note_kmm}")
                            elif lvl_kmm == "warn":
                                st.warning(note_kmm)
                            else:
                                st.caption(f"🔎 {note_kmm}")

                            ctrl_mob = evaluate_live_indicator_control(km_awal_mob, last_info_mob, now_wib_req, tipe="Mobil")
                            if ctrl_mob["is_blocking"]:
                                st.error("🛣️ **LIVE KONTROL KM & WAKTU MOBIL:**\n" + "\n".join(ctrl_mob["detail_lines"]))
                                bbm_ind_errors.append(f"Mobil ({plat_mobil}): {ctrl_mob['status_short']}")
                            elif ctrl_mob["level"] == "warn":
                                st.warning("🛣️ **LIVE KONTROL KM & WAKTU MOBIL:**\n" + "\n".join(ctrl_mob["detail_lines"]))
                            else:
                                st.info("🛣️ **LIVE KONTROL KM & WAKTU MOBIL:**\n" + "\n".join(ctrl_mob["detail_lines"]))
                            if plat_mobil:
                                _pn_m = normalize_plat_key(plat_mobil)
                                _h_mob = []
                                for _rp in reversed(pjb_r[1:]):
                                    if len(_rp) > 12 and normalize_plat_key(_rp[12]) == _pn_m and "mobil" in str(_rp[8]).lower():
                                        _h_mob.append({"Tanggal": _rp[1], "Tiket": _rp[21] if len(_rp)>21 else "-", "PIC": _rp[4], "KM Akhir": format_id_number(clean_indicator(_rp[10])), "Trip": f"{_rp[24] if len(_rp)>24 else '-'} KM"})
                                        if len(_h_mob) >= 5: break
                                if _h_mob:
                                    with st.expander(f"📜 5 Histori KM Terakhir ({plat_mobil})", expanded=False):
                                        st.dataframe(pd.DataFrame(_h_mob), hide_index=True, use_container_width=True)
                        
                        selisih_km_mob = ctrl_mob["selisih"]
                        hist_km_mob_str = f"KM {format_id_number(last_km_mob)}->{format_id_number(km_awal_mob)} (+{format_id_number(selisih_km_mob)} KM dlm {ctrl_mob['elapsed_text']} | {ctrl_mob['status_short']})" if last_km_mob > 0 else f"KM Awal: {format_id_number(km_awal_mob)}"
                        kat_mob_base = f"Mobil - {jb_mobil} [{sumber_mob.upper()}]"
                        if opsi_pengisian_mob == "1x Pengisian":
                            info_bbm_mob = f"Beli: {sumber_mob.upper()} | Tangki: {k_tangki_mob:g} L | Req Tim: {l_mob_req} L (@Rp {h_satuan_mob:,.0f}) = Rp {keb_mobil:,.0f} | Seharusnya ({jarak_km_pp:.1f} KM): {est_liter_mob} L (Rp {std_biaya_mob:,.0f}) | Selisih: {ket_selisih_mob} | {hist_km_mob_str}"
                            sub_requests.append({"tiket": f"{base_tiket_clean} [MOBIL]", "kategori": kat_mob_base, "kebutuhan": keb_mobil, "plat": plat_mobil, "indikator": km_awal_mob, "last_ind": last_km_mob, "tipe": "Mobil", "info_bbm": info_bbm_mob, "harga_satuan": h_satuan_mob, "kapasitas_tangki": k_tangki_mob, "sumber_bbm": sumber_mob})
                        else:
                            info_bbm_mob1 = f"Beli: {sumber_mob.upper()} | Tangki: {k_tangki_mob:g} L | Isi 1: {l_mob_1} L (@Rp {h_satuan_mob:,.0f}) = Rp {keb_mobil_1:,.0f} [Total 1+2: {l_mob_req} L vs Std {est_liter_mob} L | {ket_selisih_mob} | {hist_km_mob_str}]"
                            info_bbm_mob2 = f"Beli: {sumber_mob.upper()} | Tangki: {k_tangki_mob:g} L | Isi 2: {l_mob_2} L (@Rp {h_satuan_mob:,.0f}) = Rp {keb_mobil_2:,.0f} [Total 1+2: {l_mob_req} L vs Std {est_liter_mob} L | {ket_selisih_mob} | {hist_km_mob_str}]"
                            sub_requests.append({"tiket": f"{base_tiket_clean} [MOBIL-1]", "kategori": f"{kat_mob_base} (Isi 1)", "kebutuhan": keb_mobil_1, "plat": plat_mobil, "indikator": km_awal_mob, "last_ind": last_km_mob, "tipe": "Mobil", "info_bbm": info_bbm_mob1, "harga_satuan": h_satuan_mob, "kapasitas_tangki": k_tangki_mob, "sumber_bbm": sumber_mob})
                            sub_requests.append({"tiket": f"{base_tiket_clean} [MOBIL-2]", "kategori": f"{kat_mob_base} (Isi 2)", "kebutuhan": keb_mobil_2, "plat": plat_mobil, "indikator": km_awal_mob, "last_ind": last_km_mob, "tipe": "Mobil", "info_bbm": info_bbm_mob2, "harga_satuan": h_satuan_mob, "kapasitas_tangki": k_tangki_mob, "sumber_bbm": sumber_mob})

                # 2. LOGIKA MOTOR (SPBU vs ECERAN + WAJIB TANGKI + LIVE KONTROL KM & WAKTU)
                if "Motor" in jns_bbm_list:
                    is_motor = True
                    with st.expander("🏍️ Input BBM Motor (SPBU / Eceran, Tangki, Harga & Live Kontrol KM)", expanded=True):
                        c_mt1, c_mt2 = st.columns(2)
                        with c_mt1:
                            sumber_mot = st.radio("Sumber Pembelian BBM Motor:", ["SPBU", "Eceran"], horizontal=True, key="src_mot")
                            if sumber_mot == "Eceran":
                                st.warning("⚠️ **PEMBELIAN ECERAN:** Saat PJB nanti **WAJIB** melampirkan 2 foto tambahan (Foto Full Botol/Liter & Foto Bukti Bayar Toko) untuk dianalisa oleh AI.")
                            jb_motor = st.selectbox("Jenis BBM Motor", ["Pertalite", "Pertamax"], key="b_mot")
                            _, _, rule_mot = get_bbm_rule(jb_motor, sumber_mot)
                            def_harga_mot = rule_mot["default"] if rule_mot else 10000

                            mot_price_sig = f"{sumber_mot}|{jb_motor}"
                            if st.session_state.get("_prev_mot_sig") != mot_price_sig:
                                st.session_state["_prev_mot_sig"] = mot_price_sig
                                st.session_state["hs_mot"] = int(def_harga_mot)

                            k_tangki = st.number_input("Kapasitas Tangki Motor (Liter) [WAJIB DIISI]", min_value=0.0, max_value=25.0, step=0.1, value=0.0, key="kt_mot", help="Wajib cantumkan kapasitas tangki motor sebenarnya (misal: Beat/Vario 4.2-5.5 L, CRF/KLX 7.0 L) agar tidak over request.")
                            if k_tangki <= 0:
                                st.error("🚨 **WAJIB DIISI:** Cantumkan **Kapasitas Tangki Motor (Liter)** untuk pengisian 1x maupun 2x agar tidak terjadi over request!")
                                bbm_tank_lock = True

                            h_satuan = st.number_input(f"Harga Satuan BBM Motor ({sumber_mot} - Rp/Liter)", min_value=0, step=100, key="hs_mot")
                            ok_hmot, msg_hmot = validate_bbm_price(jb_motor, h_satuan, sumber_mot)
                            if not ok_hmot:
                                st.error(f"🚨 **VALIDASI HARGA BBM MOTOR ({sumber_mot.upper()}):** {msg_hmot}")
                                bbm_price_errors.append(f"Motor {jb_motor} [{sumber_mot}]: {msg_hmot}")
                            else:
                                st.caption(f"✅ {msg_hmot}")

                            est_l_mot = max(0.5, round(jarak_km_pp / 35.0, 1)) if jarak_km_pp > 0 else 2.0
                        
                            opsi_pengisian = st.radio("Opsi Pengisian Motor:", ["1x Pengisian", "2x Pengisian (Kapasitas Tangki Kurang)"], key="opt_mot")
                        
                            if opsi_pengisian == "1x Pengisian":
                                l_butuh = st.number_input("Total Liter Diperlukan (Motor)", min_value=0.0, step=0.1, value=max(0.5, float(est_l_mot)), key="lb_mot")
                                keb_motor = int(round(l_butuh * h_satuan))
                                if l_butuh <= 0:
                                    st.error("🚨 Total Liter BBM Motor wajib lebih dari 0 Liter!")
                                    bbm_tank_lock = True
                                elif k_tangki > 0 and l_butuh > k_tangki:
                                    st.error(f"🚨 **OVER REQUEST TANGKI MOTOR:** Pengisian {l_butuh:g} L melebihi kapasitas tangki ({k_tangki:g} L)! Silakan pilih **Opsi 2x Pengisian**.")
                                    bbm_tank_lock = True
                            else:
                                st.info("💡 Sistem otomatis memecah tiket ini jadi [MOTOR-1] & [MOTOR-2].")
                                def_mot_1 = max(0.5, float(k_tangki)) if k_tangki > 0 else 4.0
                                l_butuh_1 = st.number_input("Liter Pengisian 1 (Wajib)", min_value=0.0, step=0.1, value=float(def_mot_1), key="lmot_1")
                                sisa_est = max(0.5, round(est_l_mot - l_butuh_1, 1)) if est_l_mot > l_butuh_1 else 1.0
                                l_butuh_2 = st.number_input("Liter Pengisian 2 (Wajib)", min_value=0.0, step=0.1, value=float(sisa_est), key="lmot_2")
                                l_butuh = round(l_butuh_1 + l_butuh_2, 1)
                                keb_motor_1 = int(round(l_butuh_1 * h_satuan))
                                keb_motor_2 = int(round(l_butuh_2 * h_satuan))
                                keb_motor = keb_motor_1 + keb_motor_2
                            
                                if l_butuh_1 <= 0 or l_butuh_2 <= 0:
                                    st.error("🚨 Liter Pengisian 1 dan 2 masing-masing wajib lebih dari 0 Liter!")
                                    bbm_tank_lock = True
                                elif k_tangki > 0 and (l_butuh_1 > k_tangki or l_butuh_2 > k_tangki):
                                    st.error(f"🚨 **OVER REQUEST TANGKI MOTOR:** Setiap pengisian per-tahap tidak boleh melebihi kapasitas tangki ({k_tangki:g} L)!")
                                    bbm_tank_lock = True

                            std_biaya_mot = int(round(est_l_mot * h_satuan))
                            selisih_l_mot = round(l_butuh - est_l_mot, 1)
                            selisih_rp_mot = keb_motor - std_biaya_mot

                            if selisih_l_mot > 0.3:
                                ket_selisih_mot = f"OVER +{selisih_l_mot} L (+Rp {selisih_rp_mot:,.0f})"
                                st.warning(
                                    f"📊 **Komparasi Otomatis BBM Motor ({sumber_mot}):**\n"
                                    f"- **Request Tim:** {format_id_number(l_butuh)} Liter × Rp {h_satuan:,.0f} = **Rp {keb_motor:,.0f}** (Tangki: {k_tangki:g} L)\n"
                                    f"- **Seharusnya (Jarak {jarak_km_pp:.1f} KM | 1:35 KM/L):** {format_id_number(est_l_mot)} Liter (**Rp {std_biaya_mot:,.0f}**)\n"
                                    f"- **Keterangan Selisih:** ⚠️ **Lebih +{format_id_number(selisih_l_mot)} Liter (+Rp {selisih_rp_mot:,.0f})** dari standar jarak"
                                )
                            elif selisih_l_mot < -0.3:
                                ket_selisih_mot = f"HEMAT {selisih_l_mot} L (-Rp {abs(selisih_rp_mot):,.0f})"
                                st.success(
                                    f"📊 **Komparasi Otomatis BBM Motor ({sumber_mot}):**\n"
                                    f"- **Request Tim:** {format_id_number(l_butuh)} Liter × Rp {h_satuan:,.0f} = **Rp {keb_motor:,.0f}** (Tangki: {k_tangki:g} L)\n"
                                    f"- **Seharusnya (Jarak {jarak_km_pp:.1f} KM | 1:35 KM/L):** {format_id_number(est_l_mot)} Liter (**Rp {std_biaya_mot:,.0f}**)\n"
                                    f"- **Keterangan Selisih:** ✅ **Hemat {format_id_number(selisih_l_mot)} Liter (-Rp {abs(selisih_rp_mot):,.0f})**"
                                )
                            else:
                                ket_selisih_mot = f"SESUAI STANDAR (Selisih {selisih_l_mot:+.1f} L)"
                                st.info(
                                    f"📊 **Komparasi Otomatis BBM Motor ({sumber_mot}):**\n"
                                    f"- **Request Tim:** {format_id_number(l_butuh)} Liter × Rp {h_satuan:,.0f} = **Rp {keb_motor:,.0f}** (Tangki: {k_tangki:g} L)\n"
                                    f"- **Seharusnya (Jarak {jarak_km_pp:.1f} KM | 1:35 KM/L):** {format_id_number(est_l_mot)} Liter (**Rp {std_biaya_mot:,.0f}**)\n"
                                    f"- **Keterangan Selisih:** ✅ **Sesuai Standar Sistem**"
                                )
                    
                        with c_mt2:
                            idx_mot = options_nopol.index(auto_nopol) if auto_nopol in options_nopol else 0
                            pilihan_mot = st.selectbox("Plat Motor", options_nopol, index=idx_mot, key="p_mot")
                            if pilihan_mot == "-- Pilih Nopol / Ketik Baru --": plat_motor = st.text_input("Ketik Plat Motor:", key="pmot_man").strip().upper()
                            else: plat_motor = pilihan_mot.strip().upper()
                            
                            last_info_mot = get_last_indicator_detail(plat_motor, "Motor", pjb_r, req_r, app_r=app_r, spreadsheet_id=target_ss)
                            last_km_mot = last_info_mot["value"]
                            if st.session_state.get("_prev_plat_mot") != plat_motor:
                                st.session_state["_prev_plat_mot"] = plat_motor
                                st.session_state["km_mot_txt"] = str(int(last_km_mot)) if last_km_mot == int(last_km_mot) else str(last_km_mot)

                            km_mot_raw = st.text_input(
                                f"KM Awal Motor Sekarang (Histori Terakhir: {format_id_number(last_km_mot)} KM)",
                                key="km_mot_txt",
                                placeholder="Ketik angka polos tanpa titik, misal: 34500",
                                help="Jangan gunakan titik sebagai pemisah ribuan! Contoh benar: 34500."
                            )
                            km_awal_mot, lvl_kmt, note_kmt = parse_indonesian_indicator(km_mot_raw, last_km_mot, "KM")
                            if lvl_kmt == "err":
                                st.error(note_kmt)
                                bbm_ind_errors.append(f"Motor ({plat_motor}): {note_kmt}")
                            elif lvl_kmt == "warn":
                                st.warning(note_kmt)
                            else:
                                st.caption(f"🔎 {note_kmt}")

                            ctrl_mot = evaluate_live_indicator_control(km_awal_mot, last_info_mot, now_wib_req, tipe="Motor")
                            if ctrl_mot["is_blocking"]:
                                st.error("🛣️ **LIVE KONTROL KM & WAKTU MOTOR:**\n" + "\n".join(ctrl_mot["detail_lines"]))
                                bbm_ind_errors.append(f"Motor ({plat_motor}): {ctrl_mot['status_short']}")
                            elif ctrl_mot["level"] == "warn":
                                st.warning("🛣️ **LIVE KONTROL KM & WAKTU MOTOR:**\n" + "\n".join(ctrl_mot["detail_lines"]))
                            else:
                                st.info("🛣️ **LIVE KONTROL KM & WAKTU MOTOR:**\n" + "\n".join(ctrl_mot["detail_lines"]))
                    
                        selisih_km_mot = ctrl_mot["selisih"]
                        hist_km_mot_str = f"KM {format_id_number(last_km_mot)}->{format_id_number(km_awal_mot)} (+{format_id_number(selisih_km_mot)} KM dlm {ctrl_mot['elapsed_text']} | {ctrl_mot['status_short']})" if last_km_mot > 0 else f"KM Awal: {format_id_number(km_awal_mot)}"
                        kat_mot_base = f"Motor - {jb_motor} [{sumber_mot.upper()}]"
                        if opsi_pengisian == "1x Pengisian":
                            info_bbm_mot = f"Beli: {sumber_mot.upper()} | Tangki: {k_tangki:g} L | Req Tim: {l_butuh} L (@Rp {h_satuan:,.0f}) = Rp {keb_motor:,.0f} | Seharusnya ({jarak_km_pp:.1f} KM): {est_l_mot} L (Rp {std_biaya_mot:,.0f}) | Selisih: {ket_selisih_mot} | {hist_km_mot_str}"
                            sub_requests.append({"tiket": f"{base_tiket_clean} [MOTOR]", "kategori": kat_mot_base, "kebutuhan": keb_motor, "plat": plat_motor, "indikator": km_awal_mot, "last_ind": last_km_mot, "tipe": "Motor", "info_bbm": info_bbm_mot, "harga_satuan": h_satuan, "kapasitas_tangki": k_tangki, "sumber_bbm": sumber_mot})
                        else:
                            info_bbm_mot1 = f"Beli: {sumber_mot.upper()} | Tangki: {k_tangki:g} L | Isi 1: {l_butuh_1} L (@Rp {h_satuan:,.0f}) = Rp {keb_motor_1:,.0f} [Total 1+2: {l_butuh} L vs Std {est_l_mot} L | {ket_selisih_mot} | {hist_km_mot_str}]"
                            info_bbm_mot2 = f"Beli: {sumber_mot.upper()} | Tangki: {k_tangki:g} L | Isi 2: {l_butuh_2} L (@Rp {h_satuan:,.0f}) = Rp {keb_motor_2:,.0f} [Total 1+2: {l_butuh} L vs Std {est_l_mot} L | {ket_selisih_mot} | {hist_km_mot_str}]"
                            sub_requests.append({"tiket": f"{base_tiket_clean} [MOTOR-1]", "kategori": f"{kat_mot_base} (Isi 1)", "kebutuhan": keb_motor_1, "plat": plat_motor, "indikator": km_awal_mot, "last_ind": last_km_mot, "tipe": "Motor", "info_bbm": info_bbm_mot1, "harga_satuan": h_satuan, "kapasitas_tangki": k_tangki, "sumber_bbm": sumber_mot})
                            sub_requests.append({"tiket": f"{base_tiket_clean} [MOTOR-2]", "kategori": f"{kat_mot_base} (Isi 2)", "kebutuhan": keb_motor_2, "plat": plat_motor, "indikator": km_awal_mot, "last_ind": last_km_mot, "tipe": "Motor", "info_bbm": info_bbm_mot2, "harga_satuan": h_satuan, "kapasitas_tangki": k_tangki, "sumber_bbm": sumber_mot})
                    
                        current_month_str = datetime.now().strftime("%m/%Y")
                        for r in req_r[1:]:
                            if len(r) > 10:
                                try:
                                    tgl_req = parse_date(r[1])
                                    if tgl_req.strftime("%m/%Y") == current_month_str and str(r[5]).strip().upper() == nama_lookup:
                                        if "motor" in str(r[10]).lower(): total_motor_this_month += clean_nominal(r[9])
                                except: pass
                            
                # 3. LOGIKA GENSET (SOLAR & GENSET PORTABLE PERTALITE/PERTAMAX + SPBU/ECERAN + WAJIB TANGKI + LIVE KONTROL RH)
                if "Genset" in jns_bbm_list:
                    is_genset = True
                    with st.expander("⚡ Input BBM Genset (Solar / Genset Portable Pertalite-Pertamax, Tangki & Live Kontrol RH)", expanded=True):
                        tipe_genset = st.radio(
                            "🔌 Pilih Tipe Unit Genset:",
                            ["⚡ Genset Solar / Mobile (Dexlite / Bio Solar / Pertamina Dex)", "🔋 Genset Portable / Bensin (Pertalite / Pertamax)"],
                            horizontal=True,
                            key="tipe_gen_sel"
                        )
                        is_gen_portable = ("Portable" in tipe_genset)
                        rate_l_per_jam = 1.2 if is_gen_portable else 2.5
                        opsi_jb_genset = ["Pertalite", "Pertamax"] if is_gen_portable else ["Dexlite", "Bio Solar", "Pertamina Dex"]

                        c_g1, c_g2 = st.columns(2)
                        with c_g1:
                            sumber_gen = st.radio("Sumber Pembelian BBM Genset:", ["SPBU", "Eceran"], horizontal=True, key="src_gen")
                            if sumber_gen == "Eceran":
                                st.warning("⚠️ **PEMBELIAN ECERAN:** Saat PJB nanti **WAJIB** melampirkan 2 foto tambahan (1. Full foto isi BBM sesuai jumlah botol/jerigen liter, 2. Foto bukti bayar cash/transfer ke toko) yang akan **dianalisa oleh AI**.")
                            jb_genset = st.selectbox("Jenis BBM Genset", opsi_jb_genset, key="b_gen")
                            _, _, rule_gen = get_bbm_rule(jb_genset, sumber_gen)
                            def_harga_gen = rule_gen["default"] if rule_gen else (10000 if is_gen_portable else 25000)

                            gen_price_sig = f"{tipe_genset}|{sumber_gen}|{jb_genset}"
                            if st.session_state.get("_prev_gen_sig") != gen_price_sig:
                                st.session_state["_prev_gen_sig"] = gen_price_sig
                                st.session_state["hs_gen"] = int(def_harga_gen)
                            
                            lbl_tangki_gen = "Kapasitas Tangki Genset Portable / Jerigen (Liter) [WAJIB DIISI]" if is_gen_portable else "Kapasitas Tangki Genset / Jerigen (Liter) [WAJIB DIISI]"
                            k_tangki_gen = st.number_input(lbl_tangki_gen, min_value=0.0, max_value=500.0, step=1.0, value=0.0, key="kt_gen", help="Wajib cantumkan kapasitas tangki genset atau total jerigen yang dibawa per pengisian agar tidak over request.")
                            if k_tangki_gen <= 0:
                                st.error("🚨 **WAJIB DIISI:** Cantumkan **Kapasitas Tangki Genset / Jerigen (Liter)** untuk pengisian 1x maupun 2x agar tidak terjadi over request!")
                                bbm_tank_lock = True

                            est_jam_gen = st.number_input("Estimasi Durasi Running / Backup (Jam)", min_value=0.5, step=0.5, value=5.0, key="jam_gen")
                            est_liter_gen = max(0.5, round(est_jam_gen * rate_l_per_jam, 1))
                            
                            h_satuan_gen = st.number_input(f"Harga Satuan BBM Genset ({sumber_gen} - Rp/Liter)", min_value=0, step=100, key="hs_gen")
                            ok_hgen, msg_hgen = validate_bbm_price(jb_genset, h_satuan_gen, sumber_gen)
                            if not ok_hgen:
                                st.error(f"🚨 **VALIDASI HARGA BBM GENSET ({sumber_gen.upper()}):** {msg_hgen}")
                                bbm_price_errors.append(f"Genset {jb_genset} [{sumber_gen}]: {msg_hgen}")
                            else:
                                st.caption(f"✅ {msg_hgen}")

                            opsi_pengisian_gen = st.radio("Opsi Pengisian Genset:", ["1x Pengisian", "2x Pengisian (Kapasitas Tangki/Jerigen Kurang)"], key="opt_gen")
                            if opsi_pengisian_gen == "1x Pengisian":
                                l_gen_req = st.number_input("Total Liter BBM Genset Diperlukan (Liter)", min_value=0.0, step=0.5, value=max(0.5, float(est_liter_gen)), key="l_gen")
                                keb_genset = int(round(l_gen_req * h_satuan_gen))
                                if l_gen_req <= 0:
                                    st.error("🚨 Total Liter BBM Genset wajib lebih dari 0 Liter!")
                                    bbm_tank_lock = True
                                elif k_tangki_gen > 0 and l_gen_req > k_tangki_gen:
                                    st.error(f"🚨 **OVER REQUEST TANGKI GENSET:** Pengisian {l_gen_req:g} L melebihi kapasitas tangki/jerigen ({k_tangki_gen:g} L)! Kurangi liter atau pilih **Opsi 2x Pengisian**.")
                                    bbm_tank_lock = True
                            else:
                                st.info("💡 Sistem otomatis memecah tiket ini jadi [GENSET-1] & [GENSET-2]. Masing-masing pengisian tidak boleh melebihi kapasitas tangki/jerigen.")
                                def_split_gen = max(0.5, round(est_liter_gen / 2.0, 1))
                                l_gen_1 = st.number_input("Liter Pengisian Genset 1 (Wajib)", min_value=0.0, step=0.5, value=float(def_split_gen), key="lgen_1")
                                l_gen_2 = st.number_input("Liter Pengisian Genset 2 (Wajib)", min_value=0.0, step=0.5, value=float(def_split_gen), key="lgen_2")
                                l_gen_req = round(l_gen_1 + l_gen_2, 1)
                                keb_genset_1 = int(round(l_gen_1 * h_satuan_gen))
                                keb_genset_2 = int(round(l_gen_2 * h_satuan_gen))
                                keb_genset = keb_genset_1 + keb_genset_2
                                if l_gen_1 <= 0 or l_gen_2 <= 0:
                                    st.error("🚨 Liter Pengisian 1 dan Pengisian 2 Genset masing-masing wajib lebih dari 0 Liter!")
                                    bbm_tank_lock = True
                                elif k_tangki_gen > 0 and (l_gen_1 > k_tangki_gen or l_gen_2 > k_tangki_gen):
                                    st.error(f"🚨 **OVER REQUEST TANGKI GENSET (2x Pengisian):** Setiap tahap pengisian (Isi 1: {l_gen_1:g} L / Isi 2: {l_gen_2:g} L) tidak boleh melebihi kapasitas tangki/jerigen ({k_tangki_gen:g} L)!")
                                    bbm_tank_lock = True
                            
                            std_biaya_gen = int(round(est_liter_gen * h_satuan_gen))
                            selisih_l_gen = round(l_gen_req - est_liter_gen, 1)
                            selisih_rp_gen = keb_genset - std_biaya_gen
                            lbl_tipe_g = "Genset Portable" if is_gen_portable else "Genset Solar"
                            
                            if selisih_l_gen > 0.5:
                                ket_selisih_gen = f"OVER +{selisih_l_gen} L (+Rp {selisih_rp_gen:,.0f})"
                                st.warning(
                                    f"📊 **Komparasi Otomatis BBM {lbl_tipe_g} ({sumber_gen}):**\n"
                                    f"- **Request Tim:** {format_id_number(l_gen_req)} Liter × Rp {h_satuan_gen:,.0f} = **Rp {keb_genset:,.0f}** (Tangki: {k_tangki_gen:g} L)\n"
                                    f"- **Seharusnya (Backup {est_jam_gen} Jam @ {rate_l_per_jam} L/Jam):** {format_id_number(est_liter_gen)} Liter (**Rp {std_biaya_gen:,.0f}**)\n"
                                    f"- **Keterangan Selisih:** ⚠️ **Lebih +{format_id_number(selisih_l_gen)} Liter (+Rp {selisih_rp_gen:,.0f})** dari standar durasi"
                                )
                            elif selisih_l_gen < -0.5:
                                ket_selisih_gen = f"HEMAT {selisih_l_gen} L (-Rp {abs(selisih_rp_gen):,.0f})"
                                st.success(
                                    f"📊 **Komparasi Otomatis BBM {lbl_tipe_g} ({sumber_gen}):**\n"
                                    f"- **Request Tim:** {format_id_number(l_gen_req)} Liter × Rp {h_satuan_gen:,.0f} = **Rp {keb_genset:,.0f}** (Tangki: {k_tangki_gen:g} L)\n"
                                    f"- **Seharusnya (Backup {est_jam_gen} Jam @ {rate_l_per_jam} L/Jam):** {format_id_number(est_liter_gen)} Liter (**Rp {std_biaya_gen:,.0f}**)\n"
                                    f"- **Keterangan Selisih:** ✅ **Hemat {format_id_number(selisih_l_gen)} Liter (-Rp {abs(selisih_rp_gen):,.0f})**"
                                )
                            else:
                                ket_selisih_gen = f"SESUAI STANDAR (Selisih {selisih_l_gen:+.1f} L)"
                                st.info(
                                    f"📊 **Komparasi Otomatis BBM {lbl_tipe_g} ({sumber_gen}):**\n"
                                    f"- **Request Tim:** {format_id_number(l_gen_req)} Liter × Rp {h_satuan_gen:,.0f} = **Rp {keb_genset:,.0f}** (Tangki: {k_tangki_gen:g} L)\n"
                                    f"- **Seharusnya (Backup {est_jam_gen} Jam @ {rate_l_per_jam} L/Jam):** {format_id_number(est_liter_gen)} Liter (**Rp {std_biaya_gen:,.0f}**)\n"
                                    f"- **Keterangan Selisih:** ✅ **Sesuai Standar Sistem**"
                                )

                        with c_g2:
                            pilihan_gen = st.selectbox("ID / Plat Genset", options_nopol, key="p_gen")
                            if pilihan_gen == "-- Pilih Nopol / Ketik Baru --": plat_genset = st.text_input("Ketik ID Genset (Misal: PORTABLE-01):", key="pgen_man").strip().upper()
                            else: plat_genset = pilihan_gen.strip().upper()
                            
                            tanpa_rh_portable = False
                            if is_gen_portable:
                                tanpa_rh_portable = st.checkbox("🔋 Genset Portable tidak memiliki meteran RH digital (gunakan estimasi jam backup)", value=False, key="chk_gen_port_norh")

                            last_info_gen = get_last_indicator_detail(plat_genset, "Genset", pjb_r, req_r, app_r=app_r, spreadsheet_id=target_ss)
                            last_rh_gen = last_info_gen["value"]
                            if st.session_state.get("_prev_plat_gen") != plat_genset:
                                st.session_state["_prev_plat_gen"] = plat_genset
                                st.session_state["rh_gen_txt"] = str(int(last_rh_gen)) if last_rh_gen == int(last_rh_gen) else str(last_rh_gen)

                            if tanpa_rh_portable:
                                rh_awal_gen = float(last_rh_gen) if last_rh_gen > 0 else 0.0
                                selisih_rh_gen = 0.0
                                ctrl_gen = {"is_blocking": False, "level": "ok", "elapsed_text": "-", "selisih": 0.0, "status_short": "PORTABLE TANPA RH METER", "detail_lines": []}
                                st.info(f"🔋 **Mode Genset Portable (Non-RH Meter):** Estimasi backup **{est_jam_gen} Jam** | BBM **{jb_genset} ({sumber_gen})**.")
                            else:
                                rh_gen_raw = st.text_input(
                                    f"RH Awal Genset Sekarang (Histori Terakhir: {format_id_number(last_rh_gen)} RH)",
                                    key="rh_gen_txt",
                                    placeholder="Ketik angka polos tanpa titik ribuan, misal: 1450 atau 1450,5",
                                    help="Jangan gunakan titik sebagai pemisah ribuan! Gunakan koma untuk angka desimal (contoh: 1450,5)."
                                )
                                rh_awal_gen, lvl_rhg, note_rhg = parse_indonesian_indicator(rh_gen_raw, last_rh_gen, "RH")
                                if lvl_rhg == "err":
                                    st.error(note_rhg)
                                    bbm_ind_errors.append(f"Genset ({plat_genset}): {note_rhg}")
                                elif lvl_rhg == "warn":
                                    st.warning(note_rhg)
                                else:
                                    st.caption(f"🔎 {note_rhg}")

                                ctrl_gen = evaluate_live_indicator_control(rh_awal_gen, last_info_gen, now_wib_req, tipe="Genset")
                                if ctrl_gen["is_blocking"]:
                                    st.error("⏱️ **LIVE KONTROL RH & WAKTU GENSET:**\n" + "\n".join(ctrl_gen["detail_lines"]))
                                    bbm_ind_errors.append(f"Genset ({plat_genset}): {ctrl_gen['status_short']}")
                                elif ctrl_gen["level"] == "warn":
                                    st.warning("⏱️ **LIVE KONTROL RH & WAKTU GENSET:**\n" + "\n".join(ctrl_gen["detail_lines"]))
                                else:
                                    st.info("⏱️ **LIVE KONTROL RH & WAKTU GENSET:**\n" + "\n".join(ctrl_gen["detail_lines"]))
                                selisih_rh_gen = ctrl_gen["selisih"]
                            if plat_genset:
                                _pn_g = normalize_plat_key(plat_genset)
                                _h_gen = []
                                for _rp in reversed(pjb_r[1:]):
                                    if len(_rp) > 12 and normalize_plat_key(_rp[12]) == _pn_g and "genset" in str(_rp[8]).lower():
                                        _h_gen.append({"Tanggal": _rp[1], "Tiket": _rp[21] if len(_rp)>21 else "-", "PIC": _rp[4], "RH Akhir": format_id_number(clean_indicator(_rp[10])), "Run": f"{_rp[24] if len(_rp)>24 else '-'} RH"})
                                        if len(_h_gen) >= 5: break
                                if _h_gen:
                                    with st.expander(f"📜 5 Histori RH Terakhir ({plat_genset})", expanded=False):
                                        st.dataframe(pd.DataFrame(_h_gen), hide_index=True, use_container_width=True)
                        
                        hist_rh_gen_str = "Portable Non-RH" if tanpa_rh_portable else (f"RH {format_id_number(last_rh_gen)}->{format_id_number(rh_awal_gen)} (+{format_id_number(selisih_rh_gen)} RH dlm {ctrl_gen['elapsed_text']} | {ctrl_gen['status_short']})" if last_rh_gen > 0 else f"RH Awal: {format_id_number(rh_awal_gen)}")
                        kat_gen_base = f"Genset Portable - {jb_genset} [{sumber_gen.upper()}]" if is_gen_portable else f"Genset - {jb_genset} [{sumber_gen.upper()}]"
                        if opsi_pengisian_gen == "1x Pengisian":
                            info_bbm_gen = f"Unit: {lbl_tipe_g} | Beli: {sumber_gen.upper()} | Tangki: {k_tangki_gen:g} L | Req Tim: {l_gen_req} L (@Rp {h_satuan_gen:,.0f}) = Rp {keb_genset:,.0f} | Seharusnya ({est_jam_gen} Jam): {est_liter_gen} L (Rp {std_biaya_gen:,.0f}) | Selisih: {ket_selisih_gen} | {hist_rh_gen_str}"
                            sub_requests.append({"tiket": f"{base_tiket_clean} [GENSET]", "kategori": kat_gen_base, "kebutuhan": keb_genset, "plat": plat_genset, "indikator": rh_awal_gen, "last_ind": last_rh_gen, "tipe": "Genset", "info_bbm": info_bbm_gen, "harga_satuan": h_satuan_gen, "kapasitas_tangki": k_tangki_gen, "sumber_bbm": sumber_gen, "skip_ind_check": tanpa_rh_portable})
                        else:
                            info_bbm_gen1 = f"Unit: {lbl_tipe_g} | Beli: {sumber_gen.upper()} | Tangki: {k_tangki_gen:g} L | Isi 1: {l_gen_1} L (@Rp {h_satuan_gen:,.0f}) = Rp {keb_genset_1:,.0f} [Total 1+2: {l_gen_req} L vs Std {est_liter_gen} L | {ket_selisih_gen} | {hist_rh_gen_str}]"
                            info_bbm_gen2 = f"Unit: {lbl_tipe_g} | Beli: {sumber_gen.upper()} | Tangki: {k_tangki_gen:g} L | Isi 2: {l_gen_2} L (@Rp {h_satuan_gen:,.0f}) = Rp {keb_genset_2:,.0f} [Total 1+2: {l_gen_req} L vs Std {est_liter_gen} L | {ket_selisih_gen} | {hist_rh_gen_str}]"
                            sub_requests.append({"tiket": f"{base_tiket_clean} [GENSET-1]", "kategori": f"{kat_gen_base} (Isi 1)", "kebutuhan": keb_genset_1, "plat": plat_genset, "indikator": rh_awal_gen, "last_ind": last_rh_gen, "tipe": "Genset", "info_bbm": info_bbm_gen1, "harga_satuan": h_satuan_gen, "kapasitas_tangki": k_tangki_gen, "sumber_bbm": sumber_gen, "skip_ind_check": tanpa_rh_portable})
                            sub_requests.append({"tiket": f"{base_tiket_clean} [GENSET-2]", "kategori": f"{kat_gen_base} (Isi 2)", "kebutuhan": keb_genset_2, "plat": plat_genset, "indikator": rh_awal_gen, "last_ind": last_rh_gen, "tipe": "Genset", "info_bbm": info_bbm_gen2, "harga_satuan": h_satuan_gen, "kapasitas_tangki": k_tangki_gen, "sumber_bbm": sumber_gen, "skip_ind_check": tanpa_rh_portable})
                st.markdown("</div>", unsafe_allow_html=True)
            
            # =========================================================
            # B. LOGIKA UANG MAKAN & PENGINAPAN (PEMBARUAN: ATAS + RRU <80KM = Rp 30.000; PP >80KM = ATURAN ASLI)
            # =========================================================
            if "Uang Makan" in kebutuhan_dana_list or "Penginapan" in kebutuhan_dana_list:
                st.markdown("<div style='background-color:#E0F2FE; padding:15px; border-radius:10px; border-left: 5px solid #0284C7; margin-bottom: 15px;'>", unsafe_allow_html=True)
            
                c_um1, c_um2 = st.columns(2)
                with c_um1:
                    hari_req = st.number_input("Rencana Berapa Hari (Durasi Kerja)?", min_value=1, step=1, value=1)
                    jml_org = 1 + len(tim_bareng)
                
                if "Uang Makan" in kebutuhan_dana_list:
                    st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
                
                    # Blokir jika belum memilih kategori pekerjaan
                    if not val_atas and not val_bawah and not is_kirim_mat:
                        st.error("❌ SISTEM MENOLAK: Anda memilih Uang Makan tapi belum menentukan jenis pekerjaan (Atas/Bawah/Material) di atas!")
                        _wz_clamp(4)
                        st.stop()
                    
                    # Logika Sistem Cerdas (Berat = 60k jika PP >80KM, Ringan = 30k jika PP >80KM; Khusus Atas + Ganti RRU <80KM = 30k)
                    is_berat = False
                    if val_atas or is_kirim_mat: is_berat = True
                    if val_bawah:
                        for item in val_bawah:
                            # Jika ada pilihan SELAIN MCB dan BCP, otomatis dianggap kerja berat
                            if item not in ["Pengecekan MCB", "BCP"]: 
                                is_berat = True
                    
                    is_atas_rru = ("RRU" in val_atas)
                    allow_um_under_80 = False
                            
                    if jarak_km_pp < 80:
                        if is_atas_rru:
                            base_um = 30000
                            allow_um_under_80 = True
                            kategori_teks = "Uang Makan (Pekerjaan Atas - Ganti RRU <80KM)"
                            alasan = f"✅ **Pekerjaan Atas — Ganti RRU (<80 KM):** Meskipun jarak tempuh PP hanya {jarak_km_pp:.1f} KM (<80 KM), karena pekerjaan di atas tower mengganti **RRU**, tim berhak mendapatkan **Rp 30.000/orang** *(Rp 60.000/orang berlaku jika jarak PP >80 KM)*."
                            st.info(alasan)
                        else:
                            st.error(f"❌ JARAK TIDAK MEMENUHI SYARAT: Jarak tempuh Peta hanya {jarak_km_pp:.1f} KM. Syarat minimal Uang Makan adalah >80 KM (kecuali Pekerjaan Atas ganti RRU mendapat Rp 30.000). Nominal dikunci ke 0.")
                            base_um = 0
                            kategori_teks = "Uang Makan (Tidak Memenuhi Syarat)"
                    else:
                        if is_berat:
                            base_um = 60000
                            kategori_teks = "Uang Makan (Pekerjaan Berat)"
                            alasan = f"✅ **Kategori Pekerjaan Berat:** Jarak {jarak_km_pp:.1f} KM (>80 KM) tercapai. Tim berhak mendapatkan **Rp 60.000/orang**."
                        else:
                            base_um = 30000
                            kategori_teks = "Uang Makan (Pekerjaan Ringan)"
                            alasan = f"⚠️ **Kategori Pekerjaan Ringan:** Jarak {jarak_km_pp:.1f} KM (>80 KM) namun pekerjaan ringan. Tim berhak mendapatkan **Rp 30.000/orang**."
                        st.info(alasan)
                
                    st.warning("🔒 **SYSTEM LOCK AKTIF:** Nominal tidak bisa diubah manual agar tertib. Hubungi Admin / Boss jika butuh approval khusus.")
                
                    with c_um2:
                        max_um_nominal = int(base_um * jml_org)
                        # FITUR DISABLED=TRUE + key dinamis agar selalu sinkron & bebas StreamlitValueAboveMaxError
                        nom_req_um = st.number_input("Nominal UM/Hari (TERKUNCI)", min_value=0, value=max_um_nominal, step=5000, disabled=True, key=f"um_locked_{max_um_nominal}")
                    
                    tot_um = hari_req * nom_req_um
                    if tot_um > 0:
                        st.success(f"💰 Total Estimasi Uang Makan: **Rp {tot_um:,.0f}**")
                        sub_requests.append({"tiket": f"{base_tiket_clean} [UM]", "kategori": kategori_teks, "kebutuhan": tot_um, "plat": "", "indikator": 0.0, "last_ind": 0.0, "tipe": "UM", "hari": hari_req, "nom_um": nom_req_um, "allow_under_80": allow_um_under_80})
                
                if "Penginapan" in kebutuhan_dana_list:
                    with c_um1:
                        malam_inap = st.number_input("Berapa Malam Menginap?", min_value=1, step=1, value=hari_req if hari_req == 1 else hari_req - 1)
                    with c_um2:
                        max_inap_nominal = int(150000 * jml_org)
                        nom_req_inap = st.number_input(f"Nominal Inap/Malam (Maks Rp 150.000 x {jml_org} org)", min_value=0, max_value=max_inap_nominal, step=10000, value=max_inap_nominal, key=f"inap_nom_{jml_org}")
                    
                    tot_inap = malam_inap * nom_req_inap
                    st.success(f"🛏️ Total Estimasi Penginapan: **Rp {tot_inap:,.0f}**")
                    sub_requests.append({"tiket": f"{base_tiket_clean} [INAP]", "kategori": "Penginapan", "kebutuhan": tot_inap, "plat": "", "indikator": 0.0, "last_ind": 0.0, "tipe": "Inap", "hari": malam_inap, "nom_inap": nom_req_inap, "allow_under_80": False})
                st.markdown("</div>", unsafe_allow_html=True)
            
            # =========================================================
            # C. LOGIKA ASLI MATERIAL, SUPPORT, FERY & KLOTOK
            # =========================================================
            if "Material" in kebutuhan_dana_list:
                with st.expander("📦 Detail Material", expanded=True):
                    nama_brg_mat = st.text_input("Bentuk / Nama Barang & Jumlah (Contoh: MCB 32A 1 pcs, Isolasi 2 bh):", key="brg_mat")
                    keb_mat = st.number_input("Estimasi Dana Material (Rp)", min_value=0, step=1000)
                    kat_mat_label = f"Material ({nama_brg_mat})" if nama_brg_mat.strip() else "Material"
                    sub_requests.append({"tiket": f"{base_tiket_clean} [MATERIAL]", "kategori": kat_mat_label, "kebutuhan": keb_mat, "plat": "", "indikator": 0.0, "last_ind": 0.0, "tipe": "Material"})
                
            if "Support" in kebutuhan_dana_list:
                with st.expander("🤝 Detail Support", expanded=True):
                    keb_support = st.number_input("Estimasi Dana Support (Rp)", min_value=0, step=1000)
                    sub_requests.append({"tiket": f"{base_tiket_clean} [SUPPORT]", "kategori": "Support", "kebutuhan": keb_support, "plat": "", "indikator": 0.0, "last_ind": 0.0, "tipe": "Support"})
                
            if "Fery Reguler/Carter" in kebutuhan_dana_list:
                with st.expander("⛴️ Detail Fery Reguler/Carter", expanded=True):
                    keb_fery = st.number_input("Estimasi Dana Fery (Rp)", min_value=0, step=1000)
                    sub_requests.append({"tiket": f"{base_tiket_clean} [FERY]", "kategori": "Fery", "kebutuhan": keb_fery, "plat": "", "indikator": 0.0, "last_ind": 0.0, "tipe": "Fery"})
                
            if "Klotok/Kapal Carter" in kebutuhan_dana_list:
                with st.expander("🛥️ Detail Klotok/Kapal Carter", expanded=True):
                    keb_klotok = st.number_input("Estimasi Dana Klotok (Rp)", min_value=0, step=1000)
                    sub_requests.append({"tiket": f"{base_tiket_clean} [KLOTOK]", "kategori": "Klotok", "kebutuhan": keb_klotok, "plat": "", "indikator": 0.0, "last_ind": 0.0, "tipe": "Klotok"})

            total_kebutuhan_all = sum([r['kebutuhan'] for r in sub_requests])
            if sub_requests: st.markdown(f"<div class='metric-3d' style='border-top: 6px solid #10B981;'><div class='metric-title'>Total Kalkulasi Kebutuhan Dana</div><div class='metric-value'>Rp {total_kebutuhan_all:,.0f}</div></div>", unsafe_allow_html=True)
        with _wz_box("wz5_a"):
            st.markdown("<div class='section-title'>🏦 5. Pembayaran & Lampiran</div>", unsafe_allow_html=True)
            col_pay1, col_pay2 = st.columns(2)
            with col_pay1:
                bank_idx = ["BNI", "BCA", "MANDIRI", "BRI"].index(default_bank) if default_bank in ["BNI", "BCA", "MANDIRI", "BRI"] else 0
                rek_penerima = st.selectbox("Bank Penerima", ["BNI", "BCA", "MANDIRI", "BRI"], index=bank_idx)
                no_rek = st.text_input("Nomor Rekening", value=default_no_rek)
            with col_pay2:
                nominal_tf_str = st.text_input("Total Nominal Transfer Final", str(total_kebutuhan_all))
                try: nominal_tf = int(nominal_tf_str.replace(".", "").replace(",", "").strip())
                except: nominal_tf = 0
            
            st.markdown("<div class='section-title'>📸 Lampiran (Forensik AI)</div>", unsafe_allow_html=True)
            c_up1, c_up2 = st.columns(2)
            with c_up1: foto_km = ui_image_uploader("1. Foto KM / RH Genset Awal", key="req_km")
            with c_up2: foto_evidance = ui_image_uploader("2. Foto Evidance Request", key="req_ev")
        
        with _wz_box("wz6_a"):
            if WZ_ON:
                _id_ok = bool(nama) and bool(cluster) and role != "-- Pilih Role --" and bool(keperluan) and bool(base_tiket_clean)
                _perlu_peta = any(r["tipe"] in ("UM", "Inap") for r in sub_requests)
                if is_kirim_mat and (not mat_module or not mat_site):
                    _s2 = ("err", "Pengiriman Material: nama module & site tujuan wajib diisi")
                elif not deskripsi.strip():
                    _s2 = ("warn", "deskripsi pekerjaan masih kosong")
                else:
                    _s2 = ("ok", "")
                if not invalid_coords: _s3 = ("ok", "")
                elif _perlu_peta: _s3 = ("err", "koordinat wajib valid untuk Uang Makan / Penginapan")
                else: _s3 = ("warn", "koordinat belum lengkap, jarak tidak terhitung")
                if nominal_tf <= 0: _s5 = ("err", "total nominal transfer harus lebih dari 0")
                elif not no_rek.strip(): _s5 = ("warn", "nomor rekening belum diisi")
                else: _s5 = ("ok", "")
                _wz_ringkasan([
                    (1, "Petugas & tiket pokok", "ok" if _id_ok else "err", "nama, cluster, role, keperluan & nomor tiket wajib diisi"),
                    (2, "Detail pekerjaan", _s2[0], _s2[1]),
                    (3, "Rute peta", _s3[0], _s3[1]),
                    (4, "Rincian dana", "ok" if sub_requests else "err", "pilih minimal 1 kebutuhan dana"),
                    (5, "Pembayaran & lampiran", _s5[0], _s5[1]),
                ])

            # --- TAMBAHAN CHECKLIST DINAMIS (MULAI) ---
            st.markdown("<div class='section-title'>✅ 6. Checklist Persiapan & Komitmen Tim</div>", unsafe_allow_html=True)
            st.markdown("<div style='background-color:#FFFBEB; padding:15px; border-radius:10px; border-left: 5px solid #F59E0B; margin-bottom: 20px;'>", unsafe_allow_html=True)
            st.write("⚠️ **WAJIB DICENTANG SELURUHNYA UNTUK MEMUNCULKAN TOMBOL SUBMIT:**")
        
            all_checked = True
        
            # Trigger Checklist Pintar dari pilihan Atas/Bawah/PM
            show_atas = len(val_atas) > 0
            show_bawah = len(val_bawah) > 0
            show_pm = any("Preventive Maintenance" in x for x in val_bawah)
        
            if show_atas:
                st.markdown("<b style='color:#EF4444;'>🛠️ TSHOOT BAGIAN ATAS:</b>", unsafe_allow_html=True)
                if not st.checkbox("1. Body harnes", key="c_a1"): all_checked = False
                if not st.checkbox("2. Tambang", key="c_a2"): all_checked = False
                if not st.checkbox("3. Material/module", key="c_a3"): all_checked = False
                if not st.checkbox("4. Helm Climbing", key="c_a4"): all_checked = False
                if not st.checkbox("5. Tang amper", key="c_a5"): all_checked = False
                if not st.checkbox("6. Pastikan sebelum naik semua material kondisi baik & berfungsi. JANGAN DIMULAI JIKA ADA KEKURANGAN.", key="c_a6"): all_checked = False
                st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
            
            if show_bawah:
                st.markdown("<b style='color:#3B82F6;'>🔌 TSHOOT BAGIAN BAWAH:</b>", unsafe_allow_html=True)
                if not st.checkbox("1. Tang Amper", key="c_b1"): all_checked = False
                if not st.checkbox("2. Sarung tangan", key="c_b2"): all_checked = False
                if not st.checkbox("3. Material/Module", key="c_b3"): all_checked = False
                if not st.checkbox("4. Sepatu Safety", key="c_b4"): all_checked = False
                if not st.checkbox("5. Perkabelan dan optikal/sfp", key="c_b5"): all_checked = False
                if not st.checkbox("6. Pastikan semua berfungsi, jangan memulai pekerjaan jika ada kekurangan.", key="c_b6"): all_checked = False
                st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
            
            if show_pm:
                st.markdown("<b style='color:#10B981;'>🦺 KHUSUS PREVENTIVE MAINTENANCE (JSA):</b>", unsafe_allow_html=True)
                if not st.checkbox("1. Sertifikat", key="c_p1"): all_checked = False
                if not st.checkbox("2. Box P3K standart (Eskalasi jika perlu)", key="c_p2"): all_checked = False
                if not st.checkbox("3. Sepatu Safety", key="c_p3"): all_checked = False
                if not st.checkbox("4. Banner ditulis site id dan nomor hp sesuai kebutuhan", key="c_p4"): all_checked = False
                if not st.checkbox("5. Policeline", key="c_p5"): all_checked = False
                if not st.checkbox("6. Semua tools JSA Wajib lengkap (MENGHINDARI REJECT PM DAN TEMUAN)", key="c_p6"): all_checked = False
                st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
            
            if not (show_atas or show_bawah or show_pm):
                if not st.checkbox("🤝 Saya BERKOMITMEN menyelesaikan pekerjaan ini dengan tuntas & bertanggung jawab.", key="c_def1"): all_checked = False
            
            st.markdown("</div>", unsafe_allow_html=True)
            # --- TAMBAHAN CHECKLIST DINAMIS (SELESAI) ---

            form_invalid = (nama == "" or cluster == "" or role == "-- Pilih Role --" or keperluan == "" or not base_tiket_clean)

            if is_locked_user or len(tim_terkunci) > 0:
                if is_locked_user: st.error(f"⛔ DILARANG REQUEST: Anda memiliki tiket pending atau ditolak!")
                if len(tim_terkunci) > 0: st.error(f"⛔ DILARANG REQUEST: Tim bawaan Anda memiliki PJB pending!")
            else:
                if is_motor:
                    motor_kebutuhan = sum([r['kebutuhan'] for r in sub_requests if r['tipe'] == 'Motor'])
                    if (total_motor_this_month + motor_kebutuhan) > 500000:
                        st.markdown("<div style='background-color:#FFE4E6; padding:20px; border-radius:10px; border-left: 5px solid #E11D48; margin-bottom: 25px;'>", unsafe_allow_html=True)
                        safe_app_r = app_r[1:] if len(app_r) > 1 else []
                        for r in reversed(safe_app_r):
                            if len(r) > 5 and str(r[2]).strip().upper() == base_tiket_clean and r[3] == "Limit Motor":
                                status_app_motor = str(r[5]).strip().upper()
                                break
                        if status_app_motor == "APPROVED": st.success("✅ Limit Motor disetujui Admin.")
                        elif status_app_motor == "PENDING":
                            st.warning("⏳ Menunggu verifikasi limit motor dari Admin.")
                            motor_limit_lock = True
                        elif status_app_motor == "REJECTED":
                            st.error("❌ Limit DITOLAK.")
                            motor_limit_lock = True
                        else:
                            st.error("🚨 Anda mencapai batas limit BBM Motor bulanan (>500k).")
                            if st.button("🚨 Minta Approval Limit Motor", type="primary", use_container_width=True):
                                append_data(SHEET_APP, [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), nama, base_tiket_clean, "Limit Motor", motor_kebutuhan, "PENDING", f"Bulan ini: Rp {total_motor_this_month:,.0f}"], target_ss)
                                st.success("Terkirim!"); time.sleep(2.5); st.rerun()
                            motor_limit_lock = True
                        st.markdown("</div>", unsafe_allow_html=True)
            
                # VALIDASI KETAT HARGA BBM (MOBIL & GENSET & MOTOR) — BISA MINTA APPROVAL KHUSUS ADMIN
                bbm_price_lock = False
                if bbm_price_errors:
                    st.markdown("<div style='background-color:#FEF2F2; padding:18px; border-radius:10px; border-left: 5px solid #DC2626; margin-bottom: 20px;'>", unsafe_allow_html=True)
                    st.error("🚨 **VALIDASI HARGA BBM TIDAK LOLOS:**\n" + "\n".join([f"- {e}" for e in bbm_price_errors]))
                    status_app_harga_bbm = "NONE"
                    safe_app_r_bbm = app_r[1:] if len(app_r) > 1 else []
                    for r in reversed(safe_app_r_bbm):
                        if len(r) > 5 and str(r[2]).strip().upper() == base_tiket_clean and r[3] == "Harga BBM":
                            status_app_harga_bbm = str(r[5]).strip().upper()
                            break
                    if status_app_harga_bbm == "APPROVED":
                        st.success("✅ Harga BBM khusus untuk tiket ini sudah disetujui Admin.")
                    elif status_app_harga_bbm == "PENDING":
                        st.warning("⏳ Permintaan Approval Harga BBM khusus sedang menunggu verifikasi Admin.")
                        bbm_price_lock = True
                    elif status_app_harga_bbm == "REJECTED":
                        st.error("❌ Permintaan Harga BBM khusus DITOLAK Admin. Wajib sesuaikan ke harga aktual wajar.")
                        bbm_price_lock = True
                    else:
                        if st.button("🚨 Minta Approval Harga BBM Khusus ke Admin", type="primary", use_container_width=True, key="btn_app_harga_bbm"):
                            if base_tiket_clean and nama:
                                append_data(SHEET_APP, [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), nama, base_tiket_clean, "Harga BBM", total_kebutuhan_all, "PENDING", " | ".join(bbm_price_errors)], target_ss)
                                st.success("Permintaan Approval Harga BBM terkirim ke Admin!"); time.sleep(2); st.rerun()
                            else:
                                st.error("Isi Nama dan Nomor Tiket terlebih dahulu sebelum meminta approval!")
                        bbm_price_lock = True
                    st.markdown("</div>", unsafe_allow_html=True)

                if bbm_ind_errors:
                    st.error("🚨 **VALIDASI KM / RH TIDAK LOLOS (CEK TITIK/KOMA & HISTORI):**\n" + "\n".join([f"- {e}" for e in bbm_ind_errors]))
                elif bbm_tank_lock:
                    st.error("🚨 **REQUEST BBM TERKUNCI:** Pastikan **Kapasitas Tangki (Liter)** sudah diisi (>0) dan jumlah liter setiap pengisian tidak melebihi kapasitas tangki di Langkah 4!")
                elif bbm_price_lock:
                    st.error("🚨 **REQUEST BBM TERKUNCI:** Perbaiki Harga Satuan BBM sesuai harga aktual atau tunggu Approval Admin di atas!")
                elif motor_limit_lock:
                    st.error("🚨 Selesaikan status Limit Motor di atas sebelum Anda dapat men-submit request ini.")
                else:
                    if not all_checked:
                        st.warning("⚠️ Silakan centang Checklist Persiapan di atas agar Tombol Submit terbuka.")
                
                    # Fitur 'disabled' akan membuat tombol tetap TAMPIL tapi tidak bisa diklik jika belum dicentang
                    if st.button("📤 Submit Request Dana", type="primary", use_container_width=True, disabled=not all_checked):
                    
                        # BLOKADE KHUSUS PENGIRIMAN MATERIAL
                        if is_kirim_mat and (not mat_module or not mat_site):
                            st.error("❌ PENGIRIMAN DITOLAK: Anda mencentang Pengiriman Material, WAJIB mengisi Nama Module dan Site ID Tujuan di bagian atas!")
                            st.stop()
                    
                        if form_invalid or not sub_requests or nominal_tf <= 0:
                            st.error("❌ Mohon lengkapi formulir (Rincian Dana, Nominal, dan Tiket wajib diisi)!")
                            st.stop()
                        
                        for req in sub_requests:
                            if req['tipe'] in ['UM', 'Inap']:
                                if invalid_coords:
                                    st.error("❌ Peta belum valid. Pastikan Lat & Long tidak 0.")
                                    st.stop()
                                if jarak_km_pp < 80 and not req.get('allow_under_80', False):
                                    st.error(f"❌ Jarak {jarak_km_pp:.1f} KM tidak memenuhi syarat akomodasi (Minimal 80 KM, kecuali Pekerjaan Atas ganti RRU untuk Uang Makan Rp 30.000).")
                                    st.stop()
                            elif req['tipe'] in ['Mobil', 'Motor', 'Genset']:
                                if req.get('kapasitas_tangki', 0) <= 0:
                                    st.error(f"❌ Kapasitas Tangki pada {req['tipe']} wajib diisi (> 0 Liter) agar tidak over request!")
                                    st.stop()
                                if not req.get('skip_ind_check', False) and (req['indikator'] <= 0 or req['indikator'] < req['last_ind']):
                                    st.error(f"❌ KM/RH Awal pada {req['tipe']} bermasalah (0 atau lebih kecil dari histori {req['last_ind']}).")
                                    st.stop()
                    
                        with st.spinner("🚀 Memecah data & Mengirim ke Server (Mohon tunggu)..."):
                            url_km = upload_foto(foto_km)
                            url_evidance = upload_foto(foto_evidance)
                            ts_now = get_now_wib().strftime("%d/%m/%Y %H:%M:%S")
                            tgl_str = tanggal.strftime("%d/%m/%Y")
                        
                            rincian_wa_items = []
                            batch_data_req = [] # <-- WADAH KOTAK UNTUK SISTEM BATCH
                        
                            for idx_r, req in enumerate(sub_requests, 1):
                                desc_final = deskripsi
                                if tim_bareng: desc_final += f"\n\n[Tim: {', '.join(tim_bareng)}]"
                                if req.get('info_bbm'): desc_final += f"\n\n[ANALISA BBM: {req['info_bbm']}]"
                                if req['tipe'] == 'UM': desc_final += f"\n\n[REQ AKOMODASI: {req['hari']} Hari @ Rp {req['nom_um']:,.0f}/hari = Rp {req['kebutuhan']:,.0f}]"
                                elif req['tipe'] == 'Inap': desc_final += f"\n\n[REQ PENGINAPAN: {req['hari']} Malam @ Rp {req['nom_inap']:,.0f}/malam = Rp {req['kebutuhan']:,.0f}]"
                            
                                data_req = [
                                    ts_now, tgl_str, nop, req['tiket'], cluster, nama, role, site_id, keperluan, 
                                    req['kebutuhan'], req['kategori'], desc_final, str(req['indikator']), 
                                    jarak_final_text, lat_berangkat, long_berangkat, req['plat'], 
                                    rek_penerima, no_rek, nominal_tf, url_km, url_evidance, lat_tujuan, long_tujuan
                                ]
                                # Masukkan semua tiket ke dalam wadah (belum dikirim)
                                batch_data_req.append(data_req)
                            
                                if req['plat'] and req['plat'] not in list_nopol_bersih: save_new_nopol_to_csv(req['plat'])

                                # Rangkum rincian item untuk WA TANPA NOMINAL UANG
                                detail_item = f"{idx_r}. *{req['tiket']}* — {req['kategori']}"
                                if req['plat']:
                                    detail_item += f" | Nopol/ID: {req['plat']}"
                                if req['tipe'] in ['Mobil', 'Motor', 'Genset']:
                                    label_ind = "RH Awal" if req['tipe'] == 'Genset' else "KM Awal"
                                    detail_item += f" | {label_ind}: {req['indikator']}"
                                elif req['tipe'] == 'UM':
                                    detail_item += f" | Durasi: {req['hari']} Hari"
                                elif req['tipe'] == 'Inap':
                                    detail_item += f" | Durasi: {req['hari']} Malam"
                                rincian_wa_items.append(detail_item)
                                
                            # PUSH SEMUA TIKET (BATCH) SEKALI JALAN KE GOOGLE SHEETS! (MENCEGAH OVERWRITE)
                            sukses_simpan = append_data_multiple(SHEET_REQUEST, batch_data_req, target_ss)
                        
                            if sukses_simpan:
                                if pm_selected_list: update_pm_ticket_status(target_ss, pm_selected_list, "REQUESTED")
                                
                                # GENERATE TEKS WA PENGAJUAN REQUEST (TANPA NOMINAL UANG)
                                tim_str = ", ".join(tim_bareng) if tim_bareng else "-"
                                rincian_str = "\n".join(rincian_wa_items)
                                wa_req_text = (
                                    f"*PENGAJUAN REQUEST DANA OPERASIONAL (SiRAPI)*\n"
                                    f"📅 Tanggal : {tgl_str} ({ts_now.split(' ')[1]})\n"
                                    f"🌐 Wilayah : NOP {nop} ({cluster})\n"
                                    f"👤 Nama PIC : {nama} ({role})\n"
                                    f"👥 Rekan Tim : {tim_str}\n"
                                    f"🎫 Tiket Pokok : {base_tiket_clean}\n"
                                    f"📍 Site ID : {site_id if site_id else '-'}\n"
                                    f"🛠️ Keperluan : {keperluan}\n"
                                    f"🛣️ Estimasi Rute : {jarak_final_text if jarak_final_text else '-'}\n\n"
                                    f"*📋 Detail Pekerjaan:*\n{deskripsi if deskripsi else '-'}\n\n"
                                    f"*🛒 Rincian Kebutuhan (Sub-Tiket):*\n{rincian_str}\n\n"
                                    f"*🏦 Rekening Penerima:*\n{rek_penerima} - {no_rek}\n\n"
                                    f"*📸 Lampiran Foto Evidance:*\n"
                                    f"• Foto KM/RH Awal : {url_km if url_km else '-'}\n"
                                    f"• Foto Evidance : {url_evidance if url_evidance else '-'}"
                                )
                                st.session_state.req_wa_ready = wa_req_text
                                st.success(f"🎉 Berhasil menyimpan & memecah {len(sub_requests)} sub-tiket secara berurutan! Silakan salin laporan WhatsApp di bawah ini.")

        # TAMPILKAN GENERATOR WA SETELAH REQUEST DISUBMIT
        with _wz_box("wz6_b"):
            if st.session_state.get("req_wa_ready"):
                st.markdown("<hr style='margin: 25px 0;'>", unsafe_allow_html=True)
                st.markdown("<div class='section-title'>📲 Laporan WhatsApp Pengajuan Request (Tanpa Nominal)</div>", unsafe_allow_html=True)
                st.info("💡 Klik ikon **Copy** di pojok kanan atas kotak teks di bawah ini, atau klik tombol **Kirim ke WhatsApp**.")
                st.code(st.session_state.req_wa_ready, language="markdown")
            
                wa_encoded = quote(st.session_state.req_wa_ready)
                c_wa1, c_wa2 = st.columns(2)
                with c_wa1:
                    st.markdown(
                        f'<a href="https://wa.me/?text={wa_encoded}" target="_blank" class="btn-sidata-blue" style="background: linear-gradient(135deg, #22C55E 0%, #16A34A 100%) !important;">📲 BUKA & KIRIM KE WHATSAPP</a>',
                        unsafe_allow_html=True
                    )
                with c_wa2:
                    if st.button("✅ Selesai & Kembali ke Beranda Utama", type="primary", use_container_width=True):
                        st.session_state.req_wa_ready = ""
                        st.session_state.wz_step = 1
                        st.session_state.page = "🏠 Hub Menu Utama"
                        st.rerun()

# ==========================================
# PAGE 2: FORM PJB OPERASIONAL 
# ==========================================
elif st.session_state.page == "✅ Form PJB Operasional":
    st.markdown("<div class='header-card'><h2>Penyelesaian PJB</h2><p>Pilih dan selesaikan sub-tiket Anda secara spesifik.</p></div>", unsafe_allow_html=True)
    
    nop_cari = st.selectbox("📂 1. Pilih Database (NOP):", ["-- Pilih NOP --"] + list(MASTER_DATA.keys()))
    
    if nop_cari != "-- Pilih NOP --":
        target_ss = MASTER_DATA[nop_cari]["spreadsheet_id"]
        data_all = fetch_spreadsheet_data(target_ss)
        req_r, pjb_r, app_r = data_all[SHEET_REQUEST], data_all[SHEET_PJB], data_all[SHEET_APP]
        
        site_dict, site_list, tim_dict, list_nopol_csv, nik_dict = load_excel_data()
        
        # --- ALGORITMA PJB SERAGAM UNTUK SEMUA NOP ---
        status_verif_dict = {}
        for r in app_r[1:]:
            if len(r) > 5 and r[3] == "Verifikasi PJB":
                tiket_app = str(r[2]).strip().upper()
                if tiket_app != "": 
                    status_verif_dict[tiket_app] = str(r[5]).strip()

        pjb_counts = {}
        pjb_tickets_all_set = set()
        for r in pjb_r[1:]:
            if len(r) > 21 and r[21].strip() != "":
                tk_str = r[36].strip() if (len(r) > 36 and r[36].strip()) else r[21].strip()
                tk_list = [t.strip().upper() for t in tk_str.split(",")]
                pjb_tickets_all_set.update(tk_list)
                for t_clean in tk_list:
                    if t_clean and status_verif_dict.get(t_clean) != "REJECTED":
                        pjb_counts[t_clean] = pjb_counts.get(t_clean, 0) + 1
        
        req_app_status = {}
        for r in app_r[1:]:
            if len(r) > 5 and r[3] == "Request Dana":
                tiket_app = str(r[2]).strip().upper()
                if tiket_app != "": 
                    req_app_status[tiket_app] = str(r[5]).strip().upper()
        
        st.markdown("<div class='section-title'>🔍 2. Identifikasi Tim & Tarik Sub-Tiket Data</div>", unsafe_allow_html=True)
        col_id1, col_id2 = st.columns([2, 2])
        with col_id1: 
            idx_nama_pjb = MASTER_DATA[nop_cari]["names"].index(st.session_state.logged_in_user) if st.session_state.logged_in_user in MASTER_DATA[nop_cari]["names"] else 0
            nama_pjb = st.selectbox("👤 Pilih Nama Anda:", ["-- Pilih Nama --"] + MASTER_DATA[nop_cari]["names"], index=idx_nama_pjb+1 if idx_nama_pjb != 0 else 0)
        
        if nama_pjb != "-- Pilih Nama --":
            out_all, out_lock, aging_tickets, hist_cek = get_user_tickets_status(nama_pjb, req_r, pjb_r, app_r)
            if aging_tickets: 
                st.warning(f"🔔 NOTIFIKASI: Anda memiliki **{len(aging_tickets)}** tiket tertunda >3 hari.")

        with col_id2: 
            pass_nominal = st.text_input("🔑 Akses Nominal (Admin):", type="password")
            
        req_counts = {}
        pending_list, pending_options = [], []
        
        for r in req_r[1:]:
            if len(r) > 5 and str(r[3]).strip() != "":
                req_tk_raw = str(r[3]).strip().upper()
                nm = str(r[5]).strip().upper()
                
                req_counts[req_tk_raw] = req_counts.get(req_tk_raw, 0) + 1
                base_tiket = req_tk_raw.split(" [")[0].strip()
                
                if req_app_status.get(req_tk_raw) == "REJECTED" or req_app_status.get(base_tiket) == "REJECTED":
                    continue 
                
                if req_counts[req_tk_raw] > pjb_counts.get(req_tk_raw, 0):
                    is_ready_to_pjb = True
                    
                    if "[MOTOR-2]" in req_tk_raw or "[MOBIL-2]" in req_tk_raw or "[GENSET-2]" in req_tk_raw:
                        tiket_tahap_1 = req_tk_raw.replace("-2]", "-1]")
                        if pjb_counts.get(tiket_tahap_1, 0) == 0:
                            is_ready_to_pjb = False
                            
                    if is_ready_to_pjb:
                        item = {
                            "Tanggal": r[1], 
                            "Nama": r[5], 
                            "No Request": req_tk_raw, 
                            "Kategori Item": r[10] if len(r)>10 else "", 
                            "Keperluan": r[8] if len(r)>8 else ""
                        }
                        if pass_nominal == "B0924649": 
                            item["Nominal Request"] = f"Rp {clean_nominal(r[9]):,.0f}" if len(r)>9 else "Rp 0"
                        
                        if "PM" in (r[8] if len(r)>8 else ""):
                            pm_list = [t.strip() for t in req_tk_raw.split(",") if t.strip()]
                            rem = [t for t in pm_list if pjb_counts.get(t, 0) == 0]
                            item["Sisa Tiket PM"] = ", ".join(rem) if rem else "Menunggu Verifikasi"
                        
                        if nama_pjb != "-- Pilih Nama --":
                            nama_bersih = nama_pjb.strip().upper()
                            if nama_bersih in nm or nm in nama_bersih:
                                pending_list.append(item)
                                if req_tk_raw not in pending_options: pending_options.append(req_tk_raw)
                        else: 
                            pending_list.append(item)
                            if req_tk_raw not in pending_options: pending_options.append(req_tk_raw)
        
        if pending_list: 
            st.dataframe(pd.DataFrame(pending_list), hide_index=True, use_container_width=True)
        else: 
            st.success("💎 Seluruh sub-tiket sudah di-PJB!")
            
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
                            "LatBerangkat": r[14] if len(r)>14 else "0", "LongBerangkat": r[15] if len(r)>15 else "0",
                            "LatTujuan": r[22] if len(r)>22 else "0", "LongTujuan": r[23] if len(r)>23 else "0",
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
                    st.error("❌ Data Pengajuan (Request) Tidak ditemukan di Database.")        
                    
        if st.session_state.get("pjb_data"):
            d = st.session_state.pjb_data
            
            # --- JIKA LOLOS, LANJUTKAN MENAMPILKAN FORM PJB SEPERTI BIASA ---
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
            if any(k in str(d["BBM"]).lower() for k in ["akomodasi", "uang makan"]) or "[UM]" in valid_cari_tiket:
                jns_pjb = "🍽️ Biaya Akomodasi"
                st.info(f"📌 **Kategori Sub-Tiket:** BIAYA AKOMODASI ({str(d['BBM']).upper()})")
            else:
                jns_pjb = "🛠️ Operational Umum"
                st.info(f"📌 **Kategori Sub-Tiket:** {str(d['BBM']).upper()}")
            
            st.markdown("<div class='section-title'>💸 Validasi Bukti Transfer</div>", unsafe_allow_html=True)
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
                    
                    if "Operational" in jns_pjb: nominal_pjb = st.number_input("Nominal PJB Terpakai", value=int(d["NominalReq"]))
                    else: st.info("Nominal PJB dikalkulasi di panel Uang Makan di bawah.")

                real_km_awal = float(d["KMAwal"])
                km_akhir = real_km_awal
                total_km_tempuh = 0.0
                tot_liter = "0"
                harga_satuan = 0
                tot_nilai_nota = 0
                f_isi = f_nota_bbm = f_mat = f_notamat = f_inap = f_kerja = f_km = None
                f_eceran_botol = f_eceran_bayar = None
                f_um1 = f_um2 = f_um3 = f_um4 = None
                sumber_bbm_pjb = "SPBU"
                ai_eceran_ok, ai_eceran_status, ai_eceran_lines, ai_eceran_remark = True, "", [], ""
                pjb_ind_error_flag = False
                
                is_genset = "genset" in str(d["BBM"]).lower()
                is_vehicle = "mobil" in str(d["BBM"]).lower() or "motor" in str(d["BBM"]).lower() or is_genset
                label_akhir = "RH Genset Akhir" if is_genset else "KM Akhir Kendaraan"
                
                jam_mulai_gen, jam_akhir_gen = None, None
                f_tiket_genset = None
                
                if "Operational" in jns_pjb:
                    st.markdown("<div class='section-title'>📝 Realisasi Lapangan & Nominal (Fisik)</div>", unsafe_allow_html=True)
                    
                    if is_genset:
                        st.markdown("<div style='background-color:#FFFBEB; padding:15px; border-radius:10px; border-left: 5px solid #F59E0B; margin-bottom: 15px;'><b>⚡ Validasi Wajib Genset MBP</b></div>", unsafe_allow_html=True)
                        c_g1, c_g2, c_g3 = st.columns(3)
                        with c_g1: jam_mulai_gen = st.time_input("Jam Mulai Backup", value=None)
                        with c_g2: jam_akhir_gen = st.time_input("Jam Berakhir Backup", value=None)
                        with c_g3: f_tiket_genset = st.file_uploader("Screenshot Tiket WAJIB", type=['jpg','png'])

                    if is_vehicle:
                        now_wib_pjb = get_now_wib()
                        st.markdown("""
                        <div style='background-color:#FEF2F2; padding:16px 18px; border-radius:12px; border: 2px solid #DC2626; margin-bottom: 16px;'>
                            <div style='color:#991B1B !important; font-weight:800; font-size:1.02rem;'>
                                🚨 PERHATIAN KERAS: BBM WAJIB HARGA ACTUAL!
                            </div>
                            <div style='color:#7F1D1D !important; font-weight:600; font-size:0.92rem; margin-top:4px;'>
                                Penginputan harga satuan dan liter BBM wajib sesuai harga actual di lapangan/SPBU/Toko. <b>Jika ditemukan kecurangan, maka akan langsung di-audit oleh Management.</b>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Deteksi otomatis SPBU vs Eceran dari data Request
                        is_req_eceran = ("eceran" in str(d.get("BBM", "")).lower()) or ("beli: eceran" in str(d.get("Desc", "")).lower())
                        sumber_bbm_pjb = st.radio(
                            "🏪 Sumber Pembelian BBM Aktual (Sesuai Pembelian di Lapangan):",
                            ["SPBU", "Eceran"],
                            index=1 if is_req_eceran else 0,
                            horizontal=True,
                            key=f"pjb_src_{valid_cari_tiket}"
                        )
                        _, _, rule_pjb_bbm = get_bbm_rule(d["BBM"], sumber_bbm_pjb)
                        if rule_pjb_bbm:
                            if sumber_bbm_pjb == "SPBU":
                                st.caption(f"⛽ Acuan Harga SPBU ({d['BBM']}): **Maks Rp {rule_pjb_bbm['max']:,.0f}/Liter**")
                            else:
                                st.warning(f"🛢️ **MODE PJB ECERAN AKTIF** — Range Harga Eceran: **Rp {rule_pjb_bbm['min']:,.0f} – Rp {rule_pjb_bbm['max']:,.0f}/Liter**. WAJIB unggah 2 Foto Tambahan Eceran di bawah (dianalisa AI).")

                        # TAMPILKAN RINGKASAN KALKULASI JARAK NOPOL & HISTORI TERAKHIR SAAT PJB
                        nopol_stats_pjb, _ = build_nopol_distance_summary(pjb_r, req_r)
                        plat_pjb_key = re.sub(r'\s+', ' ', str(d.get("Plat", "")).strip().upper())
                        nopol_rec_pjb = nopol_stats_pjb.get(plat_pjb_key, {})
                        unit_pjb_lbl = "RH" if is_genset else "KM"
                        is_pjb_portable = ("portable" in str(d.get("BBM", "")).lower()) or ("portable non-rh" in str(d.get("Desc", "")).lower())

                        if plat_pjb_key and plat_pjb_key not in ["", "-", "0", "NONE"]:
                            last_odo_npl = nopol_rec_pjb.get("last_odo", 0.0)
                            tot_trip_npl = nopol_rec_pjb.get("total_trip", 0.0)
                            cnt_trip_npl = nopol_rec_pjb.get("trip_count", 0)
                            last_dt_npl = nopol_rec_pjb.get("last_date", "-")
                            st.info(
                                f"🛣️ **KALKULASI JARAK NOPOL / UNIT (`{plat_pjb_key}`):**\n"
                                f"- **{unit_pjb_lbl} Terakhir Tercatat di PJB:** **{format_id_number(last_odo_npl)} {unit_pjb_lbl}** *(Tgl: {last_dt_npl} | Akumulasi Histori: {format_id_number(tot_trip_npl)} {unit_pjb_lbl} dari {cnt_trip_npl} Trip)*\n"
                                f"- **{unit_pjb_lbl} Awal Tiket Ini:** **{format_id_number(real_km_awal)} {unit_pjb_lbl}**  |  **Estimasi Jarak Satelit Request:** `{d.get('Jarak', '-')}`"
                            )

                        c_c1, c_d1 = st.columns(2)
                        with c_c1:
                            st.info(f"📍 {unit_pjb_lbl} Awal (Saat Request): **{format_id_number(real_km_awal)} {unit_pjb_lbl}**  |  ⏱️ `{now_wib_pjb.strftime('%d/%m/%Y %H:%M WIB')}`")
                            default_km_akhir = max(0.0, float(d.get("km_akhir_lama", real_km_awal)))
                            def_km_str = str(int(default_km_akhir)) if default_km_akhir == int(default_km_akhir) else str(default_km_akhir)
                            km_akhir_raw = st.text_input(
                                f"{label_akhir} AKTUAL (Ketik Polos Tanpa Titik Ribuan)",
                                value=def_km_str,
                                key=f"pjb_km_txt_{valid_cari_tiket}",
                                help="Jangan pakai titik pemisah ribuan! Contoh benar: 125650 atau 1455,5."
                            )
                            km_akhir, lvl_pjb_km, note_pjb_km = parse_indonesian_indicator(km_akhir_raw, real_km_awal, unit_pjb_lbl)
                            if lvl_pjb_km == "err":
                                st.error(note_pjb_km)
                                pjb_ind_error_flag = True
                            elif lvl_pjb_km == "warn":
                                st.warning(note_pjb_km)
                            else:
                                st.caption(f"🔎 {note_pjb_km}")

                            total_km_tempuh = round(km_akhir - real_km_awal, 2)
                            if km_akhir > 0 and total_km_tempuh >= 0:
                                st.info(f"🛣️ Kalkulasi {'Total RH' if is_genset else 'Trip'}: **{format_id_number(total_km_tempuh)} {unit_pjb_lbl}** ({format_id_number(real_km_awal)} → {format_id_number(km_akhir)})")
                                if real_km_awal >= 100 and km_akhir > real_km_awal * 5 and total_km_tempuh > (500 if is_genset else 5000):
                                    st.error(f"🚨 **ANOMALI LONJAKAN DIGIT {unit_pjb_lbl}:** Selisih +{format_id_number(total_km_tempuh)} {unit_pjb_lbl} terlalu ekstrem! Cek apakah salah ketik angka 0 atau titik/koma.")
                                    pjb_ind_error_flag = True
                            elif km_akhir < real_km_awal:
                                st.error(f"🚨 {unit_pjb_lbl} Akhir ({format_id_number(km_akhir)}) lebih kecil dari {unit_pjb_lbl} Awal ({format_id_number(real_km_awal)})!")
                                pjb_ind_error_flag = True
                        with c_d1:
                            tot_liter_raw = st.text_input("Total Liter BBM Aktual (Gunakan koma/titik desimal, misal: 15,5)", value=str(d.get("liter_lama", "0")), key=f"pjb_ltr_{valid_cari_tiket}")
                            _l_num, lvl_ltr, note_ltr = parse_indonesian_indicator(tot_liter_raw, 0.0, "Liter")
                            tot_liter = str(_l_num)
                            if lvl_ltr == "err" and str(tot_liter_raw).strip() not in ["", "0"]:
                                st.error(note_ltr)
                            else:
                                st.caption(f"🔎 Terbaca: **{format_id_number(_l_num)} Liter**")

                            harga_satuan = st.number_input(f"Harga Satuan BBM Aktual ({sumber_bbm_pjb} - Rp/Liter)", min_value=0, step=100, value=max(0, int(d.get("harga_lama", 0))), key=f"pjb_hrg_{valid_cari_tiket}")
                            tot_nilai_nota = st.number_input("Total Fisik Sesuai Nota / Bayar Toko (Rp)", min_value=0, step=1000, value=max(0, int(d.get("nota_lama", 0))), key=f"pjb_nota_{valid_cari_tiket}")
                            ok_pjb_harga, msg_pjb_harga = validate_bbm_price(d["BBM"], harga_satuan, sumber_bbm_pjb)
                            if harga_satuan > 0:
                                if not ok_pjb_harga:
                                    st.error(f"🚨 **VALIDASI HARGA BBM PJB ({sumber_bbm_pjb.upper()}):** {msg_pjb_harga}")
                                else:
                                    st.caption(f"✅ {msg_pjb_harga}")
                            if _l_num > 0 and harga_satuan > 0:
                                _calc_nota = int(round(_l_num * harga_satuan))
                                st.info(f"🧮 Kalkulasi Nota Aktual: **{format_id_number(_l_num)} L × Rp {harga_satuan:,.0f} = Rp {_calc_nota:,.0f}**")
                            
                        st.markdown("<div class='section-title'>📸 Lampiran Bukti Utama</div>", unsafe_allow_html=True)
                        p1, p2, p3 = st.columns(3)
                        with p1: f_isi = ui_image_uploader("1. Evidance Pengisian", key="pjb_isi")
                        with p2: f_km = ui_image_uploader("2. Nota KM/RH", key="pjb_km")
                        with p3: f_kerja = ui_image_uploader("3. Evidance Pekerjaan", key="pjb_krj1")

                        # FOTO TAMBAHAN WAJIB + ANALISA AI KHUSUS PEMBELIAN BBM ECERAN
                        if sumber_bbm_pjb == "Eceran":
                            st.markdown("""
                            <div style='background-color:#FFFBEB; padding:14px 16px; border-radius:10px; border: 2px solid #F59E0B; margin-top: 14px; margin-bottom: 12px;'>
                                <b style='color:#92400E;'>🤖 FOTO TAMBAHAN WAJIB PEMBELIAN ECERAN (DIANALISA OLEH AI):</b><br>
                                <span style='color:#78350F; font-size:0.9rem;'>
                                1. <b>Full Foto Isi BBM</b> yang menampilkan keseluruhan botol/jerigen sesuai jumlah liter yang dibeli.<br>
                                2. <b>Foto Bukti Bayar Cash / Transfer ke Toko Eceran</b> (struk/nota toko/screenshot transfer sesuai harga bayar).
                                </span>
                            </div>
                            """, unsafe_allow_html=True)
                            pe1, pe2 = st.columns(2)
                            with pe1:
                                f_eceran_botol = ui_image_uploader("4. WAJIB ECERAN: Full Foto Isi BBM Sesuai Jumlah Botol/Liter", key="pjb_ec_botol")
                            with pe2:
                                f_eceran_bayar = ui_image_uploader("5. WAJIB ECERAN: Foto Bukti Bayar Cash/Transfer ke Toko", key="pjb_ec_bayar")

                            if f_eceran_botol is not None and f_eceran_bayar is not None:
                                ai_eceran_ok, ai_eceran_status, ai_eceran_lines, ai_eceran_remark = ai_eceran_checker(
                                    f_eceran_botol, f_eceran_bayar, _l_num, harga_satuan, tot_nilai_nota
                                )
                                panel_txt = f"🤖 **HASIL ANALISA AI ECERAN — [{ai_eceran_status}]:**\n" + "\n".join([f"- {ln}" for ln in ai_eceran_lines])
                                if ai_eceran_ok:
                                    st.success(panel_txt)
                                else:
                                    st.warning(panel_txt)
                            else:
                                st.error("⚠️ **WAJIB UPLOAD:** Kedua foto tambahan Eceran (Foto Full Botol/Liter & Foto Bukti Bayar Toko) harus diunggah sebelum bisa mensahkan PJB!")
                    else:
                        c_m1, c_m2 = st.columns(2)
                        with c_m1:
                            tot_nilai_nota = st.number_input("Total Fisik Sesuai Kwitansi (Rp)", min_value=0, step=1000, value=d.get("nota_lama", 0))
                        
                        st.markdown("<div class='section-title'>📸 Lampiran Bukti Utama</div>", unsafe_allow_html=True)
                        p1, p2, p3 = st.columns(3)
                        with p1: f_nota_bbm = ui_image_uploader("1. Kwitansi Support", key="pjb_nota1")
                        
                        if "penginapan" in str(d["BBM"]).lower():
                            with p2: f_inap = ui_image_uploader("2. Foto Hotel", key="pjb_inap")
                        else:
                            with p2: f_notamat = ui_image_uploader("2. Foto Material", key="pjb_mat")
                        with p3: f_kerja = ui_image_uploader("3. Evidance Pekerjaan", key="pjb_krj2")
                else:
                    st.markdown("<div class='section-title'>🗓️ Rincian Keberangkatan & Nominal Uang Makan</div>", unsafe_allow_html=True)
                    c_um_a, c_um_b, c_um_c = st.columns(3)
                    with c_um_a: tgl_berangkat = st.date_input("Tanggal Keberangkatan", value=tgl_pjb)
                    with c_um_b: lama_hari = st.number_input("Lama Hari (Durasi Kerja)", min_value=1, step=1, value=1)
                    with c_um_c: 
                        total_um_calc = st.number_input("Total Nominal Uang Makan (Rp)", min_value=0, step=1000, value=int(d.get("NominalReq", 0)))
                        nom_um_harian = total_um_calc // lama_hari if lama_hari > 0 else total_um_calc
                    
                    tgl_kembali = tgl_berangkat + timedelta(days=lama_hari)
                    st.success(f"📅 Tanggal Kembali: **{tgl_kembali.strftime('%d/%m/%Y')}** | 💰 Total Uang Makan: **Rp {total_um_calc:,.0f}**")
                    
                    st.markdown("<div class='section-title'>📸 Lampiran Eviden Aktivitas Uang Makan</div>", unsafe_allow_html=True)
                    c_um1, c_um2, c_um3, c_um4 = st.columns(4)
                    with c_um1: f_um1 = ui_image_uploader("Foto Aktivitas 1", key="um1")
                    with c_um2: f_um2 = ui_image_uploader("Foto Aktivitas 2", key="um2")
                    with c_um3: f_um3 = ui_image_uploader("Foto Aktivitas 3", key="um3")
                    with c_um4: f_um4 = ui_image_uploader("Foto Aktivitas 4", key="um4")

                st.markdown("<br>", unsafe_allow_html=True)
                # ====================================================
                # --- PAKTA INTEGRITAS, PERINGATAN BBM ACTUAL & TOMBOL PJB ---
                # ====================================================
                
                # 1. Deteksi Role Langsung dari Data Tiket PJB (100% Akurat)
                role_pjb = str(d.get("Role", "")).strip().upper()
                if not role_pjb:
                    try:
                        nama_petugas = str(d.get("Nama", st.session_state.logged_in_user)).strip().upper()
                        for r in reversed(req_r[1:]):
                            if len(r) > 6 and str(r[5]).strip().upper() == nama_petugas:
                                role_pjb = str(r[6]).strip().upper()
                                break
                    except Exception:
                        pass
                
                # 2. Kotak Pakta Integritas
                cek_integritas = True 
                
                if "MBP" in role_pjb or "CME" in role_pjb:
                    st.markdown("<div style='background-color:#FEF2F2; padding:15px; border-radius:10px; border-left: 5px solid #EF4444; margin-bottom: 20px;'>", unsafe_allow_html=True)
                    st.write("⚠️ **WAJIB DIBACA SEBELUM SUBMIT PJB (Khusus Tim MBP & CME):**")
                    st.markdown("""
                    1. Saya tidak melakukan kecurangan dengan perusahaan, apa yang saya pertanggungjawabkan adalah benar.
                    2. Saya tidak mark up harga BBM mobil dan Solar.
                    3. Saya tidak dengan sadar merugikan perusahaan dengan tiket anomali dan mark up operasional.
                    4. Saya pribadi yang berintegritas dan jujur.
                    """)
                    cek_integritas = st.checkbox("✅ Saya sudah membaca", key="chk_mbp_final_vip")
                    if cek_integritas:
                        st.success("Terima kasih telah jujur. Perusahaan tidak akan menyulitkan karyawan, uang makan dan lain sudah ada aturan main. Jika pekerjaan dengan jarak >80km adalah 60.000, jika dekat dan backup >8 jam atau pekerjaan atas ganti RRU adalah 30.000. Jadi tidak harus berbisnis dengan rumah kita sendiri tempat kita cari makan.\n\n**Semangat Rekan!**")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                elif "TE" in role_pjb:
                    st.markdown("<div style='background-color:#F0FDF4; padding:15px; border-radius:10px; border-left: 5px solid #22C55E; margin-bottom: 20px;'>", unsafe_allow_html=True)
                    st.write("⚠️ **WAJIB DIBACA SEBELUM SUBMIT PJB (Khusus Tim TE):**")
                    st.markdown("""
                    1. Saya tidak melakukan pengisian BBM dengan tidak wajar dan tidak terukur.
                    2. Saya pribadi yang jujur dan berintegritas karena apa yang saya kerjakan untuk keluarga saya di rumah.
                    3. Kejujuran adalah kunci untuk segala hal.
                    4. Saya pribadi yang beriman dan tidak mungkin melakukan ketidakjujuran dalam permintaan operasional yang sesuai.
                    """)
                    cek_integritas = st.checkbox("✅ Saya sudah membaca", key="chk_te_final_vip")
                    if cek_integritas:
                        st.success("Saya bekerja demi orang rumah dan pribadi saya, saya memberi makan mereka dengan cara yang halal.\n\n**Tetap semangat!**")
                    st.markdown("</div>", unsafe_allow_html=True)

                # 2b. Peringatan & Pernyataan Wajib BBM Harga Actual (Audit Management)
                st.markdown("""
                <div style='background-color:#FFF1F2; padding:14px 16px; border-radius:10px; border-left: 5px solid #BE123C; margin-bottom: 16px;'>
                    <b style='color:#9F1239;'>⚖️ PERNYATAAN AUDIT MANAGEMENT:</b><br>
                    <span style='color:#881337;'><b>BBM wajib harga actual. Jika ditemukan kecurangan maka akan di-audit oleh Management.</b></span>
                </div>
                """, unsafe_allow_html=True)
                cek_bbm_actual = True
                if "Operational" in jns_pjb and is_vehicle:
                    cek_bbm_actual = st.checkbox("✅ Saya menyatakan BBM menggunakan HARGA ACTUAL dan bersedia di-audit oleh Management jika ditemukan kecurangan.", key="chk_bbm_actual_audit")

                # 3. Tombol Submit (Anti Double-Submit & Validasi Harga BBM Ketat)
                if st.button("🚀 Sahkan Pelaporan PJB", type="primary", use_container_width=True, key="btn_submit_pjb_final_vip"):
                    
                    if not cek_integritas:
                        st.error("❌ PENGIRIMAN DITOLAK: Anda WAJIB membaca dan mencentang Pakta Integritas di atas sebelum melakukan Submit PJB!")
                        st.stop()
                    if not cek_bbm_actual:
                        st.error("❌ PENGIRIMAN DITOLAK: Anda WAJIB mencentang pernyataan BBM wajib harga actual & siap di-audit oleh Management!")
                        st.stop()

                    # --- AI CHECKER NOTA ---
                    ai_mismatch_flag = False
                    msg_nota = ""
                    if "Operational" in jns_pjb and (f_nota_bbm is not None or f_km is not None) and tot_nilai_nota > 0:
                        is_valid_nota, msg_nota = ai_nota_checker(f_nota_bbm if f_nota_bbm else f_km, tot_nilai_nota, tgl_pjb)
                        if not is_valid_nota:
                            ai_mismatch_flag = True

                    if "Operational" in jns_pjb and is_vehicle:
                        if (not (is_pjb_portable and real_km_awal == 0 and km_akhir == 0)) and (pjb_ind_error_flag or km_akhir <= 0 or km_akhir < real_km_awal):
                            st.error("❌ PENGIRIMAN DITOLAK: KM/RH Akhir bermasalah (salah titik/koma, 0, lonjakan ekstrem, atau lebih kecil dari KM/RH Awal)!")
                            st.stop()
                        if sumber_bbm_pjb == "Eceran":
                            if f_eceran_botol is None or f_eceran_bayar is None:
                                st.error("❌ PENGIRIMAN DITOLAK (PEMBELIAN ECERAN): Wajib mengunggah **Full Foto Isi BBM (Jumlah Botol/Liter)** DAN **Foto Bukti Bayar Cash/Transfer ke Toko**!")
                                st.stop()
                            if not ai_eceran_ok:
                                ai_mismatch_flag = True
                                msg_nota = ai_eceran_remark
                        try:
                            liter_pjb_num = float(str(tot_liter).replace(",", ".").strip())
                        except Exception:
                            liter_pjb_num = 0.0
                        if liter_pjb_num <= 0 or harga_satuan <= 0 or tot_nilai_nota <= 0:
                            st.error("❌ PENGIRIMAN DITOLAK: Total Liter BBM, Harga Satuan Aktual, dan Total Fisik Nota wajib diisi lebih dari 0!")
                            st.stop()

                        # Cek apakah tiket ini punya Approval Harga BBM khusus dari Admin
                        base_tk_pjb = valid_cari_tiket.split(" [")[0].strip().upper()
                        has_special_price_app = False
                        for r_app_h in reversed(app_r[1:]):
                            if len(r_app_h) > 5 and str(r_app_h[3]).strip() == "Harga BBM" and str(r_app_h[5]).strip().upper() == "APPROVED":
                                if str(r_app_h[2]).strip().upper() in [valid_cari_tiket, base_tk_pjb]:
                                    has_special_price_app = True
                                    break
                        ok_hpjb, msg_hpjb = validate_bbm_price(d["BBM"], harga_satuan, sumber_bbm_pjb)
                        if not ok_hpjb and not has_special_price_app:
                            st.error(f"❌ PENGIRIMAN DITOLAK — VALIDASI HARGA BBM KETAT ({sumber_bbm_pjb.upper()}): {msg_hpjb}")
                            st.stop()

                        # Validasi silang (Liter x Harga Satuan vs Total Fisik Nota)
                        est_nota_calc = liter_pjb_num * harga_satuan
                        toleransi_nota = max(5000, 0.05 * tot_nilai_nota)
                        if abs(est_nota_calc - tot_nilai_nota) > toleransi_nota:
                            st.error(
                                f"❌ PENGIRIMAN DITOLAK — SELISIH KALKULASI NOTA: "
                                f"{liter_pjb_num:g} L × Rp {harga_satuan:,.0f} = Rp {est_nota_calc:,.0f}, "
                                f"tetapi Total Fisik Nota diisi Rp {tot_nilai_nota:,.0f}. Harap sesuaikan angka liter/harga aktual sesuai nota!"
                            )
                            st.stop()
                    elif "Akomodasi" in jns_pjb:
                        if not (f_um1 and f_um2 and f_um3 and f_um4):
                            st.error("❌ PENGIRIMAN DITOLAK: Anda WAJIB mengunggah 4 Foto Aktivitas!")
                            st.stop()
                            
                    with st.spinner("Mengupload foto dan men-generate laporan ke sistem..."):
                        if "Akomodasi" in jns_pjb: nominal_pjb = total_um_calc 
                            
                        url_transfer = upload_foto(f_transfer)
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
                        url_tiket_gen = upload_foto(f_tiket_genset) if f_tiket_genset else ""
                        url_eceran_botol = upload_foto(f_eceran_botol) if f_eceran_botol else ""
                        url_eceran_bayar = upload_foto(f_eceran_bayar) if f_eceran_bayar else ""            
                        
                        tgl_berangkat_str = tgl_berangkat.strftime("%d/%m/%Y") if "Akomodasi" in jns_pjb else ""
                        lama_hari_str = str(lama_hari) if "Akomodasi" in jns_pjb else ""
                        nom_um_harian_str = str(nom_um_harian) if "Akomodasi" in jns_pjb else ""
                        
                        str_mulai_gen = jam_mulai_gen.strftime("%H:%M") if jam_mulai_gen else ""
                        str_akhir_gen = jam_akhir_gen.strftime("%H:%M") if jam_akhir_gen else ""
                        
                        pdf_link_cloud = ""
                        b64_html = ""

                        # GENERATE HTML SURAT TUGAS & UANG MAKAN DULU SEBELUM APPEND (AGAR LINK PDF TERCATAT & TIDAK DOUBLE SUBMIT!)
                        if "Akomodasi" in jns_pjb:
                            bulan_romawi = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]
                            romawi = bulan_romawi[tgl_pjb.month] if 1 <= tgl_pjb.month <= 12 else "VIII"
                            logo_base64 = get_local_img_base64("koperasi-jasa-konstruksi-tower-event-organizer-network-monitoring-telekomunikasi-kisel-group-logo-kut.webp")
                            is_pbu_doc = ("pangkalan" in str(d.get("NOP", nop_cari)).lower())
                            kota_doc = "Pangkalan Bun" if is_pbu_doc else "Palangka Raya"
                            koor_nama_doc = "Roni Yudi Iswanto" if is_pbu_doc else "Okta Pradika"
                            koor_jab_doc = "Koordinator NOP Pangkalan Bun" if is_pbu_doc else "Koordinator NOP Palangka Raya"
                            koor_nik_doc = nik_dict.get("RONI YUDI ISWANTO", nik_dict.get("RONI YUDI ISYANTO", "-")) if is_pbu_doc else "B0924649"

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
                                            <tr><td width="150">Nama</td><td width="10">:</td><td>{koor_nama_doc}</td></tr>
                                            <tr><td>NIK</td><td>:</td><td>{koor_nik_doc}</td></tr>
                                            <tr><td>Jabatan</td><td>:</td><td>{koor_jab_doc}</td></tr>
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
                                        <div style="text-align: right; margin-top: 30px;">{kota_doc}, {tgl_pjb.strftime("%d/%m/%Y")}</div>
                                        <div class="signature">
                                            <div><p>{koor_jab_doc},</p><br><br><br><p><b><u>{koor_nama_doc}</u></b><br>NIK. {koor_nik_doc}</p></div>
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
                                            <tr><td colspan="3">Uang Makan ({d['Nama']})</td><td align="center">{lama_hari} Hari (Lumpsum)</td><td width="30">Rp.</td><td align="right">{total_um_calc:,.0f}</td></tr>
                                            <tr><th colspan="5" align="right">Jumlah Total</th><th align="right">Rp. {total_um_calc:,.0f}</th></tr>
                                        </table>
                                        <div class="signature">
                                            <div><p>{koor_jab_doc},</p><br><br><br><p><b><u>{koor_nama_doc}</u></b><br>NIK. {koor_nik_doc}</p></div>
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

                        # SIMPAN DATA PJB SEKALI SAJA (ANTI DUPLIKAT) — KOLOM 25 & 26 UNTUK FOTO WAJIB ECERAN
                        ts_pjb_wib = get_now_wib().strftime("%d/%m/%Y %H:%M:%S")
                        bbm_label_final = d["BBM"]
                        if is_vehicle and f"[{sumber_bbm_pjb.upper()}]" not in str(bbm_label_final).upper():
                            bbm_label_final = f"{bbm_label_final} [{sumber_bbm_pjb.upper()}]"
                        data_pjb = [
                            ts_pjb_wib, tgl_pjb.strftime("%d/%m/%Y"), d["NOP"], d["Cluster"], d["Nama"], d["Role"], d["Site"], d["Keperluan"], bbm_label_final, d["Desc"], str(km_akhir), nominal_pjb, d["Plat"], url_isi, url_notabbm, url_km, url_mat, url_notamat, url_inap, url_kerja, tot_nilai_nota, valid_cari_tiket, tot_liter, harga_satuan, str(round(total_km_tempuh, 2)), url_eceran_botol, url_eceran_bayar, url_transfer, url_um1, url_um2, url_um3, url_um4, tgl_berangkat_str, lama_hari_str, nom_um_harian_str, pdf_link_cloud, specific_pm_tickets, 
                            str_mulai_gen, str_akhir_gen, url_tiket_gen
                        ]
                        
                        data_pjb_padded = (data_pjb + [""] * 40)[:40]
                        sukses_pjb = append_data(SHEET_PJB, data_pjb_padded, target_ss)
                        
                        if sukses_pjb: 
                            if sumber_bbm_pjb == "Eceran" and ai_eceran_remark:
                                remark_app = ai_eceran_remark
                            else:
                                remark_app = "⚠️ AI Mismatch OCR (Butuh Cek Manual)" if ai_mismatch_flag else "-"
                            append_data(SHEET_APP, [ts_pjb_wib, d["Nama"], valid_cari_tiket, "Verifikasi PJB", nominal_pjb, "PENDING", remark_app], target_ss)
                            
                            kata_motivasi = [
                                "Kejujuran adalah kunci keberhasilan. Terima kasih atas kerja kerasmu hari ini! 💪",
                                "Jujur dalam bekerja demi senyum keluarga di rumah. Keringatmu adalah ibadah! 🏡✨",
                                "Satu kejujuran bernilai lebih dari seribu kebohongan. Lanjutkan dedikasimu! 🌟",
                                "Tetap semangat! Hasil yang berkah berasal dari proses yang jujur dan transparan. 🤝",
                                "Keringat di lapangan adalah pahlawan keluarga. Jaga integritas dan pulanglah dengan bangga! 💼"
                            ]
                            st.toast(f"💡 {random.choice(kata_motivasi)}", icon="✨")
                            
                            if ai_mismatch_flag:
                                st.warning(f"🚨 **PERINGATAN AI:** {msg_nota}")
                                st.error("PJB Anda tetap berhasil disubmit, namun dengan status **TERKUNCI (Membutuhkan Approval Manual)** karena tulisan nota sulit dibaca AI.")
                                st.info("📲 **Harap konfirmasi ke Koordinator via WA untuk persetujuan PJB:** [Klik Disini (08115251515)](https://wa.me/628115251515)")
                                st.session_state.pjb_data = None
                                if "Operational" in jns_pjb:
                                    time.sleep(8)
                                    st.session_state.page = "🏠 Hub Menu Utama"
                                    st.rerun()
                            else:
                                st.success("🎉 PJB Berhasil Dikirim untuk Verifikasi Admin!")
                                st.session_state.pjb_data = None
                                if "Operational" in jns_pjb:
                                    time.sleep(2.5)
                                    st.session_state.page = "🏠 Hub Menu Utama"
                                    st.rerun()
                        else:
                            st.error("🚨 Gagal mengirim ke Google Sheet.")

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


elif st.session_state.page == "🛡️ Approval Center":
    st.markdown("<div class='header-card'><h2>🛡️ APPROVAL CENTER</h2><p>Pusat Verifikasi PJB, Izin Revisi, & Harga BBM Anomali</p></div>", unsafe_allow_html=True)
    
    nop_admin = st.selectbox("📂 Wilayah (NOP):", ["-- Pilih NOP --"] + list(MASTER_DATA.keys()))
    if nop_admin != "-- Pilih NOP --":
        target_ss = MASTER_DATA[nop_admin]["spreadsheet_id"]
        data_all = fetch_spreadsheet_data(target_ss)
        
        # Tambahkan req_r untuk mencari norek
        app_r = data_all.get(SHEET_APP, [])
        pjb_r = data_all.get(SHEET_PJB, [])
        req_r = data_all.get(SHEET_REQUEST, [])
        
        pending_anomali, pending_pjb = [], []
        if len(app_r) > 0:
            for idx, r in enumerate(app_r):
                if len(r) > 5 and str(r[5]).strip() == "PENDING":
                    
                    # --- CARI REKENING BERDASARKAN TIKET ---
                    target_tiket = str(r[2]).strip().upper()
                    rek_tim = "-"
                    for req in reversed(req_r[1:]):
                        if len(req) > 18 and str(req[3]).strip().upper() == target_tiket:
                            rek_tim = f"{req[17]} - {req[18]}"
                            break
                            
                    item = {
                        "Row Index": idx, "Waktu": str(r[0]), "Nama": str(r[1]), "Request Ref / Tiket": target_tiket, 
                        "Jenis Pengajuan": str(r[3]), "Nominal": f"Rp {clean_nominal(r[4]):,.0f}", 
                        "Rekening Tim": rek_tim,
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
                    has_ec1 = len(pjb_target) > 25 and str(pjb_target[25]).startswith("http")
                    has_ec2 = len(pjb_target) > 26 and str(pjb_target[26]).startswith("http")
                    if has_ec1 or has_ec2:
                        st.markdown("##### 🛢️ Bukti Wajib Pembelian BBM ECERAN (Hasil Audit AI)")
                        ce_p1, ce_p2 = st.columns(2)
                        with ce_p1:
                            if has_ec1: st.image(pjb_target[25], caption="4. Full Foto Isi BBM (Botol/Liter Eceran)", use_container_width=True)
                        with ce_p2:
                            if has_ec2: st.image(pjb_target[26], caption="5. Bukti Bayar Cash/Transfer Toko Eceran", use_container_width=True)
                
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

                st.markdown("<hr>", unsafe_allow_html=True)
                st.markdown("#### 📲 Generate WA Report Harian Penggunaan Dana & Sisa Uang Muka")
                ck1, ck2, ck3 = st.columns([1, 1, 2])
                with ck1: tgl_wa_kas = st.date_input("Tanggal Laporan:", value=get_now_wib().date(), key="wa_kas_tgl")
                with ck2: batch_wa_kas = st.selectbox("Pilih Batch UM:", ["Semua Batch"] + sorted(in_data.keys()), key="wa_kas_batch")
                with ck3: note_wa_kas = st.text_input("Catatan Tambahan (Opsional):", key="wa_kas_note")

                wa_kas_txt, _ = generate_daily_finance_wa_report(nop_admin, tgl_wa_kas, data_all, selected_batch=batch_wa_kas, extra_note=note_wa_kas)
                st.code(wa_kas_txt, language="markdown")
                wa_kas_enc = quote(wa_kas_txt)
                st.markdown(
                    f'<a href="https://wa.me/?text={wa_kas_enc}" target="_blank" class="btn-sidata-blue" style="background: linear-gradient(135deg, #22C55E 0%, #16A34A 100%) !important;">📲 BUKA & KIRIM WA REPORT HARIAN (KAS & SISA UM)</a>',
                    unsafe_allow_html=True
                )

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
        
        t1, t2, t3, t4, t5 = st.tabs(["💰 1. Sisa Kas", "🚨 2. Anomali", "🕵️ 3. Evaluasi Satelit", "🚗 4. Performa Mobil (NOPOL)", "⚡ 5. Datalog Genset"])
        
        with t1:
            total_um = sum([clean_nominal(r[3]) for r in um_r[1:] if len(r)>3]) if len(um_r)>1 else 0
            tot_serap = sum([clean_nominal(r[15]) for r in rekap_r[1:] if len(r)>15]) if len(rekap_r)>1 else 0
            sisa_kas = total_um - tot_serap
            m1, m2, m3 = st.columns(3)
            m1.markdown(f"<div class='metric-3d'><div class='metric-title'>Total Kas Masuk</div><div class='metric-value'>Rp {total_um:,.0f}</div></div>", unsafe_allow_html=True)
            m2.markdown(f"<div class='metric-3d'><div class='metric-title'>Total Penyerapan</div><div class='metric-value'>Rp {tot_serap:,.0f}</div></div>", unsafe_allow_html=True)
            m3.markdown(f"<div class='metric-3d'><div class='metric-title'>Sisa Kas</div><div class='metric-value'>Rp {sisa_kas:,.0f}</div></div>", unsafe_allow_html=True)
            
            if len(pjb_r) > 1:
                df_pjb_all = pd.DataFrame([(r + [""] * 40)[:40] for r in pjb_r[1:]], columns=["Waktu","Tanggal","N","C","Nama","R","S","Keperluan","BBM","D","KMAkhir","Nominal","Pl","u1","u2","u3","u4","u5","u6","u7","NN","NoTiket","Lt","Hs","TKM_RH","u8","u9","BuktiTF","UM1","UM2","UM3","UM4", "TglB", "LmHr", "NomH", "PDFLink", "PMMulti", "JamMulai", "JamAkhir", "LinkTiket"])
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
                        if (is_genset or is_mobil or is_motor) and harga_satuan_val > 0:
                            sumber_anm = "Eceran" if ("eceran" in str(kategori_bbm).lower() or "eceran" in str(pjb[8]).lower() or "beli: eceran" in str(req_match[11]).lower()) else "SPBU"
                            ok_anm_h, msg_anm_h = validate_bbm_price(kategori_bbm, harga_satuan_val, sumber_anm)
                            if not ok_anm_h:
                                is_boros = True
                                ket_status = f"🚨 Anomali Harga BBM {sumber_anm} ({kategori_bbm}: Rp {harga_satuan_val:,}/L)"
                            
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
            st.info("💡 **ANALISA LENGKAP:** Menampilkan akumulasi jarak tempuh (KM), konsumsi BBM (Liter), total dana (Rp), serta **Biaya Dana per KM (Rp/KM)** untuk setiap NOPOL.")
            
            req_lookup_car = {}
            for rq in req_r[1:]:
                if len(rq) > 12 and str(rq[3]).strip():
                    req_lookup_car[str(rq[3]).strip().upper()] = float(clean_indicator(rq[12]))

            car_stats = {}
            car_trips_detail = []

            for pjb in pjb_r[1:]:
                if len(pjb) > 23:
                    kategori = str(pjb[8]).strip()
                    plat_raw = str(pjb[12]).strip().upper()
                    plat_clean = re.sub(r'\s+', ' ', plat_raw)
                    
                    if "mobil" in kategori.lower() and plat_clean not in ["", "0", "NONE", "NAN", "-"]:
                        no_tkt = str(pjb[21]).strip().upper() if len(pjb) > 21 else "-"
                        tgl_pjb_str = str(pjb[1]).strip() if len(pjb) > 1 else "-"
                        nama_pic = str(pjb[4]).strip() if len(pjb) > 4 else "-"
                        
                        km_akhir_val = float(clean_indicator(pjb[10])) if len(pjb) > 10 else 0.0
                        trip_col = float(clean_indicator(pjb[24])) if len(pjb) > 24 and str(pjb[24]).strip() else 0.0
                        km_awal_val = req_lookup_car.get(no_tkt, 0.0)
                        
                        if trip_col > 0:
                            trip_km = trip_col
                            if km_awal_val == 0 and km_akhir_val >= trip_km:
                                km_awal_val = km_akhir_val - trip_km
                        elif km_akhir_val > km_awal_val and km_awal_val > 0:
                            trip_km = km_akhir_val - km_awal_val
                        else:
                            trip_km = 0.0

                        liter_val = float(clean_indicator(pjb[22])) if len(pjb) > 22 else 0.0
                        harga_l_val = clean_nominal(pjb[23]) if len(pjb) > 23 else 0
                        dana_aktual = clean_nominal(pjb[11]) if len(pjb) > 11 else (clean_nominal(pjb[20]) if len(pjb)>20 else 0)

                        if liter_val <= 0 and dana_aktual > 0:
                            liter_val = round(dana_aktual / (harga_l_val if harga_l_val >= 6000 else 10000), 2)

                        rasio_trip_kml = (trip_km / liter_val) if liter_val > 0 else 0.0
                        biaya_per_km_trip = (dana_aktual / trip_km) if trip_km > 0 else 0.0

                        if plat_clean not in car_stats:
                            car_stats[plat_clean] = {"PIC Terakhir": nama_pic, "Jml Trip": 0, "KM Akhir Max": km_akhir_val, "Total KM": 0.0, "Total Liter": 0.0, "Total Dana": 0}

                        car_stats[plat_clean]["PIC Terakhir"] = nama_pic
                        car_stats[plat_clean]["Jml Trip"] += 1
                        if km_akhir_val > car_stats[plat_clean]["KM Akhir Max"]: car_stats[plat_clean]["KM Akhir Max"] = km_akhir_val
                        car_stats[plat_clean]["Total KM"] += trip_km
                        car_stats[plat_clean]["Total Liter"] += liter_val
                        car_stats[plat_clean]["Total Dana"] += dana_aktual

                        status_trip = "🟢 Efisien" if rasio_trip_kml >= 8 else ("🟡 Standar" if rasio_trip_kml >= 7 else ("🔴 Boros" if rasio_trip_kml > 0 else "⚪ N/A"))
                        car_trips_detail.append({
                            "Tanggal PJB": tgl_pjb_str, "NOPOL": plat_clean, "Nama PIC": nama_pic, "No Tiket": no_tkt,
                            "KM Awal": round(km_awal_val, 1), "KM Akhir": round(km_akhir_val, 1),
                            "Jarak Tempuh (KM)": round(trip_km, 2), "BBM (Liter)": round(liter_val, 2),
                            "Dana BBM (Rp)": dana_aktual, "Efisiensi (KM/L)": round(rasio_trip_kml, 2),
                            "Biaya per KM (Rp/KM)": round(biaya_per_km_trip, 0), "Status": status_trip
                        })

            if car_stats:
                car_list = []
                for plat, d_car in car_stats.items():
                    eff_kml = (d_car["Total KM"] / d_car["Total Liter"]) if d_car["Total Liter"] > 0 else 0.0
                    cost_per_km = (d_car["Total Dana"] / d_car["Total KM"]) if d_car["Total KM"] > 0 else 0.0
                    st_unit = "🟢 Efisien" if eff_kml >= 8.0 else ("🟡 Standar" if eff_kml >= 7.0 else "🔴 Boros")
                    
                    car_list.append({
                        "NOPOL Kendaraan": plat, "PIC Terakhir": d_car["PIC Terakhir"], "Jml Trip": d_car["Jml Trip"],
                        "Odometer Terakhir (KM)": round(d_car["KM Akhir Max"], 1), "Total Jarak (KM)": round(d_car["Total KM"], 2),
                        "Total BBM (Liter)": round(d_car["Total Liter"], 2), "Total Dana BBM": f"Rp {d_car['Total Dana']:,.0f}",
                        "Efisiensi Mesin": f"{eff_kml:.2f} KM/L", "Biaya Dana / KM": f"Rp {cost_per_km:,.0f} / KM", "Status": st_unit
                    })
                df_cars = pd.DataFrame(car_list)
                st.dataframe(df_cars, hide_index=True, use_container_width=True)
                st.download_button("📥 Export Data Mobil (CSV)", data=df_cars.to_csv(index=False).encode('utf-8'), file_name=f"Analisa_Mobil_{nop_live}.csv", mime="text/csv")
            else:
                st.info("Belum ada data perjalanan Mobil di wilayah ini.")

        with t5:
            st.markdown("### ⚡ Analisa Penggunaan Dana & Datalog Performa Genset")
            st.info("Memantau akumulasi Running Hours (RH), konsumsi BBM per Jam (Liter/RH), dan biaya operasional per Jam (Rp/RH).")
            
            req_lookup_gen = {}
            for rq in req_r[1:]:
                if len(rq) > 12 and str(rq[3]).strip():
                    req_lookup_gen[str(rq[3]).strip().upper()] = float(clean_indicator(rq[12]))

            gen_summary = {}
            datalog_genset = []

            for pjb in pjb_r[1:]:
                if len(pjb) > 23 and "genset" in str(pjb[8]).lower():
                    tgl_pjb_g = str(pjb[1]).strip() if len(pjb) > 1 else "-"
                    no_tiket_gen = str(pjb[21]).strip().upper() if len(pjb) > 21 else "-"
                    nama_mbp = str(pjb[4]).strip() if len(pjb) > 4 else "-"
                    id_genset = str(pjb[12]).strip().upper() if len(pjb) > 12 and str(pjb[12]).strip() else "GENSET"

                    jam_mulai = str(pjb[37]).strip() if len(pjb) > 37 and str(pjb[37]).strip() else "-"
                    jam_akhir = str(pjb[38]).strip() if len(pjb) > 38 and str(pjb[38]).strip() else "-"
                    link_tiket = str(pjb[39]).strip() if len(pjb) > 39 and str(pjb[39]).strip() else ""

                    rh_akhir = float(clean_indicator(pjb[10])) if len(pjb) > 10 else 0.0
                    rh_trip_col = float(clean_indicator(pjb[24])) if len(pjb) > 24 and str(pjb[24]).strip() else 0.0
                    rh_awal = req_lookup_gen.get(no_tiket_gen, 0.0)

                    if rh_trip_col > 0:
                        total_rh = rh_trip_col
                        if rh_awal == 0 and rh_akhir >= total_rh: rh_awal = rh_akhir - total_rh
                    elif rh_akhir > rh_awal and rh_awal > 0:
                        total_rh = rh_akhir - rh_awal
                    else:
                        total_rh = 0.0

                    liter_gen = float(clean_indicator(pjb[22])) if len(pjb) > 22 else 0.0
                    dana_gen = clean_nominal(pjb[11]) if len(pjb) > 11 else 0
                    if liter_gen <= 0 and dana_gen > 0:
                        _, _, _rgen_fb = get_bbm_rule(str(pjb[8]), "Eceran" if "eceran" in str(pjb[8]).lower() else "SPBU")
                        _hrg_fb = _rgen_fb["default"] if _rgen_fb else 14500
                        liter_gen = round(dana_gen / _hrg_fb, 2)

                    liter_per_rh = (liter_gen / total_rh) if total_rh > 0 else 0.0
                    biaya_per_rh = (dana_gen / total_rh) if total_rh > 0 else 0.0

                    if id_genset not in gen_summary:
                        gen_summary[id_genset] = {"PIC Terakhir": nama_mbp, "Jml Backup": 0, "Total RH": 0.0, "Total Liter": 0.0, "Total Dana": 0}
                    gen_summary[id_genset]["PIC Terakhir"] = nama_mbp
                    gen_summary[id_genset]["Jml Backup"] += 1
                    gen_summary[id_genset]["Total RH"] += total_rh
                    gen_summary[id_genset]["Total Liter"] += liter_gen
                    gen_summary[id_genset]["Total Dana"] += dana_gen

                    datalog_genset.append({
                        "Tanggal PJB": tgl_pjb_g, "No Tiket": no_tiket_gen, "Nama MBP": nama_mbp, "ID Genset": id_genset,
                        "Jam Mulai": jam_mulai, "Jam Selesai": jam_akhir, "RH Awal": round(rh_awal, 2), "RH Akhir": round(rh_akhir, 2),
                        "Total Run (RH)": round(total_rh, 2), "BBM (Liter)": round(liter_gen, 2), "Total Dana PJB": f"Rp {dana_gen:,.0f}",
                        "Konsumsi (L/RH)": f"{liter_per_rh:.2f} L/RH", "Biaya / RH": f"Rp {biaya_per_rh:,.0f}/RH", "Bukti Tiket": link_tiket
                    })
            
            if datalog_genset:
                st.markdown("##### 📋 Datalog Riwayat Backup Genset per Tiket")
                df_genset = pd.DataFrame(datalog_genset)
                st.dataframe(df_genset, hide_index=True, use_container_width=True)
                st.download_button("📥 Export Datalog Genset (CSV)", data=df_genset.to_csv(index=False).encode('utf-8'), file_name=f"Datalog_Genset_{nop_live}.csv", mime="text/csv")
            else:
                st.info("Belum ada datalog PJB Genset yang divalidasi.")

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
            if len(pjb_r) > 1 or len(rekap_r) > 1:
                # Kolom foto sesuai urutan di Sheet PJB
                PHOTO_COLS_SPEC = [
                    (13, "Evidance Pengisian BBM"), (14, "Kwitansi Support / Non-BBM"),
                    (15, "Foto Nota & KM/RH"), (16, "Foto Material"), (17, "Foto Nota Material"),
                    (18, "Foto Penginapan / Hotel"), (19, "Evidance Pekerjaan"),
                    (28, "Foto Aktivitas UM 1"), (29, "Foto Aktivitas UM 2"),
                    (30, "Foto Aktivitas UM 3"), (31, "Foto Aktivitas UM 4"),
                    (25, "Foto Full Botol/Liter Eceran"), (26, "Foto Bukti Bayar Toko Eceran"),
                    (39, "Screenshot Tiket Genset"), (27, "Bukti Transfer Dana"),
                ]
                inc_bukti_tf = st.checkbox("Sertakan Foto Bukti Transfer Dana (Jika Ada)", value=False)

                # Hitung Rekap Jarak & Odometer Terakhir per Nopol untuk ditampilkan di Tabel & PDF PJB
                nopol_stats_rep, req_info_rep = build_nopol_distance_summary(pjb_r, req_r)

                dict_pjb_exact = defaultdict(list)
                for r in pjb_r[1:]:
                    if len(r) > 21:
                        tk = str(r[21]).strip().upper()
                        if tk:
                            photos = []
                            seen_urls = set()
                            for col_idx, col_label in PHOTO_COLS_SPEC:
                                if col_idx == 27 and not inc_bukti_tf: continue
                                if len(r) > col_idx:
                                    u = str(r[col_idx]).strip()
                                    if u.startswith("http") and u not in seen_urls:
                                        photos.append((col_label, u))
                                        seen_urls.add(u)
                                        
                            pdf_url = str(r[35]).strip() if len(r) > 35 and str(r[35]).strip().startswith("http") else ""
                            tgl_pjb_d = parse_date(r[1] if len(r) > 1 else "", r[0] if len(r) > 0 else "")
                            tgl_pjb_clean = tgl_pjb_d.strftime("%d/%m/%Y") if tgl_pjb_d != datetime(1970, 1, 1).date() else (str(r[1]).strip() if len(r) > 1 else "-")

                            plat_val = re.sub(r'\s+', ' ', str(r[12]).strip().upper()) if len(r) > 12 else ""
                            km_akhir_v = float(clean_indicator(r[10])) if len(r) > 10 else 0.0
                            trip_col_v = float(clean_indicator(r[24])) if len(r) > 24 else 0.0
                            req_m = req_info_rep.get(tk, {})
                            km_awal_v = req_m.get("km_awal", 0.0)
                            if trip_col_v > 0:
                                trip_v = trip_col_v
                                if km_awal_v == 0 and km_akhir_v >= trip_v:
                                    km_awal_v = round(km_akhir_v - trip_v, 2)
                            elif km_akhir_v > km_awal_v and km_awal_v > 0:
                                trip_v = round(km_akhir_v - km_awal_v, 2)
                            else:
                                trip_v = 0.0

                            kat_v = str(r[8]).strip() if len(r) > 8 else "-"
                            is_gen_v = "genset" in kat_v.lower()
                            is_veh_v = is_gen_v or ("mobil" in kat_v.lower()) or ("motor" in kat_v.lower())
                            unit_v = "RH" if is_gen_v else "KM"

                            npl_stat = nopol_stats_rep.get(plat_val, {})
                            if is_veh_v and (km_akhir_v > 0 or trip_v > 0 or plat_val):
                                last_odo_n = npl_stat.get("last_odo", km_akhir_v)
                                tot_acc_n = npl_stat.get("total_trip", trip_v)
                                cnt_tr_n = npl_stat.get("trip_count", 1)
                                jarak_nopol_txt = (
                                    f"Awal: {format_id_number(km_awal_v)} → Akhir: {format_id_number(km_akhir_v)} {unit_v} "
                                    f"(Trip: +{format_id_number(trip_v)} {unit_v}) | "
                                    f"Terakhir Nopol: {format_id_number(last_odo_n)} {unit_v} (Total {format_id_number(tot_acc_n)} {unit_v} / {cnt_tr_n} Trip)"
                                )
                            else:
                                jarak_nopol_txt = req_m.get("jarak_satelit", "-") or "-"

                            desc_real = str(r[9]).strip() if len(r) > 9 else ""
                            if not desc_real or desc_real == "-":
                                desc_real = req_m.get("desc", "-")

                            dict_pjb_exact[tk].append({
                                "tanggal": tgl_pjb_clean, "nama": r[4] if len(r) > 4 else "-",
                                "role": r[5] if len(r) > 5 else "-", "kategori": kat_v,
                                "keperluan": r[7] if len(r) > 7 else "-", "deskripsi": desc_real or "-",
                                "plat": plat_val or "-", "jarak_nopol": jarak_nopol_txt,
                                "nominal": clean_nominal(r[11]) if len(r) > 11 else 0,
                                "photos": photos, "pdf_link": pdf_url
                            })
                
                list_periode = sorted(list(set([r[16].strip() for r in rekap_r[1:] if len(r) > 16 and r[16].strip() != ""])))
                list_role = sorted(list(set([r[6].strip() for r in rekap_r[1:] if len(r) > 6 and r[6].strip() != ""])))
                
                st.markdown("<div class='section-title'>🔍 1. Parameter Filter & Mode Layout PDF</div>", unsafe_allow_html=True)
                col_f1, col_f2 = st.columns(2)
                with col_f1: filter_periode = st.selectbox("📅 Periode Dana Ops:", ["Semua Periode"] + list_periode)
                with col_f2: filter_role = st.multiselect("💼 Role Pekerjaan:", list_role, default=list_role)

                mode_pdf_layout = st.radio(
                    "🖨️ Pilih Format Cetak PDF Foto PJB:",
                    [
                        "📄 Full 1 Lembar Per Foto (Ukuran Asli Proporsional — Rekomendasi Audit)",
                        "🗂️ Mode Ringkas (Grid Semua Foto Dalam 1 Halaman per Tiket)"
                    ],
                    index=0,
                    horizontal=True,
                    key="pdf_layout_mode"
                )

                draft_rows = []
                ticket_counts = defaultdict(int)
                for row in rekap_r[1:]:
                    row_periode = row[16].strip() if len(row) > 16 else ""
                    row_role = row[6].strip() if len(row) > 6 else ""
                    pass_periode = (filter_periode == "Semua Periode") or (row_periode == filter_periode)
                    pass_role = (len(filter_role) == 0) or (row_role in filter_role)
                    
                    if pass_periode and pass_role:
                        found_tiket = None
                        for cell in row:
                            c_up = str(cell).strip().upper()
                            if c_up in dict_pjb_exact:
                                found_tiket = c_up
                                break
                        if found_tiket:
                            idx_for_tk = ticket_counts[found_tiket]
                            rec_list = dict_pjb_exact[found_tiket]
                            rec_pjb = rec_list[idx_for_tk] if idx_for_tk < len(rec_list) else rec_list[-1]
                            ticket_counts[found_tiket] += 1

                            # FIX TANGGAL TERBALIK / TERTULIS BULAN:
                            # Di sheet Rekap PJB, Kolom A (row[0]) adalah BULAN, Kolom B (row[1]) adalah TANGGAL.
                            # Prioritaskan tanggal asli dari Form PJB (rec_pjb["tanggal"]) atau Kolom B (row[1]) yang sudah dinormalisasi DD/MM/YYYY!
                            tgl_rekap_b = parse_date(row[1] if len(row) > 1 else "")
                            if rec_pjb["tanggal"] and rec_pjb["tanggal"] != "-":
                                tgl_final_pdf = rec_pjb["tanggal"]
                            elif tgl_rekap_b != datetime(1970, 1, 1).date():
                                tgl_final_pdf = tgl_rekap_b.strftime("%d/%m/%Y")
                            else:
                                tgl_final_pdf = str(row[1]).strip() if len(row) > 1 and str(row[1]).strip() else "-"

                            # FIX DESKRIPSI vs NOPOL:
                            # Prioritaskan Deskripsi asli dari Form PJB (rec_pjb["deskripsi"]), BUKAN row[9] dari Rekap PJB yang berisi Nopol/No Tiket!
                            desc_asli = str(rec_pjb.get("deskripsi", "")).strip()
                            if not desc_asli or desc_asli == "-":
                                desc_asli = str(row[9]).strip() if len(row) > 9 and str(row[9]).strip() else "-"
                            
                            photo_links_str = " | ".join([f"{lbl}::{url}" for lbl, url in rec_pjb["photos"]])
                            draft_rows.append({
                                "Cetak": True, "No Tiket": found_tiket, "Periode": row_periode or (str(row[0]).strip() if len(row) > 0 else "-"),
                                "Tanggal": tgl_final_pdf,
                                "Nama": row[4] if len(row) > 4 and str(row[4]).strip() else rec_pjb["nama"],
                                "Role": row_role if row_role else rec_pjb["role"],
                                "Kategori": rec_pjb["kategori"],
                                "Nopol / ID Unit": rec_pjb["plat"],
                                "Kalkulasi Jarak Nopol": rec_pjb["jarak_nopol"],
                                "Keperluan": row[8] if len(row) > 8 and str(row[8]).strip() else rec_pjb["keperluan"],
                                "Deskripsi": desc_asli,
                                "Nominal": clean_nominal(row[15]) if len(row) > 15 and str(row[15]).strip() else rec_pjb["nominal"],
                                "Jml Foto": len(rec_pjb["photos"]),
                                "Data Foto (Label::URL)": photo_links_str, "Link PDF UM": rec_pjb["pdf_link"]
                            })

                st.markdown("<div class='section-title'>✏️ 2. Tabel Auto-Edit List PJB, Nopol, Jarak & Foto (Khusus Admin)</div>", unsafe_allow_html=True)
                st.info("💡 **AUTO-EDIT ADMIN:** Tanggal sudah dikoreksi otomatis ke format `DD/MM/YYYY`, Nopol & Deskripsi sudah dipisahkan dengan benar, serta **Kalkulasi Jarak & Odometer Terakhir Nopol** tampil langsung di tabel & PDF.")
                
                if draft_rows:
                    df_draft = pd.DataFrame(draft_rows)
                    edited_df = st.data_editor(
                        df_draft, use_container_width=True, hide_index=True, num_rows="dynamic",
                        column_config={"Cetak": st.column_config.CheckboxColumn("✅ Cetak?", default=True), "Nominal": st.column_config.NumberColumn("Nominal (Rp)", format="Rp %d")}
                    )
                    df_selected = edited_df[edited_df["Cetak"] == True].copy()
                    
                    c_btn_exp, c_btn_gen = st.columns(2)
                    with c_btn_exp:
                        st.download_button("📥 Download List Tabel PJB (CSV)", data=df_selected.drop(columns=["Cetak"], errors="ignore").to_csv(index=False).encode("utf-8"), file_name=f"List_Edited_PJB_{nop_report}.csv", mime="text/csv", use_container_width=True)
                    with c_btn_gen:
                        btn_gen_html = st.button("🚀 Generate Laporan PDF Lumpsum", type="primary", use_container_width=True)

                    if btn_gen_html:
                        is_full_per_photo = ("Full 1 Lembar Per Foto" in mode_pdf_layout)
                        html_content = ""
                        page_counter = 0
                        ticket_counter = 0

                        for _, erow in df_selected.iterrows():
                            ticket_counter += 1
                            raw_photos_str = str(erow.get("Data Foto (Label::URL)", "")).strip()
                            valid_photos = []
                            if raw_photos_str and raw_photos_str != "nan":
                                for part in raw_photos_str.split("|"):
                                    if "::" in part:
                                        lbl, u = part.split("::", 1)
                                        if u.strip().startswith("http"):
                                            valid_photos.append((lbl.strip(), u.strip()))
                            
                            jml_foto = len(valid_photos)
                            nopol_pdf = erow.get("Nopol / ID Unit", "-")
                            jarak_nopol_pdf = erow.get("Kalkulasi Jarak Nopol", "-")
                            desc_pdf = str(erow.get("Deskripsi", "-")).replace("\n", "<br>")

                            if is_full_per_photo:
                                # MODE FULL 1 LEMBAR A4 PORTRAIT PER FOTO (UKURAN ASLI PROPORSIONAL)
                                photos_to_render = valid_photos if valid_photos else [("Tidak Ada Lampiran Foto", "")]
                                for idx_f, (lbl_foto, url_foto) in enumerate(photos_to_render, 1):
                                    page_counter += 1
                                    img_html = f"<img src='{url_foto}' alt='{lbl_foto}'>" if url_foto else "<div style='color:#94A3B8; font-weight:700;'>Tidak ada gambar terlampir</div>"
                                    html_content += f"""
                                    <div class='ticket-card full-page-photo'>
                                        <div class='report-top-bar'>
                                            <span>LAPORAN PERTANGGUNGJAWABAN (PJB) — NOP {nop_report.upper()}</span>
                                            <span>Tiket #{ticket_counter} | Foto {idx_f}/{len(photos_to_render)} | Hal. {page_counter}</span>
                                        </div>
                                        <div class='ticket-header'>
                                            <span>🎫 SUB-TIKET: {erow.get("No Tiket", "-")}</span>
                                            <span>📦 KATEGORI: {erow.get("Kategori", "-")}</span>
                                        </div>
                                        <table class='info-table'>
                                            <tr>
                                                <td width='14%'><b>Tanggal</b></td><td width='36%'>: {erow.get("Tanggal", "-")}</td>
                                                <td width='14%'><b>Periode</b></td><td width='36%'>: {erow.get("Periode", "-")}</td>
                                            </tr>
                                            <tr>
                                                <td><b>Nama PIC</b></td><td>: {erow.get("Nama", "-")} ({erow.get("Role", "-")})</td>
                                                <td><b>Nominal PJB</b></td><td>: <span style='color:#059669; font-weight:800;'>Rp {clean_nominal(erow.get("Nominal", 0)):,.0f}</span></td>
                                            </tr>
                                            <tr>
                                                <td><b>Nopol / Unit</b></td><td>: <b>{nopol_pdf}</b></td>
                                                <td><b>Keperluan</b></td><td>: {erow.get("Keperluan", "-")}</td>
                                            </tr>
                                            <tr style='background:#F0F9FF;'>
                                                <td><b>Jarak Nopol</b></td><td colspan='3'>: <b style='color:#0369A1;'>{jarak_nopol_pdf}</b></td>
                                            </tr>
                                            <tr>
                                                <td valign='top'><b>Deskripsi</b></td><td colspan='3'>: {desc_pdf}</td>
                                            </tr>
                                        </table>
                                        <div class='single-photo-stage'>
                                            <div class='single-photo-title'>📸 {lbl_foto} (Ukuran Asli Proporsional)</div>
                                            <div class='single-img-wrapper'>
                                                {img_html}
                                            </div>
                                        </div>
                                    </div>
                                    """
                            else:
                                # MODE RINGKAS (GRID 1 HALAMAN PER TIKET)
                                page_counter += 1
                                if jml_foto == 1:
                                    grid_cols, img_height = "1fr", "430px"
                                elif jml_foto == 2:
                                    grid_cols, img_height = "1fr 1fr", "350px"
                                elif jml_foto in [3, 4]:
                                    grid_cols, img_height = "1fr 1fr", "245px"
                                else:
                                    grid_cols, img_height = "1fr 1fr 1fr", "205px"

                                html_content += f"""
                                <div class='ticket-card'>
                                    <div class='report-top-bar'>
                                        <span>LAPORAN PERTANGGUNGJAWABAN (PJB) — NOP {nop_report.upper()}</span>
                                        <span>Hal. {page_counter}</span>
                                    </div>
                                    <div class='ticket-header'>
                                        <span>🎫 SUB-TIKET: {erow.get("No Tiket", "-")}</span>
                                        <span>📦 KATEGORI: {erow.get("Kategori", "-")}</span>
                                    </div>
                                    <table class='info-table'>
                                        <tr>
                                            <td width='14%'><b>Tanggal</b></td><td width='36%'>: {erow.get("Tanggal", "-")}</td>
                                            <td width='14%'><b>Periode</b></td><td width='36%'>: {erow.get("Periode", "-")}</td>
                                        </tr>
                                        <tr>
                                            <td><b>Nama PIC</b></td><td>: {erow.get("Nama", "-")} ({erow.get("Role", "-")})</td>
                                            <td><b>Nominal PJB</b></td><td>: <span style='color:#059669; font-weight:800;'>Rp {clean_nominal(erow.get("Nominal", 0)):,.0f}</span></td>
                                        </tr>
                                        <tr>
                                            <td><b>Nopol / Unit</b></td><td>: <b>{nopol_pdf}</b></td>
                                            <td><b>Keperluan</b></td><td>: {erow.get("Keperluan", "-")}</td>
                                        </tr>
                                        <tr style='background:#F0F9FF;'>
                                            <td><b>Jarak Nopol</b></td><td colspan='3'>: <b style='color:#0369A1;'>{jarak_nopol_pdf}</b></td>
                                        </tr>
                                        <tr>
                                            <td valign='top'><b>Deskripsi</b></td><td colspan='3'>: {desc_pdf}</td>
                                        </tr>
                                    </table>
                                    <div class='photo-grid' style='grid-template-columns: {grid_cols};'>
                                """
                                for idx_f, (lbl_foto, url_foto) in enumerate(valid_photos, 1):
                                    span_style = "grid-column: span 2; width: 65%; margin: 0 auto;" if (jml_foto == 3 and idx_f == 3) else ""
                                    html_content += f"""
                                        <div class='photo-box' style='{span_style}'>
                                            <div class='img-wrapper' style='height: {img_height};'>
                                                <img src='{url_foto}' alt='{lbl_foto}'>
                                            </div>
                                            <div class='photo-caption'>📸 {lbl_foto}</div>
                                        </div>
                                    """
                                html_content += "</div></div>"

                        if page_counter > 0:
                            full_html = f"""
                            <!DOCTYPE html>
                            <html>
                            <head>
                                <meta charset="UTF-8">
                                <title>Laporan Auto PJB - {nop_report}</title>
                                <style>
                                    @page {{
                                        size: A4 portrait;
                                        margin: 8mm 10mm;
                                    }}
                                    * {{
                                        box-sizing: border-box;
                                        -webkit-print-color-adjust: exact !important;
                                        print-color-adjust: exact !important;
                                    }}
                                    body {{
                                        font-family: 'Segoe UI', Helvetica, Arial, sans-serif;
                                        color: #0F172A;
                                        margin: 0;
                                        padding: 0;
                                        background: #FFFFFF;
                                    }}
                                    .ticket-card {{
                                        width: 100%;
                                        height: 277mm;
                                        max-height: 277mm;
                                        border: 1.5px solid #1E293B;
                                        padding: 10px 14px;
                                        border-radius: 8px;
                                        display: flex;
                                        flex-direction: column;
                                        justify-content: flex-start;
                                        page-break-inside: avoid;
                                        page-break-after: always;
                                        overflow: hidden;
                                        margin-bottom: 12px;
                                    }}
                                    .ticket-card:last-child {{
                                        page-break-after: auto;
                                    }}
                                    .report-top-bar {{
                                        display: flex;
                                        justify-content: space-between;
                                        align-items: center;
                                        background: #0F172A;
                                        color: #FFFFFF;
                                        font-size: 9pt;
                                        font-weight: 700;
                                        padding: 5px 12px;
                                        border-radius: 5px 5px 0 0;
                                        letter-spacing: 0.4px;
                                        flex-shrink: 0;
                                    }}
                                    .ticket-header {{
                                        display: flex;
                                        justify-content: space-between;
                                        background-color: #EFF6FF;
                                        color: #1E3A8A;
                                        padding: 6px 12px;
                                        font-weight: 800;
                                        font-size: 9.5pt;
                                        border-bottom: 2px solid #2563EB;
                                        margin-bottom: 6px;
                                        border-radius: 0 0 5px 5px;
                                        flex-shrink: 0;
                                    }}
                                    .info-table {{
                                        width: 100%;
                                        border-collapse: collapse;
                                        margin-bottom: 8px;
                                        font-size: 8.5pt;
                                        flex-shrink: 0;
                                    }}
                                    .info-table td {{
                                        padding: 3.5px 6px;
                                        border-bottom: 1px solid #E2E8F0;
                                        line-height: 1.28;
                                    }}
                                    /* FULL 1 LEMBAR PER FOTO — UKURAN ASLI PROPORSIONAL */
                                    .single-photo-stage {{
                                        flex: 1 1 auto;
                                        min-height: 0;
                                        display: flex;
                                        flex-direction: column;
                                        border: 1.2px solid #CBD5E1;
                                        border-radius: 8px;
                                        background: #F8FAFC;
                                        padding: 8px;
                                        overflow: hidden;
                                    }}
                                    .single-photo-title {{
                                        text-align: center;
                                        font-weight: 800;
                                        font-size: 9.5pt;
                                        color: #1E293B;
                                        padding-bottom: 6px;
                                        margin-bottom: 6px;
                                        border-bottom: 1px dashed #CBD5E1;
                                        flex-shrink: 0;
                                    }}
                                    .single-img-wrapper {{
                                        flex: 1 1 auto;
                                        min-height: 0;
                                        width: 100%;
                                        display: flex;
                                        align-items: center;
                                        justify-content: center;
                                        background: #FFFFFF;
                                        border-radius: 6px;
                                        overflow: hidden;
                                    }}
                                    .single-img-wrapper img {{
                                        max-width: 100%;
                                        max-height: 100%;
                                        width: auto;
                                        height: auto;
                                        object-fit: contain;
                                        display: block;
                                    }}
                                    /* GRID RINGKAS */
                                    .photo-grid {{
                                        display: grid;
                                        gap: 10px;
                                        width: 100%;
                                        align-items: stretch;
                                    }}
                                    .photo-box {{
                                        border: 1px solid #CBD5E1;
                                        border-radius: 6px;
                                        padding: 6px;
                                        background: #F8FAFC;
                                        display: flex;
                                        flex-direction: column;
                                        justify-content: space-between;
                                        text-align: center;
                                    }}
                                    .img-wrapper {{
                                        width: 100%;
                                        display: flex;
                                        align-items: center;
                                        justify-content: center;
                                        background: #FFFFFF;
                                        border-radius: 4px;
                                        overflow: hidden;
                                    }}
                                    .img-wrapper img {{
                                        max-width: 100%;
                                        max-height: 100%;
                                        width: auto;
                                        height: auto;
                                        object-fit: contain;
                                        display: block;
                                    }}
                                    .photo-caption {{
                                        color: #0F172A;
                                        font-weight: 700;
                                        font-size: 8.5pt;
                                        padding-top: 5px;
                                        margin-top: 4px;
                                        border-top: 1px dashed #E2E8F0;
                                        white-space: nowrap;
                                        overflow: hidden;
                                        text-overflow: ellipsis;
                                    }}
                                    @media screen {{
                                        .ticket-card {{
                                            height: 277mm;
                                            margin-bottom: 24px;
                                            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                                        }}
                                    }}
                                </style>
                            </head>
                            <body>
                                {html_content}
                            </body>
                            </html>
                            """
                            mode_msg = "Full 1 Lembar per Foto (Ukuran Asli)" if is_full_per_photo else "Grid 1 Halaman per Tiket"
                            st.success(f"✅ Berhasil men-generate **{page_counter}** lembar A4 Portrait dari **{ticket_counter}** tiket ({mode_msg}).")
                            b64_html = base64.b64encode(full_html.encode("utf-8")).decode()
                            st.markdown(f'<a href="data:text/html;base64,{b64_html}" download="Laporan_PJB_{nop_report}.html" style="display: block; text-align: center; background-color: #007BFF; color: white !important; padding: 15px 20px; text-decoration: none; border-radius: 10px; font-weight: bold; font-size: 1.05em;">📥 Download Laporan HTML Siap Cetak PDF (Tekan CTRL+P -> Save as PDF)</a>', unsafe_allow_html=True)
                            st.markdown("<hr>", unsafe_allow_html=True)
                            st.components.v1.html(full_html, height=850, scrolling=True)
        
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
                                is_pbu_adm = ("pangkalan" in str(nop_report).lower())
                                kota_adm = "Pangkalan Bun" if is_pbu_adm else "Palangka Raya"
                                koor_nama_adm = "Roni Yudi Iswanto" if is_pbu_adm else "Okta Pradika"
                                koor_jab_adm = "Koordinator NOP Pangkalan Bun" if is_pbu_adm else "Koordinator NOP Palangka Raya"
                                koor_nik_adm = nik_dict.get("RONI YUDI ISWANTO", nik_dict.get("RONI YUDI ISYANTO", "-")) if is_pbu_adm else "B0924649"
                                
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
                                                <tr><td width="150">Nama</td><td width="10">:</td><td>{koor_nama_adm}</td></tr>
                                                <tr><td>NIK</td><td>:</td><td>{koor_nik_adm}</td></tr>
                                                <tr><td>Jabatan</td><td>:</td><td>{koor_jab_adm}</td></tr>
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
                                            <div style="text-align: right; margin-top: 30px; margin-bottom: 30px;">{kota_adm}, {tgl_pjb_cetak.strftime("%d/%m/%Y")}</div>
                                            <div class="signature">
                                                <div><p>{koor_jab_adm},</p><br><br><br><p><b><u>{koor_nama_adm}</u></b><br>NIK. {koor_nik_adm}</p></div>
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
                                            <p>{koor_jab_adm} PT. Kinarya Utama Teknik, dengan ini menugaskan kepada :</p>
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
                                                <tr><td colspan="3">Uang Makan ({nama_petugas_cetak})</td><td align="center">{lama_hari_cetak} Hari (Lumpsum)</td><td width="30" style="border-right: none;">Rp.</td><td align="right" style="border-left: none;">{nom_pjb_cetak:,.0f}</td></tr>
                                                <tr><td colspan="3">Bantuan Penginapan</td><td align="center">0 Malam x Rp. 0</td><td width="30" style="border-right: none;">Rp.</td><td align="right" style="border-left: none;">0</td></tr>
                                                <tr><th colspan="5" align="right">Jumlah Total</th><th align="right">Rp. {nom_pjb_cetak:,.0f}</th></tr>
                                            </table>
                                            <table class="tbl-info" style="width: 300px; float: right; margin-top: 20px;">
                                                <tr><td width="120">Dikeluarkan di</td><td>: {kota_adm}</td></tr>
                                                <tr><td>Pada Tanggal</td><td>: {tgl_pjb_cetak.strftime("%d/%m/%Y")}</td></tr>
                                            </table>
                                            <div style="clear: both;"></div>
                                            <div class="signature">
                                                <div><p>{koor_jab_adm},</p><br><br><br><p><b><u>{koor_nama_adm}</u></b><br>NIK. {koor_nik_adm}</p></div>
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
# PAGE 8: REQ & PJB MONITORING
# ==========================================
elif st.session_state.page == "👀 Request & PJB Monitoring":
    st.markdown("<div class='header-card'><h2>📋 REQ & PJB MONITORING</h2><p>Pantau Aktivitas Tim Daily, Warning Tiket Gantung & Cek Sisa Dana</p></div>", unsafe_allow_html=True)
    
    nop_mon = st.selectbox("🌐 Pilih Wilayah Database (NOP):", ["-- Pilih NOP --"] + list(MASTER_DATA.keys()))
    if nop_mon != "-- Pilih NOP --":
        target_ss = MASTER_DATA[nop_mon]["spreadsheet_id"]
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
            st.markdown(f"#### 💸 Request Dana Masuk (Menunggu Diproses) - {filter_date_str}")
            
            processed_tickets = set()
            for app in app_r[1:]:
                if len(app) > 5 and app[3] == "Request Dana":
                    status_tiket = str(app[5]).strip().upper()
                    if status_tiket in ["REJECTED", "APPROVED"]:
                        processed_tickets.add(str(app[2]).strip().upper())

            daily_req = []
            tot_req_daily = 0
            
            # Format pencocokan tanggal anti-error
            d1 = filter_date.strftime("%d/%m/%Y")
            d2 = filter_date.strftime("%m/%d/%Y")
            d3 = filter_date.strftime("%Y-%m-%d")
            
            for r in req_r[1:]:
                if len(r) > 13:
                    raw_ts = str(r[0]).strip()
                    raw_tgl = str(r[1]).strip()
                    
                    if (d1 in raw_ts or d2 in raw_ts or d3 in raw_ts) or (d1 in raw_tgl or d2 in raw_tgl or d3 in raw_tgl):
                        tiket_req = str(r[3]).strip().upper()
                        
                        if tiket_req in processed_tickets: 
                            continue
                            
                        nom = clean_nominal(r[9])
                        tot_req_daily += nom
                        
                        tgl_tampil = raw_tgl if raw_tgl else raw_ts.split(" ")[0]
                        kep_item = str(r[8]).strip() if len(r) > 8 else "-"
                        kat_item = str(r[10]).strip() if len(r) > 10 else "-"
                        desc_raw = str(r[11]).strip() if len(r) > 11 else "-"
                        plat_info = str(r[16]).strip() if len(r) > 16 and str(r[16]).strip() else ""
                        bank_info = str(r[17]).strip() if len(r) > 17 else "-"
                        norek_info = str(r[18]).strip() if len(r) > 18 else "-"
                        
                        # Ekstrak Analisa Komparasi BBM jika ada di dalam Deskripsi
                        analisa_bbm_match = re.search(r"\[ANALISA BBM:\s*(.*?)\]", desc_raw)
                        analisa_bbm_str = analisa_bbm_match.group(1).strip() if analisa_bbm_match else ""
                        
                        # Bersihkan teks deskripsi utama dari tag sistem agar rapi
                        desc_clean_lines = []
                        for line in desc_raw.splitlines():
                            l_str = line.strip()
                            if l_str and not l_str.startswith("[ANALISA BBM:"):
                                desc_clean_lines.append(l_str)
                        desc_clean = " | ".join(desc_clean_lines) if desc_clean_lines else "-"
                            
                        # Deteksi otomatis Jumlah Liter & Selisih BBM atau Bentuk Barang
                        kat_lower = kat_item.lower()
                        if analisa_bbm_str:
                            info_plat = f" [{plat_info}]" if plat_info else ""
                            detail_barang_liter = f"⛽ {analisa_bbm_str}{info_plat}"
                        elif any(k in kat_lower for k in ["mobil", "motor", "genset", "pertalite", "pertamax", "dexlite", "solar"]):
                            hrg_est = 12500 if "pertamax" in kat_lower else (14500 if "dex" in kat_lower else (6800 if "solar" in kat_lower else 10000))
                            jml_liter = round(nom / hrg_est, 1) if nom > 0 else 0
                            info_plat = f" [{plat_info}]" if plat_info else ""
                            detail_barang_liter = f"⛽ ± {jml_liter} Liter{info_plat} — {desc_clean}"
                        elif "material" in kat_lower or "pembelian" in kep_item.lower() or "pengiriman" in kep_item.lower():
                            detail_barang_liter = f"📦 Barang/Material: {desc_clean}"
                        elif "uang makan" in kat_lower or "penginapan" in kat_lower:
                            detail_barang_liter = f"🍽️ Akomodasi: {desc_clean}"
                        else:
                            detail_barang_liter = f"🛠️ Detail: {desc_clean}"
                        
                        daily_req.append({
                            "Tanggal": tgl_tampil,
                            "Nama": r[5],
                            "Tipe Request": f"{kep_item} — {kat_item}",
                            "Jml Liter / Bentuk Barang": detail_barang_liter,
                            "Nominal Request": nom,
                            "Rekening Tim": f"{bank_info} - {norek_info}",
                            "Jarak/Info": r[13],
                            "Sub-Tiket (Split)": r[3],
                            "Waktu": r[0]
                        })
            
            # TAMPILKAN TABEL JIKA ADA REQUEST
            if daily_req:
                df_dreq = pd.DataFrame(daily_req)
                df_dreq["Nominal Request"] = df_dreq["Nominal Request"].apply(lambda x: f"Rp {x:,.0f}")
                st.dataframe(
                    df_dreq[["Tanggal", "Nama", "Tipe Request", "Jml Liter / Bentuk Barang", "Nominal Request", "Rekening Tim", "Jarak/Info", "Sub-Tiket (Split)"]],
                    hide_index=True,
                    use_container_width=True
                )
                st.markdown(f"<div style='text-align:right; font-size:1.2em; color:#0ea5e9; font-weight:bold;'>Total Request: Rp {tot_req_daily:,.0f}</div>", unsafe_allow_html=True)
            else:
                st.success("Belum ada request dana (atau semua tiket hari ini sudah selesai Anda proses).")
                
            # ========================================================
            # 🚀 MENU APPROVAL & PENCAIRAN CEPAT (DENGAN RINGKASAN DETAIL)
            # ========================================================
            st.markdown("##### 🚀 Approval & Pencairan Cepat (Distribusi Tim)")
            um_r_dist = data_all.get(SHEET_UM, [])
            valid_batches = sorted(list(set([r[2].strip() for r in um_r_dist[1:] if len(r) > 2 and r[2].strip() != ""])))
            
            cd1, cd2, cd3 = st.columns(3)
            with cd1:
                tiket_to_app = st.selectbox("Pilih Tiket (Support):", ["-- Pilih Tiket --"] + [req['Sub-Tiket (Split)'] for req in daily_req])
            
            selected_req_obj = next((req for req in daily_req if req['Sub-Tiket (Split)'] == tiket_to_app), None)
            auto_nom = selected_req_obj['Nominal Request'] if selected_req_obj else 0
                
            with cd2:
                sumber_dana_app = st.selectbox("Sumber Dana (Budget)", ["-- Pilih Dana --"] + valid_batches)
            with cd3:
                nom_dist_app = st.number_input("Nominal Transfer (Rp) [Auto]", min_value=0, step=1000, value=int(auto_nom))
            
            # TAMPILKAN KARTU RINGKASAN SAAT TIKET DIPILIH AGAR ADMIN MUDAH APPROVE
            if selected_req_obj:
                st.info(
                    f"📋 **Ringkasan Tiket Terpilih:**\n"
                    f"- **Tanggal & Petugas:** {selected_req_obj['Tanggal']} | **{selected_req_obj['Nama']}**\n"
                    f"- **Tipe Request:** {selected_req_obj['Tipe Request']}\n"
                    f"- **Jumlah Liter / Bentuk Barang:** {selected_req_obj['Jml Liter / Bentuk Barang']}\n"
                    f"- **Nilai Request & Rekening:** **Rp {selected_req_obj['Nominal Request']:,.0f}** ({selected_req_obj['Rekening Tim']})"
                )
            
            c_act1, c_act2 = st.columns(2)
            with c_act1:
                btn_approve = st.button("✅ Approve & Support (Catat ke Distribusi)", type="primary", use_container_width=True)
            with c_act2:
                btn_reject = st.button("❌ Reject Request", use_container_width=True)
            
            if btn_approve:
                if tiket_to_app != "-- Pilih Tiket --" and sumber_dana_app != "-- Pilih Dana --" and nom_dist_app > 0:
                    nama_penerima = selected_req_obj['Nama'] if selected_req_obj else ""
                    
                    append_data(SHEET_DISTRIBUSI, [
                        datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                        datetime.now().strftime("%d/%m/%Y"),
                        sumber_dana_app,
                        nama_penerima,
                        nom_dist_app,
                        f"AUTO-SUPPORT: {tiket_to_app}" 
                    ], target_ss)
                    
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
                    nama_penerima = selected_req_obj['Nama'] if selected_req_obj else ""
                    
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
            
            # --- DAILY PJB ---
            st.markdown(f"#### ✅ PJB Disubmit ({filter_date_str})")
            daily_pjb = []
            tot_pjb_daily = 0
            for r in pjb_r[1:]:
                if len(r) > 24:
                    raw_ts = str(r[0]).strip()
                    raw_tgl = str(r[1]).strip()
                    
                    # 🚀 BACA TANGGAL PJB SECARA PINTAR
                    if (d1 in raw_ts or d2 in raw_ts or d3 in raw_ts) or (d1 in raw_tgl or d2 in raw_tgl or d3 in raw_tgl):
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

            # ========================================================
            # 📲 WA REPORT HARIAN PENGGUNAAN DANA & SISA UANG MUKA (UM)
            # ========================================================
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown(f"#### 📲 WA Report Harian Penggunaan Dana & Sisa Uang Muka ({filter_date_str})")
            c_wr1, c_wr2 = st.columns([1, 2])
            with c_wr1:
                batch_wa_opt = st.selectbox("Filter Batch Uang Muka (UM):", ["Semua Batch"] + valid_batches, key="wa_rep_batch_mon")
            with c_wr2:
                note_wa_daily = st.text_input("Catatan Tambahan Admin (Opsional):", placeholder="Misal: Mohon tim yang belum PJB segera melengkapi hari ini.", key="wa_rep_note_mon")

            wa_daily_txt, wa_daily_metrics = generate_daily_finance_wa_report(nop_mon, filter_date, data_all, selected_batch=batch_wa_opt, extra_note=note_wa_daily)
            mw1, mw2, mw3 = st.columns(3)
            mw1.metric("💰 Total UM Masuk", f"Rp {wa_daily_metrics['tot_um_in']:,.0f}")
            mw2.metric("💸 Cair Hari Ini", f"Rp {wa_daily_metrics['tot_dist_today']:,.0f}")
            mw3.metric("🏦 Sisa Saldo UM", f"Rp {wa_daily_metrics['sisa_um_dist']:,.0f}")

            st.code(wa_daily_txt, language="markdown")
            wa_daily_enc = quote(wa_daily_txt)
            st.markdown(
                f'<a href="https://wa.me/?text={wa_daily_enc}" target="_blank" class="btn-sidata-blue" style="background: linear-gradient(135deg, #22C55E 0%, #16A34A 100%) !important;">📲 KIRIM WA REPORT HARIAN DANA & SISA UM SEKARANG</a>',
                unsafe_allow_html=True
            )
            
        with tab_warning:
            st.markdown("#### 🚨 Daftar Aging PJB & Monitoring Tiket Gantung (Belum PJB)")
            st.info("💡 Menampilkan seluruh pengajuan dana (Request) yang **belum disubmit laporan PJB-nya** beserta umur keterlambatan (Aging).")

            # 1. Kumpulkan tiket yang di-REJECT agar tidak ikut dihitung Aging
            rejected_tickets = set()
            approved_tickets = set()
            for app in app_r[1:]:
                app_pad = (app + [""] * 10)[:10]
                if str(app_pad[3]).strip() == "Request Dana":
                    st_app = str(app_pad[5]).strip().upper()
                    tk_app = str(app_pad[2]).strip().upper()
                    if tk_app:
                        if st_app == "REJECTED":
                            rejected_tickets.add(tk_app)
                        elif st_app == "APPROVED":
                            approved_tickets.add(tk_app)

            # 2. Kumpulkan tiket yang SUDAH PJB (abaikan sel kosong agar tidak memblokir semua data)
            pjb_done_tickets = set()
            for p in pjb_r[1:]:
                p_pad = (p + [""] * 40)[:40]
                tk_sub_pjb = str(p_pad[36]).strip().upper()
                tk_base_pjb = str(p_pad[21]).strip().upper()
                if tk_sub_pjb and tk_sub_pjb not in ["-", "NAN", "NONE", "0"]:
                    pjb_done_tickets.add(tk_sub_pjb)
                if tk_base_pjb and tk_base_pjb not in ["-", "NAN", "NONE", "0"]:
                    pjb_done_tickets.add(tk_base_pjb)

            # 3. Fungsi pembaca tanggal cerdas khusus Aging (kebal format PLK & PBU)
            today_dt = datetime.now().date()
            def parse_aging_date(raw_tgl_str, raw_ts_str):
                for val in [raw_tgl_str, raw_ts_str]:
                    s = str(val).strip().split(" ")[0].strip()
                    if not s or s.upper() in ["NAN", "NONE", "-"]:
                        continue
                    cands = []
                    for fmt in ["%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d", "%d/%m/%y", "%m/%d/%y"]:
                        try:
                            d_obj = datetime.strptime(s, fmt).date()
                            if d_obj not in cands:
                                cands.append(d_obj)
                        except ValueError:
                            continue
                    if cands:
                        # Pilih tanggal yang tidak berada di masa depan & paling dekat dengan hari operasional
                        valid_past = [d for d in cands if d <= today_dt]
                        if valid_past:
                            return min(valid_past, key=lambda x: abs((today_dt - x).days))
                        return cands[0]
                return today_dt

            # 4. Tarik seluruh data Request Dana yang belum PJB
            aging_list = []
            tot_nominal_aging = 0
            for r in req_r[1:]:
                r_pad = (r + [""] * 40)[:40]
                nama_pic = str(r_pad[5]).strip().upper()
                tiket_sub = str(r_pad[3]).strip().upper()
                tiket_base = str(r_pad[2]).strip().upper()
                tiket_cek = tiket_sub if tiket_sub else tiket_base

                # Lewati baris kosong
                if not nama_pic and not tiket_cek:
                    continue

                # Lewati jika sudah di-Reject atau sudah selesai PJB
                if tiket_cek in rejected_tickets or tiket_cek in pjb_done_tickets:
                    continue

                nom_req_ag = clean_nominal(r_pad[9])
                tgl_obj = parse_date(r_pad[1], r_pad[0])
                if tgl_obj == datetime(1970, 1, 1).date(): tgl_obj = parse_aging_date(r_pad[1], r_pad[0])
                aging_days = max(0, (today_dt - tgl_obj).days)

                if aging_days == 0:
                    kat_aging = "🟢 Hari Ini (0 Hari)"
                elif aging_days <= 3:
                    kat_aging = f"🟡 1-3 Hari ({aging_days} Hari)"
                elif aging_days <= 7:
                    kat_aging = f"🟠 4-7 Hari ({aging_days} Hari)"
                else:
                    kat_aging = f"🔴 > 7 Hari ({aging_days} Hari - OVERDUE)"

                status_pencairan = "✅ Sudah Approve" if tiket_cek in approved_tickets else "⏳ Menunggu Approve"

                tot_nominal_aging += nom_req_ag
                aging_list.append({
                    "Tanggal Req": tgl_obj.strftime("%d/%m/%Y"),
                    "Nama PIC": nama_pic,
                    "Role": str(r_pad[6]).strip() or "-",
                    "Sub-Tiket": tiket_cek,
                    "Keperluan": str(r_pad[8]).strip() or "-",
                    "Kategori": str(r_pad[10]).strip() or "-",
                    "Nominal": nom_req_ag,
                    "Aging (Hari)": aging_days,
                    "Status Aging": kat_aging,
                    "Status Admin": status_pencairan
                })

            if aging_list:
                df_aging = pd.DataFrame(aging_list)
                df_aging = df_aging.sort_values(by=["Aging (Hari)", "Nominal"], ascending=[False, False])

                # Filter cepat berdasarkan Nama atau Status Aging
                cf1, cf2 = st.columns(2)
                with cf1:
                    list_pic_ag = ["Semua Personel"] + sorted(df_aging["Nama PIC"].unique().tolist())
                    pilih_pic_ag = st.selectbox("🔍 Filter Nama Personel:", list_pic_ag, key="flt_pic_aging")
                with cf2:
                    pilih_st_ag = st.selectbox("⏳ Filter Kategori Aging:", ["Semua Status", "🔴 > 7 Hari (OVERDUE)", "🟠 4-7 Hari", "🟡 1-3 Hari", "🟢 Hari Ini"], key="flt_st_aging")

                if pilih_pic_ag != "Semua Personel":
                    df_aging = df_aging[df_aging["Nama PIC"] == pilih_pic_ag]
                if pilih_st_ag == "🔴 > 7 Hari (OVERDUE)":
                    df_aging = df_aging[df_aging["Aging (Hari)"] > 7]
                elif pilih_st_ag == "🟠 4-7 Hari":
                    df_aging = df_aging[(df_aging["Aging (Hari)"] >= 4) & (df_aging["Aging (Hari)"] <= 7)]
                elif pilih_st_ag == "🟡 1-3 Hari":
                    df_aging = df_aging[(df_aging["Aging (Hari)"] >= 1) & (df_aging["Aging (Hari)"] <= 3)]
                elif pilih_st_ag == "🟢 Hari Ini":
                    df_aging = df_aging[df_aging["Aging (Hari)"] == 0]

                tot_filtered_ag = df_aging["Nominal"].sum()
                m1, m2, m3 = st.columns(3)
                m1.metric("🎫 Total Tiket Belum PJB", f"{len(df_aging)} Tiket")
                m2.metric("💰 Total Dana Menggantung", f"Rp {tot_filtered_ag:,.0f}")
                m3.metric("🚨 Tiket Overdue (> 7 Hari)", f"{len(df_aging[df_aging['Aging (Hari)'] > 7])} Tiket")

                df_aging_show = df_aging.copy()
                df_aging_show["Nominal"] = df_aging_show["Nominal"].apply(lambda x: f"Rp {x:,.0f}")
                st.dataframe(df_aging_show, hide_index=True, use_container_width=True)

                # Tombol Download CSV / Excel untuk tarikan data Aging PJB
                csv_aging = df_aging.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label=f"📥 Tarik / Download Data Aging PJB ({nop_mon})",
                    data=csv_aging,
                    file_name=f"Data_Aging_PJB_{nop_mon}_{today_dt.strftime('%d%m%Y')}.csv",
                    mime="text/csv",
                    type="primary",
                    use_container_width=True
                )
            else:
                st.success("🎉 Luar biasa! Seluruh tiket Request Dana di wilayah ini sudah diselesaikan PJB-nya (0 Tiket Gantung).")

# ==========================================
# PAGE 8: ARAHAN PENGISIAN SIDATA
# ==========================================
elif st.session_state.page == "📝 Report Lapangan":
    st.markdown("""
        <div class='header-card'>
            <h2>📊 PELAPORAN KEGIATAN LAPANGAN (SiDATA)</h2>
            <p>Seluruh pelaporan progress lapangan, dokumentasi kegiatan, dan update pekerjaan kini terpusat di Portal SiDATA.</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("""
        <div class="sidata-area-card" style="max-width: 650px; margin: 0 auto 25px auto; min-height: 220px;">
            <div>
                <div style="font-size: 3.2rem; line-height:1; margin-bottom:12px;">🚀</div>
                <div class="sidata-card-heading">Portal Resmi SiDATA KUT</div>
                <div class="sidata-card-desc" style="margin-bottom: 20px !important;">
                    Khusus Role TE, MBP, & CME: Silakan klik tombol di bawah ini untuk mengisi laporan kegiatan lapangan (Troubleshooting / PM / Site Visit) langsung di aplikasi SiDATA.
                </div>
            </div>
            <a href="https://sidata.streamlit.app/" target="_blank" class="btn-sidata-red" style="max-width: 400px;">
                👉 BUKA PORTAL SIDATA SEKARANG (https://sidata.streamlit.app/)
            </a>
        </div>
    """, unsafe_allow_html=True)
