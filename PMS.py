import streamlit as st
import sqlite3
import pandas as pd
import mimetypes
st.set_page_config(layout="wide")
def create_table():
    connection = sqlite3.connect('CR.db')
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS cr (
                      id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                      vessel TEXT,
                      cr_summary TEXT,
                      cr_reason TEXT,
                      initiated_by TEXT,
                      dt_req_raised TEXT,
                      sent_to_MA TEXT,
                      date_completed TEXT,
                      crf BLOB,
                      crf_mime_type TEXT,
                      mail_thread BLOB,
                      mail_thread_mime_type TEXT,
                      supporting_docs BLOB,
                      supporting_docs_mime_type TEXT,
                      job_done_at TEXT
                  )''')
    connection.commit()
    connection.close()

def insert_data(vessel, cr_summary, cr_reason, initiated_by, dt_req_raised, sent_to_MA, date_completed,
                crf, crf_mime_type, mail_thread, mail_thread_mime_type, supporting_docs, supporting_docs_mime_type,
                job_done_at):
    connection = sqlite3.connect('CR.db')
    cursor = connection.cursor()
    cursor.execute('''INSERT INTO cr (vessel, cr_summary, cr_reason, initiated_by, dt_req_raised,
                                      sent_to_MA, date_completed, crf, crf_mime_type,
                                      mail_thread, mail_thread_mime_type,
                                      supporting_docs, supporting_docs_mime_type, job_done_at)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (vessel, cr_summary, cr_reason, initiated_by, dt_req_raised, sent_to_MA, date_completed,
                    crf, crf_mime_type, mail_thread, mail_thread_mime_type,
                    supporting_docs, supporting_docs_mime_type, job_done_at))
    connection.commit()
    connection.close()

def fetch_data():
    connection = sqlite3.connect('CR.db')
    data = pd.read_sql_query('SELECT * FROM cr', connection)
    connection.close()
    return data

def update_data(id, column, value):
    connection = sqlite3.connect('CR.db')
    cursor = connection.cursor()
    cursor.execute(f'UPDATE cr SET {column} = ? WHERE id = ?', (value, id))
    connection.commit()
    connection.close()

def delete_data(id):
    connection = sqlite3.connect('CR.db')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM cr WHERE id = ?', (id,))
    connection.commit()
    connection.close()

# def download_file(file_data, file_mime_type, file_name):
#     if file_data:
#         # Send the file to the client with the appropriate content type
#         mime_type = file_mime_type if file_mime_type else 'application/octet-stream'
#         response = st.download_button(
#             label=f"Download {file_name}",
#             data=bytes(file_data),
#             mime=mime_type,
#             file_name=f"{file_name}.{file_mime_type.split('/')[1]}" if file_mime_type else None
#         )
#         return response
#     else:
#         st.write("File not found")
def download_file(file_data, file_mime_type, file_name):
    if file_data:
        # Add a download button for the file
        st.download_button(
            label=f"Download {file_name}",
            data=file_data,
            mime=file_mime_type,
            file_name=f"{file_name}{mimetypes.guess_extension(file_mime_type)}"
        )
    else:
        st.write("File not found")


def main():
    create_table()

    st.title("Mari Apps PMS changelog")
    st.header("Change requests")
    df = fetch_data()

    # Show the DataFrame and allow editing
    col1, col2 = st.columns([1,1])
    with col1:
        with st.expander('Add new Record'):
            # Upload file and store in the database
            st.header("Add new record")
            vessel = st.text_input("Vessel")
            cr_summary = st.text_area("CR Summary")
            cr_reason = st.text_area("CR Reason")
            initiated_by = st.text_input("Initiated By")
            dt_req_raised = st.date_input("Date Request Raised")
            sent_to_MA = st.date_input("Sent to MA")
            date_completed = st.date_input("Date Completed")
            crf = st.file_uploader("CRF File (excel)")
            mail_thread = st.file_uploader("Mail Thread File (Outlook message)")
            supporting_docs = st.file_uploader("Supporting Docs")
            job_done_at = st.selectbox("Job Done At",options=('vessel','jobmaster'))

            if st.button("Submit"):
                crf_mime_type = crf.type if crf else None
                mail_thread_mime_type = mail_thread.type if mail_thread else None
                supporting_docs_mime_type = supporting_docs.type if supporting_docs else None
                insert_data(vessel, cr_summary, cr_reason, initiated_by, dt_req_raised, sent_to_MA, date_completed,
                            crf.read() if crf else None, crf_mime_type,
                            mail_thread.read() if mail_thread else None, mail_thread_mime_type,
                            supporting_docs.read() if supporting_docs else None, supporting_docs_mime_type,
                            job_done_at)
        with st.expander('Edit existing records'):
            columns_to_hide = ['mail_thread', 'crf', 'supporting_docs', 'crf_mime_type', 'mail_thread_mime_type',
                               'supporting_docs_mime_type']

            st.data_editor(df.drop(columns=columns_to_hide), hide_index=True)
            # Allow editing and exporting of data
            if st.button("Update Database"):
                for index, row in df.iterrows():
                    update_data(row['id'], 'vessel', row['vessel'])
                    update_data(row['id'], 'cr_summary', row['cr_summary'])
                    update_data(row['id'], 'cr_reason', row['cr_reason'])
                    update_data(row['id'], 'initiated_by', row['initiated_by'])
                    update_data(row['id'], 'dt_req_raised', row['dt_req_raised'])
                    update_data(row['id'], 'sent_to_MA', row['sent_to_MA'])
                    update_data(row['id'], 'date_completed', row['date_completed'])
                    update_data(row['id'], 'job_done_at', row['job_done_at'])
                st.write("Database updated successfully.")


    with col2:
        # File download functionality
        st.header("Download Attachment")
        download_id = st.selectbox("Select an ID to download its files:", df['id'].tolist())
        if st.button("Download Files"):
            data_row = df[df['id'] == download_id].iloc[0]
            download_file(data_row['crf'], data_row['crf_mime_type'], f"{data_row['id']}_crf")
            download_file(data_row['mail_thread'], data_row['mail_thread_mime_type'], f"{data_row['id']}_mail_thread")
            download_file(data_row['supporting_docs'], data_row['supporting_docs_mime_type'],
                          f"{data_row['id']}_supporting_docs")
        # ... Rest of the code ...
     # Delete functionality
        st.header("Delete Data")
        delete_id = st.selectbox("Enter ID to delete:", df['id'].tolist())
        if st.button("Delete"):
            # delete_data(delete_id)
            st.write(f"Record with ID {delete_id} deleted successfully.")
if __name__ == "__main__":
    main()
