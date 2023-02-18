import sqlite3
import streamlit as st
import pandas as pd
import uuid

from streamlit_qrcode_scanner import qrcode_scanner


def manage_entry():
    qr_code = qrcode_scanner(key="qrcode_scanner")

    if qr_code:
        st.write(qr_code)


def database_ops():
    pass


st.sidebar.markdown("""---""")
st.sidebar.title("Event Attendance App")
st.sidebar.markdown("Built with :heart: by [Ankur](https://instagram.com/raagarock)")
st.sidebar.markdown("""---""")

page_names_to_funcs = {
    "Manage Entry": manage_entry,
    "Database Ops": database_ops,
}

selected_page = st.sidebar.selectbox("Select a page", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]()
