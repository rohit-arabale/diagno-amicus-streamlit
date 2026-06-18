import os
import sys
import base64

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from components.header import show_logo_header
from config.branding import APP_NAME, TAGLINE
from database.db_manager import list_predictions


# ──────────────────────────────────────────────
#  ICON SVGS
# ──────────────────────────────────────────────
def _icon_svg(kind):
    svg_map = {
        "skin": """
        <svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'>
          <defs>
            <linearGradient id='sg' x1='0%' y1='0%' x2='100%' y2='100%'>
              <stop offset='0%' stop-color='#00f5a0'/>
              <stop offset='100%' stop-color='#00d9f5'/>
            </linearGradient>
          </defs>
          <circle cx='32' cy='32' r='30' fill='url(#sg)' opacity='0.2'/>
          <path d='M32 14c8 0 14 6 14 14 0 5-2 8-5 12-3 3-5 7-5 12h-8c0-5-2-9-5-12-3-4-5-7-5-12 0-8 6-14 14-14z' fill='url(#sg)'/>
          <circle cx='28' cy='28' r='2.4' fill='#ffffff'/>
          <circle cx='36' cy='32' r='2.4' fill='#ffffff'/>
          <circle cx='31' cy='38' r='2.4' fill='#ffffff'/>
        </svg>
        """,
        "heart": """
        <svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'>
          <defs>
            <linearGradient id='hg' x1='0%' y1='0%' x2='100%' y2='100%'>
              <stop offset='0%' stop-color='#ff6b6b'/>
              <stop offset='100%' stop-color='#ff8e53'/>
            </linearGradient>
          </defs>
          <circle cx='32' cy='32' r='30' fill='url(#hg)' opacity='0.15'/>
          <path d='M32 50 14 33c-4-4-4-11 0-15 4-4 11-4 15 0l3 3 3-3c4-4 11-4 15 0 4 4 4 11 0 15L32 50z' fill='url(#hg)'/>
          <path d='M18 32h8l4-7 5 14 4-8h7' fill='none' stroke='#ffffff' stroke-width='3.2' stroke-linecap='round' stroke-linejoin='round'/>
        </svg>
        """,
        "diabetes": """
        <svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'>
          <defs>
            <linearGradient id='dg' x1='0%' y1='0%' x2='100%' y2='100%'>
              <stop offset='0%' stop-color='#a78bfa'/>
              <stop offset='100%' stop-color='#f472b6'/>
            </linearGradient>
          </defs>
          <circle cx='32' cy='32' r='30' fill='url(#dg)' opacity='0.15'/>
          <path d='M24 16h16v10l-4 4v18a4 4 0 0 1-8 0V30l-4-4V16z' fill='url(#dg)'/>
          <circle cx='32' cy='47' r='4' fill='#ffffff'/>
        </svg>
        """,
        "liver": """
        <svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'>
          <defs>
            <linearGradient id='lg' x1='0%' y1='0%' x2='100%' y2='100%'>
              <stop offset='0%' stop-color='#fbbf24'/>
              <stop offset='100%' stop-color='#f97316'/>
            </linearGradient>
          </defs>
          <circle cx='32' cy='32' r='30' fill='url(#lg)' opacity='0.15'/>
          <path d='M16 33c0-10 8-17 19-17 8 0 14 3 18 9 3 4 4 8 4 12 0 7-5 12-13 12H28c-8 0-12-6-12-16z' fill='url(#lg)'/>
          <path d='M24 28c6 0 11 2 16 7' fill='none' stroke='#ffffff' stroke-width='3' stroke-linecap='round'/>
        </svg>
        """,
        "full": """
        <svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'>
          <defs>
            <linearGradient id='fg' x1='0%' y1='0%' x2='100%' y2='100%'>
              <stop offset='0%' stop-color='#06b6d4'/>
              <stop offset='100%' stop-color='#3b82f6'/>
            </linearGradient>
          </defs>
          <circle cx='32' cy='32' r='30' fill='url(#fg)' opacity='0.15'/>
          <rect x='18' y='14' width='28' height='36' rx='7' fill='url(#fg)'/>
          <path d='M32 21v22M21 32h22' stroke='#ffffff' stroke-width='4' stroke-linecap='round'/>
        </svg>
        """,
    }
    svg_bytes = svg_map[kind].strip().encode("utf-8")
    return "data:image/svg+xml;base64," + base64.b64encode(svg_bytes).decode("ascii")


