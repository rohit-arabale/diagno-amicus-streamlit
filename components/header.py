import base64
import os

import streamlit as st


def show_logo_header(size=180):
    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <div style="display:flex; justify-content:center; padding:1.2rem 0 1.5rem;">
                <img src="data:image/png;base64,{data}" width="{size}" alt="Diagno Amicus logo" 
                     style="filter: drop-shadow(0 0 12px rgba(255,255,255,0.4)) drop-shadow(0 0 24px rgba(0,245,160,0.2)); 
                            transition: transform 0.3s ease, filter 0.3s ease;
                            border-radius: 8px;"
                     onmouseover="this.style.transform='scale(1.05)'; this.style.filter='drop-shadow(0 0 16px rgba(255,255,255,0.6)) drop-shadow(0 0 32px rgba(0,245,160,0.4))';"
                     onmouseout="this.style.transform='scale(1)'; this.style.filter='drop-shadow(0 0 12px rgba(255,255,255,0.4)) drop-shadow(0 0 24px rgba(0,245,160,0.2))';">
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        from config.branding import APP_NAME

        st.markdown(
            f"<h1 style='text-align:center; font-family:Syne; font-weight:800; background:-webkit-linear-gradient(135deg, #10b981, #34d399); -webkit-background-clip:text; -webkit-text-fill-color:transparent; font-size:3rem; padding:1rem 0; text-shadow:0 10px 30px rgba(16,185,129,0.2);'>{APP_NAME}</h1>",
            unsafe_allow_html=True,
        )
