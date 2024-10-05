import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

# Generate sample data
np.random.seed(0)
time = pd.date_range(start='2024-01-01', periods=10, freq='D')
temperature = 300 + np.random.normal(0, 1, size=len(time))  # Random temperature around 300K

# Create a DataFrame
data = pd.DataFrame({'Time': time, 'Temperature (K)': temperature})

# Create the Altair chart
chart = (
    alt.Chart(data)
    .mark_line(point=True)
    .encode(
        x='Time:T',
        y=alt.Y('Temperature (K):Q', title='Temperature (K)', scale=alt.Scale(domain=[data['Temperature (K)'].min() - 1, data['Temperature (K)'].max() + 1])),
        tooltip=['Time:T', 'Temperature (K):Q']
    )
    .properties(title='Temperature Time Series with Annotations')
)

# Add text annotations for the data points
text = chart.mark_text(
    align='left',
    dx=5,  # Nudges text to the right
    dy=-5  # Nudges text up
).encode(
    text=alt.Text('Temperature (K):Q', format=".1f")
)

# Combine the line chart and the text annotations
final_chart = chart + text

# Display the chart in Streamlit
st.altair_chart(final_chart, use_container_width=True)
