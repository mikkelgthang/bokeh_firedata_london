import pandas as pd
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput, FactorRange, Legend, CheckboxGroup, CustomJS
from bokeh.plotting import figure
from bokeh.palettes import all_palettes
from bokeh.themes import Theme
from bokeh.io import show, curdoc

firedata = pd.read_pickle("./firedata2020.pkl")

daysOrdered = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul','Aug', 'Sep', 'Oct', 'Nov', 'Dec']
x_map = {
    "Hourly": {
        "id": "HourOfCall",
        "time": [str(x) for x in range(1, 25)]
    },
    "Daily": {
        "id": "DayOfCall",
        "time": daysOrdered #[str(x) for x in range(1, 8)]
    },
    "Monhtly": {
        "id": "MonthOfCall",
        "time": months
    },
    "Yearly": {
        "id": "CalYear",
        "time": [str(x) for x in range(2009, 2022)]
    }
}

y_map = {
    "Incident Group": "IncidentGroup",
    "Stop Code Description": "StopCodeDescription",
    "Special Service type": "SpecialServiceType",
    "Property Category": "PropertyCategory",
    "Address Qualifier": "AddressQualifier"
}

data_map = {
    "Normalized": True,
    "Raw": False
}

colors_all = all_palettes['Turbo'][256][20:-20]

df = firedata.copy()

# Prepare axes
x_axis = Select(title="X Axis (Time)", options=list(x_map.keys()), value="Hourly")
y_axis = Select(title="Y Axis (Occurrences)", options=list(y_map.keys()), value="Incident Group")
data_edit = Select(title="Data manipulation", options=list(data_map.keys()), value="Normalized")

def filterData():
    # Group the data by selected time
    group_count = df.groupby([y_map[y_axis.value], x_map[x_axis.value]['id']]).size().unstack(y_map[y_axis.value])
    groups = list(group_count.columns)
    
    if data_map[data_edit.value]:
        # Normalize the data
        total_group = [] 
        for col in group_count:
            total_group.append(sum(group_count[col]))
        group_count = group_count / total_group

    # Add the time to the normalized dataframe
    time = x_map[x_axis.value]['time']
    group_count["time"] = time
    
    # Update color palette
    color_split = len(colors_all) // len(groups)
    colors = [c for i, c in enumerate(colors_all) if i % color_split == 0]
    
    return group_count, groups, time, colors

def updatePlot():
    df, groups, time, colors = filterData()
    
    # Prepare the data to be added to the Bokeh graph
    source = ColumnDataSource(df)
    p = figure(x_range = FactorRange(factors = time),
                title = '{}: {} View, {} Data'.format(y_axis.value,x_axis.value,data_edit.value),
                plot_width = 900, plot_height = 550, toolbar_location='above') #
    bar = {} # to store vbars
    items = []

    for i, group in enumerate(groups):
        strengur = colors[i-1]
        bar[group] = p.vbar(x = 'time', top = group, fill_color = strengur, source = source, muted_alpha = 0.05, muted = True, width = 0.8) 
        items.append((group, [bar[group]])) 

    # Move the legend outside of the figure
    legend = Legend(items = items) 
    p.add_layout(legend, 'right')
    
    p.legend.click_policy = "mute"
    
    # Clear former figure and add new modified
    curdoc().clear()
    curdoc().add_root(column(row(controls), p))

# Set axis controls
controls = [x_axis, y_axis, data_edit]
for control in controls:
    control.on_change('value', lambda attr, old, new: updatePlot())
    
# Initial data load
updatePlot()