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
  print(f"All Cells: {len(df)}")
  # Live Cells
  def oval(x, y, semi_major, semi_minor, x_offset, y_offset, rads = 0, default_sin = None, default_cos = None):
    sin_theta = math.sin(rads) if default_sin is None else default_sin
    cos_theta = math.cos(rads) if default_cos is None else default_cos
    return ((x - x_offset) * cos_theta - (y - y_offset) * sin_theta)**2 / semi_major**2 + ((x - x_offset) * sin_theta + (y - y_offset) * cos_theta)**2 / semi_minor**2
  # print(df["FSC-H"][0], df["SSC-H"][0])
  # print(oval(df["FSC-H"][0], df["SSC-H"][0], 2.54 * 10**6, 1.29 * 10**6, 2.08 * 10**6, 2.18 * 10**6, math.pi * 1.75))
  df = df[oval(df["FSC-H"], df["SSC-H"], 2.54 * 10**6, 1.29 * 10**6, 2.08 * 10**6, 2.18 * 10**6, math.pi * 1.75) <= 1]
  print(f"Live Cells: {len(df)}")

  # Zombie (if present)
  for key in df.keys():
    if "Zombie" in key:
      df = df[(2900 <= df[key]) & (df[key] <= 148000)]
  print(f"Live Cells (Zombie): {len(df)}")

  # Single Cells
  df = df[(-205000 <= (df["FSC-H"] - 0.58 * df["FSC-A"])) & ((df["FSC-H"] - 0.58 * df["FSC-A"]) <= 275000)] # FCS-H - 0.58*FSC-A = 275,000/-205,000
  print(f"Single Cells: {len(df)}")
  return df

if x_select != "No Selection" and y_select != "No Selection":
  colors = ["red", "blue"]
  opacity_slider1 = st.slider("Mock Opacity", 0.0, 1.0, 1.0, 0.01)
  opacity_slider2 = st.slider("Dox Opacity", 0.0, 1.0, 1.0, 0.01)
  colors = [(1, 0, 0, opacity_slider1), (0, 0, 1, opacity_slider2)]
  files = [file for file in st.session_state.facs_dataframes if "Reference Group" not in file["name"] and "Unmixed" in file["name"]]
  fig, axs = plt.subplots(nrows = 2, ncols = 2, figsize = (24, 30)) # math.ceil(len(files) / 2 / 5)
  # axs = [ax for row in axs for ax in row]
  axs = axs.flatten()
  for i in range(1, len(files), 2):
    ax = axs[int(i / 2)]
    file_mock = files[i - 1]
    file_dox = files[i]
    filtered_mock = filter_cells(file_mock["data"])
    ax.scatter(filtered_mock[x_select], filtered_mock[y_select], s = 1, color = colors[0])
    filtered_dox = filter_cells(file_dox["data"])
    ax.scatter(filtered_dox[x_select], filtered_dox[y_select], s = 1, color = colors[1])
    ax.set_title(textwrap.fill(file_mock["name"][file_mock["name"].index("TubeRack"):file_mock["name"].index(".fcs")], 30))
    def eqn(a, b):
      return [[0, 4*10**6], [b, a*4*10**6+b]]
    a=0.58
    ax.plot([0, 4*10**6], eqn(a, 0.275*10**6)[1], color = "green")
    ax.plot([0, 4*10**6], eqn(a, -0.205*10**6)[1], color = "green")

    ax.set_xlabel(x_select)
    # ax.set_xscale("log")
    ax.set_xlim(left = 0, right = 4.5*10**6)

    ax.set_ylabel(y_select)
    # ax.set_yscale("log")
    ax.set_ylim(bottom = 0, top = 4.5*10**6)
    
  st.pyplot(fig)