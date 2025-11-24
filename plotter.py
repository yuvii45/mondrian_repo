import plotly.graph_objects as go
from plotly.offline import plot
import math

# Data
n = [3,4,5,6,7,8,9,10,
     11,12,13,14,15,16,17,
     18,19,20,21,22,23,24,
     25,26,27,28,29,30]

d = [2,4,4,5,5,6,6,8,
     6,7,8,6,8,8,8,
     8,8,9,9,9,8,9,
     10,9,10,9,9,11]

# Computed sqrt values
sqrt_n_scaled = [2.75 * math.sqrt(x) for x in n]
sqrt_n = [1.25 * math.sqrt(x) for x in n]

# Create figure
fig = go.Figure()

# d vs n
fig.add_trace(go.Scatter(
    x=n, y=d, mode='lines+markers', name='d',
    line=dict(color='blue', width=2),
    marker=dict(symbol='circle', size=8)
))

# 2.5 * sqrt(n) vs n
fig.add_trace(go.Scatter(
    x=n, y=sqrt_n_scaled, mode='lines+markers', name='2.5 * sqrt(n)',
    line=dict(color='red', width=2, dash='dash'),
    marker=dict(symbol='diamond', size=8)
))

# sqrt(n) vs n
fig.add_trace(go.Scatter(
    x=n, y=sqrt_n, mode='lines+markers', name='sqrt(n)',
    line=dict(color='green', width=2, dash='dot'),
    marker=dict(symbol='square', size=8)
))

# Layout
fig.update_layout(
    xaxis_title="n",
    yaxis_title="Value",
    title="Comparison of d, sqrt(n), and 2.5*sqrt(n)",
    legend=dict(x=0.05, y=0.95)
)

# Save and open offline
plot(fig, filename='plot.html', auto_open=True)
