import streamlit as st

def radio_buttons_exclusive(row_labels = ["one", "two", "three"], col_headers = [1, 2, 3]):
  horizontal = len(col_headers) > len(row_labels)
  
  var_names = row_labels if horizontal else col_headers
  var_names = [str(val) for val in var_names] # var_names is used for the label arg in st.radio() which requires a string input

  button_options = col_headers if horizontal else row_labels

  for i, default_val in enumerate(button_options):
    key = f"rad{i}"
    if key not in st.session_state:
      st.session_state[key] = default_val

  cols = var_names if horizontal else st.columns(len(col_headers), border = False)

  def rad_change(changed):
    for i in [i for i in range(len(var_names)) if i != changed]:
      if st.session_state[f"rad{changed}"] == st.session_state[f"rad{i}"]:
        available_indices = list(set(range(len(button_options))) ^ {button_options.index(st.session_state[f"rad{j}"]) for j in range(len(var_names)) if j != i}) # The available indices are the indices not currently being used (all indices xor in-use indices)
        st.session_state[f"rad{i}"] = button_options[available_indices[0]]
        break

  for i, col in enumerate(cols):
    try:
      with col:
        st.radio(label = var_names[i], options = button_options, horizontal = horizontal, key = f"rad{i}", on_change = rad_change, args = (i,))
    except:
      st.radio(label = var_names[i], options = button_options, horizontal = horizontal, key = f"rad{i}", on_change = rad_change, args = (i,))

radio_buttons_exclusive()