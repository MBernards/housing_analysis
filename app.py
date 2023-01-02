from flask import Flask, render_template
from bokeh.models import ColumnDataSource, Slider
from bokeh.resources import INLINE
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models.callbacks import CustomJS
import numpy as np

app = Flask(__name__)

@app.route('/')
def index():

    x = np.arange(120)
    h_p = 450
    R = 2.5
    i_r =1/120
    I = 4
    h_dp = 15*h_p/100
    h_a = 4/1200
    h_m = 3*h_p / 1200
    Interest = 7.5/1200

    Mortgage = h_p * (Interest * (1 + Interest)**360) / ((1 + Interest)**360 - 1)

    savings_rent = I - R*(1+h_a)**x
    home_equity = h_p * (-1.07 + (1 + h_a)**x) + h_dp + (Mortgage - Interest * h_p)*x

    nw_rent = [savings_rent[0] + h_dp]
    investment_equity = [I - Mortgage - h_m]
    nw_buy = [home_equity[0] + investment_equity[0]]

    for i in range(1, len(x)):
        nw_rent.append(nw_rent[i-1] * (1 + i_r) + savings_rent[i])
        investment_equity.append(investment_equity[i-1] * (1+i_r) + (I - Mortgage))
        nw_buy.append(home_equity[i] + investment_equity[i])

    source = ColumnDataSource(data = dict(
        x = x,
        savings_rent = savings_rent,
        nw_rent = nw_rent,
        nw_buy = nw_buy,
        home_equity = home_equity,
        investment_equity = investment_equity,
    ))

    income = Slider(title="Takehome Income - Expenses ($, thoousands)", start=2, end=10, value=I, step=0.5)
    rent = Slider(title="Rent ($)", value=R*1000, start=500, end=4000, step=50)
    home_price = Slider(title="Home price ($, thousands)", value=h_p, start=150, end=850, step=10)
    home_maintenance = Slider(title="Home maintenance, taxes, insurance (% / yr)", value=h_m*1200/h_p, start=0, end=5, step=0.25)
    investment_returns = Slider(title="Investment Returns (%/yr)", start=0, end=20, value=i_r*1200, step=1)
    down_payment = Slider(title="Downpayment (%)", value=h_dp*100/h_p, start=0, end=20, step=1)
    house_appreciation = Slider(title="House appreciation (%/yr)", value=h_a*1200, start=0, end=12, step=0.5)
    interest = Slider(title="Loan Interest (%)", value=Interest*1200, start=0, end=12, step=0.5)

    callback = CustomJS(args=dict(source=source, home_price=home_price, rent=rent, investment_returns=investment_returns, income=income, down_payment=down_payment, house_appreciation=house_appreciation, interest=interest, home_maintenance=home_maintenance), code="""
        const data = source.data;

        const h_p = home_price.value;
        const R = rent.value/1000;
        const i_r = investment_returns.value/1200;
        const I = income.value;
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
            home_equity[i] = h_p * (-1.07 + Math.pow(1+h_a, x[i])) + h_dp+ (Mortgage - Interest * h_p)*x[i];
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
    app.run(host="0.0.0.0", debug=True, port=9000)