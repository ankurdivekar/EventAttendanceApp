import datetime
import random
import sqlite3
import uuid
from datetime import date

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
    if "ABBF" not in qr_code:
        return None

    qr_code = qr_code.split(":")[1]
    # Find the entry in the master table
    with create_connection(st.secrets["db_file"]) as conn:

        query = conn.execute(
            f"SELECT * FROM {st.secrets['master_table_name']} WHERE UUID ='{qr_code}'"
        )
        if data := query.fetchall():
            cols = [column[0] for column in query.description]
            results_df = pd.DataFrame.from_records(data=data, columns=cols)
            # st.dataframe(results_df)

            try:
                # Write to the attendance table
                cur = conn.cursor()
                cur.execute(
                    f"INSERT INTO {st.secrets['attendees_table_name']} (UUID, \
                    FirstName, LastName, Category, Date, Time) \
                        VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        results_df.UUID.iloc[0],
                        results_df.FirstName.iloc[0],
                        results_df.LastName.iloc[0],
                        results_df.Category.iloc[0],
                        str(date.today()),
                        str(datetime.datetime.now().strftime("%H:%M:%S")),
                    ),
                )
                conn.commit()

                return f"{results_df.Category.iloc[0]}: {results_df.FirstName.iloc[0]} {results_df.LastName.iloc[0]}"

            except sqlite3.IntegrityError:
                return f"{results_df.Category.iloc[0]}: {results_df.FirstName.iloc[0]} {results_df.LastName.iloc[0]}"

            except Exception as e:
                st.write(e)
                return None

        else:
            return None


def show_attendees_today():
    with create_connection(st.secrets["db_file"]) as conn:
        # st.write(conn)  # success message?

        query = conn.execute(
            f"SELECT * FROM {st.secrets['attendees_table_name']} WHERE Date = '{str(date.today())}'"
        )
        cols = [column[0] for column in query.description]
        results_df = pd.DataFrame.from_records(data=query.fetchall(), columns=cols)

        st.write(f"Attendees today: {len(results_df)}")
        st.dataframe(results_df)


def show_attendees_all():
    with create_connection(st.secrets["db_file"]) as conn:
        # st.write(conn)  # success message?

        query = conn.execute(f"SELECT * FROM {st.secrets['attendees_table_name']}")
        cols = [column[0] for column in query.description]
        results_df = pd.DataFrame.from_records(data=query.fetchall(), columns=cols)

        st.write(f"Total attendees: {len(results_df)}")
        st.dataframe(results_df)


def show_master():
    with create_connection(st.secrets["db_file"]) as conn:
        # st.write(conn)  # success message?

        st.write("Master Table")
        query = conn.execute(f"SELECT * FROM {st.secrets['master_table_name']}")
        cols = [column[0] for column in query.description]
        results_df = pd.DataFrame.from_records(data=query.fetchall(), columns=cols)
        st.dataframe(results_df)


def reinitialize_master_db():
    with create_connection(st.secrets["db_file"]) as conn:
        st.write(conn)  # success message?
        cur = conn.cursor()

        # Drop and recreate the master table
        cur.execute(f"DROP TABLE IF EXISTS {st.secrets['master_table_name']}")
        cur.execute(
            f"CREATE TABLE {st.secrets['master_table_name']} (UUID, \
                FirstName TEXT, LastName TEXT, \
                MobileNumber TEXT, EmailAddress TEXT, Category TEXT, \
                UNIQUE(UUID, MobileNumber))"
        )
        conn.commit()


def reinitialize_attendees_db():
    with create_connection(st.secrets["db_file"]) as conn:
        # st.write(conn)  # success message?
        cur = conn.cursor()

        # Reset Attendance Table
        cur.execute(f"DROP TABLE IF EXISTS {st.secrets['attendees_table_name']}")
        cur.execute(
            f"CREATE TABLE {st.secrets['attendees_table_name']} (UUID, \
                FirstName TEXT, LastName TEXT, \
                Category TEXT, Date TEXT, Time TEXT, UNIQUE(UUID, Date))"
        )
        conn.commit()


def download_data():
    with create_connection(st.secrets["db_file"]) as conn:
        # st.write(conn)  # success message?

        query = conn.execute(f"SELECT * FROM {st.secrets['master_table_name']}")
        cols = [column[0] for column in query.description]
        results_df = pd.DataFrame.from_records(data=query.fetchall(), columns=cols)
        st.download_button(
            label="Download Data",
            data=results_df.to_csv(index=False),
            file_name="Master_Data.csv",
            mime="text/csv",
        )


def upload_data(uploaded_file):
    # read csv
    try:
        print(50 * "____")
        # Read CSV to dataframe and fill UUID column with new UUIDs where NaN
        df = pd.read_csv(uploaded_file, dtype=str).set_index("UUID")
        # print(df)
        with create_connection(st.secrets["db_file"]) as conn:
            overwrite_table_from_df(conn, st.secrets["master_table_name"], df)
    except Exception as e:
        st.write(e)


# TODO Rename this here and in `upload_data`
def overwrite_table_from_df(conn, table, df):
    cur = conn.cursor()
    cur.execute(f"DROP TABLE IF EXISTS {table}")
    df.to_sql(name=table, con=conn)
    st.write("Data uploaded successfully. These are the first 5 rows.")
    st.dataframe(df.head(5))
    conn.commit()
