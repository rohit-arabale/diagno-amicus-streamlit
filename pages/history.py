import os
import sys

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from components.header import show_logo_header
from config.branding import APP_NAME, TAGLINE
from database.db_manager import list_predictions
from medical_knowledge import NORMAL_RANGES


# ──────────────────────────────────────────────
#  INJECT STYLES
# ──────────────────────────────────────────────
def inject_history_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

        :root {
            --bg-deep:      #04101f;
            --bg-card:      rgba(6,18,38,0.82);
            --accent-g:     #00f5a0;
            --accent-b:     #00d9f5;
            --accent-p:     #818cf8;
            --accent-r:     #fb7185;
            --accent-y:     #fbbf24;
            --text-main:    #e8f4fd;
            --text-muted:   #7a9ab8;
            --glass-border: rgba(0,245,160,0.16);
            --input-bg:     rgba(4,14,30,0.7);
        }

        /* ── APP SHELL ── */
        .stApp {
            background: var(--bg-deep) !important;
            font-family: 'DM Sans', sans-serif !important;
            color: var(--text-main) !important;
        }
        .stApp > header { display: none !important; }
        .block-container { padding-top: 0 !important; max-width: 1200px !important; }

        /* ── ANIMATED BACKGROUND ── */
        .stApp::before {
            content: '';
            position: fixed; inset: 0; z-index: 0;
            background:
                radial-gradient(ellipse 75% 55% at 10% 30%, rgba(0,245,160,0.09) 0%, transparent 55%),
                radial-gradient(ellipse 60% 50% at 90% 15%, rgba(0,217,245,0.08) 0%, transparent 50%),
                radial-gradient(ellipse 50% 65% at 70% 90%, rgba(129,140,248,0.07) 0%, transparent 55%),
                radial-gradient(ellipse 40% 45% at 30% 85%, rgba(251,161,36,0.05) 0%, transparent 50%),
                linear-gradient(145deg, #04101f 0%, #060f1e 50%, #050d1b 100%);
            animation: bgPulse 14s ease-in-out infinite alternate;
            pointer-events: none;
        }
        @keyframes bgPulse {
            0%   { filter: hue-rotate(0deg)  brightness(1); }
            100% { filter: hue-rotate(18deg) brightness(1.05); }
        }

        /* ── GRID TEXTURE ── */
        .stApp::after {
            content: '';
            position: fixed; inset: 0; z-index: 0;
            background-image:
                linear-gradient(rgba(0,245,160,0.025) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0,245,160,0.025) 1px, transparent 1px);
            background-size: 48px 48px;
            pointer-events: none;
            animation: gridSlide 35s linear infinite;
        }
        @keyframes gridSlide {
            from { background-position: 0 0; }
            to   { background-position: 48px 48px; }
        }

        /* ── FLOATING ORBS ── */
        .orb-layer {
            position: fixed; inset: 0; z-index: 0;
            pointer-events: none; overflow: hidden;
        }
        .orb {
            position: absolute; border-radius: 50%;
            filter: blur(90px); opacity: 0.18;
            animation: orbFloat linear infinite;
        }
        .o1{width:400px;height:400px;background:#00f5a0;left:-130px;top:5%; animation-duration:26s;}
        .o2{width:320px;height:320px;background:#00d9f5;right:-90px;top:45%;animation-duration:32s;animation-delay:-10s;}
        .o3{width:260px;height:260px;background:#818cf8;left:42%;top:75%;animation-duration:22s;animation-delay:-6s;}
        .o4{width:220px;height:220px;background:#fbbf24;right:22%;top:2%; animation-duration:38s;animation-delay:-16s;}
        @keyframes orbFloat {
            0%  {transform:translateY(0) scale(1);}
            35% {transform:translateY(-55px) scale(1.07);}
            70% {transform:translateY(28px) scale(0.94);}
            100%{transform:translateY(0) scale(1);}
        }

        /* ── FLOATING PARTICLES ── */
        .particles {
            position: fixed; inset: 0; z-index: 0; pointer-events: none;
        }
        .particle {
            position: absolute; font-size: 1.3rem; opacity: 0;
            animation: pFloat linear infinite;
            filter: drop-shadow(0 0 8px rgba(0,245,160,0.5));
        }
        .pa{left:6%; top:18%;animation-duration:20s;animation-delay:0s;}
        .pb{left:88%;top:32%;animation-duration:24s;animation-delay:-7s;}
        .pc{left:18%;top:68%;animation-duration:17s;animation-delay:-3s;}
        .pd{left:78%;top:78%;animation-duration:28s;animation-delay:-12s;}
        .pe{left:48%;top:8%; animation-duration:22s;animation-delay:-9s;}
        .pf{left:32%;top:90%;animation-duration:15s;animation-delay:-2s;}
        @keyframes pFloat {
            0%  {opacity:0;transform:translateY(0) rotate(0deg) scale(0.8);}
            10% {opacity:0.45;}
            50% {opacity:0.25;transform:translateY(-130px) rotate(180deg) scale(1.1);}
            90% {opacity:0.45;}
            100%{opacity:0;transform:translateY(-260px) rotate(360deg) scale(0.8);}
        }

        /* ── PAGE HERO ── */
        .page-hero {
            position: relative; z-index: 1;
            text-align: center;
            padding: 3.2rem 2rem 1.8rem;
            animation: heroIn 0.9s ease both;
        }
        @keyframes heroIn {
            from{opacity:0;transform:translateY(-22px);}
            to{opacity:1;transform:translateY(0);}
        }
        .page-hero h2 {
            font-family: 'Syne', sans-serif !important;
            font-size: 2.8rem !important;
            font-weight: 800 !important;
            background: linear-gradient(135deg, #00f5a0, #00d9f5, #818cf8);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem !important;
            letter-spacing: -1px;
        }
        .page-hero p {
            font-size: 1.05rem !important;
            color: var(--text-muted) !important;
            font-weight: 300 !important;
            max-width: 520px; margin: 0 auto;
            line-height: 1.6;
        }

        /* ── PULSE ICON ── */
        .hero-icon {
            display: flex; justify-content: center; margin-bottom: 1rem;
        }
        .hero-icon-core {
            width: 58px; height: 58px; border-radius: 50%;
            background: linear-gradient(135deg,#00f5a0,#00d9f5);
            display: flex; align-items: center; justify-content: center;
            font-size: 1.7rem;
            animation: iconPulse 2.6s ease-in-out infinite;
            box-shadow: 0 0 0 0 rgba(0,245,160,0.5);
        }
        @keyframes iconPulse {
            0%,100%{box-shadow:0 0 0 0 rgba(0,245,160,0.5);}
            50%    {box-shadow:0 0 0 20px rgba(0,245,160,0);}
        }

        /* ── ECG BAR ── */
        .ecg-bar {
            position: relative; z-index: 1;
            width: 100%; height: 48px; overflow: hidden; margin: 0.8rem 0 1.6rem;
        }
        .ecg-bar svg { position: absolute; animation: ecgScroll 3s linear infinite; width: 200%; }
        @keyframes ecgScroll {
            from{transform:translateX(0);}
            to{transform:translateX(-50%);}
        }

        /* ── SUMMARY STAT STRIP ── */
        .stat-strip {
            position: relative; z-index: 1;
            display: flex; gap: 1px;
            background: var(--glass-border);
            border-radius: 16px; overflow: hidden;
            margin-bottom: 2.2rem;
            backdrop-filter: blur(12px);
            animation: stripIn 0.8s ease 0.3s both;
        }
        @keyframes stripIn {
            from{opacity:0;transform:scaleX(0.93);}
            to{opacity:1;transform:scaleX(1);}
        }
        .stat-cell {
            flex:1; background:rgba(10,22,45,0.72);
            padding: 1rem 0.5rem; text-align: center;
            transition: background 0.3s;
        }
        .stat-cell:hover { background: rgba(0,245,160,0.06); }
        .stat-num {
            font-family: 'Syne', sans-serif;
            font-size: 1.75rem; font-weight: 800;
            background: linear-gradient(135deg,#00f5a0,#00d9f5);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent;
            background-clip:text;
        }
        .stat-lbl { font-size:0.7rem; color:var(--text-muted); letter-spacing:0.5px; margin-top:2px; }

        /* ── SECTION BANNER ── */
        .section-banner {
            position: relative; z-index: 1;
            display: flex; align-items: center; gap: 0.8rem;
            margin: 2rem 0 1rem;
        }
        .sb-line {
            flex:1; height:1px;
            background: linear-gradient(90deg, rgba(0,245,160,0.35), transparent);
        }
        .sb-line.r { background: linear-gradient(90deg, transparent, rgba(0,245,160,0.35)); }
        .sb-title {
            font-family: 'Syne', sans-serif;
            font-size: 1.05rem; font-weight: 700;
            color: var(--text-main); white-space: nowrap;
        }
        .sb-dot {
            width: 8px; height: 8px; border-radius: 50%;
            background: linear-gradient(135deg,#00f5a0,#00d9f5);
            box-shadow: 0 0 10px rgba(0,245,160,0.8);
            animation: dotPulse 2s ease-in-out infinite;
        }
        @keyframes dotPulse {
            0%,100%{transform:scale(1);opacity:1;}
            50%    {transform:scale(1.4);opacity:0.6;}
        }

        /* ── GLASS CARD ── */
        .glass-card {
            position: relative; z-index: 1;
            background: var(--bg-card);
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            padding: 1.8rem 1.8rem 1.5rem;
            backdrop-filter: blur(18px);
            box-shadow: 0 24px 60px rgba(0,0,0,0.45), 0 0 0 1px rgba(0,245,160,0.04);
            margin-bottom: 1.4rem;
            animation: cardIn 0.7s ease 0.2s both;
            overflow: hidden;
        }
        @keyframes cardIn {
            from{opacity:0;transform:translateY(24px) scale(0.97);}
            to{opacity:1;transform:translateY(0) scale(1);}
        }
        .glass-card::before {
            content:'';
            position:absolute; top:0; left:10%; right:10%; height:1px;
            background: linear-gradient(90deg, transparent, #00f5a0 40%, #00d9f5 60%, transparent);
            animation: topGlow 3.5s ease-in-out infinite;
        }
        @keyframes topGlow {
            0%,100%{opacity:0.5;} 50%{opacity:1;}
        }

        /* ── RECORD CARD ── */
        .record-card {
            position: relative; z-index: 1;
            background: rgba(6,18,40,0.78);
            border: 1px solid var(--glass-border);
            border-radius: 18px;
            padding: 1.6rem;
            backdrop-filter: blur(16px);
            box-shadow: 0 16px 48px rgba(0,0,0,0.4);
            animation: cardIn 0.7s ease 0.35s both;
            overflow: hidden;
        }
        .record-card::before {
            content:'';
            position:absolute; top:0; left:8%; right:8%; height:1px;
            background: linear-gradient(90deg, transparent, #818cf8 40%, #00d9f5 60%, transparent);
        }

        /* ── PROBABILITY BAR ── */
        .prob-bar-wrap { margin: 6px 0; }
        .prob-label {
            display: flex; justify-content: space-between;
            font-size: 0.8rem; color: var(--text-muted); margin-bottom: 4px;
        }
        .prob-label span:last-child { color: var(--text-main); font-weight: 500; }
        .prob-track {
            height: 8px; border-radius: 999px;
            background: rgba(255,255,255,0.06);
            overflow: hidden;
        }
        .prob-fill {
            height: 100%; border-radius: 999px;
            background: linear-gradient(90deg, #00f5a0, #00d9f5);
            box-shadow: 0 0 8px rgba(0,245,160,0.45);
            animation: barGrow 1s cubic-bezier(.22,.68,0,1.1) both;
        }
        @keyframes barGrow {
            from{width:0 !important;}
        }

        /* ── PARAM VALUE BADGE ── */
        .param-row {
            display: flex; align-items: center; justify-content: space-between;
            padding: 0.5rem 0;
            border-bottom: 1px solid rgba(0,245,160,0.06);
        }
        .param-row:last-child { border-bottom: none; }
        .param-key { font-size:0.82rem; color:var(--text-muted); }
        .param-val {
            font-family:'Syne',sans-serif; font-size:0.88rem;
            font-weight:600; color:var(--text-main);
        }
        .param-range {
            font-size:0.72rem; color:rgba(122,154,184,0.55);
            margin-left:0.5rem;
        }
        .status-ok  { color:#00f5a0; }
        .status-hi  { color:#fb7185; }
        .status-low { color:#fbbf24; }

        /* ── TOP FINDING BADGE ── */
        .finding-badge {
            display: inline-flex; align-items: center; gap: 0.5rem;
            background: linear-gradient(135deg, rgba(0,245,160,0.12), rgba(0,217,245,0.08));
            border: 1px solid rgba(0,245,160,0.3);
            border-radius: 12px;
            padding: 0.6rem 1.2rem;
            margin-bottom: 1.2rem;
        }
        .finding-badge-label {
            font-size:0.72rem; color:var(--text-muted);
            letter-spacing:0.5px; text-transform:uppercase;
        }
        .finding-badge-value {
            font-family:'Syne',sans-serif; font-size:1.05rem;
            font-weight:700; color:var(--accent-g);
        }
        .finding-badge-prob {
            background: rgba(0,245,160,0.15);
            color: #00f5a0;
            font-size:0.75rem; font-weight:700;
            padding: 2px 8px; border-radius:999px;
        }

        /* ── DATAFRAME OVERRIDES ── */
        .stDataFrame {
            border: 1px solid var(--glass-border) !important;
            border-radius: 14px !important; overflow: hidden !important;
            backdrop-filter: blur(12px);
        }
        .stDataFrame thead th {
            background: rgba(0,245,160,0.07) !important;
            color: #00f5a0 !important;
            font-family:'Syne',sans-serif !important;
            font-size:0.75rem !important;
            letter-spacing:1px !important;
            text-transform:uppercase !important;
        }
        .stDataFrame td { color: var(--text-main) !important; font-size:0.88rem !important; }
        .stDataFrame tbody tr:hover td { background:rgba(0,245,160,0.04) !important; }

        /* ── SELECTBOX ── */
        div[data-testid="stSelectbox"] label {
            color: var(--text-muted) !important;
            font-size:0.78rem !important; font-weight:500 !important;
            letter-spacing:0.4px !important; text-transform:uppercase !important;
        }
        div[data-testid="stSelectbox"] > div > div {
            background: var(--input-bg) !important;
            border: 1px solid rgba(0,245,160,0.18) !important;
            border-radius: 12px !important;
            color: var(--text-main) !important;
            font-family:'DM Sans',sans-serif !important;
        }
        div[data-testid="stSelectbox"] > div > div:focus-within {
            border-color: rgba(0,245,160,0.5) !important;
            box-shadow: 0 0 0 3px rgba(0,245,160,0.1) !important;
        }

        /* ── BUTTONS ── */
        div.stButton > button {
            font-family:'DM Sans',sans-serif !important;
            background: linear-gradient(135deg, #00f5a0, #00d9f5) !important;
            color:#04101f !important; border:none !important;
            border-radius:12px !important; font-weight:700 !important;
            font-size:0.9rem !important; padding:0.65rem 1.4rem !important;
            transition: transform 0.25s, box-shadow 0.25s !important;
        }
        div.stButton > button:hover {
            transform:translateY(-3px) !important;
            box-shadow:0 12px 36px rgba(0,245,160,0.35) !important;
        }
        /* Back button — ghost style */
        div.stButton > button[data-testid*="back"],
        div.stButton:last-child > button {
            background: transparent !important;
            border: 1px solid rgba(0,245,160,0.28) !important;
            color: #00f5a0 !important;
        }
        div.stButton:last-child > button:hover {
            background: rgba(0,245,160,0.07) !important;
            box-shadow:0 6px 20px rgba(0,245,160,0.18) !important;
        }

        /* ── ALERTS ── */
        .stAlert {
            border-radius:12px !important;
            border:1px solid var(--glass-border) !important;
            background:rgba(4,14,30,0.8) !important;
            backdrop-filter:blur(12px) !important;
        }

        /* ── HEADINGS ── */
        h3, .stSubheader {
            font-family:'Syne',sans-serif !important;
            color:var(--text-main) !important; font-weight:700 !important;
        }

        /* ── DIVIDER ── */
        hr { border:none !important; border-top:1px solid rgba(0,245,160,0.1) !important; margin:2rem 0 !important; }

        /* ── COL HEADER ── */
        .col-header {
            font-family:'Syne',sans-serif;
            font-size:0.82rem; font-weight:700;
            letter-spacing:1.5px; text-transform:uppercase;
            color:var(--accent-b); margin-bottom:0.9rem;
            display:flex; align-items:center; gap:0.5rem;
        }
        .col-header-dot {
            width:6px; height:6px; border-radius:50%;
            background:var(--accent-b);
            box-shadow:0 0 8px rgba(0,217,245,0.9);
        }

        /* ── FOOTER ── */
        .da-footer {
            position:relative; z-index:1;
            text-align:center; padding:2rem 1rem 1rem;
            color:var(--text-muted); font-size:0.82rem; line-height:1.8;
            border-top:1px solid var(--glass-border); margin-top:2.5rem;
        }
        .da-footer strong {
            font-family:'Syne',sans-serif;
            background:linear-gradient(135deg,#00f5a0,#00d9f5);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent;
            background-clip:text;
        }
        .shimmer-text {
            background:linear-gradient(90deg,#00f5a0,#00d9f5,#818cf8,#00f5a0);
            background-size:300% auto;
            -webkit-background-clip:text; -webkit-text-fill-color:transparent;
            background-clip:text;
            animation:shimmer 4s linear infinite;
        }
        @keyframes shimmer {
            0%{background-position:-200% center;}
            100%{background-position:200% center;}
        }

        /* ── SCROLLBAR ── */
        ::-webkit-scrollbar { width:5px; }
        ::-webkit-scrollbar-track { background:var(--bg-deep); }
        ::-webkit-scrollbar-thumb {
            background:linear-gradient(180deg,#00f5a0,#00d9f5);
            border-radius:5px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────
#  HELPERS
# ──────────────────────────────────────────────
def ecg_bar():
    st.markdown(
        """
        <div class="ecg-bar">
          <svg viewBox="0 0 1200 48" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="eg" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%"   stop-color="#00f5a0" stop-opacity="0"/>
                <stop offset="20%"  stop-color="#00f5a0" stop-opacity="1"/>
                <stop offset="80%"  stop-color="#00d9f5" stop-opacity="1"/>
                <stop offset="100%" stop-color="#00d9f5" stop-opacity="0"/>
              </linearGradient>
            </defs>
            <polyline
              points="0,24 55,24 70,24 78,7 86,41 94,11 102,36 110,24 180,24
                      235,24 250,24 258,7 266,41 274,11 282,36 290,24 360,24
                      415,24 430,24 438,7 446,41 454,11 462,36 470,24 540,24
                      595,24 610,24 618,7 626,41 634,11 642,36 650,24 720,24
                      775,24 790,24 798,7 806,41 814,11 822,36 830,24 900,24
                      955,24 970,24 978,7 986,41 994,11 1002,36 1010,24 1080,24
                      1135,24 1150,24 1158,7 1166,41 1174,11 1182,36 1190,24 1200,24"
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
          <div class="sb-line"></div>
          <div class="sb-dot"></div>
          <div class="sb-title">{title}</div>
          <div class="sb-dot"></div>
          <div class="sb-line r"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def stat_strip(total, unique_diseases, top_prob):
    top_pct = f"{top_prob * 100:.0f}%" if top_prob else "—"
    st.markdown(
        f"""
        <div class="stat-strip">
          <div class="stat-cell">
            <div class="stat-num">{total}</div>
            <div class="stat-lbl">Total Assessments</div>
          </div>
          <div class="stat-cell">
            <div class="stat-num">{unique_diseases}</div>
            <div class="stat-lbl">Unique Findings</div>
          </div>
          <div class="stat-cell">
            <div class="stat-num">{top_pct}</div>
            <div class="stat-lbl">Highest Probability</div>
          </div>
          <div class="stat-cell">
            <div class="stat-num">AI</div>
            <div class="stat-lbl">Analysed</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def probability_bars(results: dict):
    """Render custom animated probability bars."""
    sorted_items = sorted(results.items(), key=lambda x: x[1], reverse=True)
    bars_html = ""
    for disease, prob in sorted_items:
        pct = prob * 100
        color = (
            "linear-gradient(90deg,#fb7185,#f97316)" if pct > 60
            else "linear-gradient(90deg,#fbbf24,#00d9f5)" if pct > 30
            else "linear-gradient(90deg,#00f5a0,#00d9f5)"
        )
        bars_html += f"""
        <div class="prob-bar-wrap">
          <div class="prob-label">
            <span>{disease}</span>
            <span>{pct:.1f}%</span>
          </div>
          <div class="prob-track">
            <div class="prob-fill" style="width:{pct}%;background:{color};"></div>
          </div>
        </div>
        """
    st.markdown(bars_html, unsafe_allow_html=True)


def param_table(input_data: dict):
    """Render styled parameter rows with normal range comparison."""
    rows_html = ""
    for k, v in input_data.items():
        lo, hi = NORMAL_RANGES.get(k, (None, None))
        try:
            val_f = float(v)
            if lo is not None and hi is not None:
                if val_f < lo:
                    status = "status-low"; icon = "▼"
                elif val_f > hi:
                    status = "status-hi"; icon = "▲"
                else:
                    status = "status-ok"; icon = "✓"
                range_txt = f"{lo} – {hi}"
            else:
                status = ""; icon = ""; range_txt = "—"
        except (TypeError, ValueError):
            status = ""; icon = ""; range_txt = "—"

        rows_html += f"""
        <div class="param-row">
          <span class="param-key">{k}</span>
          <span>
            <span class="param-val {status}">{icon} {v}</span>
            <span class="param-range">{range_txt}</span>
          </span>
        </div>
        """
    st.markdown(rows_html, unsafe_allow_html=True)


# ──────────────────────────────────────────────
#  MAIN SHOW FUNCTION
# ──────────────────────────────────────────────
def show():
    inject_history_styles()

    # ── Orbs
    st.markdown(
        """
        <div class="orb-layer">
          <div class="orb o1"></div><div class="orb o2"></div>
          <div class="orb o3"></div><div class="orb o4"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Particles
    st.markdown(
        """
        <div class="particles">
          <span class="particle pa">📋</span>
          <span class="particle pb">🔬</span>
          <span class="particle pc">🧬</span>
          <span class="particle pd">📊</span>
          <span class="particle pe">🫀</span>
          <span class="particle pf">🩺</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    show_logo_header(size=180)

    # ── HERO
    st.markdown(
        """
        <div class="page-hero">
          <div class="hero-icon">
            <div class="hero-icon-core">📋</div>
          </div>
          <h2>Assessment History</h2>
          <p>Review previous predictions, entered biomarker values, and saved clinical summaries.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    ecg_bar()

    # ── AUTH GATE
    if not st.session_state.get("authenticated") or not st.session_state["user"].get("id"):
        st.markdown(
            """
            <div class="glass-card" style="text-align:center;padding:3rem;">
              <div style="font-size:3rem;margin-bottom:1rem;">🔐</div>
              <div style="font-family:Syne,sans-serif;font-size:1.3rem;font-weight:700;
                          margin-bottom:0.5rem;color:#e8f4fd;">Sign in Required</div>
              <div style="color:#7a9ab8;font-size:0.9rem;">
                Please sign in to view your assessment history.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Go to Login", use_container_width=True):
            st.session_state["page"] = "login"
            st.rerun()
        return

    user_id = st.session_state["user"]["id"]

    try:
        history_data = []
        for data in list_predictions(user_id):
            history_data.append(
                {
                    "id":        data.get("id"),
                    "timestamp": data.get("timestamp", "Unknown"),
                    "top_disease": data.get("top_disease", ""),
                    "top_prob":  data.get("top_probability", 0),
                    "input":     data.get("input_data", {}),
                    "results":   data.get("results", {}),
                }
            )

        if not history_data:
            st.markdown(
                """
                <div class="glass-card" style="text-align:center;padding:3rem;">
                  <div style="font-size:3rem;margin-bottom:1rem;">🔍</div>
                  <div style="font-family:Syne,sans-serif;font-size:1.2rem;font-weight:700;
                              margin-bottom:0.5rem;color:#e8f4fd;">No Assessments Yet</div>
                  <div style="color:#7a9ab8;font-size:0.9rem;">
                    Run a new analysis to populate your history.
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            return

        # ── Stat strip
        unique_diseases = len({h["top_disease"] for h in history_data if h["top_disease"]})
        max_prob = max((h["top_prob"] for h in history_data), default=0)
        stat_strip(len(history_data), unique_diseases, max_prob)

        # ── Overview table
        section_banner("All Assessments")

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        df_display = pd.DataFrame(
            [
                {
                    "Date":            h["timestamp"],
                    "Primary Finding": h["top_disease"],
                    "Probability":     f"{h['top_prob'] * 100:.1f}%",
                    "Conditions Checked": f"{len(h['results'])}",
                }
                for h in history_data
            ]
        )
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # ── DETAILED RECORD
        section_banner("Detailed Record")

        selected_idx = st.selectbox(
            "Choose an assessment to inspect",
            options=range(len(history_data)),
            format_func=lambda i: (
                f"{history_data[i]['timestamp']}  ·  {history_data[i]['top_disease']} "
                f"({history_data[i]['top_prob'] * 100:.1f}%)"
            ),
        )

        if selected_idx is not None:
            record = history_data[selected_idx]

            # Top finding badge
            st.markdown(
                f"""
                <div class="finding-badge">
                  <div>
                    <div class="finding-badge-label">Primary Finding</div>
                    <div class="finding-badge-value">{record['top_disease'] or '—'}</div>
                  </div>
                  <div class="finding-badge-prob">{record['top_prob']*100:.1f}%</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns(2)

            with col1:
                st.markdown('<div class="record-card">', unsafe_allow_html=True)
                st.markdown(
                    '<div class="col-header"><div class="col-header-dot"></div>Input Biomarkers</div>',
                    unsafe_allow_html=True,
                )
                if record["input"]:
                    param_table(record["input"])
                else:
                    st.markdown(
                        '<div style="color:var(--text-muted);font-size:0.85rem;">No input data recorded.</div>',
                        unsafe_allow_html=True,
                    )
                st.markdown("</div>", unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="record-card">', unsafe_allow_html=True)
                st.markdown(
                    '<div class="col-header"><div class="col-header-dot"></div>Prediction Probabilities</div>',
                    unsafe_allow_html=True,
                )
                if record["results"]:
                    probability_bars(record["results"])
                else:
                    st.markdown(
                        '<div style="color:var(--text-muted);font-size:0.85rem;">No results recorded.</div>',
                        unsafe_allow_html=True,
                    )
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("🔁  Run This Analysis Again", use_container_width=True):
                    st.session_state["rerun_data"]     = record["input"]
                    st.session_state["page"]           = "predictor"
                    st.session_state["predictor_mode"] = "full"
                    st.rerun()
            with btn_col2:
                if st.button("← Back to Dashboard", use_container_width=True):
                    st.session_state["page"] = "dashboard"
                    st.rerun()

    except Exception as e:
        st.error(f"Error loading history: {e}")
        if st.button("← Back to Dashboard"):
            st.session_state["page"] = "dashboard"
            st.rerun()

    # ── FOOTER
    st.markdown(
        f"""
        <div class="da-footer">
          <strong>{APP_NAME}</strong> &nbsp;|&nbsp;
          <span class="shimmer-text">{TAGLINE}</span><br>
          <span style="font-size:0.76rem;opacity:0.55;">For educational screening support only. Not a substitute for medical advice.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )