from flask import Flask, render_template
from bokeh.models import ColumnDataSource, Slider
from bokeh.resources import INLINE
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models.callbacks import CustomJS
import numpy as np

app = Flask(__name__)

x = np.arange(120)

@app.route('/')
def index():

    source = ColumnDataSource(data = dict(
        x = x,
        savings_rent = 0*x,
        nw_rent = 0*x,
        nw_buy = 0*x,
        home_equity = 0*x,
        investment_equity = 0*x,
    ))

    income = Slider(title="Takehome Income - Expenses ($, thoousands)", start=30, end=120, value=60, step=5)
    rent = Slider(title="Rent ($)", value=1000, start=500, end=4000, step=50)
    home_price = Slider(title="Home price ($, thousands)", value=250, start=150, end=850, step=10)
    home_maintenance = Slider(title="Home maintenance, taxes, insurance (% / yr)", value=2, start=0, end=5, step=0.25)
    investment_returns = Slider(title="Investment Returns (%/yr)", start=0, end=20, value=10, step=1)
    down_payment = Slider(title="Downpayment (%)", value=10, start=0, end=20, step=1)
    house_appreciation = Slider(title="House appreciation (%/yr)", value=4, start=0, end=12, step=0.5)
    interest = Slider(title="Loan Interest (%)", value=7.5, start=0, end=12, step=0.5)

    callback = CustomJS(args=dict(source=source, home_price=home_price, rent=rent, investment_returns=investment_returns, income=income, down_payment=down_payment, house_appreciation=house_appreciation, interest=interest, home_maintenance=home_maintenance), code="""
        const data = source.data;

        const h_p = home_price.value;
        const R = rent.value/1000;
        const i_r = investment_returns.value/1200;
        const I = income.value/12;
        const h_dp = down_payment.value * h_p / 100;
        const h_a = house_appreciation.value/1200;
        const h_m = h_p * home_maintenance.value/1200;
        const Interest = interest.value/1200;
        const Mortgage = h_p * (Interest * Math.pow((1 + Interest), 360)) / (Math.pow((1 + Interest), 360) - 1);

        const x = data['x']
        const savings_rent = data['savings_rent']
        const nw_rent = data['nw_rent']
        const nw_buy = data['nw_buy']
        const home_equity = data['home_equity']
        const investment_equity = data['investment_equity']

        for (let i = 0; i < x.length; i++) {
            home_equity[i] = h_p * (-1.07 + Math.pow(1+h_a, x[i]));

            savings_rent[i] = I - R*Math.pow(1+h_a, x[i]);
            if (i == 0){
                nw_rent[i] = savings_rent[i] + h_dp;
                investment_equity[i] = I - Mortgage - h_m;
            }
            else {
                nw_rent[i] = nw_rent[i-1] * (1+i_r) + savings_rent[i];
                investment_equity[i] = investment_equity[i-1] * (1+i_r) + (I - Mortgage);
            }

            nw_buy[i] = home_equity[i] + investment_equity[i];
            
        }
        source.change.emit();
    """)

    income.js_on_change('value', callback)
    home_price.js_on_change('value', callback)
    down_payment.js_on_change('value', callback)
    rent.js_on_change('value', callback)
    investment_returns.js_on_change('value', callback)
    house_appreciation.js_on_change('value', callback)
    interest.js_on_change('value', callback)
    home_maintenance.js_on_change('value', callback)

    fig = figure(height=600, width=720, tooltips=[("t", "@x"), ("Buy", "@nw_buy"), ("Rent", "@nw_rent")])
    fig.line(x="x", y="nw_rent", source=source, line_width=2, color='blue', legend_label = 'Cumulative savings - Renting')
    fig.line(x="x", y="nw_buy", source=source, line_width=2, color='red', legend_label = 'Cumulative savings - Buying')
    # fig.line(x="x", y="investment_equity", source=source, line_width=2, color='green', legend_label = 'Investment Equity')
    fig.xaxis.axis_label = "Time (months)"
    fig.yaxis.axis_label = "Dollars (thousands)"

    inputs_column = column([income, home_price, down_payment, house_appreciation, interest, home_maintenance, rent, investment_returns], width=320, height=1000)
    layout_row = row([ inputs_column, fig ])

    script, div = components(layout_row)
    return render_template(
        'index.html',
        plot_script=script,
        plot_div=div,
        js_resources=INLINE.render_js(),
        css_resources=INLINE.render_css()
    )

if __name__ == "__main__":
    app.run(debug=True)