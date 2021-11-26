import streamlit as st
import numpy as np
import pandas as pd


st.markdown("""# Water Pollution
""")

st.markdown("# What are we analyzing today ? :")

#Our model graph (TBD)
st.markdown("## This could be our model :")
@st.cache
def prediction_model_():

    return pd.DataFrame(
            np.random.randn(20, 3),
            columns=['Time', 'Series', 'other']
        )

df = prediction_model_()

st.line_chart(df)

#This could be our viz map (TBD) we would need the lat and long

st.markdown("## This could be our map")
@st.cache
def get_map_data():

    return pd.DataFrame(
            np.random.randn(1, 2) / [50, 50] + [45.7640, 4.8357],
            columns=['lat', 'lon']
        )

df = get_map_data()

st.map(df)






df = pd.DataFrame({
          'first column': list(range(1, 11)),
          'second column': np.arange(10, 101, 10)
        })

# this slider allows the user to select a number of lines
# to display in the dataframe
# the selected value is returned by st.slider
line_count = st.slider('Select a line count', 1, 10, 3)

# and used in order to select the displayed lines
head_df = df.head(line_count)

head_df
