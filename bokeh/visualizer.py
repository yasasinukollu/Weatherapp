from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, Div
from bokeh.layouts import column
import pandas as pd

# Load and prepare data
weather_data = pd.read_csv("../src/weather_data_with_predictions.csv")
weather_data['timestamp'] = pd.to_datetime(weather_data['date_time'])
weather_data['temperature'] = pd.to_numeric(weather_data['temperature'], errors='coerce')

# Extract last predicted point
last_point = weather_data.iloc[-1]
prediction_source = ColumnDataSource(data=dict(
    timestamp=[last_point['timestamp']],
    temperature=[last_point['temperature']],
    weather_condition=[last_point['weather_condition']]
))

# HTML Title and Description
title_div = Div(text="""
    <h1 style="color:#2c3e50; font-size:28px; font-weight:700; text-align:center; text-shadow:1px 1px 2px rgba(0,0,0,0.1); margin-bottom:10px;">
        🌡️ Weather Dashboard: Hyderabad Temperature
    </h1>
    <p style="font-size:14px; color:#34495e; text-align:center; line-height:1.5; max-width:800px; margin:0 auto;">
        Explore observed temperature trends in Hyderabad with hourly and daily views.<br>
        <strong style="color:#e74c3c;">🔺 Hover over the red square</strong> in the hourly chart for the predicted temperature.
    </p>
""", width=1200, css_classes=['title-div'])

# Hourly Plot
hourly_data = weather_data.set_index('timestamp').resample('h').mean(numeric_only=True).reset_index()
hourly_source = ColumnDataSource(hourly_data)

hourly_plot = figure(
    title="🌇 Hourly Temperature Trend",
    x_axis_type='datetime',
    x_axis_label='Time',
    y_axis_label='Temperature (°C)',
    width=1200,
    height=350,
    tools="pan,wheel_zoom,box_zoom,reset,save",
    toolbar_location="above",
    background_fill_color="#f0f0f0",
    title_location="above",
    margin=(20, 10, 20, 10)
)
hourly_plot.title.text_font_size = "16px"
hourly_plot.title.text_color = "#2c3e50"
hourly_plot.xaxis.axis_label_text_font_size = "12px"
hourly_plot.yaxis.axis_label_text_font_size = "12px"
hourly_plot.xaxis.axis_label_text_font_style = "normal"
hourly_plot.yaxis.axis_label_text_font_style = "normal"
hourly_plot.xaxis.major_label_text_font_size = "10px"
hourly_plot.yaxis.major_label_text_font_size = "10px"

# Plot observed and predicted
hourly_plot.line('timestamp', 'temperature', source=hourly_source, line_width=3, color='dodgerblue', legend_label="Observed")
obs_renderer = hourly_plot.circle('timestamp', 'temperature', source=hourly_source, size=6, color='dodgerblue', alpha=0.6)
pred_renderer = hourly_plot.square('timestamp', 'temperature', source=prediction_source, size=12, color='red', legend_label="Predicted", line_width=2)

# Hover for observed points
hover_observed = HoverTool(
    tooltips=[("Date", "@timestamp{%F %H:%M}"), ("Observed Temp", "@temperature{0.0} °C")],
    formatters={'@timestamp': 'datetime'},
    mode='vline',
    renderers=[obs_renderer]
)
hourly_plot.add_tools(hover_observed)

# Hover for predicted point
hover_predicted = HoverTool(
    tooltips=[("Date", "@timestamp{%F %H:%M}"), ("Predicted Temp", "@temperature{0.0} °C")],
    formatters={'@timestamp': 'datetime'},
    mode='vline',
    renderers=[pred_renderer]
)
hourly_plot.add_tools(hover_predicted)

# Style legend
hourly_plot.legend.location = "top_right"
hourly_plot.legend.label_text_font_size = "10px"
hourly_plot.legend.padding = 8
hourly_plot.legend.spacing = 5
hourly_plot.legend.background_fill_alpha = 0.7

# Daily Plot
daily_data = weather_data.set_index('timestamp').resample('D').mean(numeric_only=True).reset_index()
daily_source = ColumnDataSource(daily_data)

daily_plot = figure(
    title="📆 Daily Average Temperature",
    x_axis_type='datetime',
    x_axis_label='Date',
    y_axis_label='Temperature (°C)',
    width=1200,
    height=350,
    tools="pan,wheel_zoom,box_zoom,reset,save",
    toolbar_location="above",
    background_fill_color="#f0f0f0",
    title_location="above",
    margin=(20, 10, 20, 10)
)
daily_plot.title.text_font_size = "16px"
daily_plot.title.text_color = "#2c3e50"
daily_plot.xaxis.axis_label_text_font_size = "12px"
daily_plot.yaxis.axis_label_text_font_size = "12px"
daily_plot.xaxis.axis_label_text_font_style = "normal"
daily_plot.yaxis.axis_label_text_font_style = "normal"
daily_plot.xaxis.major_label_text_font_size = "10px"
daily_plot.yaxis.major_label_text_font_size = "10px"

# Plot daily
daily_plot.line('timestamp', 'temperature', source=daily_source, line_width=3, color='green', legend_label="Daily Avg")
daily_plot.circle('timestamp', 'temperature', source=daily_source, size=6, color='green', alpha=0.6)

# Hover for daily
hover_daily = HoverTool(
    tooltips=[("Date", "@timestamp{%F}"), ("Temp", "@temperature{0.0} °C")],
    formatters={'@timestamp': 'datetime'},
    mode='vline'
)
daily_plot.add_tools(hover_daily)
daily_plot.legend.location = "top_right"
daily_plot.legend.label_text_font_size = "10px"
daily_plot.legend.padding = 8
daily_plot.legend.spacing = 5
daily_plot.legend.background_fill_alpha = 0.7

# Layout
layout = column(title_div, hourly_plot, daily_plot, sizing_mode="stretch_width", css_classes=['dashboard-layout'])
curdoc().add_root(layout)
