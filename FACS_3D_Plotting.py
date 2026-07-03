import io
import flowio
import numpy as np
import pandas as pd
import streamlit as st
# import radio_buttons as rad
import plotly.express as px

st.session_state.setdefault("facs_dataframes", [])
st.session_state.setdefault("uploader_key", 0)


variables = {}

@st.cache_data
def load_fcs(uploaded_file_bytes):
  flow = flowio.FlowData(io.BytesIO(uploaded_file_bytes))
  return pd.DataFrame(flow.as_array(), columns = flow.pnn_labels), flow.text

def load_all_fcs():
  files = st.session_state[f"uploader_key_{st.session_state.uploader_key}"]
  if files:
    for file in [file for file in files if "._" not in file.name]:
      df, metadata = load_fcs(file.getvalue())
      st.session_state.facs_dataframes.append({"name" : file.name, "data" : df, "metadata" : metadata})
  else:
    st.session_state.facs_dataframes = []

def clear_files_on_click():
  if uploaded_files is not None:
    st.session_state.uploader_key += 1

uploaded_files = st.file_uploader("Upload FCS file", type = ["fcs"], key=f"uploader_key_{st.session_state.uploader_key}", accept_multiple_files = True, on_change = load_all_fcs)

clear_files = st.button("Clear Uploaded Files", on_click = clear_files_on_click) #, help = "Warning: Clearing the downloads automatically requires rerunning the page")

# for i, uploaded_file in enumerate(uploaded_files):
#   files.append(pd.read_csv(uploaded_file))

files_selected = st.multiselect("Files", [file.name[:file.name.rfind(".")] for file in uploaded_files if "._" not in file.name], default=[])

if uploaded_files is not None:# and len(files) > 0:
  st.text(f"{[file.name for file in uploaded_files]}")
  # fig = px.scatter_3d(files[0], x=' BV421-A', y=' Alexa Fluor 647-A', z=' GFP-A')
  # fig.update_xaxes(title_text = "SREBP1")
  # fig.update_yaxes(title_text = "BMRF1")
  # # fig.update_zaxes(title_text = "SREBP1")
  # st.plotly_chart(fig)

# Should make three inter-connected dropdowns instead of using radio buttons
# if len(st.session_state.facs_dataframes) > 0:
#   rad.radio_buttons_exclusive(row_labels = list(set(key for df in st.session_state.facs_dataframes for key in df["data"].keys())), col_headers = ["x-axis", "y-axis", "z-axis"])

# if len(files_selected) == 3:
#   print("plot stuff")