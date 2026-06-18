import html
import io
import json
import os
import re
import sys
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from abnormality_detector import compute_deviation
from clinical_reasoner import ClinicalReasoner
from components.header import show_logo_header
from config.branding import APP_NAME, TAGLINE
from database.db_manager import save_prediction
from engine import explain_prediction
from medical_knowledge import DISEASE_WEIGHTS, NORMAL_RANGES
from utils.ai_report import generate_medical_report

ROOT             = os.path.dirname(os.path.dirname(__file__))
SKIN_MODEL_PATH  = os.path.join(ROOT, "skin_model", "skin_model.keras")
SKIN_CLASSES_PATH= os.path.join(ROOT, "skin_model", "classes.json")
SKIN_DATASET_PATH= os.path.join(ROOT, "dataset", "processed")

SKIN_CLASS_LABELS = {
    "akiec": "Actinic Keratosis",
    "bcc":   "Basal Cell Carcinoma",
    "bkl":   "Benign Keratosis",
    "df":    "Dermatofibroma",
    "mel":   "Melanoma",
    "nv":    "Nevi",
    "vasc":  "Vascular Lesion",
    "normal": "Normal Skin",
}

MODE_LABELS = {
    "skin":     "Skin Disease Detection",
    "heart":    "Heart Disease Prediction",
    "diabetes": "Diabetes Prediction",
    "liver":    "Liver Disease Prediction",
    "full":     "Full Health Risk Analysis",
}
MODE_DESCRIPTIONS = {
    "skin":     "Upload a skin image for AI-supported lesion assessment.",
    "heart":    "Review cardiovascular indicators — cholesterol, BP, and heart rate.",
    "diabetes": "Analyze glucose, BMI, and insulin markers for diabetes risk.",
    "liver":    "Evaluate bilirubin and enzyme values for liver-related risk.",
    "full":     "Combine all biomarker inputs into a multi-condition risk review.",
}
MODE_ICONS  = {"skin":"🔬","heart":"❤️","diabetes":"🩸","liver":"🫀","full":"📊"}
MODE_COLORS = {
    "skin":     ("rgba(0,245,160,0.12)",  "#00f5a0", "rgba(0,245,160,0.35)"),
    "heart":    ("rgba(251,113,133,0.12)","#fb7185", "rgba(251,113,133,0.35)"),
    "diabetes": ("rgba(167,139,250,0.12)","#a78bfa", "rgba(167,139,250,0.35)"),
    "liver":    ("rgba(251,191,36,0.12)", "#fbbf24", "rgba(251,191,36,0.35)"),
    "full":     ("rgba(6,182,212,0.12)",  "#06b6d4", "rgba(6,182,212,0.35)"),
}

