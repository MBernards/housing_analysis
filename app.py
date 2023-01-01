from flask import Flask, render_template
from bokeh.models import ColumnDataSource, Div, Slider
from bokeh.io import curdoc
from bokeh.resources import INLINE
from bokeh.embed import components
from bokeh.layouts import column, row
from bokeh.plotting import figure
import numpy as np
from bokeh.models.callbacks import CustomJS

app = Flask(__name__)

@app.route('/')
def index():
    month_arr = np.arange(120)
    house_value = 300e3 * (1 + 0.04 / 12)**month_arr
##################################

    controls = {
        "house_price": Slider(title="House Price (thousands)", start=200, value=350, end=1000, step=10),
        "housing_return": Slider(title="Housing Returns", start=0, end=25, value=10, step=1)
    }

    controls_array = controls.values()
    
    source = ColumnDataSource(data=dict(
        months = month_arr,
        home_value = house_value
    ))

    callback = CustomJS(args=dict(source = source, controls=controls), code="""

        var data_length = full_data.months.length;
        # console.log(date_length)

        for (var i = 0; i < data_length; i++) {
            source.data.house_value[i] = controls.house_price.value*controls.housing_return.value**i;
        }

        console.log(new_data.months);

        source.data = new_data;
        source.change.emit();
    
    """)

    fig = figure(height=600, width=720, tooltips=[("Title", "@title"), ("Released", "@released")])
    fig.line(x="months", y="home_value", source=source)
    fig.xaxis.axis_label = "Months"
    fig.yaxis.axis_label = "Value ($)"

    for control in controls_array:
        control.js_on_change('value', callback)

    inputs_column = column(*controls_array, width=320, height=1000)
    layout_row = row([ inputs_column, fig ])

    script, div = components(layout_row)
    return render_template('index.html',
        plot_script=script,
        plot_div=div,
        js_resources=INLINE.render_js(),
        css_resources=INLINE.render_css(),
    ).encode(encoding='UTF-8')

if __name__ == "__main__":
    app.run(debug=True)