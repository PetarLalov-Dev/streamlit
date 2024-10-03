import streamlit as st
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time

lenght = 60
# Generate sample data
times = [time(hour=0, minute=x) for x in range(lenght)]  # 24 hours
dates = [datetime.today() - timedelta(days=x) for x in range(lenght)][::-1]  # Last 100 days

# Time Series 1: e.g., Stock Prices
np.random.seed(0)
ts1 = np.cumsum(np.random.randn(lenght)) + 100  # Random walk around 100

# Time Series 2: e.g., Trading Volume
ts2 = np.random.randint(1000, 5000, size=lenght)  # Random integers between 1000 and 5000

# Create DataFrame
df = pd.DataFrame({
    'Date': times,
    'Stock Price': ts1,
    'Trading Volume': ts2
})

# Title of the app
st.title("Dual Y-Axis Time Series Plot with Streamlit and Plotly")

# Sidebar for user inputs (optional)
st.sidebar.header("Configuration")

# Select columns (assuming you have multiple time series)
# For simplicity, we use the two generated series
y1 = 'Stock Price'
y2 = 'Trading Volume'

# Create Plotly figure
fig = go.Figure()

# Add first time series
fig.add_trace(
    go.Scatter(
        x=df['Date'],
        y=df[y1],
        name=y1,
        mode='lines',
        line=dict(color='blue')
    )
)

# Add second time series with a different Y-axis
fig.add_trace(
    go.Scatter(
        x=df['Date'],
        y=df[y2],
        name=y2,
        mode='lines',
        line=dict(color='red'),
        yaxis='y2'
    )
)

# Update layout to add second Y-axis
fig.update_layout(
    xaxis=dict(
        title='Date'
    ),
    yaxis=dict(
        title=y1,
        titlefont=dict(color='blue'),
        tickfont=dict(color='blue')
    ),
    yaxis2=dict(
        title=y2,
        titlefont=dict(color='red'),
        tickfont=dict(color='red'),
        overlaying='y',
        side='right'
    ),
    legend=dict(x=0, y=1.2, orientation='h'),
    title="Two Time Series with Dual Y-Axes",
    template='plotly_white'
)

# Display the plot in Streamlit
st.plotly_chart(fig, use_container_width=True)
