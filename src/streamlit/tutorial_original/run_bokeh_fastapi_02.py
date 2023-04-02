"""Streamlit example with Bokeh and FastAPI using stock time series data."""

import pandas as pd
from datetime import timedelta

from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    CustomJS,
    Label,
    Circle,
)
from bokeh.plotting import figure
from bokeh.layouts import column
import streamlit as st


def get_df_all() -> pd.DataFrame:
    """Load the time series data from a CSV file."""
    df_all = pd.read_csv(
        "https://raw.githubusercontent.com/vega/vega-datasets/master/data/stocks.csv"
    )
    # Convert the date column to a pandas datetime object
    df_all["date"] = pd.to_datetime(df_all["date"])
    df_all = df_all.sort_values(["symbol", "date"], ascending=True)
    return df_all


def get_df(df_all: pd.DataFrame, selected_stock: str) -> pd.DataFrame:
    """Get a subset for one selected stock."""
    df = df_all[df_all.symbol == selected_stock]
    df = df.sort_values(["date"], ascending=True)
    df = df.iloc[0:100, :]
    return df


if True:
    st.title("Streamlit app for Stock time series.")

    st.write("Dataframe of all stocks")
    df_all = get_df_all()
    # select a stock
    # Create a selectbox for choosing a column
    selected_stock = "AAPL"
    # only one option is possible at the same time
    selected_stock = st.sidebar.selectbox(
        "Select Column", sorted(df_all["symbol"].unique())
    )
    st.write(f"Historical Stock Prices of {selected_stock}")
    df = get_df(df_all, selected_stock)
    st.write(f"First as a data frame table that has {len(df)} elements")
    # create the plot with x axis as datetime
    xaxis = "date"
    yaxis = "price"
    line_width = 2
    line_color = "red"
    title = f"Bokeh interactive plot of time series of stock {selected_stock}"
    x_axis_label = "Date"
    y_axis_label = "Stock price"
    num_day_extension = 5 * 365

    # create p figure
    p = figure(
        width=800,
        height=400,
        x_axis_type="datetime",
        title=title,
        x_axis_label=x_axis_label,
        y_axis_label=y_axis_label,
        # tools=("lasso_select", "box_select, wheel_zoom"),
        tools=(),
        # match_aspect=True,
    )

    # add a label to the figure
    i = -1
    x0 = df["date"].values[i]
    y0 = df["price"].values[i]

    i = 0
    x_start = df["date"].values[i]
    y_start = df["price"].values[i]

    i = -1
    x_end = df["date"].values[i]
    y_end = df["price"].values[i]

    y_min = df["price"].min()
    y_max = df["price"].max()

    x_width = x_end - x_start
    y_height = y_max - y_min

    print(f"y_min={y_min}, y_max={y_max}, y_height={y_height}")

    # add a rectangle that covers the entire plot area
    p.rect(
        x=x0 + x_width / 2,
        y=y_min + y_height / 2,
        width=x_width,
        height=y_height,
        fill_color="blue",
        line_color="blue",
        alpha=0.10,
    )

    # source
    source = ColumnDataSource(
        data=dict(date=list(df[xaxis].values), price=list(df[yaxis].values))
    )
    # add a line renderer
    p.line(
        x=xaxis,
        y=yaxis,
        source=source,
        line_width=line_width,
        line_color=line_color,
    )

    label = Label(x=x0, y=y0, text="", text_color="green", text_font_size="8pt")
    p.add_layout(label)

    # create a new data source for the clicked point
    point_source = ColumnDataSource(data=dict(x=[x0], y=[y0]))
    # add a circle glyph to the plot with the point data source
    # p.circle(x='x', y='y', size=10, color='blue', alpha=0.5, source=point_source)
    # add a circle renderer to display the clicked points
    circle = Circle(x="x", y="y", size=10, fill_color="blue", fill_alpha=0.5)
    p.add_glyph(point_source, circle)

    # create a data source for the points and the line
    line_source = ColumnDataSource(data=dict(x=[x0, x0], y=[y0, y0]))
    # create a line renderer and add it to the figure
    line = p.line(x="x", y="y", source=line_source)

    # guessed values
    guessed_x = x0
    guessed_y = y0

    # extend the x-range one year
    # calculate a new end date for the x-range
    new_end_date = max(df["date"]) + timedelta(days=num_day_extension)
    # update the x-range of the figure with the new end date
    p.x_range.end = new_end_date

    # add a HoverTool to display the x, y coordinates
    hover = HoverTool(
        tooltips=[("date", "$x{%F}"), ("price", "$y{1.11}")],
        formatters={"$x": "datetime"},
        mode="mouse",
        point_policy="none",
    )
    p.add_tools(hover)

    # print(guessed_x, guessed_y)

    # show(p)

    p2 = figure(
        width=800,
        height=400,
        x_axis_type="datetime",
        title=title,
        x_axis_label=x_axis_label,
        y_axis_label=y_axis_label,
        # tools=("lasso_select", "box_select, wheel_zoom"),
        tools=(),
        # match_aspect=True,
    )
    # source2
    source2 = ColumnDataSource(
        data=dict(date=list(df[xaxis].values), price=[100 for x in range(len(df))])
    )

    p2.line(
        x=xaxis,
        y=yaxis,
        source=source2,
        line_width=line_width,
        line_color=line_color,
    )
    p2.y_range.start = y_min
    p2.y_range.end = y_max

    code_js = """
    // how to write to console
    // console.error("This is an error message.");
    // console.warn("This is a warning message.");
    // console.info("This is an informational message.");

    // tap event: retrieve, format, log to cosole
    var x = cb_obj.x;
    var y = cb_obj.y;
    // convert x from number to a date
    var x_date = new Date(x);
    // format the date
    var x_date_formatted = x_date.toISOString().split('T')[0];
    // format y to keep only two significant digits
    var y_formatted = y.toFixed(2)
    // log the tap event to console
    var tap_event_text = `Tap event occured at x=${x_date_formatted}, y=${y_formatted}`
    console.log(tap_event_text)

    // add new points to the line
    line_source.data.x.push(x);
    line_source.data.y.push(y);
    line_source.change.emit();

    // change the position of the marker to the new tap
    // point_source.data expects a list of markers
    // recreate a list with only one point, the new tap point
    point_source.data.x = [x];
    point_source.data.y = [y];
    point_source.change.emit();

    // create at the tap position a new text label
    // new label position
    label.x = x;
    label.y = y;
    var label_text = `x=${x_date_formatted}, y=${y_formatted}`
    label.text = label_text
    label.change.emit();

    //source2 for the plot below plot a line at height y
    //for (var i = 0; i < source2.data.price.length; i++) {
    //    source2.data.price[i] = y;
    //}
    //source2.change.emit();

    // do the same, but with FastAPI GET method with no headers and no body
    // it that takes y and returns also y
    // pass input to FastAPI, get response and use that to update plot below
    // const url = 'http://127.0.0.1:8000/multiply?x=' + x + '&y=' + y;
    const url = `http://localhost:8011/identity?value=${y}`
    console.log(`GET request to FastAPI at url=${url}`)
    fetch(url)
        .then(response => response.json())
        .then(data => {
            const y = data.value;
            console.log(`Retrieved from GET y=${y}`)
            //source2 for the plot below
            for (var i = 0; i < source2.data.price.length; i++) {
                source2.data.price[i] = y;
            }
            //source2.change.emit();
        })
        .catch(error => console.error(error));

    // update the plot below using a POST request with headers and body
    const url_post = "http://localhost:8011/identity-router-post//";
    const apiKey = "foo";
    const requestBody = {
        asset_name: "OIL",
        datetime: "2023-03-22T09:00:00",
        price: y
    };
    console.log(`POST request to FastAPI at url=${url_post}`);
    fetch(url_post, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "x-api-key": apiKey
        },
        body: JSON.stringify(requestBody)
    })
    .then(response => response.json())
    .then(data => {
        const y = data.value;
        console.log(`Retrieved from POST y=${y}`);
        //source2 for the plot below
        for (var i = 0; i < source2.data.price.length; i++) {
            source2.data.price[i] = y;
        }
        source2.change.emit();
    })
    .catch(error => console.error(error));
    """
    callback = CustomJS(
        args=dict(
            label=label,
            point_source=point_source,
            line_source=line_source,
            guessed_x=guessed_x,
            guessed_y=guessed_y,
            source2=source2,
        ),
        code=code_js,
    )
    p.js_on_event("tap", callback)

    # Layout
    layout = column(p, p2)
    # show(layout)

    # display the plots in the Streamlit app
    st.bokeh_chart(layout)

    # time.sleep(1000)
