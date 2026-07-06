import io
import flowio
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt

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
  files = st.session_state[f"uploader_key_{st.session_state.uploader_key}"] # Could I use `uploaded_files` in places of `files`?
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

def plt_formatting(fig):
  fig.update_xaxes(showline = True,
                   linewidth = 1,
                   linecolor = "black",
                   mirror = True,
                   title_font_color = "black",
                   tickfont_color = "black",
                   ticks = "outside",
                   ticklen = 6,
                   tickwidth = 1,
                   showgrid = False)
  xmax = max(trace.x.max() for trace in fig.data)
  fig.update_xaxes(range=[0, xmax * 1.05])
  
  fig.update_yaxes(showline = True,
                   linewidth = 1,
                   linecolor = "black",
                   mirror = True,
                   title_font_color = "black",
                   tickfont_color = "black",
                   ticks = "outside",
                   ticklen = 6,
                   tickwidth = 1,
                   showgrid = False,
                   zeroline = False)
  ymax = max(trace.y.max() for trace in fig.data)
  fig.update_yaxes(range=[0, ymax * 1.05])
        
  fig.update_layout(plot_bgcolor = "white",
                    paper_bgcolor = "white",
                    font = {"family" : "Arial",
                            "size" : 16,
                            "color" : "black"},
                    legend = {"bgcolor" : "rgba(255,255,255,0)",
                              "font_color" : "black",
                              "title_font_color" : "black",
                              "borderwidth" : 0},
                    width = 700,
                    height = 500,
                    margin = {"l" : 50, "r" : 20, "t" : 30, "b" : 50})
  fig.update_traces(marker = {"size" : 4})

  return fig

match (x_select != "No Selection") + (y_select != "No Selection") + (z_select != "No Selection"): # Number of axes with selections
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
        colors = [plt.get_cmap("hsv")(i/len(files_selected)) for i in range(len(files_selected))]
        colors = [f"rgba({255 * color[0]}, {255 * color[1]}, {255 * color[2]}, {color[3] * 0.8})" for color in colors]
        figure = px.scatter(x = files_selected[0]["data"][selections[0]], y = files_selected[0]["data"][selections[1]])
        figure.update_traces(marker = {"color" : colors[0]})
        for i, file in enumerate(files_selected[1:]):
          temp_fig = px.scatter(x = file["data"][selections[0]], y = file["data"][selections[1]])
          temp_fig.update_traces(marker = {"color" : colors[i + 1]})
          figure.add_traces(temp_fig.data)
        figure.update_xaxes(title_text = selections[0])
        figure.update_yaxes(title_text = selections[1])
        st.plotly_chart(plt_formatting(figure))
        break
  case 3:
    # 3D scatter code here
    st.text("Triple")