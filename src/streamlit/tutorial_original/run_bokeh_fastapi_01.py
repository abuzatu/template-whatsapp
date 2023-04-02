"""A streamlit example with a bokeh plot and with FastAPI request as a hello world."""

import streamlit as st
from bokeh.layouts import row
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, TapTool, CustomJS
from bokeh.models import Range1d

# create a data source for the first plot
source1 = ColumnDataSource(data=dict(x=[], y=[]))

# create a new plot with a title
p1 = figure(title="Interactive Line Plot", tools="tap", tooltips=[("x", "$x{0}")])
p1.x_range = Range1d(start=0, end=50)
p1.y_range = Range1d(start=0, end=50)
# add a line renderer with the data source
line1 = p1.line("x", "y", source=source1, line_width=2)
circle_glyph = p1.circle(
    "x", "y", source=source1, size=10, fill_color="white", line_color="red"
)
# create a data source for the second plot
source2 = ColumnDataSource(data=dict(x=[], y=[]))

# create a new plot with a title
p2 = figure(title="Updated Line Plot")
p2.x_range = Range1d(start=0, end=50)
p2.y_range = Range1d(start=0, end=50)
# add a line renderer with the data source
line2 = p2.line("x", "y", source=source2, line_width=2)

# define the JavaScript callback function for the first plot
callback1 = CustomJS(
    args=dict(source=source1, source2=source2),
    code="""
    var data = source.data;
    var x = cb_obj.x;
    var y = cb_obj.y;

    var data1 = source2.data;

    console.log('Tap event occurred at x-position: ' + cb_obj.x);
    console.log('Tap event occurred at y-position: ' + cb_obj.y);


    data['x'].push(x);
    data['y'].push(y);
    source.change.emit();

    const factor = 0.5
    const url = `http://localhost:8011/multiply?factor=${factor}&x=${x}&y=${y}`
    console.log(`GET request to FastAPI at url=${url}`)
    fetch(url)
        .then(response => response.json())
        .then(data => {
            const x = data.x_multiplied;
            const y = data.y_multiplied;
            console.log(`Retrieved from GET x=${x} and y=${y}`)
            data1['x'].push(x);
            data1['y'].push(y);
            source2.change.emit();
        })
        .catch(error => console.error(error));



""",
)

# create a TapTool with the callback function for the first plot
taptool1 = p1.select(type=TapTool)
taptool1.callback = callback1

p1.js_on_event("tap", callback1)

# display the plots in the Streamlit app
st.bokeh_chart(row(p1, p2))
