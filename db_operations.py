import sqlite3
from datetime import datetime, date
import pandas as pd
import streamlit as st


def create_connection(db_file):
    """create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Exception as e:
        st.write(e)

    return conn


def register_entry(qr_code):
    # Find the entry in the master table
    with create_connection(st.secrets["db_file"]) as conn:

        query = conn.execute(
            f"SELECT * FROM {st.secrets['master_table_name']} WHERE UUID ='{qr_code}'"
        )
        data = query.fetchall()
        # print(data)
        if data:
            cols = [column[0] for column in query.description]
            results_df = pd.DataFrame.from_records(data=data, columns=cols)
            # st.dataframe(results_df)

            try:
                # Write to the attendance table
                cur = conn.cursor()
                cur.execute(
                    f"INSERT INTO {st.secrets['attendees_table_name']} (UUID, \
                    FirstName, LastName, MobileNo, Email, Date, Time) \
                        VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        results_df.UUID.iloc[0],
                        results_df.FirstName.iloc[0],
                        results_df.LastName.iloc[0],
                        results_df.MobileNo.iloc[0],
                        results_df.Email.iloc[0],
                        str(date.today()),
                        str(datetime.now().strftime("%H:%M:%S")),
                    ),
                )
                conn.commit()

                return f"{results_df.FirstName.iloc[0]} {results_df.LastName.iloc[0]}"

            except sqlite3.IntegrityError:
                return f"{results_df.FirstName.iloc[0]} {results_df.LastName.iloc[0]}"

        else:
            return None


def show_db():
    with create_connection(st.secrets["db_file"]) as conn:
        st.write(conn)  # success message?

        st.write("Attendees Table")
        query = conn.execute(f"SELECT * FROM {st.secrets['attendees_table_name']}")
        cols = [column[0] for column in query.description]
        results_df = pd.DataFrame.from_records(data=query.fetchall(), columns=cols)
        st.dataframe(results_df)

        st.write("Master Table")
        query = conn.execute(f"SELECT * FROM {st.secrets['master_table_name']}")
        cols = [column[0] for column in query.description]
        results_df = pd.DataFrame.from_records(data=query.fetchall(), columns=cols)
        st.dataframe(results_df)


def reinitialize_db():
    with create_connection(st.secrets["db_file"]) as conn:
        st.write(conn)  # success message?
        cur = conn.cursor()

        # Reset Attendance Table
        cur.execute(f"DROP TABLE IF EXISTS {st.secrets['attendees_table_name']}")
        cur.execute(
            f"CREATE TABLE {st.secrets['attendees_table_name']} (UUID, \
                FirstName TEXT, LastName TEXT, \
                MobileNo TEXT, Email TEXT, Date TEXT, Time TEXT, UNIQUE(UUID, Date))"
        )

        # # Reset {st.secrets['master_table_name']} Table
        # cur.execute(f"DROP TABLE IF EXISTS {st.secrets['master_table_name']}")
        # cur.execute(
        #     f"CREATE TABLE {st.secrets['master_table_name']} (UUID UNIQUE, \
        #         FirstName TEXT, LastName TEXT, \
        #         MobileNo TEXT PRIMARY KEY, Email TEXT, City TEXT)"
        # )

        # cur.execute(
        #     f"INSERT INTO {st.secrets['master_table_name']} (UUID, \
        #         FirstName, LastName, MobileNo, Email, City) VALUES (?, ?, ?, ?, ?, ?)",
        #     (
        #         str(uuid.uuid4()),
        #         "Ankur",
        #         "Divekar",
        #         "1111111111",
        #         "ankur@streamlit.com",
        #         "Mumbai",
        #     ),
        # )
        # cur.execute(
        #     f"INSERT INTO {st.secrets['master_table_name']} (UUID, \
        #         FirstName, LastName, MobileNo, Email, City) VALUES (?, ?, ?, ?, ?, ?)",
        #     (
        #         str(uuid.uuid4()),
        #         "Meghana",
        #         "Dharap",
        #         "2222222222",
        #         "meghana@streamlit.com",
        #         "Mumbai",
        #     ),
        # )
        # cur.execute(
        #     f"INSERT INTO {st.secrets['master_table_name']} (UUID, \
        #         FirstName, LastName, MobileNo, Email, City) VALUES (?, ?, ?, ?, ?, ?)",
        #     (
        #         str(uuid.uuid4()),
        #         "Divyanshu",
        #         "Ganatra",
        #         "3333333333",
        #         "divyanshu@streamlit.com",
        #         "Pune",
        #     ),
        # )
        # cur.execute(
        #     f"INSERT INTO {st.secrets['master_table_name']} (UUID, \
        #         FirstName, LastName, MobileNo, Email, City) VALUES (?, ?, ?, ?, ?, ?)",
        #     (
        #         str(uuid.uuid4()),
        #         "Nimisha",
        #         "Ganatra",
        #         "4444444444",
        #         "nimisha@streamlit.com",
        #         "Pune",
        #     ),
        # )
        # cur.execute(
        #     f"INSERT INTO {st.secrets['master_table_name']} (UUID, \
        #         FirstName, LastName, MobileNo, Email, City) VALUES (?, ?, ?, ?, ?, ?)",
        #     (
        #         str(uuid.uuid4()),
        #         "Khushroo",
        #         "Mehta",
        #         "5555555555",
        #         "khushroo@streamlit.com",
        #         "Pune",
        #     ),
        # )
        conn.commit()


def upload_data():
    st.error("WARNING: Uploading will overwrite the existing data in the database.")
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        # read csv
        try:
            df = pd.read_csv(uploaded_file)
            with create_connection(st.secrets["db_file"]) as conn:
                cur = conn.cursor()
                cur.execute(f"DROP TABLE IF EXISTS {st.secrets['master_table_name']}")
                conn.commit()
                df.to_sql(name=st.secrets["master_table_name"], con=conn)
                st.write("Data uploaded successfully. These are the first 5 rows.")
                st.dataframe(df.head(5))

        except Exception as e:
            st.write(e)