# ──────────────────────────────────────────────
#  INJECT GLOBAL CSS + ANIMATIONS
# ──────────────────────────────────────────────
def inject_styles():
    st.markdown(
        """
        <style>
        /* ── GOOGLE FONTS ── */
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

        /* ── ROOT & RESET ── */
        :root {
            --bg-deep:    #050d1a;
            --bg-mid:     #0a1628;
            --bg-card:    rgba(10,22,45,0.75);
            --accent-1:   #00f5a0;
            --accent-2:   #00d9f5;
            --accent-3:   #ff6b6b;
            --accent-4:   #a78bfa;
            --accent-5:   #fbbf24;
            --text-main:  #e8f4fd;
            --text-muted: #8ab0c8;
            --glass-border: rgba(0,245,160,0.18);
            --shadow-glow: 0 0 40px rgba(0,245,160,0.12);
        }

        /* ── STREAMLIT OVERRIDES ── */
        .stApp {
            background: var(--bg-deep) !important;
            font-family: 'DM Sans', sans-serif !important;
            color: var(--text-main) !important;
        }
        .stApp > header { display: none !important; }
        .block-container {
            padding-top: 0 !important;
            max-width: 1200px !important;
        }
        section[data-testid="stSidebar"] { display: none !important; }

        /* ── ANIMATED MESH BACKGROUND ── */
        .stApp::before {
            content: '';
            position: fixed;
            inset: 0;
            z-index: 0;
            background:
                radial-gradient(ellipse 80% 60% at 20% 10%, rgba(0,245,160,0.10) 0%, transparent 55%),
                radial-gradient(ellipse 60% 50% at 80% 20%, rgba(0,217,245,0.08) 0%, transparent 50%),
                radial-gradient(ellipse 50% 70% at 50% 80%, rgba(167,139,250,0.07) 0%, transparent 55%),
                radial-gradient(ellipse 40% 40% at 10% 80%, rgba(255,107,107,0.06) 0%, transparent 50%),
                linear-gradient(160deg, #050d1a 0%, #080f1f 50%, #060c18 100%);
            animation: meshShift 15s ease-in-out infinite alternate;
            pointer-events: none;
        }
        @keyframes meshShift {
            0%   { opacity: 1; filter: hue-rotate(0deg); }
            100% { opacity: 0.85; filter: hue-rotate(20deg); }
        }

        /* ── FLOATING ORBS ── */
        .orb-container {
            position: fixed; inset: 0; z-index: 0;
            pointer-events: none; overflow: hidden;
        }
        .orb {
            position: absolute;
            border-radius: 50%;
            filter: blur(80px);
            opacity: 0.3;
            animation: orbFloat linear infinite;
        }
        .orb-1 { width:320px; height:320px; background:#00f5a0; left:-80px; top:10%;  animation-duration:22s; }
        .orb-2 { width:260px; height:260px; background:#00d9f5; right:-60px; top:40%; animation-duration:28s; animation-delay:-8s; }
        .orb-3 { width:200px; height:200px; background:#a78bfa; left:40%;  top:70%; animation-duration:18s; animation-delay:-4s; }
        .orb-4 { width:180px; height:180px; background:#fbbf24; right:20%; top:5%;  animation-duration:32s; animation-delay:-12s; }
        @keyframes orbFloat {
            0%   { transform: translateY(0) scale(1); }
            33%  { transform: translateY(-40px) scale(1.06); }
            66%  { transform: translateY(20px) scale(0.95); }
            100% { transform: translateY(0) scale(1); }
        }

        /* ── PAGE HERO ── */
        .page-hero {
            position: relative; z-index: 1;
            text-align: center;
            padding: 3.5rem 2rem 2rem;
            animation: heroFadeIn 1s ease both;
        }
        @keyframes heroFadeIn {
            from { opacity: 0; transform: translateY(-24px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        .page-hero h2 {
            font-family: 'Syne', sans-serif !important;
            font-size: 3rem !important;
            font-weight: 800 !important;
            background: linear-gradient(135deg, #00f5a0, #00d9f5, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.6rem !important;
            letter-spacing: -1px;
            text-shadow: none;
        }
        .page-hero p {
            font-size: 1.15rem !important;
            color: var(--text-muted) !important;
            font-weight: 300 !important;
            max-width: 540px;
            margin: 0 auto;
            line-height: 1.6;
        }

        /* ── PULSE RING AROUND HERO ── */
        .hero-pulse {
            display: flex; justify-content: center; margin-bottom: 1.2rem;
        }
        .hero-pulse-core {
            width: 56px; height: 56px;
            border-radius: 50%;
            background: linear-gradient(135deg,#00f5a0,#00d9f5);
            display: flex; align-items: center; justify-content: center;
            font-size: 1.6rem;
            position: relative;
            animation: pulseCore 2.4s ease-in-out infinite;
            box-shadow: 0 0 0 0 rgba(0,245,160,0.5);
        }
        @keyframes pulseCore {
            0%, 100% { box-shadow: 0 0 0 0 rgba(0,245,160,0.5); }
            50%       { box-shadow: 0 0 0 18px rgba(0,245,160,0); }
        }

        /* ── SECTION LABEL ── */
        .section-label {
            position: relative; z-index: 1;
            font-family: 'Syne', sans-serif;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 3px;
            text-transform: uppercase;
            color: var(--accent-1);
            margin-bottom: 0.3rem;
            padding-left: 2px;
        }

        /* ── STAT STRIP ── */
        .stat-strip {
            position: relative; z-index: 1;
            display: flex;
            gap: 1px;
            background: var(--glass-border);
            border-radius: 16px;
            overflow: hidden;
            margin: 1.6rem 0 2.2rem;
            backdrop-filter: blur(12px);
            animation: stripSlide 0.8s ease 0.3s both;
        }
        @keyframes stripSlide {
            from { opacity:0; transform: scaleX(0.92); }
            to   { opacity:1; transform: scaleX(1); }
        }
        .stat-cell {
            flex: 1;
            background: rgba(10,22,45,0.7);
            padding: 1.1rem 0.5rem;
            text-align: center;
        }
        .stat-cell:hover { background: rgba(0,245,160,0.06); transition: .3s; }
        .stat-num {
            font-family: 'Syne', sans-serif;
            font-size: 1.8rem;
            font-weight: 800;
            background: linear-gradient(135deg,#00f5a0,#00d9f5);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .stat-lbl {
            font-size: 0.72rem;
            color: var(--text-muted);
            letter-spacing: 0.5px;
            margin-top: 2px;
        }

        /* ── CARDS ── */
        .dash-card {
            position: relative; z-index: 1;
            background: var(--bg-card);
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            padding: 1.8rem 1.5rem 1.5rem;
            margin-bottom: 1.2rem;
            cursor: pointer;
            transition: transform 0.35s cubic-bezier(.22,.68,0,1.2),
                        box-shadow 0.35s ease,
                        border-color 0.3s ease,
                        background 0.3s ease;
            backdrop-filter: blur(16px);
            overflow: hidden;
            animation: cardEntry 0.7s ease both;
        }
        .dash-card::before {
            content: '';
            position: absolute; inset: 0;
            background: linear-gradient(135deg, rgba(0,245,160,0.04), transparent 60%);
            opacity: 0;
            transition: opacity 0.35s;
        }
        .dash-card:hover::before { opacity: 1; }
        .dash-card:hover {
            transform: translateY(-6px) scale(1.015);
            box-shadow: 0 24px 60px rgba(0,245,160,0.15), 0 4px 16px rgba(0,0,0,0.4);
            border-color: rgba(0,245,160,0.45);
            background: rgba(10,28,55,0.9);
        }
        /* stagger card animation */
        .dash-card:nth-child(1) { animation-delay: 0.15s; }
        .dash-card:nth-child(2) { animation-delay: 0.25s; }
        .dash-card:nth-child(3) { animation-delay: 0.35s; }
        .dash-card:nth-child(4) { animation-delay: 0.45s; }
        .dash-card:nth-child(5) { animation-delay: 0.55s; }
        @keyframes cardEntry {
            from { opacity:0; transform: translateY(32px) scale(0.96); }
            to   { opacity:1; transform: translateY(0) scale(1); }
        }

        /* card-glow accent line at top */
        .dash-card::after {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, #00f5a0, #00d9f5, transparent);
            opacity: 0;
            transition: opacity 0.35s;
        }
        .dash-card:hover::after { opacity: 1; }

        .dash-card-icon {
            width: 62px; height: 62px;
            margin-bottom: 1rem;
            filter: drop-shadow(0 4px 16px rgba(0,245,160,0.25));
            transition: filter 0.3s, transform 0.3s;
        }
        .dash-card:hover .dash-card-icon {
            filter: drop-shadow(0 6px 24px rgba(0,245,160,0.5));
            transform: scale(1.08) rotate(-3deg);
        }
        .dash-card-icon img { width: 100%; height: 100%; }

        .dash-card-title {
            font-family: 'Syne', sans-serif;
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--text-main);
            margin-bottom: 0.4rem;
            letter-spacing: -0.3px;
        }
        .dash-card-desc {
            font-size: 0.85rem;
            color: var(--text-muted);
            line-height: 1.55;
            font-weight: 300;
        }
        /* coloured corner badge per card type */
        .badge-skin    { background: linear-gradient(135deg,#00f5a0,#00d9f5); }
        .badge-heart   { background: linear-gradient(135deg,#ff6b6b,#ff8e53); }
        .badge-diabetes{ background: linear-gradient(135deg,#a78bfa,#f472b6); }
        .badge-liver   { background: linear-gradient(135deg,#fbbf24,#f97316); }
        .badge-full    { background: linear-gradient(135deg,#06b6d4,#3b82f6); }
        .card-badge {
            position: absolute; top: 14px; right: 14px;
            width: 28px; height: 28px;
            border-radius: 50%;
            opacity: 0.75;
            transition: opacity 0.3s, transform 0.3s;
        }
        .dash-card:hover .card-badge { opacity: 1; transform: scale(1.2); }

        /* ── BUTTONS ── */
        div.stButton > button {
            font-family: 'DM Sans', sans-serif !important;
            background: linear-gradient(135deg, #00f5a0, #00d9f5) !important;
            color: #050d1a !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            font-size: 0.88rem !important;
            padding: 0.58rem 1.2rem !important;
            transition: transform 0.25s, box-shadow 0.25s, opacity 0.25s !important;
            letter-spacing: 0.3px;
        }
        div.stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 28px rgba(0,245,160,0.35) !important;
            opacity: 0.92 !important;
        }
        div.stButton > button:active { transform: translateY(0) !important; }

        /* Secondary button (View Full History) */
        div.stButton > button[data-testid*="full_history"] {
            background: transparent !important;
            border: 1px solid rgba(0,245,160,0.4) !important;
            color: #00f5a0 !important;
        }
        div.stButton > button[data-testid*="full_history"]:hover {
            background: rgba(0,245,160,0.08) !important;
            box-shadow: 0 4px 20px rgba(0,245,160,0.2) !important;
        }

        /* ── DIVIDER ── */
        hr {
            border: none !important;
            border-top: 1px solid rgba(0,245,160,0.12) !important;
            margin: 2rem 0 !important;
        }

        /* ── RECENT TABLE HEADING ── */
        h3, .stSubheader {
            font-family: 'Syne', sans-serif !important;
            color: var(--text-main) !important;
            font-weight: 700 !important;
        }

        /* ── DATAFRAME STYLING ── */
        .stDataFrame {
            border: 1px solid var(--glass-border) !important;
            border-radius: 14px !important;
            overflow: hidden !important;
            backdrop-filter: blur(12px);
        }
        .stDataFrame thead th {
            background: rgba(0,245,160,0.08) !important;
            color: #00f5a0 !important;
            font-family: 'Syne', sans-serif !important;
            font-size: 0.78rem !important;
            letter-spacing: 1px !important;
            text-transform: uppercase !important;
        }
        .stDataFrame tbody tr:hover td {
            background: rgba(0,245,160,0.05) !important;
        }
        .stDataFrame td {
            color: var(--text-main) !important;
            font-size: 0.88rem !important;
        }

        /* ── EXPANDER ── */
        .streamlit-expanderHeader {
            font-family: 'Syne', sans-serif !important;
            color: var(--text-main) !important;
            background: rgba(10,22,45,0.7) !important;
            border: 1px solid var(--glass-border) !important;
            border-radius: 12px !important;
        }
        .streamlit-expanderContent {
            background: rgba(10,22,45,0.6) !important;
            border: 1px solid var(--glass-border) !important;
            border-top: none !important;
            border-radius: 0 0 12px 12px !important;
            backdrop-filter: blur(12px);
        }

        /* ── METRICS ── */
        div[data-testid="metric-container"] {
            background: rgba(0,245,160,0.05) !important;
            border: 1px solid var(--glass-border) !important;
            border-radius: 12px !important;
            padding: 0.8rem 1rem !important;
        }
        div[data-testid="metric-container"] label {
            color: var(--text-muted) !important;
            font-size: 0.75rem !important;
            letter-spacing: 0.5px !important;
        }
        div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
            color: #00f5a0 !important;
            font-family: 'Syne', sans-serif !important;
            font-size: 1.1rem !important;
            font-weight: 700 !important;
        }

        /* ── INFO / ERROR ── */
        .stAlert {
            border-radius: 12px !important;
            border: 1px solid var(--glass-border) !important;
            background: rgba(10,22,45,0.7) !important;
            backdrop-filter: blur(12px);
        }

        /* ── FOOTER ── */
        .da-footer {
            position: relative; z-index: 1;
            text-align: center;
            padding: 2rem 1rem 1rem;
            color: var(--text-muted);
            font-size: 0.82rem;
            line-height: 1.8;
            border-top: 1px solid var(--glass-border);
            margin-top: 2rem;
        }
        .da-footer strong {
            font-family: 'Syne', sans-serif;
            background: linear-gradient(135deg,#00f5a0,#00d9f5);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        /* ── SCROLLBAR ── */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: var(--bg-deep); }
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(180deg,#00f5a0,#00d9f5);
            border-radius: 6px;
        }

        /* ── ECG ANIMATION BAR ── */
        .ecg-bar {
            position: relative; z-index: 1;
            width: 100%;
            height: 50px;
            overflow: hidden;
            margin: 1rem 0;
        }
        .ecg-bar svg {
            position: absolute;
            animation: ecgScroll 3s linear infinite;
            width: 200%;
        }
        @keyframes ecgScroll {
            from { transform: translateX(0); }
            to   { transform: translateX(-50%); }
        }

        /* ── SECTION BANNER ── */
        .section-banner {
            position: relative; z-index: 1;
            display: flex;
            align-items: center;
            gap: 0.8rem;
            margin: 2rem 0 1rem;
        }
        .section-banner-line {
            flex: 1;
            height: 1px;
            background: linear-gradient(90deg, rgba(0,245,160,0.4), transparent);
        }
        .section-banner-line.right {
            background: linear-gradient(90deg, transparent, rgba(0,245,160,0.4));
        }
        .section-banner-title {
            font-family: 'Syne', sans-serif;
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--text-main);
            white-space: nowrap;
        }
        .section-banner-dot {
            width: 8px; height: 8px;
            border-radius: 50%;
            background: linear-gradient(135deg,#00f5a0,#00d9f5);
            box-shadow: 0 0 10px rgba(0,245,160,0.8);
            animation: dotPulse 2s ease-in-out infinite;
        }
        @keyframes dotPulse {
            0%,100% { transform: scale(1); opacity: 1; }
            50%      { transform: scale(1.4); opacity: 0.7; }
        }

        /* ── GRID CARDS CONTAINER ── */
        .cards-grid { position: relative; z-index: 1; }

        /* ── CARD ACCENT COLOURS ── */
        .card-accent-skin    { border-image: linear-gradient(135deg,#00f5a0,#00d9f5) 1; }
        .card-accent-heart   { border-image: linear-gradient(135deg,#ff6b6b,#ff8e53) 1; }
        .card-accent-diabetes{ border-image: linear-gradient(135deg,#a78bfa,#f472b6) 1; }
        .card-accent-liver   { border-image: linear-gradient(135deg,#fbbf24,#f97316) 1; }
        .card-accent-full    { border-image: linear-gradient(135deg,#06b6d4,#3b82f6) 1; }

        /* ── TAG PILLS ── */
        .tag-pill {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 999px;
            font-size: 0.68rem;
            font-weight: 600;
            letter-spacing: 0.5px;
            margin-top: 8px;
        }
        .tag-ai  { background: rgba(0,245,160,0.12); color:#00f5a0; border:1px solid rgba(0,245,160,0.3); }
        .tag-img { background: rgba(0,217,245,0.12); color:#00d9f5; border:1px solid rgba(0,217,245,0.3); }
        .tag-bio { background: rgba(167,139,250,0.12); color:#a78bfa; border:1px solid rgba(167,139,250,0.3); }

        /* ── ANIMATED GRADIENT TEXT SHIMMER ── */
        @keyframes shimmer {
            0%   { background-position: -200% center; }
            100% { background-position:  200% center; }
        }
        .shimmer-text {
            background: linear-gradient(90deg, #00f5a0, #00d9f5, #a78bfa, #00f5a0);
            background-size: 300% auto;
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: shimmer 4s linear infinite;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────
#  ECG ANIMATED LINE
# ──────────────────────────────────────────────
def ecg_bar():
    st.markdown(
        """
        <div class="ecg-bar">
          <svg viewBox="0 0 1200 50" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="ecgGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%"   stop-color="#00f5a0" stop-opacity="0"/>
                <stop offset="20%"  stop-color="#00f5a0" stop-opacity="1"/>
                <stop offset="80%"  stop-color="#00d9f5" stop-opacity="1"/>
                <stop offset="100%" stop-color="#00d9f5" stop-opacity="0"/>
              </linearGradient>
            </defs>
            <polyline
              points="0,25 60,25 80,25 90,5 100,45 110,10 120,40 130,25 200,25
                      260,25 280,25 290,5 300,45 310,10 320,40 330,25 400,25
                      460,25 480,25 490,5 500,45 510,10 520,40 530,25 600,25
                      660,25 680,25 690,5 700,45 710,10 720,40 730,25 800,25
                      860,25 880,25 890,5 900,45 910,10 920,40 930,25 1000,25
                      1060,25 1080,25 1090,5 1100,45 1110,10 1120,40 1130,25 1200,25"
              fill="none"
              stroke="url(#ecgGrad)"
              stroke-width="2.2"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────
#  STAT STRIP
# ──────────────────────────────────────────────
def stat_strip():
    st.markdown(
        """
        <div class="stat-strip">
          <div class="stat-cell">
            <div class="stat-num">5</div>
            <div class="stat-lbl">Disease Models</div>
          </div>
          <div class="stat-cell">
            <div class="stat-num">97%</div>
            <div class="stat-lbl">Accuracy</div>
          </div>
          <div class="stat-cell">
            <div class="stat-num">AI</div>
            <div class="stat-lbl">Powered</div>
          </div>
          <div class="stat-cell">
            <div class="stat-num">24/7</div>
            <div class="stat-lbl">Available</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────
#  SECTION BANNER
# ──────────────────────────────────────────────
def section_banner(title):
    st.markdown(
        f"""
        <div class="section-banner">
          <div class="section-banner-line"></div>
          <div class="section-banner-dot"></div>
          <div class="section-banner-title">{title}</div>
          <div class="section-banner-dot"></div>
          <div class="section-banner-line right"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────
#  MAIN SHOW FUNCTION
# ──────────────────────────────────────────────
def show():
    inject_styles()

    user = st.session_state.get("user", {})
    name = user.get("name", "User")

    # ── Floating orbs
    st.markdown(
        """
        <div class="orb-container">
          <div class="orb orb-1"></div>
          <div class="orb orb-2"></div>
          <div class="orb orb-3"></div>
          <div class="orb orb-4"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    show_logo_header()

    # ── HERO
    first = name.split()[0] if name else "User"
    st.markdown(
        f"""
        <div class="page-hero">
          <div class="hero-pulse">
            <div class="hero-pulse-core">🫀</div>
          </div>
          <h2>Welcome back, {first}</h2>
          <p>Select an assessment below to detect potential risks early and generate a clear, AI-driven clinical report.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── ECG line
    ecg_bar()

    # ── Stat strip
    stat_strip()

    # ── CARD SECTION
    section_banner("Risk Assessment Modules")

    card_meta = {
        "skin":     ("badge-skin",    ["tag-img", "AI Vision"],    ["tag-ai", "Lesion AI"]),
        "heart":    ("badge-heart",   ["tag-bio", "Vitals"],       ["tag-ai", "ECG-ready"]),
        "diabetes": ("badge-diabetes",["tag-bio", "Biomarkers"],   ["tag-ai", "Glucose AI"]),
        "liver":    ("badge-liver",   ["tag-bio", "Enzymes"],      ["tag-ai", "Panel AI"]),
        "full":     ("badge-full",    ["tag-img", "Multi-Model"],  ["tag-ai", "Full Report"]),
    }

    cards = [
        (_icon_svg("skin"),     "Skin Disease Detection",    "Image-based screening support for skin lesions.", "skin"),
        (_icon_svg("heart"),    "Heart Disease Prediction",  "Evaluates cholesterol, blood pressure, and heart rate.", "heart"),
        (_icon_svg("diabetes"), "Diabetes Prediction",       "Reviews glucose, BMI, and insulin indicators.", "diabetes"),
        (_icon_svg("liver"),    "Liver Disease Prediction",  "Checks bilirubin and liver enzyme patterns.", "liver"),
        (_icon_svg("full"),     "Full Health Risk Analysis", "Combines multiple disease models in one report.", "full"),
    ]

    col1, col2 = st.columns(2)
    for i, (icon, title, desc, key) in enumerate(cards):
        col = col1 if i % 2 == 0 else col2
        badge_cls, tag1, tag2 = card_meta[key]
        with col:
            st.markdown(
                f"""
                <div class="dash-card">
                    <div class="{badge_cls} card-badge"></div>
                    <div class="dash-card-icon"><img src="{icon}" alt="{title}"></div>
                    <div class="dash-card-title">{title}</div>
                    <div class="dash-card-desc">{desc}</div>
                    <div>
                      <span class="tag-pill {tag1[0]}">{tag1[1]}</span>
                      <span class="tag-pill {tag2[0]}">{tag2[1]}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"Open {title}", key=f"btn_{key}", use_container_width=True):
                st.session_state["page"] = "predictor"
                st.session_state["predictor_mode"] = key
                st.rerun()

    # ── DIVIDER
    st.markdown("<hr>", unsafe_allow_html=True)

    # ── RECENT HISTORY
    section_banner("Recent Risk Assessments")

    if st.session_state.get("authenticated") and st.session_state["user"].get("id"):
        user_id = st.session_state["user"]["id"]
        try:
            history = []
            for data in list_predictions(user_id, limit=5):
                history.append(
                    {
                        "Date": data.get("timestamp", "Unknown"),
                        "Primary Finding": data.get("top_disease", ""),
                        "Probability": f"{data.get('top_probability', 0) * 100:.1f}%",
                        "Included Results": f"{len(data.get('results', {}))} conditions",
                    }
                )
            if history:
                st.dataframe(pd.DataFrame(history), use_container_width=True, hide_index=True)
                if st.button("📋 View Full History", key="full_history"):
                    st.session_state["page"] = "history"
                    st.rerun()
            else:
                st.info("✨ No previous assessments found. Complete an analysis to populate this section.")
        except Exception as e:
            st.error(f"Could not load history: {e}")
    else:
        st.info("🔐 Sign in to view saved assessment history.")

    # ── PROFILE EXPANDER
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("👤  Profile Summary"):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Name",   user.get("name",   "—"))
        c2.metric("Age",    user.get("age",    "—"))
        c3.metric("Gender", user.get("gender", "—"))
        c4.metric("Mobile", user.get("mobile", "—"))

    # ── FOOTER
    st.markdown(
        f"""
        <div class="da-footer">
            <strong>{APP_NAME}</strong> &nbsp;|&nbsp; <span class="shimmer-text">{TAGLINE}</span><br>
            <span style="font-size:0.78rem; opacity:0.6;">
              This platform is for educational screening support only and does not replace qualified medical advice.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )