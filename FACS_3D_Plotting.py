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

def files_selected_formatting(file):
  return file["name"][:file["name"].rfind(".")]

files_selected = st.multiselect(label = "Files", options = [file for file in st.session_state.facs_dataframes if "._" not in file["name"]], format_func = files_selected_formatting, default = [], placeholder = "No files selected")

# if uploaded_files is not None:# and len(files) > 0:
#   st.text(f"{[file.name for file in uploaded_files]}")
  # fig = px.scatter_3d(files[0], x=' BV421-A', y=' Alexa Fluor 647-A', z=' GFP-A')
  # fig.update_xaxes(title_text = "SREBP1")
  # fig.update_yaxes(title_text = "BMRF1")
  # # fig.update_zaxes(title_text = "SREBP1")
  # st.plotly_chart(fig)

selectbox_columns = st.columns(3)

with selectbox_columns[0]:
  x_select = st.selectbox(label = "x-axis", options = ["No Selection"] + list(set(key for df in files_selected for key in df["data"].keys())), key = "x-axis", disabled = len(files_selected) == 0)
with selectbox_columns[1]:
  y_select = st.selectbox(label = "y-axis", options = ["No Selection"] + list(set(key for df in files_selected for key in df["data"].keys())), key = "y-axis", disabled = len(files_selected) == 0)
with selectbox_columns[2]:
  z_select = st.selectbox(label = "z-axis", options = ["No Selection"] + list(set(key for df in files_selected for key in df["data"].keys())), key = "z-axis", disabled = len(files_selected) == 0)

def num_axes():
  st.text((x_select != "No Selection") + (y_select != "No Selection") + (z_select != "No Selection"))
  return (x_select != "No Selection") + (y_select != "No Selection") + (z_select != "No Selection")

match num_axes():
  case 1:
    for select in [x_select, y_select, z_select]:
      if select != "No Selection":
        # Histogram code here
        st.text("Single")
        break
  case 2:
    for select in [x_select, y_select, z_select]:
      selections = [val for val in [x_select, y_select, z_select] if val != select]
      if select == "No Selection":
        for file in files_selected:
          pxFig = px.scatter(x = file["data"][selections[0]], y = file["data"][selections[1]])
        pxFig.update_xaxes(showline = True, linecolor = 'black', linewidth = 2, title_font_color = "black", tickfont_color = "black")
        pxFig.update_yaxes(showline = True, linecolor = 'black', linewidth = 2, title_font_color = "black", tickfont_color = "black", showgrid = False)
        pxFig.update_layout(paper_bgcolor = "white", plot_bgcolor = "white", legend_font_color = "black", legend_title_font_color = "black")
        st.plotly_chart(pxFig)
        break
  case 3:
    # 3D scatter code here
    st.text("Triple")