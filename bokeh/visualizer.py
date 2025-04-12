from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, Span, Title, Label
from bokeh.layouts import column
import pandas as pd

weather_data = pd.read_csv("weather_data_with_predictions.csv")
weather_data['timestamp'] = pd.to_datetime(weather_data['datetime'])

source = ColumnDataSource(weather_data)

temperature_plot = figure(
    title="🌡️ Temperature Over Time",
    x_axis_label='Time',
    y_axis_label='Temperature (°C)',
    x_axis_type='datetime',
    width=1200,
    height=400
)

temperature_plot.line('timestamp', 'temperature', source=source, line_width=2, color='dodgerblue', legend_label="Temperature")
temperature_plot.circle('timestamp', 'temperature', source=source, size=4, color='blue', alpha=0.5)

hover_temp = HoverTool(
    tooltips=[
        ("Date", "@timestamp{%F %H:%M}"),
        ("Temp", "@temperature °C"),
        ("Condition", "@weather_condition")
    ],
    formatters={'@timestamp': 'datetime'},
    mode='vline'
)

temperature_plot.add_tools(hover_temp)
temperature_plot.legend.location = "top_left"
temperature_plot.xaxis.major_label_orientation = 0.5  # Rotate x-axis labels

last_point = weather_data.iloc[-1]
last_timestamp = last_point['timestamp']

highlight = Span(location=last_timestamp.timestamp() * 1000, dimension='height',
                 line_color='crimson', line_dash='dashed', line_width=2)
temperature_plot.add_layout(highlight)

temperature_plot.diamond(
    x=[last_point['timestamp']],
    y=[last_point['temperature']],
    size=14,
    color='crimson',
    alpha=0.9,
    legend_label="🔮 Predicted"
)

label = Label(
    x=last_point['timestamp'],
    y=last_point['temperature'] + 1.5,
    text="🔮 Predicted",
    text_color='crimson',
    text_font_size='10pt'
)
temperature_plot.add_layout(label)

weather_counts = weather_data['weather_condition'].value_counts().reset_index()
weather_counts.columns = ['condition', 'count']
weather_bar_source = ColumnDataSource(weather_counts)

weather_plot = figure(
    title="☁️ Weather Condition Frequency",
    x_range=weather_counts['condition'],
    y_axis_label='Count',
    width=600,
    height=350
)

weather_plot.vbar(x='condition', top='count', source=weather_bar_source, width=0.7, color="seagreen")
weather_plot.xaxis.major_label_orientation = 0.8  # Also rotate bar chart x-axis labels if needed

temperature_plot.title.text_font_size = '18pt'
weather_plot.title.text_font_size = '18pt'
temperature_plot.add_layout(Title(text="🔴 Dashed line = Latest Prediction", align="center"), "below")

layout = column(temperature_plot, weather_plot)

curdoc().add_root(layout)
curdoc().title = "Weather Forecast Dashboard"
