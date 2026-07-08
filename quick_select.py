import io
import zipfile
import streamlit as st

"Download a zip file of filtered fcs files here"

uploader = st.file_uploader(label = "Upload Files Here", type = ["fcs"], accept_multiple_files = True, key = "file_uploader")

case_sensitive = st.toggle(label = "Filter is case-sensitive", value = True)
filter_text = st.text_input("Input keyword here", value = "", key = "text_filter")

if uploader and filter_text:
  st.text(f"{len([file for file in uploader if (filter_text if case_sensitive else filter_text.lower()) in (file.name if case_sensitive else filter_text.lower())])} files selected")
  # Create an in-memory ZIP file
  zip_buffer = io.BytesIO()

  with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
    for uploaded_file in [file for file in uploader if (filter_text if case_sensitive else filter_text.lower()) in (file.name if case_sensitive else filter_text.lower())]:
      zip_file.writestr(
        uploaded_file.name,     # Filename inside the ZIP
        uploaded_file.getvalue() # File contents
      )

  zip_buffer.seek(0)

  st.download_button(
    "Download ZIP",
    data=zip_buffer,
    file_name="fcs_files.zip",
    mime="application/zip",
  )