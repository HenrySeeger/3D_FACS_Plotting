import io
import math
import flowio
import textwrap
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import text_formatting as tf
import matplotlib.pyplot as plt
import plotly.graph_objects as go

st.session_state.setdefault("facs_dataframes",[])
st.session_state.setdefault("uploader_key", 0)

@st.cache_data
def load_fcs(uploaded_file_bytes):
  flow = flowio.FlowData(io.BytesIO(uploaded_file_bytes))
  return pd.DataFrame(flow.as_array(), columns = flow.pnn_labels), flow.text

def load_all_fcs():
  """Loads all the fcs files from the file uploader to Pandas dataframes. The file name, data (newly created Pandas dataframe), and metadata are stored in a dict {"name", "data", "metadata"}, which is stored in the list contained in st.session_state.facs_dataframes.

  Args:
    None:
    
  Returns:
    None:
  """
  st.session_state.facs_dataframes = []
  files = st.session_state[f"uploader_key_{st.session_state.uploader_key}"] # Could I use `uploaded_files` in places of `files`?
  if files:
    for file in [file for file in files if "._" not in file.name and "Unmixed" in file.name]:
      if file.name not in [file2["name"] for file2 in st.session_state.facs_dataframes]:
        df, metadata = load_fcs(file.getvalue())
        st.session_state.facs_dataframes.append({"name" : file.name, "data" : df, "metadata" : metadata})
  else:
    st.session_state.facs_dataframes = []

def clear_files_on_click():
  if uploaded_files is not None:
    st.session_state.uploader_key += 1

uploaded_files = st.file_uploader("Upload FCS file", type = ["fcs"], key=f"uploader_key_{st.session_state.uploader_key}", accept_multiple_files = True, on_change = load_all_fcs)

clear_files = st.button("Clear Uploaded Files", on_click = clear_files_on_click) #, help = "Warning: Clearing the downloads automatically requires rerunning the page")

st.text([file["name"] for file in st.session_state.facs_dataframes])

selectbox_columns = st.columns(2)

with selectbox_columns[0]:
  x_select = st.selectbox(label = "x-axis", options = ["No Selection"] + list(set(key for df in st.session_state.facs_dataframes for key in df["data"].keys())), key = "x-axis", disabled = len(st.session_state.facs_dataframes) == 0)
with selectbox_columns[1]:
  y_select = st.selectbox(label = "y-axis", options = ["No Selection"] + list(set(key for df in st.session_state.facs_dataframes for key in df["data"].keys())), key = "y-axis", disabled = len(st.session_state.facs_dataframes) == 0)

def filter_cells(df):
  # Live Cells
  def oval(x, y, semi_major, semi_minor, x_offset, y_offset, rads = 0, default_sin = None, default_cos = None):
    sin_theta = math.sin(rads) if default_sin is None else default_sin
    cos_theta = math.cos(rads) if default_cos is None else default_cos
    return ((x - x_offset) * cos_theta - (y - y_offset) * sin_theta)**2 / semi_major**2 + ((x - x_offset) * sin_theta + (y - y_offset) * cos_theta)**2 / semi_minor**2
  df = df[oval(df["FSC-H"], df["SSC-H"], 2.54, 1.29, 2.08, 2.18, math.pi * 1.75) <= 1]

  # Zombie (if present)
  if "Zombie" in df.keys():
    print("stuff")

  # Single Cells
  return df
st.text(math.sin(3.14))

if x_select != "No Selection" and y_select != "No Selection":
  colors = ["red", "blue"]
  opacity_slider1 = st.slider("Mock Opacity", 0.0, 1.0, 1.0, 0.01)
  opacity_slider2 = st.slider("Dox Opacity", 0.0, 1.0, 1.0, 0.01)
  colors = [(1, 0, 0, opacity_slider1), (0, 0, 1, opacity_slider2)]
  files = [file for file in st.session_state.facs_dataframes if "Reference Group" not in file["name"] and "Unmixed" in file["name"]]
  fig, axs = plt.subplots(nrows = 5, ncols = 5, figsize = (24, 30)) # math.ceil(len(files) / 2 / 5)
  # axs = [ax for row in axs for ax in row]
  axs = axs.flatten()
  for i in range(1, len(files), 2):
    ax = axs[int(i / 2)]
    file_mock = files[i - 1]
    file_dox = files[i]
    ax.scatter(file_mock["data"][x_select], file_mock["data"][y_select], s = 1, color = colors[0])
    ax.scatter(file_dox["data"][x_select], file_dox["data"][y_select], s = 1, color = colors[1])
    ax.set_title(textwrap.fill(file_mock["name"][file_mock["name"].index("TubeRack"):file_mock["name"].index(".fcs")], 30))

    ax.set_xlabel(x_select)
    ax.set_xscale("log")
    ax.set_xlim(left = 1, right = pow(10, 7))

    ax.set_ylabel(y_select)
    ax.set_yscale("log")
    ax.set_ylim(bottom = 1, top = pow(10, 7))
    
  st.pyplot(fig)