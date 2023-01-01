import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE

# dataframe with data
df = pd.DataFrame(
    {'message': ['gray dog jumped over fence while other dog ate gray rabbit',
                 'Some animals have no idea what doing life yes talking about cats',
                 'roses red violets blue jasmine  white it smells tulips nice flowers not smell spring up bunches Spring',
                 'animal poem awaits elephants gray horses eat hay neigh ok dear friends poem for',
                 'flowers nice come all kinds colors must appreciate all flowers regardless status income race gender']})


# creates a vectorization of data. We will use these vector values for plotting later.
def vectorize(text):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(text)
    return X


vector = vectorize(df['message'].values)
arr = vector.toarray()

# kmeans algorithm running on data
k = 3
kmeans = KMeans(n_clusters=k)
y_pred = kmeans.fit_predict(arr)
df['kmean_fit'] = y_pred

# tsne will plot the data on a plot
tsne = TSNE()
xe = tsne.fit_transform(arr)
vis_x = xe[:, 0]
vis_y = xe[:, 1]


# --------------------------BOKEH PLOT----------------------------

# Bokeh plot is the plotting interface that I am using for this code.
# It is necessary to install bokeh for using the plotting features

from bokeh.models.callbacks import CustomJS
from bokeh.models import ColumnDataSource, HoverTool, LinearColorMapper, CustomJS, Slider, BooleanFilter, CDSView, Legend, LegendItem
from bokeh.palettes import Category20
from bokeh.transform import linear_cmap, transform
from bokeh.io import output_file, show, output_notebook
from bokeh.plotting import figure
from bokeh.models import TextInput, Div, Paragraph
from bokeh.layouts import column, widgetbox, row, layout

# target labels
y_labels = y_pred

# data source
source = ColumnDataSource(data=dict(
    x=vis_x,
    y=vis_y,
    desc=y_labels,
    message=df['message'],
    labels=["C-" + str(x) for x in y_labels]
))

# Keywords
text_banner = Paragraph(text='Keywords: Slide to specific cluster to see the keywords.', height=45)

# options = sorted(set(source.data['desc']))

bool = BooleanFilter([True if x else False for x in source.data['desc']])


view = CDSView(source=source, filters=[bool])

# WIDGETS
slider = Slider(start=0, end=3, value=0, step=1, title="Cluster #")
slider.js_on_change('value', CustomJS(args=dict(b=bool, source=source),
                                      code="""
                                      const val = cb_obj.value; 
                                      if (val == 3) {
                                            b.booleans = Array.from(source.data['desc'], x=> x = x)
                                      }
                                      else {
                                            b.booleans = Array.from(source.data['desc'], x=> x == val);
                                      }
                                      source.change.emit()
                                      """))

# map colors
mapper = linear_cmap(field_name='desc',
                     palette=Category20[3],
                     low=min(y_labels), high=max(y_labels))

# prepare the figure
plot = figure(plot_width=1200, plot_height=850,
              tools=['lasso_select', 'box_select', 'pan', 'box_zoom', 'reset', 'save', 'tap'],
              title="LDA and Clustering",
              toolbar_location="above")

# plot settings
plot.scatter('x', 'y', size=30,
             source=source, view=view,
             fill_color=mapper,
             line_alpha=0.3,
             line_color="black",
             legend='labels',
             muted_alpha=0.2)

plot.legend.background_fill_alpha = 0.8
plot.legend.location = "top_right"
plot.legend.click_policy = "mute"

# STYLE
slider.sizing_mode = "stretch_width"
slider.margin = 15

text_banner.style = {'color': '#0269A4', 'font-family': 'Helvetica Neue, Helvetica, Arial, sans-serif;',
                     'font-size': '1.1em'}
text_banner.sizing_mode = "scale_both"
text_banner.margin = 20

plot.sizing_mode = "scale_both"
plot.margin = 5

r = row(text_banner)
r.sizing_mode = "stretch_width"

# LAYOUT OF THE PAGE
l = layout([plot],
           [slider],
           [text_banner])
l.sizing_mode = "scale_both"

# show
show(l)