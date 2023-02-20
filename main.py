import streamlit as st
from streamlit_qrcode_scanner import qrcode_scanner

from db_operations import (
    download_data,
    register_entry,
    reinitialize_db,
    show_db,
    upload_data,
)


def manage_entry():
    qr_code = qrcode_scanner(key="qrcode_scanner")
    if qr_code:
        st.write(qr_code)
        found = register_entry(qr_code)
        if found:
            st.success(found)
        else:
            st.error("No record found!")
            # st.markdown("## :red[No record found!]")


def database_view():

    st.markdown("# View Attendees Database")
    view_db = st.button("View Database")
    if view_db:
        show_db()
    st.markdown("""---""")

    st.markdown("# Reset Attendees Database")
    reset_db = st.button("Reset Database")
    if reset_db:
        reinitialize_db()
    st.markdown("""---""")


def database_admin():

    st.markdown(" # Download Master Data")
    download_data()
    st.markdown("""---""")

    st.markdown(" # Upload Master Data")
    upload_data()
    st.markdown("""---""")


st.sidebar.markdown("""---""")
st.sidebar.title("Event Attendance App")
st.sidebar.markdown("Built with :heart: by [Ankur](https://instagram.com/raagarock)")
st.sidebar.markdown("""---""")

page_names_to_funcs = {
    "Register Entry": manage_entry,
    "Database: Attendees": database_view,
    "Database: Master": database_admin,
}

selected_page = st.sidebar.selectbox("Select a page", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]()
