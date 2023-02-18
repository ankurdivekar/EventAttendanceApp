import sqlite3
import streamlit as st
import pandas as pd
import uuid

from streamlit_qrcode_scanner import qrcode_scanner

qr_code = qrcode_scanner(key="qrcode_scanner")

if qr_code:
    st.write(qr_code)
