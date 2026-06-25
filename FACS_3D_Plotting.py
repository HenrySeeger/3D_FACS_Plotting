import pandas as pd
import streamlit as st
import plotly.express as px

uploaded_files = st.file_uploader("Upload FACS Data Folder Here", accept_multiple_files=True, type = "fcs")

files = []

for i, uploaded_file in enumerate(uploaded_files):
  files.append(pd.read_csv(uploaded_file))

file_names_text = st.text("")

files_selected = st.multiselect("Users", [file.name for file in uploaded_files], default=[])

if uploaded_files is not None and len(files) > 0:
  file_names_text.text([file.name for file in uploaded_files])
  fig = px.scatter_3d(files[0], x=' BV421-A', y=' Alexa Fluor 647-A', z=' GFP-A')
  fig.update_xaxes(title_text = "SREBP1")
  fig.update_yaxes(title_text = "BMRF1")
  # fig.update_zaxes(title_text = "SREBP1")
  st.plotly_chart(fig)