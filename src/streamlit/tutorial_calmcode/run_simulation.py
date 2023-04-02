"""Streamlit example of a simulation.

Taken from https://calmcode.io/streamlit/sliders.html
"""

import numpy as np
import matplotlib.pylab as plt
import streamlit as st

# writes a title
st.title("Simulation Streamlit app.")

# ask if user wants the user interface on the sidebar or in the main body
use_sidebar = st.checkbox("Do you want to set your choices in the sidebar?", True)
if use_sidebar:
    st.write("Great, sidebar it is!")
else:
    st.write("Great, the main body it is!")

user_inputs = {}

if not use_sidebar:
    user_inputs["slope"] = st.slider(
        "Slope", min_value=0.01, max_value=0.10, step=0.01, value=0.06
    )
    user_inputs["noise"] = st.slider(
        "Noise", min_value=0.01, max_value=0.10, step=0.01, value=0.04
    )
    user_inputs["num_lines"] = st.slider(
        "num_lines", min_value=1, max_value=20, step=1, value=4
    )
    user_inputs["num_entries_per_line"] = st.slider(
        "num_entries_per_line", min_value=1, max_value=1000, step=1, value=100
    )
else:
    st.sidebar.markdown("## Controls")
    st.sidebar.markdown("You can **change** the values to change the *chart*.")
    user_inputs["slope"] = st.sidebar.slider(
        "Slope", min_value=0.01, max_value=0.10, step=0.01, value=0.06
    )
    user_inputs["noise"] = st.sidebar.slider(
        "Noise", min_value=0.01, max_value=0.10, step=0.01, value=0.04
    )
    user_inputs["num_lines"] = st.sidebar.slider(
        "num_lines", min_value=1, max_value=20, step=1, value=4
    )
    user_inputs["num_entries_per_line"] = st.sidebar.slider(
        "num_entries_per_line", min_value=1, max_value=1000, step=1, value=100
    )

st.write(f"Chosen user inputs: {user_inputs}")

"""
Create random numbers from a gaussian distributions with chosen parameters.
"""
values = np.cumprod(
    1
    + np.random.normal(
        user_inputs["slope"],
        user_inputs["noise"],
        (user_inputs["num_entries_per_line"], user_inputs["num_lines"]),
    ),
    axis=0,
)
st.write(values)
st.write(f"values.shape={values.shape}")

"""Plot natively to Streamlit with st.line_chart()."""
st.line_chart(values)

"""Plot with external matplotlib."""
fig, ax = plt.subplots()
for i in range(values.shape[1]):
    ax.plot(values[:, i])
st.pyplot(fig)
