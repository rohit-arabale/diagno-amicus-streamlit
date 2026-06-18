import os
import sys
import time

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from components.header import show_logo_header
from config.branding import APP_NAME, TAGLINE
from database.db_manager import create_user


def show():
    show_logo_header()

    _, center, _ = st.columns([1, 1.35, 1])
    with center:
        st.markdown('<div class="auth-title">Create your account</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="auth-sub">Register to access health assessments, saved reports, and history.</div>',
            unsafe_allow_html=True,
        )

        with st.form("register_form"):
            name = st.text_input("Full Name", placeholder="Your full name")
            mobile = st.text_input("Mobile Number", placeholder="+91 XXXXX XXXXX")
            col_a, col_b = st.columns(2)
            with col_a:
                age = st.number_input("Age", min_value=1, max_value=120, value=25, step=1)
            with col_b:
                gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"])
            pwd = st.text_input("Password", type="password", placeholder="Minimum 6 characters")
            pwd2 = st.text_input("Confirm Password", type="password", placeholder="Repeat password")

            submitted = st.form_submit_button("Create Account", use_container_width=True)

        if submitted:
            errors = []
            if not name.strip():
                errors.append("Name is required.")
            if not mobile.strip():
                errors.append("Mobile number is required.")
            if not pwd:
                errors.append("Password is required.")
            if len(pwd) < 6:
                errors.append("Password must be at least 6 characters.")
            if pwd != pwd2:
                errors.append("Passwords do not match.")

            if errors:
                for error in errors:
                    st.error(error)
            else:
                with st.spinner("Creating your account..."):
                    result = create_user(name, mobile, int(age), gender, pwd)

                if result["ok"]:
                    st.success("Account created successfully. Please sign in.")
                    time.sleep(1.2)
                    st.session_state["page"] = "login"
                    st.rerun()
                else:
                    st.error(result["error"])

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            "<div style='text-align:center;color:rgba(22,40,29,0.65);font-size:0.9rem;'>"
            "Already registered?</div>",
            unsafe_allow_html=True,
        )
        if st.button("Sign In", use_container_width=True, key="go_login"):
            st.session_state["page"] = "login"
            st.rerun()

    st.markdown(
        f"""
        <div class="da-footer">
            <strong>{APP_NAME}</strong> | {TAGLINE}<br>
            Clinical intelligence platform for educational use only.
        </div>
        """,
        unsafe_allow_html=True,
    )
