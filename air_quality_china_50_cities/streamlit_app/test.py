import plotly.graph_objects as go

fig = go.Figure(data=go.Scatter(y=[1, 3, 2]))
fig.write_image("test.png", engine="orca")
