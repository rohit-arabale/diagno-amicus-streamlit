import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from components.header import show_logo_header
from config.branding import TAGLINE
from database.db_manager import login_user


# ──────────────────────────────────────────────
#  FULL-PAGE CSS + ANIMATIONS
# ──────────────────────────────────────────────
def inject_login_styles():
    st.markdown(
        """
        <style>
        /* ── GOOGLE FONTS ── */
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

        /* ── ROOT VARIABLES ── */
        :root {
            --bg-deep:      #04101f;
            --bg-card:      rgba(6,18,38,0.82);
            --accent-g:     #00f5a0;
            --accent-b:     #00d9f5;
            --accent-p:     #818cf8;
            --accent-r:     #fb7185;
            --text-main:    #e8f4fd;
            --text-muted:   #7a9ab8;
            --glass-border: rgba(0,245,160,0.18);
            --input-bg:     rgba(4,14,30,0.7);
        }

        /* ── APP SHELL ── */
        .stApp {
            background: var(--bg-deep) !important;
            font-family: 'DM Sans', sans-serif !important;
            color: var(--text-main) !important;
            min-height: 100vh;
        }
        .stApp > header { display: none !important; }
        .block-container {
            padding: 0 !important;
            max-width: 100% !important;
        }

        /* ── ANIMATED LAYERED BACKGROUND ── */
        .stApp::before {
            content: '';
            position: fixed; inset: 0; z-index: 0;
            background:
                radial-gradient(ellipse 70% 55% at 15% 50%, rgba(0,245,160,0.11) 0%, transparent 55%),
                radial-gradient(ellipse 55% 45% at 85% 20%, rgba(0,217,245,0.09) 0%, transparent 50%),
                radial-gradient(ellipse 45% 65% at 75% 85%, rgba(129,140,248,0.08) 0%, transparent 55%),
                radial-gradient(ellipse 35% 40% at 50% 50%, rgba(4,10,22,0.95) 0%, transparent 70%),
                linear-gradient(145deg, #04101f 0%, #060f1e 50%, #050d1b 100%);
            animation: bgBreath 12s ease-in-out infinite alternate;
            pointer-events: none;
        }
        @keyframes bgBreath {
            0%   { filter: hue-rotate(0deg)   brightness(1); }
            100% { filter: hue-rotate(15deg)  brightness(1.04); }
        }

        /* ── GRID OVERLAY TEXTURE ── */
        .stApp::after {
            content: '';
            position: fixed; inset: 0; z-index: 0;
            background-image:
                linear-gradient(rgba(0,245,160,0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0,245,160,0.03) 1px, transparent 1px);
            background-size: 44px 44px;
            pointer-events: none;
            animation: gridDrift 30s linear infinite;
        }
        @keyframes gridDrift {
            from { background-position: 0 0; }
            to   { background-position: 44px 44px; }
        }

        /* ── FLOATING ORBS ── */
        .orb-wrap {
            position: fixed; inset: 0; z-index: 0;
            pointer-events: none; overflow: hidden;
        }
        .orb {
            position: absolute; border-radius: 50%;
            filter: blur(90px); opacity: 0.22;
            animation: orbDrift linear infinite;
        }
        .o1 { width:380px;height:380px;background:#00f5a0;left:-120px;top:15%;animation-duration:24s; }
        .o2 { width:300px;height:300px;background:#00d9f5;right:-80px;top:55%;animation-duration:30s;animation-delay:-9s; }
        .o3 { width:240px;height:240px;background:#818cf8;left:45%;top:75%;animation-duration:20s;animation-delay:-5s; }
        .o4 { width:200px;height:200px;background:#fb7185;right:18%;top:3%;animation-duration:36s;animation-delay:-14s; }
        @keyframes orbDrift {
            0%  { transform: translateY(0)   scale(1); }
            35% { transform: translateY(-50px) scale(1.07); }
            70% { transform: translateY(25px) scale(0.94); }
            100%{ transform: translateY(0)   scale(1); }
        }

        /* ── FLOATING MEDICAL PARTICLES ── */
        .particles {
            position: fixed; inset: 0; z-index: 0;
            pointer-events: none;
        }
        .particle {
            position: absolute;
            font-size: 1.4rem;
            opacity: 0;
            animation: particleFloat linear infinite;
            filter: drop-shadow(0 0 8px rgba(0,245,160,0.6));
        }
        .p1  { left:5%;  top:20%; animation-duration:18s; animation-delay:0s; }
        .p2  { left:90%; top:35%; animation-duration:22s; animation-delay:-6s; }
        .p3  { left:15%; top:70%; animation-duration:16s; animation-delay:-3s; }
        .p4  { left:80%; top:80%; animation-duration:25s; animation-delay:-10s; }
        .p5  { left:50%; top:10%; animation-duration:20s; animation-delay:-8s; }
        .p6  { left:35%; top:88%; animation-duration:14s; animation-delay:-2s; }
        .p7  { left:70%; top:15%; animation-duration:28s; animation-delay:-15s; }
        .p8  { left:25%; top:50%; animation-duration:19s; animation-delay:-7s; }
        @keyframes particleFloat {
            0%   { opacity:0; transform: translateY(0)    rotate(0deg)   scale(0.8); }
            10%  { opacity:0.5; }
            50%  { opacity:0.3; transform: translateY(-120px) rotate(180deg) scale(1.1); }
            90%  { opacity:0.5; }
            100% { opacity:0; transform: translateY(-240px) rotate(360deg) scale(0.8); }
        }

        /* ── LEFT PANEL (decorative) ── */
        .left-panel {
            position: fixed; left: 0; top: 0; bottom: 0;
            width: 42%;
            z-index: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 3rem 2.5rem;
            pointer-events: none;
        }
        .left-panel-content {
            position: relative; z-index: 2;
            text-align: center;
            animation: leftReveal 1.1s cubic-bezier(.22,.68,0,1.1) both;
        }
        @keyframes leftReveal {
            from { opacity:0; transform: translateX(-40px); }
            to   { opacity:1; transform: translateX(0); }
        }
        .lp-dna {
            width: 220px; height: 220px;
            margin: 0 auto 2rem;
            position: relative;
        }

        /* ── ROTATING MEDICAL RING ── */
        .med-ring {
            width: 220px; height: 220px;
            position: relative; margin: 0 auto 2.5rem;
        }
        .med-ring svg { width: 100%; height: 100%; }
        .ring-outer {
            animation: spinCW  8s linear infinite;
            transform-origin: center;
        }
        .ring-inner {
            animation: spinCCW 5s linear infinite;
            transform-origin: center;
        }
        .ring-core {
            animation: corePulse 2.5s ease-in-out infinite;
        }
        @keyframes spinCW  { from{transform:rotate(0deg)}   to{transform:rotate(360deg)} }
        @keyframes spinCCW { from{transform:rotate(0deg)}   to{transform:rotate(-360deg)} }
        @keyframes corePulse {
            0%,100% { opacity:1; r:28; }
            50%     { opacity:0.7; r:32; }
        }

        /* ── TAGLINE & BRAND TEXT ── */
        .lp-brand {
            font-family: 'Syne', sans-serif;
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #00f5a0, #00d9f5, #818cf8);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text;
            line-height: 1.15;
            margin-bottom: 1rem;
            letter-spacing: -1px;
        }
        .lp-tagline {
            font-size: 1rem;
            color: var(--text-muted);
            font-weight: 300;
            font-style: italic;
            line-height: 1.65;
            max-width: 320px;
            margin: 0 auto 2rem;
        }

        /* ── FEATURE PILLS ── */
        .feature-pills {
            display: flex; flex-direction: column; gap: 0.7rem;
            align-items: flex-start;
            margin: 0 auto;
            width: fit-content;
        }
        .fp {
            display: flex; align-items: center; gap: 0.6rem;
            background: rgba(0,245,160,0.06);
            border: 1px solid rgba(0,245,160,0.18);
            border-radius: 999px;
            padding: 0.42rem 1.1rem 0.42rem 0.7rem;
            font-size: 0.82rem;
            color: var(--text-muted);
            animation: pillIn 0.7s ease both;
            backdrop-filter: blur(8px);
        }
        .fp:nth-child(1){ animation-delay:0.5s; }
        .fp:nth-child(2){ animation-delay:0.7s; }
        .fp:nth-child(3){ animation-delay:0.9s; }
        @keyframes pillIn {
            from { opacity:0; transform: translateX(-16px); }
            to   { opacity:1; transform: translateX(0); }
        }
        .fp-dot {
            width:8px; height:8px; border-radius:50%;
            background: linear-gradient(135deg,#00f5a0,#00d9f5);
            box-shadow: 0 0 8px rgba(0,245,160,0.8);
            flex-shrink: 0;
        }

        /* ── ECG STRIP (left panel bottom) ── */
        .ecg-strip {
            width: 100%; height: 44px;
            overflow: hidden;
            margin-top: 2.5rem;
            opacity: 0.55;
        }
        .ecg-strip svg { animation: ecgMove 3s linear infinite; width: 200%; }
        @keyframes ecgMove {
            from { transform: translateX(0); }
            to   { transform: translateX(-50%); }
        }

        /* ── VERTICAL DIVIDER ── */
        .v-divider {
            position: fixed; left: 42%; top: 8%; bottom: 8%;
            width: 1px; z-index: 2;
            background: linear-gradient(180deg,
                transparent 0%,
                rgba(0,245,160,0.35) 20%,
                rgba(0,245,160,0.35) 80%,
                transparent 100%);
            pointer-events: none;
        }

        /* ── RIGHT FORM PANEL ── */
        .right-zone {
            position: relative; z-index: 2;
            padding: 3rem 0 3rem;
        }

        /* ── AUTH CARD ── */
        .auth-card {
            background: var(--bg-card);
            border: 1px solid var(--glass-border);
            border-radius: 24px;
            padding: 2.6rem 2.2rem;
            backdrop-filter: blur(20px);
            box-shadow:
                0 0 0 1px rgba(0,245,160,0.05),
                0 32px 80px rgba(0,0,0,0.55),
                0 0 60px rgba(0,245,160,0.06);
            position: relative;
            overflow: hidden;
            animation: cardIn 0.9s cubic-bezier(.22,.68,0,1.1) 0.2s both;
        }
        @keyframes cardIn {
            from { opacity:0; transform: translateY(32px) scale(0.96); }
            to   { opacity:1; transform: translateY(0)    scale(1); }
        }
        /* Glowing top edge */
        .auth-card::before {
            content:'';
            position:absolute; top:0; left:10%; right:10%; height:1px;
            background: linear-gradient(90deg,
                transparent, #00f5a0 30%, #00d9f5 70%, transparent);
            animation: topEdgeGlow 3s ease-in-out infinite;
        }
        @keyframes topEdgeGlow {
            0%,100% { opacity:0.6; }
            50%     { opacity:1; }
        }
        /* Bottom corner glow */
        .auth-card::after {
            content:'';
            position:absolute; bottom:-60px; right:-60px;
            width:200px; height:200px; border-radius:50%;
            background: radial-gradient(circle, rgba(0,245,160,0.07), transparent 70%);
            pointer-events:none;
        }

        .auth-title {
            font-family: 'Syne', sans-serif;
            font-size: 1.9rem;
            font-weight: 800;
            color: var(--text-main);
            margin-bottom: 0.3rem;
            letter-spacing: -0.8px;
            animation: fadeUp 0.7s ease 0.4s both;
        }
        .auth-sub {
            font-size: 0.88rem;
            color: var(--text-muted);
            font-weight: 300;
            line-height: 1.6;
            margin-bottom: 1.8rem;
            animation: fadeUp 0.7s ease 0.55s both;
        }
        @keyframes fadeUp {
            from { opacity:0; transform:translateY(12px); }
            to   { opacity:1; transform:translateY(0); }
        }

        /* ── INPUT FIELDS ── */
        .stTextInput > label, .stNumberInput > label {
            font-family: 'DM Sans', sans-serif !important;
            font-size: 0.78rem !important;
            font-weight: 500 !important;
            color: var(--text-muted) !important;
            letter-spacing: 0.4px !important;
            text-transform: uppercase !important;
        }
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input {
            background: var(--input-bg) !important;
            border: 1px solid rgba(0,245,160,0.18) !important;
            border-radius: 12px !important;
            color: var(--text-main) !important;
            font-family: 'DM Sans', sans-serif !important;
            font-size: 0.95rem !important;
            padding: 0.65rem 1rem !important;
            transition: border-color 0.3s, box-shadow 0.3s !important;
        }
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus {
            border-color: rgba(0,245,160,0.55) !important;
            box-shadow: 0 0 0 3px rgba(0,245,160,0.10), 0 0 20px rgba(0,245,160,0.08) !important;
            outline: none !important;
        }
        .stTextInput > div > div > input::placeholder,
        .stNumberInput > div > div > input::placeholder {
            color: rgba(122,154,184,0.45) !important;
        }

        /* ── NUMBER INPUT SPINNERS ── */
        .stNumberInput > div > div > div > button {
            background: rgba(0,245,160,0.08) !important;
            border: 1px solid rgba(0,245,160,0.15) !important;
            color: #00f5a0 !important;
            border-radius: 8px !important;
            transition: background 0.2s !important;
        }
        .stNumberInput > div > div > div > button:hover {
            background: rgba(0,245,160,0.2) !important;
        }

        /* ── FORM SUBMIT / SIGN IN BUTTON ── */
        div.stForm div.stButton > button,
        div[data-testid="stFormSubmitButton"] > button {
            font-family: 'Syne', sans-serif !important;
            background: linear-gradient(135deg, #00f5a0 0%, #00d9f5 100%) !important;
            color: #04101f !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
            letter-spacing: 0.5px !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.75rem 1.5rem !important;
            width: 100% !important;
            transition: transform 0.25s, box-shadow 0.25s, opacity 0.25s !important;
            position: relative;
            overflow: hidden;
        }
        div.stForm div.stButton > button::after,
        div[data-testid="stFormSubmitButton"] > button::after {
            content:'';
            position:absolute; inset:0;
            background: linear-gradient(135deg, rgba(255,255,255,0.15), transparent);
            pointer-events:none;
        }
        div.stForm div.stButton > button:hover,
        div[data-testid="stFormSubmitButton"] > button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 12px 40px rgba(0,245,160,0.4), 0 4px 12px rgba(0,0,0,0.3) !important;
            opacity: 0.94 !important;
        }
        div.stForm div.stButton > button:active,
        div[data-testid="stFormSubmitButton"] > button:active {
            transform: translateY(-1px) !important;
        }

        /* ── SECONDARY BUTTON (Create Account) ── */
        div.stButton > button[kind="secondary"],
        div.stButton > button {
            font-family: 'DM Sans', sans-serif !important;
            background: transparent !important;
            border: 1px solid rgba(0,245,160,0.28) !important;
            color: #00f5a0 !important;
            border-radius: 12px !important;
            font-size: 0.9rem !important;
            font-weight: 500 !important;
            padding: 0.6rem 1.2rem !important;
            transition: background 0.25s, box-shadow 0.25s, transform 0.25s !important;
        }
        div.stButton > button:hover {
            background: rgba(0,245,160,0.07) !important;
            box-shadow: 0 6px 24px rgba(0,245,160,0.15) !important;
            transform: translateY(-2px) !important;
        }

        /* ── DIVIDER INSIDE FORM ── */
        .form-divider {
            display: flex; align-items: center; gap: 0.8rem;
            margin: 1.4rem 0;
        }
        .fd-line {
            flex:1; height:1px;
            background: linear-gradient(90deg, transparent, rgba(0,245,160,0.25), transparent);
        }
        .fd-text {
            font-size: 0.75rem;
            color: var(--text-muted);
            letter-spacing: 0.5px;
        }

        /* ── ALERT OVERRIDES ── */
        .stAlert {
            border-radius: 12px !important;
            border: 1px solid rgba(0,245,160,0.18) !important;
            background: rgba(4,14,30,0.8) !important;
            backdrop-filter: blur(12px) !important;
            font-family: 'DM Sans', sans-serif !important;
        }
        div[data-testid="stNotification"] {
            border-radius: 12px !important;
        }

        /* ── SPINNER ── */
        div[data-testid="stSpinner"] > div {
            border-color: #00f5a0 transparent transparent !important;
        }

        /* ── HERO SECTION (above columns) ── */
        .hero-section {
            position: relative; z-index: 2;
            text-align: center;
            padding: 2.8rem 1rem 0;
            animation: heroIn 1s ease both;
        }
        @keyframes heroIn {
            from { opacity:0; transform:translateY(-20px); }
            to   { opacity:1; transform:translateY(0); }
        }
        .hero-tagline {
            font-family: 'Syne', sans-serif;
            font-size: 0.78rem;
            letter-spacing: 3px;
            text-transform: uppercase;
            color: #00f5a0;
            margin-bottom: 0.4rem;
        }
        .hero-badge {
            display: inline-flex; align-items: center; gap: 0.4rem;
            background: rgba(0,245,160,0.08);
            border: 1px solid rgba(0,245,160,0.25);
            border-radius: 999px;
            padding: 0.3rem 1rem;
            font-size: 0.75rem;
            color: var(--text-muted);
            letter-spacing: 0.5px;
        }
        .hero-badge::before {
            content:'';
            width:7px; height:7px; border-radius:50%;
            background:#00f5a0;
            box-shadow: 0 0 8px #00f5a0;
            animation: blinkDot 1.8s ease-in-out infinite;
        }
        @keyframes blinkDot {
            0%,100%{ opacity:1; } 50%{ opacity:0.3; }
        }

        /* ── SCROLLBAR ── */
        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-track { background: var(--bg-deep); }
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(180deg,#00f5a0,#00d9f5);
            border-radius: 5px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────
#  ROTATING MEDICAL RING SVG
# ──────────────────────────────────────────────
def med_ring_svg():
    return """
    <div class="med-ring">
      <svg viewBox="0 0 220 220" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="rg1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#00f5a0"/>
            <stop offset="100%" stop-color="#00d9f5"/>
          </linearGradient>
          <linearGradient id="rg2" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#818cf8"/>
            <stop offset="100%" stop-color="#fb7185"/>
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="4" result="blur"/>
            <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
        </defs>
        <!-- Outer ring with dashes -->
        <g class="ring-outer" style="transform-origin:110px 110px">
          <circle cx="110" cy="110" r="100"
            fill="none" stroke="url(#rg1)" stroke-width="1.5"
            stroke-dasharray="8 6" opacity="0.55" filter="url(#glow)"/>
          <!-- Tick marks -->
          <circle cx="110" cy="12" r="4" fill="#00f5a0" opacity="0.9"/>
          <circle cx="208" cy="110" r="4" fill="#00d9f5" opacity="0.9"/>
          <circle cx="110" cy="208" r="4" fill="#00f5a0" opacity="0.9"/>
          <circle cx="12" cy="110" r="4" fill="#00d9f5" opacity="0.9"/>
        </g>
        <!-- Middle ring -->
        <g class="ring-inner" style="transform-origin:110px 110px">
          <circle cx="110" cy="110" r="75"
            fill="none" stroke="url(#rg2)" stroke-width="1"
            stroke-dasharray="12 8" opacity="0.4"/>
          <circle cx="110" cy="37" r="3" fill="#818cf8" opacity="0.8"/>
          <circle cx="183" cy="110" r="3" fill="#fb7185" opacity="0.8"/>
          <circle cx="110" cy="183" r="3" fill="#818cf8" opacity="0.8"/>
          <circle cx="37" cy="110" r="3" fill="#fb7185" opacity="0.8"/>
        </g>
        <!-- Solid inner ring -->
        <circle cx="110" cy="110" r="52"
          fill="none" stroke="rgba(0,245,160,0.12)" stroke-width="1"/>
        <!-- Core glowing circle -->
        <circle class="ring-core" cx="110" cy="110" r="30"
          fill="rgba(0,245,160,0.06)" stroke="url(#rg1)" stroke-width="1.5"
          filter="url(#glow)"/>
        <!-- Medical cross -->
        <path d="M103 95 h14 v10 h10 v14 h-10 v10 h-14 v-10 h-10 v-14 h10 z"
          fill="url(#rg1)" opacity="0.9" filter="url(#glow)"/>
        <!-- Heartbeat line -->
        <polyline
          points="65,110 80,110 88,95 96,125 104,103 112,118 120,110 155,110"
          fill="none" stroke="url(#rg1)" stroke-width="2"
          stroke-linecap="round" stroke-linejoin="round"
          opacity="0.75" filter="url(#glow)"/>
      </svg>
    </div>
    """


# ──────────────────────────────────────────────
#  ECG STRIP
# ──────────────────────────────────────────────
def ecg_strip():
    return """
    <div class="ecg-strip">
      <svg viewBox="0 0 1200 44" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="eg" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%"   stop-color="#00f5a0" stop-opacity="0"/>
            <stop offset="25%"  stop-color="#00f5a0" stop-opacity="1"/>
            <stop offset="75%"  stop-color="#00d9f5" stop-opacity="1"/>
            <stop offset="100%" stop-color="#00d9f5" stop-opacity="0"/>
          </linearGradient>
        </defs>
        <polyline
          points="0,22 50,22 65,22 72,6 80,38 88,10 96,34 104,22 170,22
                  220,22 235,22 242,6 250,38 258,10 266,34 274,22 340,22
                  390,22 405,22 412,6 420,38 428,10 436,34 444,22 510,22
                  560,22 575,22 582,6 590,38 598,10 606,34 614,22 680,22
                  730,22 745,22 752,6 760,38 768,10 776,34 784,22 850,22
                  900,22 915,22 922,6 930,38 938,10 946,34 954,22 1020,22
                  1070,22 1085,22 1092,6 1100,38 1108,10 1116,34 1124,22 1200,22"
          fill="none" stroke="url(#eg)" stroke-width="2"
          stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>
    """


# ──────────────────────────────────────────────
#  MAIN SHOW FUNCTION
# ──────────────────────────────────────────────
def show():
    inject_login_styles()

    # ── Floating orbs
    st.markdown(
        """
        <div class="orb-wrap">
          <div class="orb o1"></div>
          <div class="orb o2"></div>
          <div class="orb o3"></div>
          <div class="orb o4"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Floating medical particles
    st.markdown(
        """
        <div class="particles">
          <span class="particle p1">🧬</span>
          <span class="particle p2">💊</span>
          <span class="particle p3">🫀</span>
          <span class="particle p4">🔬</span>
          <span class="particle p5">🩺</span>
          <span class="particle p6">🧪</span>
          <span class="particle p7">💉</span>
          <span class="particle p8">🩻</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Vertical divider line
    # st.markdown('<div class="v-divider"></div>', unsafe_allow_html=True)

    show_logo_header()

    # ── Hero strip above columns
    st.markdown(
        f"""
        <div class="hero-section">
          <div class="hero-tagline">✦ {TAGLINE} ✦</div>
          <div style="height:0.6rem"></div>
          <span class="hero-badge">Secure clinical access</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ── CENTERED LOGIN FORM
    _, center_col, _ = st.columns([1, 1.2, 1])

    with center_col:
        st.markdown('<div class="right-zone">', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="auth-card">
            """,
            unsafe_allow_html=True,
        )
        st.markdown('<div class="auth-title">Welcome back</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="auth-sub">Sign in to view your dashboard, reports, and assessment history.</div>',
            unsafe_allow_html=True,
        )

        with st.form("login_form"):
            name = st.text_input("Full Name", placeholder="Enter your registered name")
            age  = st.number_input("Age", min_value=1, max_value=120, value=25, step=1)
            pwd  = st.text_input("Password", type="password", placeholder="Enter your password")
            st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Sign In →", use_container_width=True)

        if submitted:
            if not name.strip() or not pwd:
                st.error("Please complete all fields before signing in.")
            else:
                with st.spinner("Authenticating your account…"):
                    result = login_user(name, int(age), pwd)

                if result["ok"]:
                    st.session_state["authenticated"] = True
                    st.session_state["user"]          = result["user"]
                    st.session_state["page"]          = "dashboard"
                    st.success(f"✓  Welcome, {result['user']['name']}.")
                    st.rerun()
                else:
                    st.error(result["error"])

        # ── Divider + Create Account
        st.markdown(
            """
            <div class="form-divider">
              <div class="fd-line"></div>
              <div class="fd-text">New here?</div>
              <div class="fd-line"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Create Account", use_container_width=True, key="go_register"):
            st.session_state["page"] = "register"
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)   # close auth-card
        st.markdown("</div>", unsafe_allow_html=True)   # close right-zone