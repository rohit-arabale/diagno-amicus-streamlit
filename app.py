import os
import sys

import streamlit as st

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from config.branding import APP_NAME, TAGLINE

st.set_page_config(
    page_title=f"{APP_NAME} - {TAGLINE}",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

css_path = os.path.join(ROOT, "assets", "styles.css")
with open(css_path, encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown(
    """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap" rel="stylesheet">
""",
    unsafe_allow_html=True,
)

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "page" not in st.session_state:
    st.session_state["page"] = "login"
if "user" not in st.session_state:
    st.session_state["user"] = {}

with st.sidebar:
    st.markdown(
        f"""
        <div style="text-align:center; padding:0.8rem 0 1.4rem;">
            <div style="font-family:'Syne',sans-serif; font-size:1.6rem; font-weight:800; background:-webkit-linear-gradient(135deg, #10b981, #34d399); -webkit-background-clip:text; -webkit-text-fill-color:transparent; text-shadow:0 5px 15px rgba(16,185,129,0.1);">
                {APP_NAME}
            </div>
            <div style="font-size:0.78rem; color:rgba(22,40,29,0.65); font-style:italic; margin-top:0.25rem;">
                {TAGLINE}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state["authenticated"]:
        user_name = st.session_state["user"].get("name", "User")
        st.markdown(
            f"""
            <div style="background:rgba(16,185,129,0.1); border:1px solid rgba(16,185,129,0.25);
                        border-radius:12px; padding:0.8rem 0.95rem; margin-bottom:1rem; font-size:0.88rem; backdrop-filter:blur(10px);">
                <strong style="color:#059669;">Signed in as {user_name}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("**Navigation**")
        if st.button("Dashboard", use_container_width=True, key="nav_dash"):
            st.session_state["page"] = "dashboard"
            st.rerun()
        if st.button("History", use_container_width=True, key="nav_history"):
            st.session_state["page"] = "history"
            st.rerun()
        if st.button("Full Analysis", use_container_width=True, key="nav_full"):
            st.session_state["page"] = "predictor"
            st.session_state["predictor_mode"] = "full"
            st.rerun()
        if st.button("Skin Assessment", use_container_width=True, key="nav_skin"):
            st.session_state["page"] = "predictor"
            st.session_state["predictor_mode"] = "skin"
            st.rerun()
        if st.button("Heart Risk", use_container_width=True, key="nav_heart"):
            st.session_state["page"] = "predictor"
            st.session_state["predictor_mode"] = "heart"
            st.rerun()
        if st.button("Diabetes Risk", use_container_width=True, key="nav_diab"):
            st.session_state["page"] = "predictor"
            st.session_state["predictor_mode"] = "diabetes"
            st.rerun()
        if st.button("Liver Risk", use_container_width=True, key="nav_liver"):
            st.session_state["page"] = "predictor"
            st.session_state["predictor_mode"] = "liver"
            st.rerun()

        st.markdown("---")
        if st.button("Logout", use_container_width=True, key="nav_logout"):
            st.session_state["authenticated"] = False
            st.session_state["user"] = {}
            st.session_state["page"] = "login"
            st.rerun()
    else:
        if st.button("Login", use_container_width=True, key="nav_login"):
            st.session_state["page"] = "login"
            st.rerun()
        if st.button("Register", use_container_width=True, key="nav_reg"):
            st.session_state["page"] = "register"
            st.rerun()

    from medical_knowledge import NORMAL_RANGES

    st.markdown("---")
    with st.expander("Normal Ranges"):
        for param, (lo, hi) in NORMAL_RANGES.items():
            st.markdown(
                f"<div style='font-size:0.82rem; color:rgba(22,40,29,0.75);'><strong>{param}</strong>: {lo} - {hi}</div>",
                unsafe_allow_html=True,
            )

page = st.session_state["page"]
auth = st.session_state["authenticated"]

if not auth and page not in ("login", "register"):
    page = "login"
    st.session_state["page"] = "login"

if page == "login":
    from pages import login

    login.show()
elif page == "register":
    from pages import register

    register.show()
elif page == "dashboard":
    from pages import dashboard

    dashboard.show()
elif page == "predictor":
    from pages import predictor

    predictor.show()
elif page == "history":
    from pages import history

    history.show()
else:
    from pages import login

    login.show()
