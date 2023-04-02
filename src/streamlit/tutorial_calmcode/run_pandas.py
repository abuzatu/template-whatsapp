"""Streamlit example with pandas."""

import pandas as pd
import matplotlib.pylab as plt
import streamlit as st

st.title("BigMac Index")


@st.cache_resource
def load_data() -> pd.DataFrame:
    """Load data of BigMac prices per countries from a .csv file.

    Convert the date variable from a string to a datetime.
    """
    data = pd.read_csv("src/streamlit/tutorial_calmcode/data_pandas.csv")
    return data.assign(date=lambda d: pd.to_datetime(d["date"]))


df = load_data()

# several options are possible at the same time
countries = st.sidebar.multiselect("Select Countries", sorted(df["name"].unique()))

# only one option is possible
varname = st.sidebar.selectbox("Select Column", ("local_price", "dollar_price"))

subset_df = df.loc[lambda d: d["name"].isin(countries)]

fig, ax = plt.subplots()
for name in countries:
    plotset = subset_df.loc[lambda d: d["name"] == name]
    ax.plot(plotset["date"], plotset[varname], label=name)
    plt.xlabel("Date")
    plt.ylabel("Price")
plt.legend()
st.pyplot(fig)

if st.sidebar.checkbox("Show Raw Data"):
    st.markdown("### Raw Data")
    st.write(subset_df)