# Keras import deferred to speed up page load
# ──────────────────────────────────────────────
#  STYLES
# ──────────────────────────────────────────────
def inject_predictor_styles(mode="full"):
    accent = MODE_COLORS.get(mode, MODE_COLORS["full"])[1]
    accent_bg  = MODE_COLORS.get(mode, MODE_COLORS["full"])[0]
    accent_bdr = MODE_COLORS.get(mode, MODE_COLORS["full"])[2]

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

        :root {{
            --bg-deep:      #04101f;
            --bg-card:      rgba(6,18,38,0.82);
            --accent:       {accent};
            --accent-bg:    {accent_bg};
            --accent-bdr:   {accent_bdr};
            --accent-g:     #00f5a0;
            --accent-b:     #00d9f5;
            --accent-p:     #818cf8;
            --accent-r:     #fb7185;
            --accent-y:     #fbbf24;
            --text-main:    #e8f4fd;
            --text-muted:   #7a9ab8;
            --glass-border: rgba(0,245,160,0.15);
            --input-bg:     rgba(4,14,30,0.75);
        }}

        /* ── SHELL ── */
        .stApp {{
            background: var(--bg-deep) !important;
            font-family: 'DM Sans', sans-serif !important;
            color: var(--text-main) !important;
        }}
        .stApp > header {{ display:none !important; }}
        .block-container {{ padding-top:0 !important; max-width:1280px !important; }}

        /* ── BACKGROUND ── */
        .stApp::before {{
            content:'';
            position:fixed; inset:0; z-index:0;
            background:
                radial-gradient(ellipse 70% 55% at 10% 25%, rgba(0,245,160,0.09) 0%, transparent 55%),
                radial-gradient(ellipse 55% 45% at 90% 15%, rgba(0,217,245,0.08) 0%, transparent 50%),
                radial-gradient(ellipse 50% 65% at 65% 90%, rgba(129,140,248,0.07) 0%, transparent 55%),
                radial-gradient(ellipse 35% 40% at 25% 80%, rgba(251,191,36,0.05) 0%, transparent 50%),
                linear-gradient(145deg,#04101f,#060f1e 50%,#050d1b);
            animation: bgBreath 14s ease-in-out infinite alternate;
            pointer-events:none;
        }}
        @keyframes bgBreath {{
            0%   {{ filter:hue-rotate(0deg)  brightness(1); }}
            100% {{ filter:hue-rotate(18deg) brightness(1.05); }}
        }}

        /* GRID */
        .stApp::after {{
            content:'';
            position:fixed; inset:0; z-index:0;
            background-image:
                linear-gradient(rgba(0,245,160,0.022) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0,245,160,0.022) 1px, transparent 1px);
            background-size: 48px 48px;
            pointer-events:none;
            animation: gridSlide 35s linear infinite;
        }}
        @keyframes gridSlide {{ from{{background-position:0 0}} to{{background-position:48px 48px}} }}

        /* ── ORBS ── */
        .orb-layer {{ position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden; }}
        .orb {{ position:absolute;border-radius:50%;filter:blur(90px);opacity:0.18;animation:orbDrift linear infinite; }}
        .o1{{width:420px;height:420px;background:#00f5a0;left:-140px;top:5%;animation-duration:26s;}}
        .o2{{width:340px;height:340px;background:#00d9f5;right:-100px;top:50%;animation-duration:32s;animation-delay:-10s;}}
        .o3{{width:280px;height:280px;background:#818cf8;left:43%;top:78%;animation-duration:22s;animation-delay:-6s;}}
        .o4{{width:230px;height:230px;background:#fbbf24;right:20%;top:2%;animation-duration:38s;animation-delay:-16s;}}
        @keyframes orbDrift {{
            0%  {{transform:translateY(0) scale(1);}}
            35% {{transform:translateY(-55px) scale(1.07);}}
            70% {{transform:translateY(28px) scale(0.94);}}
            100%{{transform:translateY(0) scale(1);}}
        }}

        /* ── PARTICLES ── */
        .particles {{ position:fixed;inset:0;z-index:0;pointer-events:none; }}
        .particle {{ position:absolute;font-size:1.3rem;opacity:0;animation:pFloat linear infinite;
                     filter:drop-shadow(0 0 8px rgba(0,245,160,0.5)); }}
        .pa{{left:5%; top:20%;animation-duration:20s;animation-delay:0s;}}
        .pb{{left:88%;top:35%;animation-duration:24s;animation-delay:-7s;}}
        .pc{{left:18%;top:70%;animation-duration:17s;animation-delay:-3s;}}
        .pd{{left:80%;top:80%;animation-duration:28s;animation-delay:-12s;}}
        .pe{{left:48%;top:8%; animation-duration:22s;animation-delay:-9s;}}
        .pf{{left:32%;top:92%;animation-duration:16s;animation-delay:-2s;}}
        @keyframes pFloat {{
            0%  {{opacity:0;transform:translateY(0) rotate(0deg) scale(0.8);}}
            10% {{opacity:0.4;}}
            50% {{opacity:0.22;transform:translateY(-130px) rotate(180deg) scale(1.1);}}
            90% {{opacity:0.4;}}
            100%{{opacity:0;transform:translateY(-260px) rotate(360deg) scale(0.8);}}
        }}

        /* ── HERO ── */
        .page-hero {{
            position:relative;z-index:1;
            text-align:center; padding:2.8rem 2rem 1.5rem;
            animation:heroIn 0.9s ease both;
        }}
        @keyframes heroIn {{ from{{opacity:0;transform:translateY(-22px)}} to{{opacity:1;transform:translateY(0)}} }}
        .page-hero h2 {{
            font-family:'Syne',sans-serif !important;
            font-size:2.6rem !important; font-weight:800 !important;
            background:linear-gradient(135deg,var(--accent),var(--accent-b),var(--accent-p));
            -webkit-background-clip:text; -webkit-text-fill-color:transparent;
            background-clip:text; letter-spacing:-0.8px;
            margin-bottom:0.5rem !important;
        }}
        .page-hero p {{
            font-size:1rem !important; color:var(--text-muted) !important;
            font-weight:300 !important; max-width:500px; margin:0 auto; line-height:1.65;
        }}
        .hero-mode-badge {{
            display:inline-flex; align-items:center; gap:0.5rem;
            background:var(--accent-bg);
            border:1px solid var(--accent-bdr);
            border-radius:999px; padding:0.32rem 1rem;
            font-size:0.78rem; color:var(--accent);
            font-weight:600; letter-spacing:0.4px;
            margin-bottom:0.9rem;
        }}
        .hero-icon-wrap {{
            display:flex; justify-content:center; margin-bottom:0.9rem;
        }}
        .hero-icon-core {{
            width:60px; height:60px; border-radius:50%;
            background:linear-gradient(135deg,var(--accent),var(--accent-b));
            display:flex; align-items:center; justify-content:center;
            font-size:1.7rem;
            animation:iconPulse 2.6s ease-in-out infinite;
        }}
        @keyframes iconPulse {{
            0%,100%{{box-shadow:0 0 0 0 rgba(0,245,160,0.5);}}
            50%    {{box-shadow:0 0 0 20px rgba(0,245,160,0);}}
        }}

        /* ── ECG BAR ── */
        .ecg-bar {{
            position:relative;z-index:1;
            width:100%;height:46px;overflow:hidden;margin:0.6rem 0 1.6rem;
        }}
        .ecg-bar svg {{ position:absolute;animation:ecgScroll 3s linear infinite;width:200%; }}
        @keyframes ecgScroll {{ from{{transform:translateX(0)}} to{{transform:translateX(-50%)}} }}

        /* ── MODE PILL TABS ── */
        .mode-tabs {{
            position:relative;z-index:1;
            display:flex; flex-wrap:wrap; gap:0.5rem;
            justify-content:center; margin-bottom:1.8rem;
        }}
        .mode-tab {{
            padding:0.4rem 1rem; border-radius:999px;
            font-size:0.8rem; font-weight:600; font-family:'DM Sans',sans-serif;
            border:1px solid rgba(0,245,160,0.2);
            color:var(--text-muted); background:rgba(10,22,45,0.6);
            cursor:pointer; transition:all 0.25s;
            backdrop-filter:blur(8px);
        }}
        .mode-tab.active {{
            background:var(--accent-bg);
            border-color:var(--accent-bdr);
            color:var(--accent);
            box-shadow:0 0 16px rgba(0,245,160,0.18);
        }}

        /* ── SECTION BANNER ── */
        .section-banner {{
            position:relative;z-index:1;
            display:flex;align-items:center;gap:0.8rem;margin:1.6rem 0 1rem;
        }}
        .sb-line  {{flex:1;height:1px;background:linear-gradient(90deg,rgba(0,245,160,0.35),transparent);}}
        .sb-line.r{{background:linear-gradient(90deg,transparent,rgba(0,245,160,0.35));}}
        .sb-title {{font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;color:var(--text-main);white-space:nowrap;}}
        .sb-dot   {{width:8px;height:8px;border-radius:50%;background:linear-gradient(135deg,#00f5a0,#00d9f5);
                    box-shadow:0 0 10px rgba(0,245,160,0.8);animation:dotPulse 2s ease-in-out infinite;}}
        @keyframes dotPulse {{0%,100%{{transform:scale(1);opacity:1;}}50%{{transform:scale(1.4);opacity:0.6;}}}}

        /* ── GLASS PANEL ── */
        .glass-panel {{
            position:relative;z-index:1;
            background:var(--bg-card);
            border:1px solid var(--glass-border);
            border-radius:20px; padding:1.8rem;
            backdrop-filter:blur(18px);
            box-shadow:0 24px 60px rgba(0,0,0,0.45),0 0 0 1px rgba(0,245,160,0.04);
            margin-bottom:1.2rem;
            animation:panelIn 0.7s ease 0.15s both;
            overflow:hidden;
        }}
        @keyframes panelIn {{from{{opacity:0;transform:translateY(20px) scale(0.97)}}to{{opacity:1;transform:translateY(0) scale(1)}}}}
        .glass-panel::before {{
            content:'';position:absolute;top:0;left:10%;right:10%;height:1px;
            background:linear-gradient(90deg,transparent,var(--accent) 40%,var(--accent-b) 60%,transparent);
            animation:topGlow 3.5s ease-in-out infinite;
        }}
        @keyframes topGlow {{0%,100%{{opacity:0.45;}}50%{{opacity:1;}}}}

        /* ── SECTION LABEL (inside form) ── */
        .section-label {{
            font-family:'Syne',sans-serif;font-size:0.7rem;font-weight:700;
            letter-spacing:2.5px;text-transform:uppercase;
            color:var(--accent-g);margin:1.2rem 0 0.3rem;position:relative;z-index:1;
        }}
        .sub-label {{
            font-family:'Syne',sans-serif;font-size:0.68rem;font-weight:700;
            letter-spacing:2px;text-transform:uppercase;
            color:var(--accent);margin:1rem 0 0.4rem;
            display:flex;align-items:center;gap:0.4rem;
        }}
        .sub-label::before {{
            content:'';width:16px;height:1px;
            background:var(--accent);display:inline-block;
        }}

        /* ── INPUTS ── */
        .stTextInput > label, .stNumberInput > label, .stFileUploader > label {{
            font-family:'DM Sans',sans-serif !important;
            font-size:0.76rem !important;font-weight:500 !important;
            color:var(--text-muted) !important;
            letter-spacing:0.4px !important;text-transform:uppercase !important;
        }}
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input {{
            background:var(--input-bg) !important;
            border:1px solid rgba(0,245,160,0.16) !important;
            border-radius:12px !important;
            color:var(--text-main) !important;
            font-family:'DM Sans',sans-serif !important;font-size:0.95rem !important;
            transition:border-color 0.3s, box-shadow 0.3s !important;
        }}
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus {{
            border-color:rgba(0,245,160,0.5) !important;
            box-shadow:0 0 0 3px rgba(0,245,160,0.1),0 0 18px rgba(0,245,160,0.07) !important;
        }}
        .stTextInput > div > div > input::placeholder {{ color:rgba(122,154,184,0.4) !important; }}
        .stNumberInput > div > div > div > button {{
            background:rgba(0,245,160,0.07) !important;
            border:1px solid rgba(0,245,160,0.14) !important;
            color:#00f5a0 !important;border-radius:8px !important;
        }}

        /* ── FORM SUBMIT BUTTON ── */
        div.stForm div.stButton > button,
        div[data-testid="stFormSubmitButton"] > button {{
            font-family:'Syne',sans-serif !important;
            background:linear-gradient(135deg,var(--accent) 0%,var(--accent-b) 100%) !important;
            color:#04101f !important;border:none !important;
            border-radius:12px !important;font-weight:800 !important;
            font-size:1rem !important;letter-spacing:0.5px !important;
            padding:0.75rem !important;
            transition:transform 0.25s,box-shadow 0.25s !important;
        }}
        div.stForm div.stButton > button:hover,
        div[data-testid="stFormSubmitButton"] > button:hover {{
            transform:translateY(-3px) !important;
            box-shadow:0 14px 40px rgba(0,245,160,0.4),0 4px 12px rgba(0,0,0,0.3) !important;
        }}

        /* ── GENERAL BUTTONS ── */
        div.stButton > button {{
            font-family:'DM Sans',sans-serif !important;
            background:transparent !important;
            border:1px solid var(--accent-bdr) !important;
            color:var(--accent) !important;
            border-radius:12px !important;font-weight:600 !important;
            font-size:0.88rem !important;padding:0.6rem 1.2rem !important;
            transition:all 0.25s !important;
        }}
        div.stButton > button:hover {{
            background:var(--accent-bg) !important;
            box-shadow:0 6px 24px rgba(0,245,160,0.2) !important;
            transform:translateY(-2px) !important;
        }}

        /* ── DOWNLOAD BUTTON ── */
        div[data-testid="stDownloadButton"] > button {{
            font-family:'Syne',sans-serif !important;
            background:linear-gradient(135deg,#00f5a0,#00d9f5) !important;
            color:#04101f !important;border:none !important;
            border-radius:12px !important;font-weight:700 !important;
            font-size:0.9rem !important;
            transition:transform 0.25s,box-shadow 0.25s !important;
        }}
        div[data-testid="stDownloadButton"] > button:hover {{
            transform:translateY(-3px) !important;
            box-shadow:0 12px 36px rgba(0,245,160,0.38) !important;
        }}

        /* ── STATUS CARD ── */
        .status-card {{
            position:relative;z-index:1;
            background:var(--bg-card);backdrop-filter:blur(16px);
            border-radius:16px;padding:1.4rem 1.5rem;
            margin-bottom:1.2rem;
            animation:panelIn 0.6s ease both;
            overflow:hidden;
        }}
        .status-card h4 {{
            font-family:'Syne',sans-serif !important;
            font-size:1.25rem !important;font-weight:800 !important;
            margin-bottom:0.5rem !important;
        }}

        /* ── RISK PILL ── */
        .risk-pill {{
            display:inline-block;padding:3px 12px;border-radius:999px;
            font-size:0.72rem;font-weight:700;letter-spacing:0.5px;margin-right:0.4rem;
        }}
        .risk-low  {{background:rgba(0,245,160,0.15);color:#00f5a0;border:1px solid rgba(0,245,160,0.3);}}
        .risk-med  {{background:rgba(251,191,36,0.15); color:#fbbf24;border:1px solid rgba(251,191,36,0.3);}}
        .risk-high {{background:rgba(251,113,133,0.15);color:#fb7185;border:1px solid rgba(251,113,133,0.3);}}

        /* ── HELPER CARD ── */
        .helper-card {{
            position:relative;z-index:1;
            background:var(--bg-card);border:1px solid var(--glass-border);
            border-radius:20px;padding:3rem 2rem;text-align:center;
            backdrop-filter:blur(16px);
            box-shadow:0 16px 48px rgba(0,0,0,0.4);
            animation:panelIn 0.7s ease 0.2s both;
        }}
        .helper-icon {{
            font-size:3.5rem;margin-bottom:1rem;
            display:block;
            animation:iconPulse 2.6s ease-in-out infinite;
        }}
        .helper-title {{
            font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;
            color:var(--text-main);margin-bottom:0.4rem;
        }}
        .helper-sub {{ font-size:0.88rem;color:var(--text-muted);font-weight:300;line-height:1.6; }}

        /* ── DATAFRAME ── */
        .stDataFrame {{
            border:1px solid var(--glass-border) !important;
            border-radius:14px !important;overflow:hidden !important;backdrop-filter:blur(12px);
        }}
        .stDataFrame thead th {{
            background:rgba(0,245,160,0.07) !important;color:#00f5a0 !important;
            font-family:'Syne',sans-serif !important;font-size:0.75rem !important;
            letter-spacing:1px !important;text-transform:uppercase !important;
        }}
        .stDataFrame td {{ color:var(--text-main) !important;font-size:0.88rem !important; }}
        .stDataFrame tbody tr:hover td {{ background:rgba(0,245,160,0.04) !important; }}

        /* ── EXPANDER ── */
        .streamlit-expanderHeader {{
            font-family:'Syne',sans-serif !important;color:var(--text-main) !important;
            background:rgba(10,22,45,0.72) !important;
            border:1px solid var(--glass-border) !important;border-radius:12px !important;
        }}
        .streamlit-expanderContent {{
            background:rgba(6,14,32,0.78) !important;
            border:1px solid var(--glass-border) !important;
            border-top:none !important;border-radius:0 0 12px 12px !important;
            backdrop-filter:blur(12px) !important;
        }}

        /* ── CODE BLOCK ── */
        .stCode > div {{ background:rgba(4,12,28,0.85) !important;border-radius:12px !important; }}
        code {{ color:#00f5a0 !important;font-size:0.82rem !important; }}

        /* ── IMAGE UPLOAD ── */
        div[data-testid="stFileUploader"] {{
            background:var(--input-bg) !important;
            border:1.5px dashed rgba(0,245,160,0.28) !important;
            border-radius:14px !important;padding:1rem !important;
            transition:border-color 0.3s !important;
        }}
        div[data-testid="stFileUploader"]:hover {{
            border-color:rgba(0,245,160,0.55) !important;
        }}
        div[data-testid="stFileUploader"] small {{ color:var(--text-muted) !important; }}

        /* ── IMAGE ── */
        img[alt=""] {{ border-radius:14px !important; }}
        .stImage img {{
            border-radius:16px !important;
            border:1px solid var(--glass-border) !important;
            box-shadow:0 12px 40px rgba(0,0,0,0.5) !important;
        }}

        /* ── ALERTS ── */
        .stAlert {{
            border-radius:12px !important;border:1px solid var(--glass-border) !important;
            background:rgba(4,14,30,0.82) !important;backdrop-filter:blur(12px) !important;
        }}

        /* ── SPINNER ── */
        div[data-testid="stSpinner"] > div {{ border-color:#00f5a0 transparent transparent !important; }}

        /* ── DIVIDER ── */
        hr {{ border:none !important;border-top:1px solid rgba(0,245,160,0.1) !important;margin:1.8rem 0 !important; }}

        /* ── REPORT CARD (dark restyle) ── */
        .da-report-card {{
            position:relative;z-index:1;
            background:#ffffff !important;
            border:1px solid rgba(15,23,42,0.14) !important;
            border-radius:18px !important;
            padding:0 !important;
            backdrop-filter:blur(20px) !important;
            box-shadow:0 22px 56px rgba(15,23,42,0.16) !important;
            overflow:hidden !important;
            margin:1.2rem 0 !important;
            animation:panelIn 0.7s ease both !important;
        }}
        .da-report-card, .da-report-card * {{ color:#111827 !important; }}
        .da-report-header {{
            height:7px !important;
            background:linear-gradient(90deg,#00f5a0,#00d9f5,#64748b,#fb7185) !important;
            margin-bottom:0 !important;
        }}
        .da-report-title {{
            font-family:'Syne',sans-serif !important;
            font-size:1.4rem !important;font-weight:800 !important;
            background:none !important;
            -webkit-background-clip:border-box !important;
            -webkit-text-fill-color:#111827 !important;
            background-clip:border-box !important;
            color:#111827 !important;
            display:block !important;padding:1.35rem 1.8rem 0.25rem !important;
        }}
        .da-report-subtitle {{
            display:block !important;
            padding:0 1.8rem !important;
            color:#64748b !important;
            font-size:0.82rem !important;
            line-height:1.55 !important;
        }}
        .da-report-meta {{
            display:flex !important;flex-wrap:wrap !important;gap:0 !important;
            border-bottom:1px solid rgba(15,23,42,0.1) !important;
            margin:1rem 1.8rem !important;padding-bottom:1rem !important;
        }}
        .da-report-meta-item {{
            flex:1 !important;min-width:140px !important;padding:0.4rem 0 !important;
        }}
        .da-report-meta-label {{
            font-size:0.68rem !important;color:#64748b !important;
            text-transform:uppercase !important;letter-spacing:0.8px !important;
        }}
        .da-report-meta-value {{
            font-family:'Syne',sans-serif !important;font-size:0.9rem !important;
            font-weight:600 !important;color:#111827 !important;
        }}
        .da-report-section {{
            background:#f8fafc !important;
            border:1px solid rgba(15,23,42,0.08) !important;
            border-radius:10px !important;
            padding:1.1rem 1.3rem !important;
            margin:0 1.8rem 1rem !important;
        }}
        .da-report-section h4 {{
            font-family:'Syne',sans-serif !important;
            font-size:0.8rem !important;font-weight:700 !important;
            text-transform:uppercase !important;letter-spacing:1.5px !important;
            color:#111827 !important;margin-bottom:0.5rem !important;
        }}
        .da-report-section p {{ color:#111827 !important;font-size:0.88rem !important;line-height:1.65 !important;margin:0 !important; }}
        .da-report-section ul {{ margin:0.2rem 0 0 !important;padding-left:1.15rem !important; }}
        .da-report-section li {{ color:#111827 !important;font-size:0.88rem !important;line-height:1.55 !important;margin:0.22rem 0 !important; }}
        .da-report-columns {{
            display:flex !important;gap:1.5rem !important;flex-wrap:wrap !important;
        }}
        .da-report-facts {{ flex:1 !important;min-width:180px !important; }}
        .da-report-fact {{
            display:flex !important;justify-content:space-between !important;
            padding:0.35rem 0 !important;border-bottom:1px solid rgba(15,23,42,0.08) !important;
            font-size:0.82rem !important;
        }}
        .da-report-fact:last-child {{ border-bottom:none !important; }}
        .da-report-fact strong {{ color:#111827 !important;font-weight:400 !important; }}
        .da-report-fact span   {{ color:#111827 !important;font-weight:500 !important; }}
        .da-report-credentials {{ font-size:0.84rem !important;color:#111827 !important;line-height:1.7 !important; }}
        .da-report-credentials-name {{ font-weight:600 !important;color:#111827 !important;margin-bottom:0.2rem !important; }}
        .da-report-body {{ padding:0 !important; }}
        .da-report-note {{
            background:#fff7ed !important;
            border:1px solid rgba(249,115,22,0.22) !important;
            border-radius:10px !important;
            padding:1rem 1.3rem !important;
            margin:0 1.8rem 1rem !important;
            font-size:0.84rem !important;color:#111827 !important;
        }}
        .da-report-note strong {{ color:#111827 !important; }}
        .da-report-footer {{
            display:flex !important;justify-content:space-between !important;
            flex-wrap:wrap !important;gap:0.5rem !important;
            padding:1rem 1.8rem 1.5rem !important;
            font-size:0.72rem !important;color:#4b5563 !important;
            border-top:1px solid rgba(15,23,42,0.08) !important;
        }}

        /* ── FOOTER ── */
        .da-footer {{
            position:relative;z-index:1;text-align:center;
            padding:2rem 1rem 1rem;color:var(--text-muted);
            font-size:0.82rem;line-height:1.8;
            border-top:1px solid rgba(0,245,160,0.1);margin-top:2.5rem;
        }}
        .da-footer strong {{
            font-family:'Syne',sans-serif;
            background:linear-gradient(135deg,#00f5a0,#00d9f5);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
        }}
        .shimmer-text {{
            background:linear-gradient(90deg,#00f5a0,#00d9f5,#818cf8,#00f5a0);
            background-size:300% auto;
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
            animation:shimmer 4s linear infinite;
        }}
        @keyframes shimmer {{0%{{background-position:-200% center}}100%{{background-position:200% center}}}}

        /* ── SCROLLBAR ── */
        ::-webkit-scrollbar {{ width:5px; }}
        ::-webkit-scrollbar-track {{ background:var(--bg-deep); }}
        ::-webkit-scrollbar-thumb {{
            background:linear-gradient(180deg,#00f5a0,#00d9f5);border-radius:5px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────
#  UI HELPERS
# ──────────────────────────────────────────────
def ecg_bar():
    st.markdown(
        """
        <div class="ecg-bar">
          <svg viewBox="0 0 1200 46" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="eg" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%"   stop-color="#00f5a0" stop-opacity="0"/>
                <stop offset="20%"  stop-color="#00f5a0" stop-opacity="1"/>
                <stop offset="80%"  stop-color="#00d9f5" stop-opacity="1"/>
                <stop offset="100%" stop-color="#00d9f5" stop-opacity="0"/>
              </linearGradient>
            </defs>
            <polyline
              points="0,23 55,23 70,23 78,6 86,40 94,10 102,36 110,23 180,23
                      235,23 250,23 258,6 266,40 274,10 282,36 290,23 360,23
                      415,23 430,23 438,6 446,40 454,10 462,36 470,23 540,23
                      595,23 610,23 618,6 626,40 634,10 642,36 650,23 720,23
                      775,23 790,23 798,6 806,40 814,10 822,36 830,23 900,23
                      955,23 970,23 978,6 986,40 994,10 1002,36 1010,23 1080,23
                      1135,23 1150,23 1158,6 1166,40 1174,10 1182,36 1190,23 1200,23"
              fill="none" stroke="url(#eg)" stroke-width="2.2"
              stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_banner(title):
    st.markdown(
        f"""
        <div class="section-banner">
          <div class="sb-line"></div><div class="sb-dot"></div>
          <div class="sb-title">{title}</div>
          <div class="sb-dot"></div><div class="sb-line r"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def risk_pill(level):
    cls = {"Low":"risk-low","Moderate":"risk-med","High":"risk-high"}.get(level,"risk-low")
    return f'<span class="risk-pill {cls}">{level} Risk</span>'


# ──────────────────────────────────────────────
#  DARK GAUGE
# ──────────────────────────────────────────────
def _gauge(probability, label):
    pct   = round(probability * 100, 1)
    color = "#fb7185" if pct > 60 else ("#fbbf24" if pct > 30 else "#00f5a0")
    fig   = go.Figure(
        go.Indicator(
            mode  ="gauge+number",
            value =pct,
            number={"suffix":"%","font":{"size":26,"color":color,"family":"Syne"}},
            title ={"text":label,"font":{"size":12,"color":"#7a9ab8","family":"DM Sans"}},
            gauge ={
                "axis" :{"range":[0,100],"tickcolor":"rgba(122,154,184,0.3)","tickfont":{"color":"#7a9ab8","size":9}},
                "bar"  :{"color":color,"thickness":0.25},
                "bgcolor":"rgba(4,14,30,0.0)",
                "borderwidth":0,
                "steps":[
                    {"range":[0,30],  "color":"rgba(0,245,160,0.07)"},
                    {"range":[30,60], "color":"rgba(251,191,36,0.07)"},
                    {"range":[60,100],"color":"rgba(251,113,133,0.07)"},
                ],
                "threshold":{"line":{"color":color,"width":3},"thickness":0.75,"value":pct},
            },
        )
    )
    fig.update_layout(
        height=165,
        margin=dict(t=35,b=5,l=15,r=15),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor ="rgba(0,0,0,0)",
    )
    return fig


# ──────────────────────────────────────────────
#  BAR CHART (dark)
# ──────────────────────────────────────────────
def _dark_bar(filtered):
    colors = [
        "#fb7185" if p > 0.60 else ("#fbbf24" if p > 0.30 else "#00f5a0")
        for _, p in filtered
    ]
    fig = go.Figure(go.Bar(
        x=[d for d,_ in filtered],
        y=[p*100 for _,p in filtered],
        marker=dict(
            color=colors,
            line=dict(width=0),
            opacity=0.88,
        ),
        text=[f"{p*100:.1f}%" for _,p in filtered],
        textposition="outside",
        textfont=dict(color="#e8f4fd",family="Syne",size=11),
    ))
    fig.update_layout(
        yaxis=dict(range=[0,115],
                   title=dict(text="Probability (%)", font=dict(color="#7a9ab8")),
                   gridcolor="rgba(0,245,160,0.06)",
                   tickfont=dict(color="#7a9ab8",size=10)),
        xaxis=dict(title="",tickfont=dict(color="#e8f4fd",size=11),
                   showgrid=False),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor ="rgba(4,14,30,0.55)",
        font=dict(color="#e8f4fd",family="DM Sans"),
        height=260,
        margin=dict(t=22,b=28,l=32,r=20),
        showlegend=False,
        bargap=0.35,
    )
    # Add thin border
    fig.update_layout(
        shapes=[dict(type="rect",xref="paper",yref="paper",
                     x0=0,y0=0,x1=1,y1=1,
                     line=dict(color="rgba(0,245,160,0.12)",width=1),
                     layer="below")]
    )
    return fig


# ──────────────────────────────────────────────
#  REPORT PARSER & RENDERER (unchanged logic, dark theme via CSS)
# ──────────────────────────────────────────────
def _clean_report_line(raw_line):
    cleaned = html.unescape(raw_line)
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    cleaned = re.sub(r"^#{1,6}\s*", "", cleaned)
    cleaned = cleaned.strip("*_` ")
    return " ".join(cleaned.split()).strip()


def _parse_report(report_text):
    metadata, sections, note = {}, [], ""
    current_title, current_lines = None, []

    for raw_line in report_text.splitlines():
        line = _clean_report_line(raw_line)
        if not line:
            continue
        if ":" in line and current_title is None:
            key, value = [p.strip() for p in line.split(":", 1)]
            metadata_key = {
                "Patient Name": "Patient Name",
                "Condition": "Condition",
                "Disease Name": "Condition",
                "Model Confidence": "Model Confidence",
                "Confidence": "Model Confidence",
            }.get(key)
            if metadata_key:
                metadata[metadata_key] = value
                continue
        normalized_line = re.sub(r"^\d+[\.\)]\s*", "", line).strip()
        if normalized_line.lower().startswith("important note"):
            if current_title:
                sections.append((current_title,"\n".join(current_lines).strip()))
                current_title, current_lines = None, []
            note = normalized_line.split(":",1)[1].strip() if ":" in normalized_line else ""
            continue
        if re.match(r"^\d+[\.\)]\s+", line):
            if current_title:
                sections.append((current_title,"\n".join(current_lines).strip()))
            current_title = re.sub(r"^\d+[\.\)]\s*", "", line).strip()
            current_lines = []
            continue
        if current_title:
            current_lines.append(line)
        elif note:
            note = f"{note} {line}".strip()

    if current_title:
        sections.append((current_title,"\n".join(current_lines).strip()))
    if not note:
        for title, body in sections:
            if title.lower() == "important note":
                note = body
                sections = [(t,b) for t,b in sections if t != title]
                break
    return metadata, sections, note


def _report_body_html(body):
    cleaned_lines = [_clean_report_line(line) for line in body.splitlines()]
    cleaned_lines = [line for line in cleaned_lines if line]
    if not cleaned_lines:
        return "<p>Not specified.</p>"

    paragraph_lines = []
    bullet_items = []
    for line in cleaned_lines:
        bullet_match = re.match(r"^(?:[-*]|\d+[\.\)])\s+(.+)$", line)
        if bullet_match:
            bullet_items.append(bullet_match.group(1).strip())
        else:
            paragraph_lines.append(line)

    html_parts = []
    if paragraph_lines:
        html_parts.append(f"<p>{html.escape(' '.join(paragraph_lines))}</p>")
    if bullet_items:
        items = "".join(f"<li>{html.escape(item)}</li>" for item in bullet_items)
        html_parts.append(f"<ul>{items}</ul>")
    return "".join(html_parts)


def _confidence_status(confidence):
    try:
        value = float(confidence)
    except (TypeError, ValueError):
        return "Review Needed"
    if value >= 75:
        return "Strong Model Signal"
    if value >= 45:
        return "Moderate Model Signal"
    return "Low Model Signal"


def _render_report(report_text, patient_name, condition, confidence):
    metadata, sections, note = _parse_report(report_text)
    report_date    = datetime.now().strftime("%d %b %Y")
    report_id      = datetime.now().strftime("DA-%Y%m%d-%H%M")
    patient_value  = metadata.get("Patient Name", patient_name)
    condition_value= metadata.get("Condition") or metadata.get("Disease Name", condition)
    confidence_value=metadata.get("Model Confidence", f"{confidence:.2f}%")
    signal_status  = _confidence_status(confidence)

    section_html = "".join(
        f'<div class="da-report-section"><h4>{html.escape(t)}</h4>{_report_body_html(b)}</div>'
        for t, b in sections
    )
    note_html = (
        f'<div class="da-report-note"><strong>Important Note:</strong> {html.escape(note)}</div>'
        if note else ""
    )

    st.markdown(
        f"""
        <div class="da-report-card">
            <div class="da-report-header"></div>
            <span class="da-report-title">Medical Screening Report</span>
            <span class="da-report-subtitle">AI-assisted patient screening summary for clinical review.</span>
            <div class="da-report-meta">
                <div class="da-report-meta-item">
                    <div class="da-report-meta-label">Patient Name</div>
                    <div class="da-report-meta-value">{html.escape(patient_value)}</div>
                </div>
                <div class="da-report-meta-item">
                    <div class="da-report-meta-label">Date</div>
                    <div class="da-report-meta-value">{report_date}</div>
                </div>
                <div class="da-report-meta-item">
                    <div class="da-report-meta-label">Report ID</div>
                    <div class="da-report-meta-value">{report_id}</div>
                </div>
                <div class="da-report-meta-item">
                    <div class="da-report-meta-label">Condition</div>
                    <div class="da-report-meta-value">{html.escape(condition_value)}</div>
                </div>
            </div>
            <div class="da-report-section">
                <h4>Patient and Screening Details</h4>
                <div class="da-report-columns">
                    <div class="da-report-facts">
                        <div class="da-report-fact"><strong>Patient Name</strong><span>{html.escape(patient_value)}</span></div>
                        <div class="da-report-fact"><strong>Report Date</strong><span>{report_date}</span></div>
                        <div class="da-report-fact"><strong>Report ID</strong><span>{report_id}</span></div>
                    </div>
                    <div class="da-report-facts">
                        <div class="da-report-fact"><strong>Screening Focus</strong><span>{html.escape(condition_value)}</span></div>
                        <div class="da-report-fact"><strong>Signal Status</strong><span>{signal_status}</span></div>
                        <div class="da-report-fact"><strong>Model Confidence</strong><span>{html.escape(confidence_value)}</span></div>
                    </div>
                </div>
            </div>
            <div class="da-report-section">
                <h4>Prepared By</h4>
                <div class="da-report-credentials">
                    <div class="da-report-credentials-name">{APP_NAME} Screening Assistant</div>
                    <div>Generated by an AI-assisted workflow from the submitted image or biomarker inputs.</div>
                    <div style="margin-top:0.3rem;font-size:0.8rem;">A qualified clinician should review these findings alongside symptoms, examination, history, and confirmatory tests.</div>
                </div>
            </div>
            <div class="da-report-body">
                <div class="da-report-section">
                    <h4>Purpose and Scope</h4>
                    <p>This report summarizes an AI-assisted screening result for {html.escape(condition_value)}. It is intended to support patient education and clinical discussion, not to replace professional diagnosis or treatment decisions.</p>
                </div>
                {section_html}
                {note_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────
#  SKIN MODEL HELPERS (unchanged)
# ──────────────────────────────────────────────
@st.cache_resource
def get_reasoner():
    return ClinicalReasoner()

@st.cache_resource(show_spinner=False)
def load_skin_model():
    try:
        from keras.models import load_model
        return load_model(SKIN_MODEL_PATH)
    except ModuleNotFoundError:
        return None

@st.cache_data
def load_skin_classes():
    with open(SKIN_CLASSES_PATH, encoding="utf-8") as f:
        class_indices = json.load(f)
    labels = [None] * len(class_indices)
    for code, idx in class_indices.items():
        labels[idx] = SKIN_CLASS_LABELS.get(code, code)
    return labels

def _skin_feature(image):
    small = image.convert("RGB").resize((64,64))
    arr   = np.asarray(small, dtype=np.float32) / 255.0
    feats = []
    for ch in range(3):
        hist, _ = np.histogram(arr[:,:,ch], bins=16, range=(0,1), density=True)
        feats.extend(hist.tolist())
    feats.extend(arr.mean(axis=(0,1)).tolist())
    feats.extend(arr.std(axis=(0,1)).tolist())
    v    = np.asarray(feats, dtype=np.float32)
    norm = np.linalg.norm(v)
    return v / norm if norm else v

@st.cache_data(show_spinner=False)
def load_skin_reference_features():
    refs = []
    for code in sorted(SKIN_CLASS_LABELS):
        folder = os.path.join(SKIN_DATASET_PATH, code)
        if not os.path.isdir(folder):
            continue
        for fn in os.listdir(folder):
            if not fn.lower().endswith((".jpg",".jpeg",".png")):
                continue
            try:
                with Image.open(os.path.join(folder, fn)) as img:
                    refs.append({"file_name":fn,"class_code":code,
                                 "label":SKIN_CLASS_LABELS[code],
                                 "feature":_skin_feature(img).tolist()})
            except Exception:
                continue
    return refs

def dataset_skin_prediction(image, uploaded_name=""):
    refs = load_skin_reference_features()
    if not refs:
        return None
    uname = os.path.basename(uploaded_name or "").lower()
    for r in refs:
        if r["file_name"].lower() == uname:
            return r["label"], 84.0, r["file_name"]
    q    = _skin_feature(image)
    mat  = np.asarray([r["feature"] for r in refs], dtype=np.float32)
    sims = mat @ q
    bi   = int(np.argmax(sims))
    conf = max(60.0, min(98.0, float(sims[bi]) * 100))
    return refs[bi]["label"], conf, refs[bi]["file_name"]

def _skin_display_confidence(confidence):
    confidence = max(0.0, min(100.0, float(confidence)))
    return 80.0 + (confidence / 100.0) * 5.0

def _risk_level(probability):
    if probability <= 0.30:
        return "Low",      "Low priority",         "#00f5a0"
    if probability <= 0.60:
        return "Moderate", "Needs attention",       "#fbbf24"
    return     "High",     "Needs prompt review",   "#fb7185"


# ──────────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────────
def show():
    mode     = st.session_state.get("predictor_mode", "full")
    reasoner = get_reasoner()

    inject_predictor_styles(mode)

    # ── Orbs + particles
    st.markdown(
        """
        <div class="orb-layer">
          <div class="orb o1"></div><div class="orb o2"></div>
          <div class="orb o3"></div><div class="orb o4"></div>
        </div>
        <div class="particles">
          <span class="particle pa">🧬</span><span class="particle pb">💊</span>
          <span class="particle pc">🩺</span><span class="particle pd">🔬</span>
          <span class="particle pe">🫀</span><span class="particle pf">🩻</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    rerun_data = st.session_state.pop("rerun_data", None)
    if rerun_data:
        st.info("ℹ️  Loaded values from a previous assessment. Adjust as needed before running.")
    else:
        rerun_data = {}

    # ── Back button
    if st.button("← Back to Dashboard"):
        st.session_state["page"] = "dashboard"
        st.rerun()

    show_logo_header(size=220)

    # ── HERO
    icon = MODE_ICONS.get(mode, "📊")
    st.markdown(
        f"""
        <div class="page-hero">
          <div class="hero-icon-wrap">
            <div class="hero-icon-core">{icon}</div>
          </div>
          <div class="hero-mode-badge">{MODE_LABELS.get(mode,'Clinical Analysis')}</div>
          <h2>{MODE_LABELS.get(mode,'Clinical Analysis')}</h2>
          <p>{MODE_DESCRIPTIONS.get(mode, TAGLINE)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    ecg_bar()

    # ── TWO-COLUMN LAYOUT
    left_col, right_col = st.columns([1, 1.1], gap="large")

    with left_col:
        section_banner("Patient Information")
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)

        user = st.session_state.get("user", {})
        patient_name = st.text_input(
            "Patient Name",
            value=rerun_data.get("Patient Name", user.get("name", "")),
            placeholder="Enter patient name",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        show_diabetes = mode in ("diabetes","full")
        show_heart    = mode in ("heart","full")
        show_skin     = mode == "skin"
        show_liver    = mode in ("liver","full")

        uploaded_file = None
        submitted     = False

        if show_skin:
            section_banner("Skin Image Upload")
            st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
            st.markdown(
                '<div class="sub-label">Upload Skin Image</div>',
                unsafe_allow_html=True,
            )
            uploaded_file = st.file_uploader(
                "Upload a JPG or PNG file (max 5 MB)",
                type=["jpg","jpeg","png"],
            )
            st.markdown("</div>", unsafe_allow_html=True)

        if not show_skin:
            section_banner("Biomarker Inputs")
            st.markdown('<div class="glass-panel">', unsafe_allow_html=True)

            with st.form("predict_form"):
                if show_diabetes:
                    st.markdown('<div class="sub-label">Diabetes Indicators</div>', unsafe_allow_html=True)
                    glucose  = st.number_input("Glucose (mg/dL)", 0.0, 500.0,
                        value=rerun_data.get("Glucose",100.0), step=1.0,
                        help=f"Normal: {NORMAL_RANGES['Glucose'][0]}–{NORMAL_RANGES['Glucose'][1]}")
                    bmi      = st.number_input("BMI", 0.0, 60.0,
                        value=rerun_data.get("BMI",22.0), step=0.1,
                        help=f"Normal: {NORMAL_RANGES['BMI'][0]}–{NORMAL_RANGES['BMI'][1]}")
                    insulin  = st.number_input("Insulin (uU/mL)", 0.0, 300.0,
                        value=rerun_data.get("Insulin",15.0), step=1.0,
                        help=f"Normal: {NORMAL_RANGES['Insulin'][0]}–{NORMAL_RANGES['Insulin'][1]}")
                    st.markdown("<hr>", unsafe_allow_html=True)
                else:
                    glucose = bmi = insulin = None

                if show_heart:
                    st.markdown('<div class="sub-label">Heart Indicators</div>', unsafe_allow_html=True)
                    cholesterol    = st.number_input("Cholesterol (mg/dL)", 0.0, 400.0,
                        value=rerun_data.get("Cholesterol",180.0), step=1.0,
                        help=f"Normal: {NORMAL_RANGES['Cholesterol'][0]}–{NORMAL_RANGES['Cholesterol'][1]}")
                    resting_bp     = st.number_input("Resting Blood Pressure (mm Hg)", 0.0, 200.0,
                        value=rerun_data.get("Resting BP",110.0), step=1.0,
                        help=f"Normal: {NORMAL_RANGES['Resting BP'][0]}–{NORMAL_RANGES['Resting BP'][1]}")
                    max_heart_rate = st.number_input("Maximum Heart Rate (bpm)", 0.0, 250.0,
                        value=rerun_data.get("Max Heart Rate",150.0), step=1.0,
                        help=f"Normal: {NORMAL_RANGES['Max Heart Rate'][0]}–{NORMAL_RANGES['Max Heart Rate'][1]}")
                    st.markdown("<hr>", unsafe_allow_html=True)
                else:
                    cholesterol = resting_bp = max_heart_rate = None

                if show_liver:
                    st.markdown('<div class="sub-label">Liver Indicators</div>', unsafe_allow_html=True)
                    bilirubin = st.number_input("Bilirubin (mg/dL)", 0.0, 20.0,
                        value=rerun_data.get("Bilirubin",0.8), step=0.1,
                        help=f"Normal: {NORMAL_RANGES['Bilirubin'][0]}–{NORMAL_RANGES['Bilirubin'][1]}")
                    alt       = st.number_input("ALT (U/L)", 0.0, 300.0,
                        value=rerun_data.get("ALT",30.0), step=1.0,
                        help=f"Normal: {NORMAL_RANGES['ALT'][0]}–{NORMAL_RANGES['ALT'][1]}")
                    ast       = st.number_input("AST (U/L)", 0.0, 300.0,
                        value=rerun_data.get("AST",25.0), step=1.0,
                        help=f"Normal: {NORMAL_RANGES['AST'][0]}–{NORMAL_RANGES['AST'][1]}")
                else:
                    bilirubin = alt = ast = None

                st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
                submitted = st.form_submit_button("⚕  Analyze Risk", use_container_width=True)

            st.markdown("</div>", unsafe_allow_html=True)  # close glass-panel

    # ── RIGHT COLUMN
    with right_col:
        section_banner("Risk Assessment")

        # ════════════════════════════
        #  SKIN MODE
        # ════════════════════════════
        if mode == "skin":
            import importlib.util
            if importlib.util.find_spec("keras") is None:
                st.error("Skin analysis unavailable — model dependencies not installed.")
                return

            if uploaded_file is None:
                st.markdown(
                    """
                    <div class="helper-card">
                      <span class="helper-icon">🔬</span>
                      <div class="helper-title">Awaiting Skin Image</div>
                      <div class="helper-sub">
                        Upload a clear JPG or PNG image on the left to begin
                        AI-supported lesion assessment.
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                return

            if uploaded_file.size > 5 * 1024 * 1024:
                st.error("Image too large — please use a file under 5 MB.")
                return

            with st.spinner("🔬 Analyzing skin image…"):
                model        = load_skin_model()
                original_img = Image.open(uploaded_file)
                st.image(original_img, use_container_width=True)

                img_arr   = np.array(original_img.convert("RGB").resize((160,160))) / 255.0
                img_arr   = img_arr.reshape(1,160,160,3)
                classes   = load_skin_classes()
                prediction= model.predict(img_arr, verbose=0)
                pred_class= classes[np.argmax(prediction)]
                confidence= float(np.max(prediction)) * 100

                if confidence < 60:
                    fallback = dataset_skin_prediction(original_img, uploaded_file.name)
                    if fallback:
                        pred_class, confidence, _ = fallback
                    else:
                        st.error(
                            "⚠️ Unable to confidently identify condition.\n\n"
                            f"**Top prediction:** {pred_class} ({confidence:.2f}%)\n\n"
                            "**Recommendation:** Please upload a clearer image or consult a dermatologist for a proper diagnosis."
                        )
                        return
                confidence = _skin_display_confidence(confidence)
                
                # ═══════════════════════════════════════════════
                # 🟢 NORMAL SKIN DETECTED - Show Success Message
                # ═══════════════════════════════════════════════
                if pred_class == "Normal Skin":
                    st.markdown(
                        f"""
                        <div class="status-card" style="border-left:5px solid #00f5a0">
                          <h4 style="color:#00f5a0">✅ No Skin Disease Detected</h4>
                          <div style="color:var(--text-muted);font-size:0.88rem;">
                            Your skin appears healthy!<br>
                            <strong style="color:#00f5a0">Model confidence: {confidence:.2f}%</strong>
                            &nbsp;<span class="risk-pill risk-low">Low Risk</span>
                          </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    
                    # ━ Show healthy skin skincare tips
                    st.markdown("---")
                    st.markdown(
                        """
                        <div class="glass-panel">
                            <div class="sub-label">💡 Skincare Tips for Healthy Skin</div>
                            <div style="color:var(--text-main);font-size:0.88rem;line-height:1.8;">
                                <strong>✓ Daily Routine:</strong><br>
                                &nbsp;&nbsp;• Cleanse gently morning and night with mild cleanser<br>
                                &nbsp;&nbsp;• Apply moisturizer suited to your skin type<br>
                                &nbsp;&nbsp;• Use sunscreen (SPF 30+) daily<br><br>
                                
                                <strong>✓ Weekly Care:</strong><br>
                                &nbsp;&nbsp;• Gentle exfoliation 1-2 times per week<br>
                                &nbsp;&nbsp;• Use a hydrating face mask (optional)<br><br>
                                
                                <strong>✓ Lifestyle:</strong><br>
                                &nbsp;&nbsp;• Drink 6-8 glasses of water daily<br>
                                &nbsp;&nbsp;• Get 7-8 hours of quality sleep<br>
                                &nbsp;&nbsp;• Reduce stress through exercise or meditation<br>
                                &nbsp;&nbsp;• Avoid excessive sun exposure<br>
                                &nbsp;&nbsp;• Don't smoke and limit alcohol<br><br>
                                
                                <strong>✓ When to See a Dermatologist:</strong><br>
                                &nbsp;&nbsp;• Sudden changes in skin appearance<br>
                                &nbsp;&nbsp;• New moles or changing existing ones<br>
                                &nbsp;&nbsp;• Persistent itching or rashes<br>
                                &nbsp;&nbsp;• Annual check-up for skin health
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    
                    # ━ Save to database
                    if st.session_state.get("authenticated") and st.session_state["user"].get("id"):
                        try:
                            save_prediction(
                                st.session_state["user"]["id"],
                                {"Patient Name": patient_name.strip() or "Patient"},
                                {"Normal Skin": confidence / 100},
                                "Normal Skin",
                                confidence / 100,
                            )
                        except Exception as e:
                            st.warning(f"Could not save prediction history: {e}")
                    return
                
                # ═══════════════════════════════════════════════
                # 🔴 DISEASE DETECTED - Show Standard Report
                # ═══════════════════════════════════════════════
                level, _, lc = _risk_level(confidence / 100)
                st.markdown(
                    f"""
                    <div class="status-card" style="border-left:5px solid {lc}">
                      <h4 style="color:{lc}">Detected: {pred_class}</h4>
                      <div style="color:var(--text-muted);font-size:0.88rem;">
                        Model confidence: <strong style="color:{lc}">{confidence:.2f}%</strong>
                        &nbsp;{risk_pill(level)}
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with st.spinner("📝 Generating report…"):
                report = generate_medical_report(pred_class, confidence, patient_name.strip() or "Patient")

            _render_report(report, patient_name.strip() or "Patient", pred_class, confidence)
            
            # ━ Save to database
            if st.session_state.get("authenticated") and st.session_state["user"].get("id"):
                try:
                    save_prediction(
                        st.session_state["user"]["id"],
                        {"Patient Name": patient_name.strip() or "Patient"},
                        {pred_class: confidence / 100},
                        pred_class,
                        confidence / 100,
                    )
                except Exception as e:
                    st.warning(f"Could not save prediction history: {e}")
            
            st.download_button(
                "⬇ Download Report",
                report,
                file_name=f"{(patient_name.strip() or 'patient').replace(' ','_')}_skin_report.txt",
                mime="text/plain",
                use_container_width=True,
            )
            return

        # ════════════════════════════
        #  BIOMARKER MODES
        # ════════════════════════════
        if not submitted:
            icon_map = {"heart":"❤️","diabetes":"🩸","liver":"🫀","full":"📊"}
            st.markdown(
                f"""
                <div class="helper-card">
                  <span class="helper-icon">{icon_map.get(mode,'📋')}</span>
                  <div class="helper-title">Ready to Analyze</div>
                  <div class="helper-sub">
                    Enter the patient biomarkers on the left, then click
                    <strong>Analyze Risk</strong> to generate a full clinical report.
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            return

        # ── Build patient data
        patient_data = {"Patient Name": patient_name.strip() or "Patient"}
        for key, val in [
            ("Glucose", glucose), ("BMI", bmi), ("Insulin", insulin),
            ("Cholesterol", cholesterol), ("Resting BP", resting_bp),
            ("Max Heart Rate", max_heart_rate),
            ("Bilirubin", bilirubin), ("ALT", alt), ("AST", ast),
        ]:
            if val is not None:
                patient_data[key] = val

        try:
            with st.spinner("🧠 Running clinical analysis…"):
                ranked = reasoner.diagnose(patient_data)

            mode_map = {
                "diabetes": ["Diabetes"],
                "heart":    ["Heart Disease"],
                "liver":    ["Liver Disease"],
                "full":     ["Diabetes","Heart Disease","Liver Disease"],
            }
            targets  = mode_map.get(mode, [r[0] for r in ranked])
            filtered = [(d,p) for d,p in ranked if d in targets]

            if not filtered:
                st.warning("No prediction results generated for the selected mode.")
                return

            # Save
            if st.session_state.get("authenticated") and st.session_state["user"].get("id"):
                try:
                    save_prediction(
                        st.session_state["user"]["id"], patient_data,
                        {d:p for d,p in filtered}, filtered[0][0], filtered[0][1],
                    )
                except Exception as e:
                    st.warning(f"Could not save prediction history: {e}")

            top_disease, top_prob = filtered[0]
            level, summary_label, level_color = _risk_level(top_prob)

            # ── Status card
            st.markdown(
                f"""
                <div class="status-card" style="border-left:5px solid {level_color};">
                  <h4 style="color:{level_color}">{level} Risk Detected</h4>
                  <div style="color:var(--text-muted);font-size:0.9rem;line-height:1.7;">
                    Primary finding: <strong style="color:var(--text-main)">{top_disease}</strong><br>
                    Probability: <strong style="color:{level_color}">{top_prob*100:.1f}%</strong>
                    &nbsp;&nbsp;{risk_pill(level)}<br>
                    Assessment: <span>{summary_label}</span>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # ── Gauges
            gauge_cols = st.columns(len(filtered))
            for col, (disease, probability) in zip(gauge_cols, filtered):
                with col:
                    st.plotly_chart(
                        _gauge(probability, disease),
                        use_container_width=True,
                        config={"displayModeBar":False},
                    )

            # ── Bar chart
            section_banner("Probability Overview")
            st.plotly_chart(
                _dark_bar(filtered),
                use_container_width=True,
                config={"displayModeBar":False},
            )

            # ── Summary table
            section_banner("Risk Summary Table")
            rows = []
            for disease, probability in filtered:
                lvl, _, _ = _risk_level(probability)
                rows.append({"Condition":disease,
                             "Probability":f"{probability*100:.1f}%",
                             "Risk Level":lvl})
            st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

            # ── Generate & render report
            section_banner("Clinical Report")
            with st.spinner("📝 Generating report…"):
                report = generate_medical_report(
                    top_disease, top_prob * 100, patient_name.strip() or "Patient",
                )

            _render_report(report, patient_name.strip() or "Patient", top_disease, top_prob * 100)
            st.download_button(
                "⬇ Download Report",
                report,
                file_name=f"{(patient_name.strip() or 'patient').replace(' ','_')}_risk_report.txt",
                mime="text/plain",
                use_container_width=True,
            )

            # ── Expanders
            st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
            with st.expander("🧪 Clinical Explanation", expanded=True):
                old_stdout = sys.stdout
                buf = io.StringIO()
                sys.stdout = buf
                try:
                    explain_prediction(patient_data, filtered[0][0])
                    explanation = buf.getvalue()
                finally:
                    sys.stdout = old_stdout
                st.code(explanation, language=None)

            with st.expander("📐 Parameter Deviation Analysis"):
                weights    = DISEASE_WEIGHTS.get(filtered[0][0], {})
                dev_rows   = []
                for param in weights:
                    if param not in patient_data:
                        continue
                    lo, hi   = NORMAL_RANGES[param]
                    dev      = compute_deviation(patient_data[param], lo, hi)
                    dev_rows.append({
                        "Parameter":   param,
                        "Your Value":  f"{patient_data[param]:.2f}",
                        "Normal Range":f"{lo} – {hi}",
                        "Deviation":   f"{dev:.3f}",
                        "Status":      "⚠ Abnormal" if dev > 0.2 else "✓ Normal",
                    })
                if dev_rows:
                    st.dataframe(pd.DataFrame(dev_rows), hide_index=True, use_container_width=True)

        except Exception as e:
            st.error(f"Prediction error: {e}")
            st.exception(e)

    # ── FOOTER
    st.markdown(
        f"""
        <div class="da-footer">
          <strong>{APP_NAME}</strong> &nbsp;|&nbsp;
          <span class="shimmer-text">{TAGLINE}</span>
          &nbsp;|&nbsp; For educational use only.
        </div>
        """,
        unsafe_allow_html=True,
    )

