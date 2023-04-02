"""Streamlit example of ML with sklearn."""

import numpy as np
import streamlit as st
import matplotlib.pylab as plt
from typing import Any, Tuple
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import AdaBoostRegressor

st.title("Machine Learning with Hyper-parameter Tuning.")

st.write(
    "From the sidebar slider select how many trees to be built "
    "for a DecisionTreeRegressor (red) and an AdaBoostRegressor (green). "
    "You can see how  more trees model better the original distribution (cyan)."
)

n = 1000
np.random.seed(42)
x = np.linspace(0, 6, n)
X = np.linspace(0, 6, n)[:, np.newaxis]
y = np.sin(X).ravel() + np.sin(6 * X).ravel() + np.random.random(n) * 0.3

n_est = st.sidebar.slider("n_est", min_value=1, max_value=500, step=1, value=5)


st.markdown("This is the code that runs it all.")
with st.echo():

    @st.cache_data
    def make_predictions(n_est: int) -> Tuple[Any, Any]:
        """Make predictions."""
        mod1 = DecisionTreeRegressor(max_depth=4)
        y1 = mod1.fit(X, y).predict(X)
        y2 = AdaBoostRegressor(mod1, n_estimators=n_est).fit(X, y).predict(X)
        return y1, y2

    y1, y2 = make_predictions(n_est=n_est)

st.markdown(
    "The two predictions. "
    "From the sidebar checkbox choose if to show the initial data as well."
)
fig, ax = plt.subplots()
if st.sidebar.checkbox("Show Original Data"):
    ax.scatter(x, y, alpha=0.1, color="cyan")
ax.plot(x, y1, label="only one tree", color="red")
ax.plot(x, y2, label=f"{n_est} trees with AdaBoost", color="green")
plt.legend()
st.pyplot(fig)
