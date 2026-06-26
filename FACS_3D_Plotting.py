import pandas as pd
import streamlit as st
import plotly.express as px

if "uploader_key" not in st.session_state:
  st.session_state.uploader_key = 0

uploaded_files = st.file_uploader("Upload FACS Data Folder Here", accept_multiple_files = True, type = ["fcs"], key=f"uploader_key_{st.session_state.uploader_key}")

def clear_files_on_click():
  if uploaded_files is not None:
    st.session_state.uploader_key += 1

clear_files = st.button("Clear Uploaded Files", on_click = clear_files_on_click)#, help = "Warning: Clearing the downloads automatically requires rerunning the page")

files = []

# for i, uploaded_file in enumerate(uploaded_files):
#   files.append(pd.read_csv(uploaded_file))

files_selected = st.multiselect("Users", [file.name for file in uploaded_files], default=[])

# if uploaded_files is not None:# and len(files) > 0:
  # fig = px.scatter_3d(files[0], x=' BV421-A', y=' Alexa Fluor 647-A', z=' GFP-A')
  # fig.update_xaxes(title_text = "SREBP1")
  # fig.update_yaxes(title_text = "BMRF1")
  # # fig.update_zaxes(title_text = "SREBP1")
  # st.plotly_chart(fig)