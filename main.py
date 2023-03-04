import streamlit as st
from streamlit_qrcode_scanner import qrcode_scanner

from db_operations import (
    download_data,
    register_entry,
    reinitialize_attendees_db,
    reinitialize_master_db,
    show_attendees_all,
    show_attendees_today,
    show_master,
    upload_data,
)


def manage_entry():
    if qr_code := qrcode_scanner(key="qrcode_scanner"):
        st.write(qr_code)
        if found := register_entry(qr_code):
            st.success(found)
        else:
            st.error("No record found!")
            # st.markdown("## :red[No record found!]")


def database_view():

    st.markdown("# View Today's Attendees")
    if st.button("Get today's records"):
        show_attendees_today()
    st.markdown("""---""")

    st.markdown("# View Attendees Database")
    if st.button("Get all records"):
        show_attendees_all()
    st.markdown("""---""")

    st.markdown("# Reset Attendees Database")
    if st.button("Reset Database"):
        reinitialize_attendees_db()
    st.markdown("""---""")


def database_admin():

    st.markdown("# View Master Database")
    if st.button("View Database"):
        show_master()
    st.markdown("""---""")

    st.markdown(" # Download Master Data")
    download_data()
    st.markdown("""---""")

    st.markdown("# Reset Master Database")
    if st.button("Reset Database"):
        reinitialize_master_db()
    st.markdown("""---""")

    st.markdown(" # Upload Master Data")
    st.error("WARNING: Uploading will overwrite the existing data in the database.")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type="csv",
        accept_multiple_files=False,
    )
    if st.button("Upload to DB"):
        if uploaded_file is not None:
            upload_data(uploaded_file)
        else:
            st.write("Please select file to upload!")

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
